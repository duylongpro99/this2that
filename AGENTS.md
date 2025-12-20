# Repository Guidelines

## Project Structure & Module Organization
- `docs/architecture.md` captures the FastMCP layers (CLI, MCP server, mapping/renderer); keep it in sync when adding code paths or new tools.
- `docs/prd.md` holds the product plan; update it whenever scope or requirements shift.
- `docs/tasks/` tracks epics and tasks; add granular work items here before opening PRs.
- When you add implementation code, place CLI entrypoints in `cli/` and the MCP server logic in `src/` (e.g., `src/mcp/`, `src/registry/`, `src/renderer/`); keep tests colocated under `tests/` mirroring module names.
- Roles live in `docs/roles/`; when you pick up a task, act in the corresponding role brief so scope,
  inputs, and risks stay aligned.

## Build, Test, and Development Commands
- No build tooling exists yet. When introducing code, add a `Makefile` with `make lint` (static checks) and `make test` (unit/integration), and document any extra setup in this section.
- Prefer reproducible envs (e.g., `.python-version` + `uv`/`pip-tools` or `npm ci`) and pin dependencies.
- Must use `uv` for Python environments and package installs (no `pip`/`python3` direct usage).
- Package installs must go through `uv` (e.g., `uv pip install ...`).
- Run tests via `uv` (e.g., `uv run pytest ...`); do not invoke `python -m pytest` directly.

## Coding Style & Naming Conventions
- Markdown: sentence-case headings, bullet lists over long paragraphs, wrap at ~100 chars, fenced code blocks for commands.
- Python (recommended for FastMCP): snake_case for functions/vars, PascalCase for classes, 4-space indent; run formatters (`ruff format`/`black`) and linters (`ruff check`) before commit.
- Keep identifiers agent-agnostic; avoid hard-coding vendor names in core mapping logic—use registry lookups instead.

## Testing Guidelines
- Add unit tests for the mapping engine, registry resolution, and renderers; use pytest-style names (`test_<unit>_does_<thing>.py`).
- Include golden-file tests for generated configs (AGENTS.md, CLAUDE.md, etc.) under `tests/fixtures/`.
- Aim for coverage on conversion edges (missing sections, unsupported concepts) and streaming output order.

## Commit & Pull Request Guidelines
- Commits: concise imperative subject (“Add Codex renderer”), body for rationale or edge cases; group related changes.
- PRs: include summary, scope of changes, tests run (`make test`, `make lint`), and links to `docs/tasks/` items; attach sample generated output when touching renderers.
- Keep changes scoped—update docs alongside code changes, especially architecture notes and task status.

## Security & Configuration Tips
- Do not commit secrets or tokens; use env vars or `.env.example` for placeholders.
- Ensure any network access is optional and documented; default to offline-friendly behavior with cached docs when possible.

## Agent activity
- 2025-12-19: codex completed T001; documented initial supported agents and normalization.
- 2025-12-19: codex completed T002; documented canonical config artifacts per agent.
- 2025-12-19: codex completed T003; documented supported migration modes.
- 2025-12-19: codex completed T004; documented non-goals in the PRD.
- 2025-12-19: codex completed T005; documented CLI syntax and required flags.
- 2025-12-19: codex completed T006; added CLI stdin/stdout streaming scaffold and tests.
- 2025-12-19: codex completed T007; added workspace auto-detection defaults and tests.
- 2025-12-19: codex completed T008; added dry-run CLI flag and tests.
- 2025-12-19: codex completed T009; added verbose/json CLI logs and tests.
- 2025-12-19: codex completed T010; implemented chunked stdout writer utilities and tests.
- 2025-12-19: codex completed T012; streamed stdout per markdown section with tests.
- 2025-12-20: codex completed T013; added multi-file streaming helper and tests.
- 2025-12-20: codex completed T014; added FastMCP server entrypoint bootstrap.
