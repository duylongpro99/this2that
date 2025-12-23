from __future__ import annotations

from src.doc_extract import DocEvidence, DocExtractInputs
from src.doc_model import normalize_doc_inputs


def test_normalize_doc_inputs_groups_filenames_and_directories() -> None:
    inputs = DocExtractInputs(
        filenames=(
            DocEvidence(
                value="AGENTS.md",
                topic="config_format",
                source="https://example.com/agents",
                version="v1",
            ),
            DocEvidence(
                value=".kiro/steering/*.md",
                topic="config_format",
                source="https://example.com/kiro",
                version="v1",
            ),
        ),
        structural_expectations=(
            DocEvidence(
                value="Required sections: safety and tools.",
                topic="config_format",
                source="https://example.com/agents",
                version="v1",
            ),
        ),
        constraints=(
            DocEvidence(
                value="Max 12,000 tokens per file.",
                topic="config_format",
                source="https://example.com/agents",
                version="v1",
            ),
        ),
        examples=(
            DocEvidence(
                value="# Example\n\nFollow these rules.",
                topic="examples",
                source="https://example.com/agents",
                version="v1",
            ),
        ),
    )

    model = normalize_doc_inputs("codex", "Codex", inputs)

    assert [group.value for group in model.config_files] == ["AGENTS.md"]
    assert [group.value for group in model.config_globs] == [".kiro/steering/*.md"]
    assert [group.value for group in model.config_directories] == [".kiro/steering"]
    assert [group.value for group in model.structural_expectations] == [
        "Required sections: safety and tools."
    ]
    assert [group.value for group in model.constraints] == [
        "Max 12,000 tokens per file."
    ]
    assert [group.value for group in model.examples] == ["# Example\n\nFollow these rules."]
    assert model.versions == ("v1",)


def test_normalize_doc_inputs_aggregates_evidence() -> None:
    inputs = DocExtractInputs(
        filenames=(
            DocEvidence(
                value="AGENTS.md",
                topic="config_format",
                source="https://example.com/agents",
                version="v1",
            ),
            DocEvidence(
                value="AGENTS.md",
                topic="config_format",
                source="https://example.com/agents-v2",
                version="v2",
            ),
        ),
        structural_expectations=(),
        constraints=(),
        examples=(),
    )

    model = normalize_doc_inputs("codex", "Codex", inputs)

    assert len(model.config_files) == 1
    assert len(model.config_files[0].evidence) == 2
    assert model.versions == ("v1", "v2")
