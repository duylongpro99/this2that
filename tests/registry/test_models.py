from __future__ import annotations

from src.registry import ArtifactKind, default_registry


def test_default_registry_includes_core_agents() -> None:
    registry = default_registry()

    agent_ids = {agent.agent_id for agent in registry.agents}

    assert agent_ids == {"claude", "codex", "gemini", "kiro"}


def test_default_registry_serializes_artifacts() -> None:
    registry_payload = default_registry().to_dict()

    agents = {agent["agent_id"]: agent for agent in registry_payload["agents"]}
    kiro_artifacts = agents["kiro"]["artifacts"]
    codex_precedence = agents["codex"]["precedence_rules"]

    assert kiro_artifacts == [
        {
            "pattern": ".kiro/steering/*.md",
            "kind": ArtifactKind.glob.value,
            "description": "Kiro steering bundle markdown files.",
        }
    ]
    assert codex_precedence == [
        "Nearest AGENTS.md to the working directory overrides parent instructions."
    ]
