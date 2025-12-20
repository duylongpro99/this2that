from __future__ import annotations

from pathlib import Path

from src.registry import default_registry


def _write_registry_config(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def test_default_registry_loads_config_extensions(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "agentcfg.registry.toml"
    _write_registry_config(
        config_path,
        """
[agent_registry]
[[agent_registry.agents]]
agent_id = "custom"
display_name = "Custom"
aliases = ["custom"]
config_filenames = ["CUSTOM.md"]
precedence_rules = ["Custom rules."]

[[agent_registry.agents.artifacts]]
pattern = "CUSTOM.md"
kind = "file"
description = "Custom config."
""",
    )
    monkeypatch.setenv("AGENTCFG_REGISTRY_CONFIG", str(config_path))

    registry = default_registry()
    agent_ids = {agent.agent_id for agent in registry.agents}

    assert "custom" in agent_ids


def test_default_registry_skips_colliding_plugin_agents(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "agentcfg.registry.toml"
    _write_registry_config(
        config_path,
        """
[agent_registry]
[[agent_registry.agents]]
agent_id = "codex"
display_name = "Shadow Codex"
aliases = ["codex-shadow"]
config_filenames = ["SHADOW.md"]

[[agent_registry.agents.artifacts]]
pattern = "SHADOW.md"
kind = "file"
description = "Shadow config."
""",
    )
    monkeypatch.setenv("AGENTCFG_REGISTRY_CONFIG", str(config_path))

    registry = default_registry()
    agent_ids = [agent.agent_id for agent in registry.agents]

    assert agent_ids.count("codex") == 1
