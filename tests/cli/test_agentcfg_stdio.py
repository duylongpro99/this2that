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
    assert result.stdout == "hello\nworld\n"
    assert result.stderr == ""


def test_migrate_reads_file_and_writes_stdout(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("file content\n", encoding="utf-8")
    result = run_agentcfg(
        ["migrate", "--from", "claude", "--to", "codex", "--input", str(source), "--output", "-"]
    )
    assert result.returncode == 0
    assert result.stdout == "file content\n"


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
    assert result.stdout == "preview\n"
    assert result.stderr == ""
    assert not output.exists()


def test_migrate_dry_run_skips_default_output_write(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "CLAUDE.md").write_text("root content\n", encoding="utf-8")

    result = run_agentcfg(["migrate", "--from", "claude", "--to", "codex", "--dry-run"], cwd=repo)

    assert result.returncode == 0
    assert result.stdout == "root content\n"
    assert result.stderr == ""
    assert not (repo / "AGENTS.md").exists()
