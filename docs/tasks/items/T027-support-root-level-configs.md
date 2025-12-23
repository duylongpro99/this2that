# Task T027 — Support root-level configs

**Epic:** EPIC 3 — Agent Registry & Discovery
**Story:** Story 3.2 — Workspace Detection Logic
**Source:** docs/tasks/epics.md

## Goal
Detect root-level configuration files for each agent.

## Definition of Done
- Goal is documented, implemented, or planned with clear owner and status.
- Outputs are linked back to the backlog with evidence (code, tests, docs, or decisions).
## Tracking
- Status: Done
- Owner: codex
- Claimed: 2025-12-21
- Completed: 2025-12-21
- Target Milestone: TBD
- Links:
  - src/registry/models.py
  - src/registry/detection.py
  - tests/registry/test_detection.py

## Summary
- Enforced root-only detection for single-file agents and added coverage for Claude/Gemini.
