"""Agent registry data model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ArtifactKind(str, Enum):
    file = "file"
    glob = "glob"
    directory = "directory"


@dataclass(frozen=True)
class AgentArtifact:
    pattern: str
    kind: ArtifactKind
    description: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {"pattern": self.pattern, "kind": self.kind.value}
        if self.description:
            payload["description"] = self.description
        return payload


@dataclass(frozen=True)
class AgentDefinition:
    agent_id: str
    display_name: str
    artifacts: tuple[AgentArtifact, ...]
    config_filenames: tuple[str, ...] = ()
    directory_patterns: tuple[str, ...] = ()
    precedence_rules: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "aliases": list(self.aliases),
            "config_filenames": list(self.config_filenames),
            "directory_patterns": list(self.directory_patterns),
            "precedence_rules": list(self.precedence_rules),
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }


@dataclass(frozen=True)
class AgentRegistry:
    agents: tuple[AgentDefinition, ...]

    def to_dict(self) -> dict[str, object]:
        return {"agents": [agent.to_dict() for agent in self.agents]}

    def get(self, agent_id: str) -> AgentDefinition | None:
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None


def default_registry() -> AgentRegistry:
    agents = (
        AgentDefinition(
            agent_id="claude",
            display_name="Claude",
            aliases=("claude", "claude code", "claude.md", "claude-md"),
            config_filenames=("CLAUDE.md",),
            precedence_rules=("Single-file config; no directory override behavior.",),
            artifacts=(
                AgentArtifact(
                    pattern="CLAUDE.md",
                    kind=ArtifactKind.file,
                    description="Single-file Claude instructions.",
                ),
            ),
        ),
        AgentDefinition(
            agent_id="codex",
            display_name="Codex",
            aliases=("codex", "openai codex", "agents.md", "agents-md"),
            config_filenames=("AGENTS.md",),
            precedence_rules=(
                "Nearest AGENTS.md to the working directory overrides parent instructions.",
            ),
            artifacts=(
                AgentArtifact(
                    pattern="AGENTS.md",
                    kind=ArtifactKind.file,
                    description="Codex instructions with root and nested overrides.",
                ),
            ),
        ),
        AgentDefinition(
            agent_id="gemini",
            display_name="Gemini",
            aliases=("gemini", "gemini cli", "gemini.md", "gemini-md"),
            config_filenames=("GEMINI.md",),
            precedence_rules=("Single-file config; no directory override behavior.",),
            artifacts=(
                AgentArtifact(
                    pattern="GEMINI.md",
                    kind=ArtifactKind.file,
                    description="Single-file Gemini instructions.",
                ),
            ),
        ),
        AgentDefinition(
            agent_id="kiro",
            display_name="Kiro",
            aliases=("kiro", "kiro cli", "kiro.md", "kiro-md"),
            directory_patterns=(".kiro/steering",),
            precedence_rules=(
                "Steering files combine by intent; nearest bundle takes precedence.",
            ),
            artifacts=(
                AgentArtifact(
                    pattern=".kiro/steering/*.md",
                    kind=ArtifactKind.glob,
                    description="Kiro steering bundle markdown files.",
                ),
            ),
        ),
    )
    try:
        from .plugins import load_registry_extensions, merge_agent_definitions
    except ImportError:
        return AgentRegistry(agents=agents)
    extensions = load_registry_extensions()
    if extensions:
        agents = merge_agent_definitions(agents, extensions)
    return AgentRegistry(
        agents=agents,
    )
