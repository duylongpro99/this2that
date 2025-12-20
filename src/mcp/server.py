"""FastMCP server bootstrap for agentcfg."""

from __future__ import annotations

from typing import Any, Callable


class FastMCPLoadError(RuntimeError):
    """Raised when FastMCP is not installed."""


def _load_fastmcp() -> type:
    try:
        from fastmcp import FastMCP  # type: ignore[import-not-found]

        return FastMCP
    except ImportError:
        try:
            from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

            return FastMCP
        except ImportError as exc:
            raise FastMCPLoadError(
                "FastMCP is required to run the MCP server. "
                "Install it in the active environment before starting the server."
            ) from exc


def build_server() -> Any:
    FastMCP = _load_fastmcp()
    server = FastMCP("agentcfg-migrator")
    return server


def _run_with_stdio(server: Any) -> None:
    if hasattr(server, "run_stdio"):
        server.run_stdio()
        return
    run: Callable[..., Any] = server.run
    try:
        run(transport="stdio")
    except TypeError:
        run()


def run_stdio() -> None:
    server = build_server()
    _run_with_stdio(server)
