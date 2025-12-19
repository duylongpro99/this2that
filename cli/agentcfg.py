"""Minimal CLI entrypoint for agent config migration."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO


CHUNK_SIZE = 4096
WORKSPACE_MARKERS = (".git", "pyproject.toml", "package.json")
DEFAULT_AGENT_FILES = {
    "claude": "CLAUDE.md",
    "codex": "AGENTS.md",
    "gemini": "GEMINI.md",
}


def _open_input(path: str) -> TextIO:
    if path == "-":
        return sys.stdin
    return open(path, "r", encoding="utf-8")


def _open_output(path: str) -> TextIO:
    if path == "-":
        return sys.stdout
    return open(path, "w", encoding="utf-8")


def _stream_copy(source: TextIO, target: TextIO) -> None:
    while True:
        chunk = source.read(CHUNK_SIZE)
        if chunk == "":
            break
        target.write(chunk)
        target.flush()


def _normalize_agent_name(name: str) -> str:
    return name.strip().lower()


def _find_workspace_root(start: Path) -> Path:
    for current in (start, *start.parents):
        for marker in WORKSPACE_MARKERS:
            if (current / marker).exists():
                return current
    return start


def _default_agent_file(agent: str) -> str:
    if agent not in DEFAULT_AGENT_FILES:
        raise ValueError(
            f"auto-detection is not available for agent '{agent}'; "
            "provide explicit --input/--output paths"
        )
    return DEFAULT_AGENT_FILES[agent]


def _resolve_paths(args: argparse.Namespace) -> tuple[str, str]:
    workspace_root = _find_workspace_root(Path.cwd())
    source_agent = _normalize_agent_name(args.source_agent)
    target_agent = _normalize_agent_name(args.target_agent)

    if args.input in (None, ""):
        input_path = workspace_root / _default_agent_file(source_agent)
        if not input_path.is_file():
            raise FileNotFoundError(
                f"default input '{input_path}' not found; "
                "provide --input or run from the workspace root"
            )
        resolved_input = str(input_path)
    else:
        resolved_input = args.input

    if args.output in (None, ""):
        output_path = workspace_root / _default_agent_file(target_agent)
        resolved_output = str(output_path)
    else:
        resolved_output = args.output

    return resolved_input, resolved_output


def migrate_command(args: argparse.Namespace) -> int:
    try:
        input_path, output_path = _resolve_paths(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    input_stream = _open_input(input_path)
    output_stream = sys.stdout if args.dry_run else _open_output(output_path)
    try:
        # Placeholder until the mapping/rendering pipeline is wired in.
        _stream_copy(input_stream, output_stream)
    finally:
        if input_stream is not sys.stdin:
            input_stream.close()
        if output_stream is not sys.stdout:
            output_stream.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentcfg")
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate = subparsers.add_parser("migrate", help="Migrate config between agents.")
    migrate.add_argument("--from", dest="source_agent", required=True)
    migrate.add_argument("--to", dest="target_agent", required=True)
    migrate.add_argument("--input")
    migrate.add_argument("--output")
    migrate.add_argument("--dry-run", action="store_true")
    migrate.set_defaults(func=migrate_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
