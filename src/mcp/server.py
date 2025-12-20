"""FastMCP server bootstrap for agentcfg."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable

import tomllib
from importlib import metadata

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

_LOGGER = logging.getLogger("agentcfg.mcp")


def _log_event(event: str, **fields: object) -> None:
    payload = {"event": event, **fields}
    _LOGGER.info(json.dumps(payload, ensure_ascii=True))


class FastMCPLoadError(RuntimeError):
    """Raised when FastMCP is not installed."""


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
        "prompts": [],
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
    """Placeholder MCP resource for agent registry data."""
    return {"agents": []}


def concept_ontology() -> dict[str, object]:
    """Placeholder MCP resource for ontology data."""
    return {"version": "v0", "concepts": []}


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
    _log_event(
        "server_build_start",
        name=metadata_payload["name"],
        version=metadata_payload["version"],
    )
    server = _init_server(FastMCP, metadata_payload)
    _apply_metadata(server, metadata_payload)
    _register_tools(server)
    _register_resources(server)
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
