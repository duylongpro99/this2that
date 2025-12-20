from __future__ import annotations

from src.mcp import server as mcp_server


class _StdioServer:
    def __init__(self) -> None:
        self.called = False

    def run_stdio(self) -> None:
        self.called = True


class _RunServer:
    def __init__(self) -> None:
        self.called_with: tuple[tuple[object, ...], dict[str, object]] | None = None

    def run(self, *args: object, **kwargs: object) -> None:
        self.called_with = (args, kwargs)


class _RunServerNoKwargs:
    def __init__(self) -> None:
        self.called = False

    def run(self) -> None:
        self.called = True


def test_run_with_stdio_prefers_run_stdio() -> None:
    server = _StdioServer()

    mcp_server._run_with_stdio(server)

    assert server.called is True


def test_run_with_stdio_uses_transport_kwarg() -> None:
    server = _RunServer()

    mcp_server._run_with_stdio(server)

    assert server.called_with == ((), {"transport": "stdio"})


def test_run_with_stdio_falls_back_when_transport_not_supported() -> None:
    server = _RunServerNoKwargs()

    mcp_server._run_with_stdio(server)

    assert server.called is True
