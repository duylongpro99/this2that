"""Minimal CLI entrypoint for agent config migration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from src.registry import resolve_agent_id
from src.renderer.streaming import emit_file_footer, emit_file_header, stream_markdown_sections


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
    source_agent = resolve_agent_id(args.source_agent)
    target_agent = resolve_agent_id(args.target_agent)

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


def _emit_log(args: argparse.Namespace, event: str, **fields: str) -> None:
    if not (args.verbose or args.json_log):
        return
    if args.json_log:
        payload = {"event": event, **fields}
        print(json.dumps(payload, ensure_ascii=True), file=sys.stderr)
        return
    details = " ".join(f"{key}={value}" for key, value in fields.items())
    message = f"{event} {details}".strip()
    print(message, file=sys.stderr)


def migrate_command(args: argparse.Namespace) -> int:
    try:
        input_path, output_path = _resolve_paths(args)
    except (FileNotFoundError, ValueError) as exc:
        if args.json_log:
            _emit_log(args, "error", message=str(exc))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2

    _emit_log(
        args,
        "resolved_paths",
        input=input_path,
        output=output_path,
        dry_run=str(args.dry_run),
    )
    input_stream = _open_input(input_path)
    output_stream = sys.stdout if args.dry_run else _open_output(output_path)
    try:
        # Placeholder until the mapping/rendering pipeline is wired in.
        _emit_log(args, "stream_start")
        if output_stream is sys.stdout:
            emit_file_header(output_stream, output_path)
            stream_markdown_sections(input_stream, output_stream)
            emit_file_footer(output_stream, output_path)
        else:
            _stream_copy(input_stream, output_stream)
        _emit_log(args, "stream_end")
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
    migrate.add_argument("--verbose", action="store_true")
    migrate.add_argument("--json-log", action="store_true")
    migrate.set_defaults(func=migrate_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
