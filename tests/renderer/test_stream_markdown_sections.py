import io

from src.renderer.streaming import stream_markdown_sections


class RecordingTarget:
    def __init__(self) -> None:
        self._buffer = io.StringIO()
        self.flush_count = 0

    def write(self, text: str) -> int:
        return self._buffer.write(text)

    def flush(self) -> None:
        self.flush_count += 1

    def getvalue(self) -> str:
        return self._buffer.getvalue()


def test_stream_markdown_sections_flushes_per_heading_section():
    source_text = (
        "Intro line\n"
        "\n"
        "## First section\n"
        "Line A\n"
        "```python\n"
        "## Not a heading\n"
        "```\n"
        "## Second section\n"
        "Line B\n"
    )
    source = io.StringIO(source_text)
    target = RecordingTarget()

    stream_markdown_sections(source, target)

    assert target.getvalue() == source_text
    assert target.flush_count == 3
