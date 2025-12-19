# Task T006 — Support stdin and stdout streaming

**Epic:** EPIC 1 — CLI Product Layer
**Story:** Story 1.1 — CLI Command Design
**Source:** docs/tasks/epics.md

## Goal
Ensure CLI can read input from stdin and stream output to stdout.

## Definition of Done
- Goal is documented, implemented, or planned with clear owner and status.
- Outputs are linked back to the backlog with evidence (code, tests, docs, or decisions).
## Tracking
- Status: done
- Owner: codex
- Claimed: 2025-12-19
- Completed: 2025-12-19
- Target Milestone: TBD
- Links: cli/agentcfg.py, tests/cli/test_agentcfg_stdio.py, README.md, Makefile, docs/architecture.md

## Summary
- Implemented a CLI entrypoint that streams stdin or file input to stdout or file output.
- Added pytest coverage for stdin/stdout behavior and basic dev tooling (Makefile, ruff, pytest).
