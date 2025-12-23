"""Workspace detection helpers for agent configs."""

from __future__ import annotations

from dataclasses import dataclass
import fnmatch
import os
from pathlib import Path
from typing import Iterable

from .models import AgentArtifact, AgentRegistry, ArtifactKind, default_registry

DEFAULT_IGNORED_DIRS = (
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "node_modules",
    "__pycache__",
)


@dataclass(frozen=True)
class AgentDetectionMatch:
    path: str
    artifact_pattern: str
    artifact_kind: str
    depth: int

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "artifact_pattern": self.artifact_pattern,
            "artifact_kind": self.artifact_kind,
            "depth": self.depth,
        }


@dataclass(frozen=True)
class AgentDetection:
    agent_id: str
    matches: tuple[AgentDetectionMatch, ...]
    confidence: float

    def to_dict(self) -> dict[str, object]:
        return {
            "agent_id": self.agent_id,
            "matches": [match.to_dict() for match in self.matches],
            "confidence": self.confidence,
        }


def detect_agent_configs(
    workspace_path: str | Path,
    *,
    registry: AgentRegistry | None = None,
    ignored_dirs: Iterable[str] = DEFAULT_IGNORED_DIRS,
) -> list[AgentDetection]:
    registry = registry or default_registry()
    root = Path(workspace_path)
    matches_by_agent: dict[str, list[AgentDetectionMatch]] = {
        agent.agent_id: [] for agent in registry.agents
    }
    seen: set[tuple[str, str, str]] = set()
    ignored = set(ignored_dirs)

    for current_root, dirs, files in os.walk(root):
        dirs[:] = [entry for entry in dirs if entry not in ignored]
        current_path = Path(current_root)
        rel_dir = _relative_posix(root, current_path)

        for agent in registry.agents:
            for artifact in agent.artifacts:
                if artifact.kind is not ArtifactKind.directory:
                    continue
                if _matches_directory(rel_dir, artifact):
                    _record_match(
                        matches_by_agent,
                        seen,
                        agent_id=agent.agent_id,
                        path=rel_dir,
                        artifact=artifact,
                    )

        for filename in files:
            rel_path = _relative_posix(root, current_path / filename)
            for agent in registry.agents:
                for artifact in agent.artifacts:
                    if artifact.kind is ArtifactKind.directory:
                        continue
                    if _matches_file(rel_path, filename, artifact):
                        _record_match(
                            matches_by_agent,
                            seen,
                            agent_id=agent.agent_id,
                            path=rel_path,
                            artifact=artifact,
                        )

    detections: list[AgentDetection] = []
    for agent in registry.agents:
        matches = matches_by_agent[agent.agent_id]
        if not matches:
            continue
        matches.sort(
            key=lambda match: (match.depth, match.path, match.artifact_pattern, match.artifact_kind)
        )
        detections.append(
            AgentDetection(
                agent_id=agent.agent_id,
                matches=tuple(matches),
                confidence=_confidence_for_matches(matches),
            )
        )
    detections.sort(key=lambda detection: (-detection.confidence, detection.agent_id))
    return detections


def _matches_file(rel_path: str, filename: str, artifact: AgentArtifact) -> bool:
    if artifact.root_only and "/" in rel_path:
        return False
    if artifact.kind is ArtifactKind.file:
        if "/" in artifact.pattern or "\\" in artifact.pattern:
            return fnmatch.fnmatch(rel_path, artifact.pattern)
        return filename == artifact.pattern
    if artifact.kind is ArtifactKind.glob:
        return fnmatch.fnmatch(rel_path, artifact.pattern)
    return False


def _matches_directory(rel_dir: str, artifact: AgentArtifact) -> bool:
    if artifact.kind is not ArtifactKind.directory:
        return False
    if rel_dir == ".":
        return fnmatch.fnmatch("", artifact.pattern) or fnmatch.fnmatch(rel_dir, artifact.pattern)
    return fnmatch.fnmatch(rel_dir, artifact.pattern)


def _record_match(
    matches_by_agent: dict[str, list[AgentDetectionMatch]],
    seen: set[tuple[str, str, str]],
    *,
    agent_id: str,
    path: str,
    artifact: AgentArtifact,
) -> None:
    signature = (agent_id, path, artifact.pattern)
    if signature in seen:
        return
    seen.add(signature)
    matches_by_agent[agent_id].append(
        AgentDetectionMatch(
            path=path,
            artifact_pattern=artifact.pattern,
            artifact_kind=artifact.kind.value,
            depth=_path_depth(path),
        )
    )


def _relative_posix(root: Path, path: Path) -> str:
    rel_path = path.relative_to(root)
    return rel_path.as_posix()


def _path_depth(path: str) -> int:
    if path in ("", "."):
        return 0
    return path.count("/")


def _confidence_for_matches(matches: list[AgentDetectionMatch]) -> float:
    if not matches:
        return 0.0
    base = max(_confidence_for_match(match) for match in matches)
    if len(matches) == 1:
        return base
    bonus = 0.05 * (len(matches) - 1)
    return min(1.0, base + bonus)


def _confidence_for_match(match: AgentDetectionMatch) -> float:
    score = 1.0 / (match.depth + 1)
    if match.artifact_kind == ArtifactKind.directory.value:
        score *= 0.4
    return score
