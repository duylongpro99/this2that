from __future__ import annotations

from pathlib import Path

from src.registry import detect_agent_configs


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("content", encoding="utf-8")


def test_detect_agent_configs_recurses_and_ignores_git(tmp_path) -> None:
    _touch(tmp_path / "AGENTS.md")
    _touch(tmp_path / "nested" / "AGENTS.md")
    _touch(tmp_path / ".kiro" / "steering" / "setup.md")
    _touch(tmp_path / ".git" / "AGENTS.md")

    detections = detect_agent_configs(tmp_path)
    detection_map = {detection.agent_id: detection for detection in detections}

    codex_matches = [match.path for match in detection_map["codex"].matches]
    kiro_matches = [match.path for match in detection_map["kiro"].matches]

    assert codex_matches == ["AGENTS.md", "nested/AGENTS.md"]
    assert kiro_matches == [".kiro/steering/setup.md"]
