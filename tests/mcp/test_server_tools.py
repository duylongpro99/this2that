from __future__ import annotations

from src.mcp import server as mcp_server


class _DecoratorServer:
    def __init__(self) -> None:
        self.tools: list[str] = []

    def tool(self, name: str | None = None, description: str | None = None):
        def decorator(func):
            self.tools.append(name or func.__name__)
            return func

        return decorator


class _DirectServer:
    def __init__(self) -> None:
        self.tools: list[str] = []

    def tool(self, func):
        self.tools.append(func.__name__)
        return func


def test_register_tools_uses_decorator_signature() -> None:
    server = _DecoratorServer()

    mcp_server._register_tools(server)

    assert server.tools == [name for name, _ in mcp_server.TOOL_DEFINITIONS]


def test_register_tools_falls_back_to_direct_registration() -> None:
    server = _DirectServer()

    mcp_server._register_tools(server)

    assert server.tools == [name for name, _ in mcp_server.TOOL_DEFINITIONS]
