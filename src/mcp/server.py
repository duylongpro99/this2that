"""FastMCP server bootstrap for agentcfg."""

from __future__ import annotations

import inspect
import json
import logging
import types
from pathlib import Path
from typing import Any, Callable, Union, get_args, get_origin, get_type_hints

import tomllib
from importlib import metadata

from src.registry import default_registry

SERVER_NAME = "agentcfg-migrator"
SERVER_DESCRIPTION = "Agent configuration migrator MCP server."
DEFAULT_VERSION = "0.0.0"
TOOL_DEFINITIONS = (
    ("detect_agent_config", "Detect candidate agent configs in a workspace."),
    ("parse_config", "Parse config files into a normalized representation."),
    ("map_config", "Map source configs to a target agent representation."),
    ("render_target", "Render target agent config output."),
)
RESOURCE_DEFINITIONS = (
    ("agent_registry", "Supported agents and config artifacts."),
    ("concept_ontology", "Normalized concept ontology definitions."),
)
PROMPT_DEFINITIONS = (
    ("migrate_config_prompt", "Guide migrating config from one agent to another."),
)

_LOGGER = logging.getLogger("agentcfg.mcp")
_NONE_TYPE = type(None)
_PRIMITIVE_SCHEMA_TYPES = {str, int, float, bool, object}


def _log_event(event: str, **fields: object) -> None:
    payload = {"event": event, **fields}
    _LOGGER.info(json.dumps(payload, ensure_ascii=True))


class FastMCPLoadError(RuntimeError):
    """Raised when FastMCP is not installed."""


class SchemaValidationError(ValueError):
    """Raised when MCP schema validation fails."""


def _is_schema_type(annotation: object) -> bool:
    if annotation in _PRIMITIVE_SCHEMA_TYPES:
        return True
    origin = get_origin(annotation)
    if origin in (list, dict):
        args = get_args(annotation)
        if origin is list:
            if len(args) != 1:
                return False
            return _is_schema_type(args[0])
        if len(args) != 2 or args[0] is not str:
            return False
        return _is_schema_type(args[1])
    if origin in (Union, types.UnionType):
        return all(arg is _NONE_TYPE or _is_schema_type(arg) for arg in get_args(annotation))
    return False


def _validate_callable_schema(label: str, func: Callable[..., Any]) -> list[str]:
    errors: list[str] = []
    signature = inspect.signature(func)
    type_hints = get_type_hints(func, globalns=globals(), localns=locals())
    for param in signature.parameters.values():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            errors.append(f"{label} uses varargs which are not MCP-schema compatible")
            continue
        annotation = type_hints.get(param.name, param.annotation)
        if annotation is inspect._empty:
            errors.append(f"{label} missing type annotation for '{param.name}'")
            continue
        if not _is_schema_type(annotation):
            errors.append(f"{label} has unsupported type annotation for '{param.name}'")
    return_annotation = type_hints.get("return", signature.return_annotation)
    if return_annotation is inspect._empty:
        errors.append(f"{label} missing return type annotation")
    elif not _is_schema_type(return_annotation):
        errors.append(f"{label} has unsupported return type annotation")
    return errors


def _validate_definition_group(
    group_name: str, definitions: tuple[tuple[str, str], ...]
) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, definition in enumerate(definitions):
        if not isinstance(definition, tuple) or len(definition) != 2:
            errors.append(f"{group_name}[{index}] must be a (name, description) tuple")
            continue
        name, description = definition
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{group_name}[{index}] has invalid name")
        if name in seen:
            errors.append(f"{group_name} '{name}' is duplicated")
        else:
            seen.add(name)
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{group_name}[{index}] has invalid description")
        func = globals().get(name)
        if func is None or not callable(func):
            errors.append(f"{group_name} '{name}' missing callable implementation")
            continue
        errors.extend(_validate_callable_schema(f"{group_name} '{name}'", func))
    return errors


def _validate_server_metadata(metadata_payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("name", "version", "description"):
        value = metadata_payload.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"metadata '{key}' must be a non-empty string")
    capabilities = metadata_payload.get("capabilities")
    if not isinstance(capabilities, dict):
        return errors + ["metadata 'capabilities' must be a dict"]
    expected = {
        "tools": [name for name, _ in TOOL_DEFINITIONS],
        "resources": [name for name, _ in RESOURCE_DEFINITIONS],
        "prompts": [name for name, _ in PROMPT_DEFINITIONS],
    }
    for key, expected_names in expected.items():
        value = capabilities.get(key)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"metadata 'capabilities.{key}' must be a list of strings")
            continue
        if value != expected_names:
            errors.append(f"metadata 'capabilities.{key}' does not match definitions")
    return errors


def _validate_mcp_schemas(metadata_payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_definition_group("tool", TOOL_DEFINITIONS))
    errors.extend(_validate_definition_group("resource", RESOURCE_DEFINITIONS))
    errors.extend(_validate_definition_group("prompt", PROMPT_DEFINITIONS))
    errors.extend(_validate_server_metadata(metadata_payload))
    return errors


def validate_mcp_schemas(metadata_payload: dict[str, Any]) -> None:
    errors = _validate_mcp_schemas(metadata_payload)
    if not errors:
        return
    message = "MCP schema validation failed:\n" + "\n".join(f"- {error}" for error in errors)
    raise SchemaValidationError(message)


def _load_fastmcp() -> type:
    _log_event("fastmcp_load_start")
    try:
        from fastmcp import FastMCP  # type: ignore[import-not-found]

        _log_event("fastmcp_load_success", provider="fastmcp")
        return FastMCP
    except ImportError:
        try:
            from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

            _log_event("fastmcp_load_success", provider="mcp.server.fastmcp")
            return FastMCP
        except ImportError as exc:
            _log_event("fastmcp_load_error", message=str(exc))
            raise FastMCPLoadError(
                "FastMCP is required to run the MCP server. "
                "Install it in the active environment before starting the server."
            ) from exc


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_version_from_pyproject() -> str | None:
    pyproject = _project_root() / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    return data.get("project", {}).get("version")


def _server_version() -> str:
    try:
        return metadata.version("agentcfg")
    except metadata.PackageNotFoundError:
        return _load_version_from_pyproject() or DEFAULT_VERSION


def _server_capabilities() -> dict[str, list[str]]:
    return {
        "tools": [name for name, _ in TOOL_DEFINITIONS],
        "resources": [name for name, _ in RESOURCE_DEFINITIONS],
        "prompts": [name for name, _ in PROMPT_DEFINITIONS],
    }


def _server_metadata() -> dict[str, Any]:
    return {
        "name": SERVER_NAME,
        "version": _server_version(),
        "capabilities": _server_capabilities(),
        "description": SERVER_DESCRIPTION,
    }


def _init_server(FastMCP: type, metadata_payload: dict[str, Any]) -> Any:
    try:
        return FastMCP(
            metadata_payload["name"],
            version=metadata_payload["version"],
            description=metadata_payload["description"],
            capabilities=metadata_payload["capabilities"],
        )
    except TypeError:
        return FastMCP(metadata_payload["name"])


def detect_agent_config(workspace_path: str) -> dict[str, object]:
    """Placeholder MCP tool for workspace detection."""
    return {"workspace_path": workspace_path, "candidates": []}


def parse_config(agent: str, files: list[str]) -> dict[str, object]:
    """Placeholder MCP tool for parsing agent configs."""
    return {"agent": agent, "files": files, "sections": []}


def map_config(
    source_ir: dict[str, object],
    target_agent: str,
    doc_snippets: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Placeholder MCP tool for mapping source configs to a target agent."""
    return {
        "source": source_ir,
        "target_agent": target_agent,
        "doc_snippets": doc_snippets or [],
        "mapped_sections": [],
    }


def render_target(target_ir: dict[str, object]) -> dict[str, object]:
    """Placeholder MCP tool for rendering target config output."""
    return {"target": target_ir, "files": []}


def agent_registry() -> dict[str, object]:
    """MCP resource for agent registry data."""
    return default_registry().to_dict()


def concept_ontology() -> dict[str, object]:
    """Placeholder MCP resource for ontology data."""
    return {"version": "v0", "concepts": []}


def migrate_config_prompt(from_agent: str, to_agent: str, input_path: str) -> str:
    """Placeholder MCP prompt for guiding a migration workflow."""
    return (
        "Migrate agent configuration from "
        f"{from_agent} to {to_agent} using input at {input_path}. "
        "Detect the source, parse into a normalized representation, map concepts to the target, "
        "and render the output with streamed sections."
    )


def _register_tools(server: Any) -> None:
    tool_attr = getattr(server, "tool", None)
    if not callable(tool_attr):
        _log_event("tool_register_skipped", reason="tool_not_available")
        return
    for name, description in TOOL_DEFINITIONS:
        func = globals()[name]
        try:
            decorator = tool_attr(name=name, description=description)
            decorator(func)
        except TypeError:
            try:
                tool_attr(func)
            except Exception as exc:  # pragma: no cover - defensive logging
                _log_event("tool_register_error", tool=name, message=str(exc))
                continue
        _log_event("tool_register_complete", tool=name)


def _register_resources(server: Any) -> None:
    resource_attr = getattr(server, "resource", None)
    if not callable(resource_attr):
        _log_event("resource_register_skipped", reason="resource_not_available")
        return
    for name, description in RESOURCE_DEFINITIONS:
        func = globals()[name]
        try:
            decorator = resource_attr(name=name, description=description)
            decorator(func)
        except TypeError:
            try:
                resource_attr(func)
            except Exception as exc:  # pragma: no cover - defensive logging
                _log_event("resource_register_error", resource=name, message=str(exc))
                continue
        _log_event("resource_register_complete", resource=name)


def _register_prompts(server: Any) -> None:
    prompt_attr = getattr(server, "prompt", None)
    if not callable(prompt_attr):
        _log_event("prompt_register_skipped", reason="prompt_not_available")
        return
    for name, description in PROMPT_DEFINITIONS:
        func = globals()[name]
        try:
            decorator = prompt_attr(name=name, description=description)
            decorator(func)
        except TypeError:
            try:
                prompt_attr(func)
            except Exception as exc:  # pragma: no cover - defensive logging
                _log_event("prompt_register_error", prompt=name, message=str(exc))
                continue
        _log_event("prompt_register_complete", prompt=name)


def _apply_metadata(server: Any, metadata_payload: dict[str, Any]) -> None:
    if hasattr(server, "metadata"):
        try:
            server.metadata.update(metadata_payload)
        except AttributeError:
            server.metadata = dict(metadata_payload)
    else:
        server.metadata = dict(metadata_payload)


def build_server() -> Any:
    FastMCP = _load_fastmcp()
    metadata_payload = _server_metadata()
    validate_mcp_schemas(metadata_payload)
    _log_event(
        "server_build_start",
        name=metadata_payload["name"],
        version=metadata_payload["version"],
    )
    server = _init_server(FastMCP, metadata_payload)
    _apply_metadata(server, metadata_payload)
    _register_tools(server)
    _register_resources(server)
    _register_prompts(server)
    _log_event("server_build_complete", name=metadata_payload["name"])
    return server


def _run_with_stdio(server: Any) -> None:
    if hasattr(server, "run_stdio"):
        _log_event("server_run_stdio", method="run_stdio")
        server.run_stdio()
        return
    run: Callable[..., Any] = server.run
    try:
        _log_event("server_run_stdio", method="run", transport="stdio")
        run(transport="stdio")
    except TypeError:
        _log_event("server_run_stdio", method="run", transport="default")
        run()


def run_stdio() -> None:
    server = build_server()
    _run_with_stdio(server)
