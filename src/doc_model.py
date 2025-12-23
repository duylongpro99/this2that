"""Normalize extracted documentation into AgentDocModel hints."""

from __future__ import annotations

from dataclasses import dataclass
import posixpath
from typing import Iterable, Sequence

from src.doc_extract import DocEvidence, DocExtractInputs


@dataclass(frozen=True)
class DocValueGroup:
    value: str
    evidence: tuple[DocEvidence, ...]


@dataclass(frozen=True)
class AgentDocModel:
    agent_id: str
    agent_name: str
    config_files: tuple[DocValueGroup, ...]
    config_globs: tuple[DocValueGroup, ...]
    config_directories: tuple[DocValueGroup, ...]
    structural_expectations: tuple[DocValueGroup, ...]
    constraints: tuple[DocValueGroup, ...]
    examples: tuple[DocValueGroup, ...]
    versions: tuple[str, ...]
    warnings: tuple[str, ...] = ()


def normalize_doc_inputs(
    agent_id: str,
    agent_name: str,
    inputs: DocExtractInputs,
) -> AgentDocModel:
    file_groups, glob_groups = _group_filenames(inputs.filenames)
    directory_groups = _group_directories(file_groups + glob_groups)
    structure_groups = _group_values(inputs.structural_expectations)
    constraint_groups = _group_values(inputs.constraints)
    example_groups = _group_values(inputs.examples)
    versions = _collect_versions(
        file_groups,
        glob_groups,
        directory_groups,
        structure_groups,
        constraint_groups,
        example_groups,
    )
    warnings = _collect_warnings(file_groups, glob_groups, versions)
    return AgentDocModel(
        agent_id=agent_id,
        agent_name=agent_name,
        config_files=tuple(file_groups),
        config_globs=tuple(glob_groups),
        config_directories=tuple(directory_groups),
        structural_expectations=tuple(structure_groups),
        constraints=tuple(constraint_groups),
        examples=tuple(example_groups),
        versions=versions,
        warnings=warnings,
    )


def _group_filenames(
    items: Sequence[DocEvidence],
) -> tuple[list[DocValueGroup], list[DocValueGroup]]:
    file_groups: list[DocValueGroup] = []
    glob_groups: list[DocValueGroup] = []
    file_index: dict[str, int] = {}
    glob_index: dict[str, int] = {}

    for item in items:
        normalized = item.value.strip()
        if not normalized:
            continue
        if _is_glob(normalized):
            _append_group(glob_groups, glob_index, normalized, item)
        else:
            _append_group(file_groups, file_index, normalized, item)

    return file_groups, glob_groups


def _group_directories(
    groups: Sequence[DocValueGroup],
) -> list[DocValueGroup]:
    directory_groups: list[DocValueGroup] = []
    directory_index: dict[str, int] = {}

    for group in groups:
        directory = _dirname(group.value)
        if not directory:
            continue
        for evidence in group.evidence:
            _append_group(directory_groups, directory_index, directory, evidence)

    return directory_groups


def _group_values(items: Sequence[DocEvidence]) -> list[DocValueGroup]:
    groups: list[DocValueGroup] = []
    index: dict[str, int] = {}
    for item in items:
        normalized = item.value.strip()
        if not normalized:
            continue
        _append_group(groups, index, normalized, item)
    return groups


def _append_group(
    groups: list[DocValueGroup],
    index: dict[str, int],
    value: str,
    evidence: DocEvidence,
) -> None:
    existing = index.get(value)
    if existing is None:
        index[value] = len(groups)
        groups.append(DocValueGroup(value=value, evidence=(evidence,)))
        return
    current = groups[existing]
    groups[existing] = DocValueGroup(
        value=current.value,
        evidence=current.evidence + (evidence,),
    )


def _is_glob(value: str) -> bool:
    return "*" in value or "?" in value


def _dirname(value: str) -> str | None:
    directory = posixpath.dirname(value)
    if not directory or directory == ".":
        return None
    return directory


def _collect_versions(*groups: Iterable[DocValueGroup]) -> tuple[str, ...]:
    versions: list[str] = []
    seen: set[str] = set()
    for group_list in groups:
        for group in group_list:
            for evidence in group.evidence:
                if not evidence.version:
                    continue
                if evidence.version in seen:
                    continue
                seen.add(evidence.version)
                versions.append(evidence.version)
    return tuple(versions)


def _collect_warnings(
    file_groups: Sequence[DocValueGroup],
    glob_groups: Sequence[DocValueGroup],
    versions: Sequence[str],
) -> tuple[str, ...]:
    warnings: list[str] = []
    if not file_groups and not glob_groups:
        warnings.append("no_config_filenames_detected")
    if len(versions) > 1:
        warnings.append("doc_versions_mixed")
    return tuple(warnings)
