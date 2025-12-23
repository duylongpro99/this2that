# Task T028 — Support nested overrides

**Epic:** EPIC 3 — Agent Registry & Discovery
**Story:** Story 3.2 — Workspace Detection Logic
**Source:** docs/tasks/epics.md

## Goal
Handle nested/child directory overrides in detection logic.

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
  - src/registry/detection.py
  - tests/registry/test_detection.py

## Summary
- Added match depth metadata to capture nested override layering and verify it in tests.
