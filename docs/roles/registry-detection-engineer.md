# Registry and detection engineer

## Mission
- Own the agent registry and workspace detection so the system knows which configs exist and how to
  address them.

## Scope
- Registry schema: agent ids, file patterns, doc sources, renderer bindings, constraints.
- Detection pipeline: recursive search rules, confidence scoring, root vs nested overrides, Kiro
  folder handling.
- Validation: reject unknown agents, surface warnings, enforce naming normalization.
- Extensibility: plugin hooks that let third parties register agents safely.

## Outputs
- Registry module with typed entries for Claude, Codex, Gemini, Kiro (plus plugin slots).
- Detection helpers that return ordered candidates with confidence and rationale.
- Validation errors for unknown or malformed agents with actionable messaging.
- Tests/fixtures covering root-level configs, nested overrides, and plugin registrations.

## Inputs needed
- Agent format docs (Context7 fetch strategy) and naming conventions from product/architecture.
- File patterns and constraints from parser and renderer owners.
- Plugin surface expectations from platform/SDK decisions.

## Collaboration signals
- Sync with parser engineer on required metadata to parse source configs correctly.
- Sync with renderer engineer on target filename conventions and constraints.
- Align with platform engineer on CLI flags that expose detection results.

## Risks to watch
- False positives on detection when repos contain sample configs.
- Registry drift vs. docs; keep TTL/cache strategy documented.
- Plugin isolation—guard against plugins overwriting core agents.
