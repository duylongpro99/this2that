from __future__ import annotations

from src import doc_extract
from src.doc_fetch import DocSnippet


def test_extract_filenames_from_snippets() -> None:
    snippet = DocSnippet(
        topic="config_format",
        source="https://example.com/agent-docs",
        content=(
            "Use `AGENTS.md` in the repo root. "
            "Kiro uses `.kiro/steering/*.md` or `.kiro/steering/project.md`.\n"
            "See https://example.com/AGENTS.md for reference."
        ),
        version="v1",
    )

    extracted = doc_extract.extract_doc_inputs([snippet])
    values = {item.value for item in extracted.filenames}

    assert values == {
        "AGENTS.md",
        ".kiro/steering/*.md",
        ".kiro/steering/project.md",
    }


def test_extract_structure_expectations() -> None:
    snippet = DocSnippet(
        topic="config_format",
        source="https://example.com/agent-docs",
        content=(
            "# Instructions\n"
            "## Setup\n"
            "Required sections: safety and tools.\n"
            "Precedence order: project overrides global."
        ),
        version="v1",
    )

    extracted = doc_extract.extract_doc_inputs([snippet])
    values = {item.value for item in extracted.structural_expectations}

    assert "Instructions" in values
    assert "Setup" in values
    assert "Required sections: safety and tools." in values
    assert "Precedence order: project overrides global." in values


def test_extract_constraints() -> None:
    snippet = DocSnippet(
        topic="config_format",
        source="https://example.com/agent-docs",
        content=(
            "Max 12,000 tokens per file.\n"
            "Limit: 64 KB for project instructions.\n"
            "Use markdown headings for sections."
        ),
        version="v1",
    )

    extracted = doc_extract.extract_doc_inputs([snippet])
    values = {item.value for item in extracted.constraints}

    assert "Max 12,000 tokens per file." in values
    assert "Limit: 64 KB for project instructions." in values


def test_extract_examples() -> None:
    snippet = DocSnippet(
        topic="examples",
        source="https://example.com/agent-docs",
        content="# Example\n\nFollow these rules.",
        version="v1",
    )

    extracted = doc_extract.extract_doc_inputs([snippet])
    assert extracted.examples[0].value == "# Example\n\nFollow these rules."
