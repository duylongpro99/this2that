"""Streaming helpers for chunked output emission."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TextIO


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
