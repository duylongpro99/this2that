# agentcfg migrator

## Overview
- CLI-first scaffolding for migrating agent configuration files.
- Current CLI streams input to output without transformation while core mapping is built.

## CLI usage
- Command: `agentcfg migrate --from <agent> --to <agent> --input <path|-> --output <path|->`
- Use `-` for stdin or stdout to stream data.

## Development setup
- Requires Python 3.11+ and `uv`.
- Create a venv and install dev dependencies: `uv venv` then `uv pip install -e '.[dev]'`.

## Commands
- Lint: `make lint`
- Test: `make test`
