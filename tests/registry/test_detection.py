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
    codex_depths = {match.path: match.depth for match in detection_map["codex"].matches}
    kiro_depths = {match.path: match.depth for match in detection_map["kiro"].matches}

    assert codex_matches == ["AGENTS.md", "nested/AGENTS.md"]
    assert kiro_matches == [".kiro/steering/setup.md"]
    assert codex_depths == {"AGENTS.md": 0, "nested/AGENTS.md": 1}
    assert kiro_depths == {".kiro/steering/setup.md": 2}


def test_detect_agent_configs_limits_root_only_files(tmp_path) -> None:
    _touch(tmp_path / "CLAUDE.md")
    _touch(tmp_path / "nested" / "CLAUDE.md")
    _touch(tmp_path / "GEMINI.md")
    _touch(tmp_path / "nested" / "GEMINI.md")

    detections = detect_agent_configs(tmp_path)
    detection_map = {detection.agent_id: detection for detection in detections}

    claude_matches = [match.path for match in detection_map["claude"].matches]
    gemini_matches = [match.path for match in detection_map["gemini"].matches]

    assert claude_matches == ["CLAUDE.md"]
    assert gemini_matches == ["GEMINI.md"]
