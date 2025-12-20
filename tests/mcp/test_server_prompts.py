from __future__ import annotations

from src.mcp import server as mcp_server


class _DecoratorServer:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def prompt(self, name: str | None = None, description: str | None = None):
        def decorator(func):
            self.prompts.append(name or func.__name__)
            return func

        return decorator


class _DirectServer:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def prompt(self, func):
        self.prompts.append(func.__name__)
        return func


def test_register_prompts_uses_decorator_signature() -> None:
    server = _DecoratorServer()

    mcp_server._register_prompts(server)

    assert server.prompts == [name for name, _ in mcp_server.PROMPT_DEFINITIONS]


def test_register_prompts_falls_back_to_direct_registration() -> None:
    server = _DirectServer()

    mcp_server._register_prompts(server)

    assert server.prompts == [name for name, _ in mcp_server.PROMPT_DEFINITIONS]
