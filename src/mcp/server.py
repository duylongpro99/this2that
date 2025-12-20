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
        "tools": [],
        "resources": [],
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
