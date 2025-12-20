"""Registry plugin and config extensions."""

from __future__ import annotations

from importlib import metadata
import logging
import os
from pathlib import Path
import tomllib
from typing import Iterable, Mapping

from .models import AgentArtifact, AgentDefinition, ArtifactKind

LOGGER = logging.getLogger(__name__)

PLUGIN_GROUP = "agentcfg.registry"
REGISTRY_CONFIG_ENV = "AGENTCFG_REGISTRY_CONFIG"
DEFAULT_CONFIG_NAME = "agentcfg.registry.toml"


def load_registry_extensions(
    *,
    config_path: str | None = None,
    entry_points: Iterable[metadata.EntryPoint] | None = None,
) -> tuple[AgentDefinition, ...]:
    extensions: list[AgentDefinition] = []
    config_path = config_path or os.getenv(REGISTRY_CONFIG_ENV)
    if not config_path:
        default_path = Path.cwd() / DEFAULT_CONFIG_NAME
        if default_path.exists():
            config_path = str(default_path)
    if config_path:
        extensions.extend(_load_from_config(Path(config_path)))
    extensions.extend(_load_from_entry_points(entry_points))
    return tuple(extensions)


def merge_agent_definitions(
    base: tuple[AgentDefinition, ...],
    extensions: tuple[AgentDefinition, ...],
) -> tuple[AgentDefinition, ...]:
    merged = list(base)
    seen = {agent.agent_id for agent in base}
    for entry in extensions:
        if entry.agent_id in seen:
            LOGGER.warning(
                "Skipping plugin agent '%s' because it collides with a core registry entry.",
                entry.agent_id,
            )
            continue
        merged.append(entry)
        seen.add(entry.agent_id)
    return tuple(merged)


def _load_from_config(path: Path) -> list[AgentDefinition]:
    if not path.exists():
        LOGGER.warning("Registry config path '%s' does not exist.", path)
        return []
    try:
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        LOGGER.warning("Failed to read registry config '%s': %s", path, exc)
        return []
    return _parse_registry_payload(payload)


def _load_from_entry_points(
    entry_points: Iterable[metadata.EntryPoint] | None,
) -> list[AgentDefinition]:
    entries = entry_points or _discover_entry_points()
    definitions: list[AgentDefinition] = []
    for entry in entries:
        try:
            provider = entry.load()
            result = provider()
            payload = _coerce_definitions(result, source=f"plugin:{entry.name}")
        except Exception as exc:  # noqa: BLE001 - best-effort plugin loading
            LOGGER.warning("Failed to load registry plugin '%s': %s", entry.name, exc)
            continue
        definitions.extend(payload)
    return definitions


def _discover_entry_points() -> Iterable[metadata.EntryPoint]:
    points = metadata.entry_points()
    if hasattr(points, "select"):
        return points.select(group=PLUGIN_GROUP)
    return points.get(PLUGIN_GROUP, [])


def _parse_registry_payload(payload: Mapping[str, object]) -> list[AgentDefinition]:
    registry_payload = payload.get("agent_registry")
    if not isinstance(registry_payload, Mapping):
        return []
    agents_payload = registry_payload.get("agents")
    if not isinstance(agents_payload, list):
        return []
    definitions: list[AgentDefinition] = []
    for agent_payload in agents_payload:
        if not isinstance(agent_payload, Mapping):
            LOGGER.warning("Skipping invalid registry agent entry: %r", agent_payload)
            continue
        try:
            definitions.append(_definition_from_mapping(agent_payload))
        except ValueError as exc:
            LOGGER.warning("Skipping registry agent entry: %s", exc)
    return definitions


def _coerce_definitions(
    result: object,
    *,
    source: str,
) -> list[AgentDefinition]:
    if result is None:
        return []
    if isinstance(result, AgentDefinition):
        return [result]
    if isinstance(result, Mapping):
        return [_definition_from_mapping(result)]
    if isinstance(result, Iterable):
        definitions: list[AgentDefinition] = []
        for item in result:
            if isinstance(item, AgentDefinition):
                definitions.append(item)
                continue
            if isinstance(item, Mapping):
                definitions.append(_definition_from_mapping(item))
                continue
            raise ValueError(f"Unsupported registry plugin item from {source}: {item!r}")
        return definitions
    raise ValueError(f"Unsupported registry plugin payload from {source}: {result!r}")


def _definition_from_mapping(payload: Mapping[str, object]) -> AgentDefinition:
    agent_id = _require_str(payload, "agent_id")
    display_name = _require_str(payload, "display_name")
    artifacts_payload = payload.get("artifacts")
    if not isinstance(artifacts_payload, list) or not artifacts_payload:
        raise ValueError(f"agent '{agent_id}' must define at least one artifact")
    artifacts = tuple(_artifact_from_mapping(agent_id, item) for item in artifacts_payload)
    return AgentDefinition(
        agent_id=agent_id,
        display_name=display_name,
        aliases=_as_tuple(payload.get("aliases")),
        config_filenames=_as_tuple(payload.get("config_filenames")),
        directory_patterns=_as_tuple(payload.get("directory_patterns")),
        precedence_rules=_as_tuple(payload.get("precedence_rules")),
        artifacts=artifacts,
    )


def _artifact_from_mapping(agent_id: str, payload: object) -> AgentArtifact:
    if not isinstance(payload, Mapping):
        raise ValueError(f"agent '{agent_id}' artifact must be a mapping")
    pattern = _require_str(payload, "pattern")
    kind_raw = _require_str(payload, "kind")
    try:
        kind = ArtifactKind(kind_raw)
    except ValueError as exc:
        raise ValueError(f"agent '{agent_id}' artifact kind '{kind_raw}' is not supported") from exc
    description = payload.get("description")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"agent '{agent_id}' artifact description must be a string")
    return AgentArtifact(pattern=pattern, kind=kind, description=description)


def _require_str(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing required '{key}' value")
    return value


def _as_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        items = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("registry list entries must be strings")
            items.append(item)
        return tuple(items)
    raise ValueError("registry list entries must be arrays of strings")
