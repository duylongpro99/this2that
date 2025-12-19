import io

import pytest

from src.renderer.streaming import (
    ChunkedStdoutWriter,
    emit_file_footer,
    emit_file_header,
    iter_chunks,
)


def test_iter_chunks_splits_by_size():
    assert list(iter_chunks("abcdef", 2)) == ["ab", "cd", "ef"]


def test_iter_chunks_rejects_non_positive_size():
    with pytest.raises(ValueError):
        list(iter_chunks("abc", 0))


def test_chunked_stdout_writer_writes_in_chunks():
    buffer = io.StringIO()
    writer = ChunkedStdoutWriter(buffer, chunk_size=3)

    writer.write("hello world")

    assert buffer.getvalue() == "hello world"


def test_chunked_stdout_writer_accepts_line_iterables():
    buffer = io.StringIO()
    writer = ChunkedStdoutWriter(buffer, chunk_size=4)

    writer.write_lines(["one\n", "two\n", "three\n"])

    assert buffer.getvalue() == "one\ntwo\nthree\n"


def test_emit_file_header_and_footer():
    buffer = io.StringIO()

    emit_file_header(buffer, "AGENTS.md")
    emit_file_footer(buffer, "AGENTS.md")

    assert buffer.getvalue() == "BEGIN FILE AGENTS.md\nEND FILE AGENTS.md\n"
