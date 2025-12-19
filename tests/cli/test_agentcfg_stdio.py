import subprocess
import sys


def run_agentcfg(args, *, stdin_text=None):
    return subprocess.run(
        [sys.executable, "-m", "cli.agentcfg", *args],
        input=stdin_text,
        text=True,
        capture_output=True,
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
