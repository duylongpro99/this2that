# Mapping and renderer engineer

## Mission
- Map normalized concepts to each target agent and emit deterministic, target-compliant files with
  streaming support.

## Scope
- Mapping rules per agent pair: 1-to-1, many-to-one collapses, one-to-many expansions, downgrade
  strategies for unsupported concepts.
- Enforcement of target-specific constraints (section ordering, naming, size limits).
- Renderers for Claude, Codex, Gemini, Kiro with deterministic ordering and per-section emission.
- Streaming mechanics: chunking, flushing, delimiters, resumable generation hooks.

## Outputs
- Mapping tables with warnings for gaps or unsupported features.
- Renderers that output correct filenames and Markdown layout per agent.
- Streaming writer that flushes per section/file with BEGIN/END delimiters when needed.
- Golden fixtures for major agent pairs and snapshot tests for regressions.

## Inputs needed
- Ontology fields and raw text from the parser owner.
- Registry constraints and filename conventions.
- Platform needs for stdout/stdin integration and error handling.

## Collaboration signals
- Co-design downgrade strategies with parser owner to avoid silent data loss.
- Align with platform engineer on streaming API and CLI UX.
- Work with QA on golden fixtures and regression matrices.

## Risks to watch
- Silent truncation when targets have tighter limits.
- Non-deterministic ordering breaking snapshot tests.
- Drift between mapping rules and renderer output formatting.
