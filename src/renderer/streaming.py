"""Streaming helpers for chunked output emission."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import TextIO


FILE_BEGIN_MARKER = "BEGIN FILE"
FILE_END_MARKER = "END FILE"
HEADING_PATTERN = re.compile(r"^#{1,6}\s")


def iter_chunks(text: str, chunk_size: int) -> Iterable[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if text == "":
        return ()
    return (text[index : index + chunk_size] for index in range(0, len(text), chunk_size))


class ChunkedStdoutWriter:
    def __init__(self, target: TextIO, *, chunk_size: int = 4096) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        self._target = target
        self._chunk_size = chunk_size

    @property
    def chunk_size(self) -> int:
        return self._chunk_size

    def write(self, text: str) -> None:
        for chunk in iter_chunks(text, self._chunk_size):
            self._target.write(chunk)

    def write_lines(self, lines: Iterable[str]) -> None:
        for line in lines:
            self.write(line)


def emit_file_header(target: TextIO, filename: str) -> None:
    target.write(f"{FILE_BEGIN_MARKER} {filename}\n")
    target.flush()


def emit_file_footer(target: TextIO, filename: str) -> None:
    target.write(f"{FILE_END_MARKER} {filename}\n")
    target.flush()


def stream_markdown_sections(source: Iterable[str], target: TextIO) -> None:
    buffer: list[str] = []
    in_code_block = False

    def flush_buffer() -> None:
        if not buffer:
            return
        target.write("".join(buffer))
        target.flush()
        buffer.clear()

    for line in source:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
        if not in_code_block and HEADING_PATTERN.match(line):
            flush_buffer()
        buffer.append(line)

    flush_buffer()


def stream_markdown_files(files: Iterable[tuple[str, Iterable[str]]], target: TextIO) -> None:
    for filename, source in files:
        emit_file_header(target, filename)
        stream_markdown_sections(source, target)
        emit_file_footer(target, filename)
