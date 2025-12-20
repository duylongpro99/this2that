from __future__ import annotations

from src.mcp import server as mcp_server


class _DecoratorServer:
    def __init__(self) -> None:
        self.resources: list[str] = []

    def resource(self, name: str | None = None, description: str | None = None):
        def decorator(func):
            self.resources.append(name or func.__name__)
            return func

        return decorator


class _DirectServer:
    def __init__(self) -> None:
        self.resources: list[str] = []

    def resource(self, func):
        self.resources.append(func.__name__)
        return func


def test_register_resources_uses_decorator_signature() -> None:
    server = _DecoratorServer()

    mcp_server._register_resources(server)

    assert server.resources == [name for name, _ in mcp_server.RESOURCE_DEFINITIONS]


def test_register_resources_falls_back_to_direct_registration() -> None:
    server = _DirectServer()

    mcp_server._register_resources(server)

    assert server.resources == [name for name, _ in mcp_server.RESOURCE_DEFINITIONS]
