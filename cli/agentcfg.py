"""Minimal CLI entrypoint for agent config migration."""

from __future__ import annotations

import argparse
import sys
from typing import TextIO


CHUNK_SIZE = 4096


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


def migrate_command(args: argparse.Namespace) -> int:
    input_stream = _open_input(args.input)
    output_stream = _open_output(args.output)
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
    migrate.add_argument("--input", required=True)
    migrate.add_argument("--output", required=True)
    migrate.set_defaults(func=migrate_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
