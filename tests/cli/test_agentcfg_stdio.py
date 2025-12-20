import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_agentcfg(args, *, stdin_text=None, cwd=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "cli.agentcfg", *args],
        input=stdin_text,
        text=True,
        capture_output=True,
        cwd=cwd or REPO_ROOT,
        env=env,
        check=False,
    )


def test_migrate_reads_stdin_and_writes_stdout():
    result = run_agentcfg(
        ["migrate", "--from", "claude", "--to", "codex", "--input", "-", "--output", "-"],
        stdin_text="hello\nworld\n",
    )
    assert result.returncode == 0
    assert result.stdout == "BEGIN FILE -\nhello\nworld\nEND FILE -\n"
    assert result.stderr == ""


def test_migrate_reads_file_and_writes_stdout(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("file content\n", encoding="utf-8")
    result = run_agentcfg(
        ["migrate", "--from", "claude", "--to", "codex", "--input", str(source), "--output", "-"]
    )
    assert result.returncode == 0
    assert result.stdout == "BEGIN FILE -\nfile content\nEND FILE -\n"


def test_migrate_defaults_to_workspace_root_paths(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "CLAUDE.md").write_text("root content\n", encoding="utf-8")
    subdir = repo / "subdir"
    subdir.mkdir()

    result = run_agentcfg(["migrate", "--from", "claude", "--to", "codex"], cwd=subdir)

    assert result.returncode == 0
    assert result.stdout == ""
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == "root content\n"


def test_migrate_missing_default_input_errors(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    result = run_agentcfg(["migrate", "--from", "claude", "--to", "codex"], cwd=repo)

    assert result.returncode == 2
    assert "CLAUDE.md" in result.stderr


def test_migrate_dry_run_outputs_stdout_without_writing_file(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("preview\n", encoding="utf-8")
    output = tmp_path / "out.md"

    result = run_agentcfg(
        [
            "migrate",
            "--from",
            "claude",
            "--to",
            "codex",
            "--input",
            str(source),
            "--output",
            str(output),
            "--dry-run",
        ]
    )

    assert result.returncode == 0
    assert result.stdout == f"BEGIN FILE {output}\npreview\nEND FILE {output}\n"
    assert result.stderr == ""
    assert not output.exists()


def test_migrate_dry_run_skips_default_output_write(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "CLAUDE.md").write_text("root content\n", encoding="utf-8")

    result = run_agentcfg(["migrate", "--from", "claude", "--to", "codex", "--dry-run"], cwd=repo)

    assert result.returncode == 0
    expected_output = repo / "AGENTS.md"
    assert (
        result.stdout == f"BEGIN FILE {expected_output}\nroot content\nEND FILE {expected_output}\n"
    )
    assert result.stderr == ""
    assert not (repo / "AGENTS.md").exists()


def test_migrate_verbose_logs_events(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("log me\n", encoding="utf-8")
    result = run_agentcfg(
        [
            "migrate",
            "--from",
            "claude",
            "--to",
            "codex",
            "--input",
            str(source),
            "--output",
            "-",
            "--verbose",
        ]
    )

    assert result.returncode == 0
    assert result.stdout == "BEGIN FILE -\nlog me\nEND FILE -\n"
    assert "resolved_paths" in result.stderr
    assert "stream_start" in result.stderr
    assert "stream_end" in result.stderr


def test_migrate_json_logs_events(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("json logs\n", encoding="utf-8")
    result = run_agentcfg(
        [
            "migrate",
            "--from",
            "claude",
            "--to",
            "codex",
            "--input",
            str(source),
            "--output",
            "-",
            "--json-log",
        ]
    )

    assert result.returncode == 0
    assert result.stdout == "BEGIN FILE -\njson logs\nEND FILE -\n"
    events = [json.loads(line)["event"] for line in result.stderr.strip().splitlines()]
    assert events == ["resolved_paths", "stream_start", "stream_end"]


def test_migrate_rejects_unknown_agents(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("content\n", encoding="utf-8")
    result = run_agentcfg(
        ["migrate", "--from", "unknown", "--to", "codex", "--input", str(source), "--output", "-"]
    )

    assert result.returncode == 2
    assert "unknown agent" in result.stderr
