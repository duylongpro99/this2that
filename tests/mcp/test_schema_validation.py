from __future__ import annotations

from src.mcp import server as mcp_server


def test_validate_mcp_schemas_passes() -> None:
    metadata = mcp_server._server_metadata()

    mcp_server.validate_mcp_schemas(metadata)
