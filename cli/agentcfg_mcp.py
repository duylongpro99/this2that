"""FastMCP server entrypoint for agentcfg."""

from __future__ import annotations

import sys

from src.mcp.server import FastMCPLoadError, run_stdio


def main() -> int:
    try:
        run_stdio()
    except FastMCPLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
