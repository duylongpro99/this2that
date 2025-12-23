"""Doc extraction helpers for AgentDocModel inputs."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence

from src.doc_fetch import DocSnippet

_FILENAME_PATTERN = re.compile(r"`?([A-Za-z0-9._/-]+\.md)`?", re.IGNORECASE)
_WILDCARD_PATTERN = re.compile(r"`?([A-Za-z0-9._/-]+/\*\.md)`?", re.IGNORECASE)
_CONSTRAINT_PATTERN = re.compile(
    r"\b(\d[\d,\.]*)\s*(bytes?|kb|mb|characters?|tokens?|lines?)\b",
    re.IGNORECASE,
)
_STRUCTURE_HINT_TERMS = (
    "section",
    "sections",
    "heading",
    "headings",
    "structure",
    "format",
    "schema",
    "layout",
    "precedence",
    "override",
)


@dataclass(frozen=True)
class DocEvidence:
    value: str
    topic: str
    source: str
    version: str | None


@dataclass(frozen=True)
class DocExtractInputs:
    filenames: tuple[DocEvidence, ...]
    structural_expectations: tuple[DocEvidence, ...]
    constraints: tuple[DocEvidence, ...]
    examples: tuple[DocEvidence, ...]


def extract_doc_inputs(snippets: Sequence[DocSnippet]) -> DocExtractInputs:
    filenames: list[DocEvidence] = []
    structure: list[DocEvidence] = []
    constraints: list[DocEvidence] = []
    examples: list[DocEvidence] = []

    for snippet in snippets:
        content = snippet.content or ""
        for value in _extract_filenames(content):
            filenames.append(_evidence(value, snippet))
        for value in _extract_structure(content):
            structure.append(_evidence(value, snippet))
        for value in _extract_constraints(content):
            constraints.append(_evidence(value, snippet))
        if snippet.topic == "examples" and content.strip():
            examples.append(_evidence(content.strip(), snippet))

    return DocExtractInputs(
        filenames=_dedupe(filenames),
        structural_expectations=_dedupe(structure),
        constraints=_dedupe(constraints),
        examples=_dedupe(examples),
    )


def _evidence(value: str, snippet: DocSnippet) -> DocEvidence:
    return DocEvidence(
        value=value,
        topic=snippet.topic,
        source=snippet.source,
        version=snippet.version,
    )


def _extract_filenames(content: str) -> Iterable[str]:
    candidates = list(_FILENAME_PATTERN.findall(content))
    candidates.extend(_WILDCARD_PATTERN.findall(content))
    seen: set[str] = set()
    for candidate in candidates:
        if "://" in candidate or candidate.startswith("//"):
            continue
        value = candidate.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        yield value


def _extract_structure(content: str) -> Iterable[str]:
    seen: set[str] = set()
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading and heading not in seen:
                seen.add(heading)
                yield heading
            continue
        lowered = stripped.lower()
        if any(term in lowered for term in _STRUCTURE_HINT_TERMS):
            if stripped not in seen:
                seen.add(stripped)
                yield stripped


def _extract_constraints(content: str) -> Iterable[str]:
    seen: set[str] = set()
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _CONSTRAINT_PATTERN.search(stripped):
            if stripped not in seen:
                seen.add(stripped)
                yield stripped


def _dedupe(items: Iterable[DocEvidence]) -> tuple[DocEvidence, ...]:
    seen: set[tuple[str, str, str, str | None]] = set()
    result: list[DocEvidence] = []
    for item in items:
        key = (item.value, item.topic, item.source, item.version)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return tuple(result)
