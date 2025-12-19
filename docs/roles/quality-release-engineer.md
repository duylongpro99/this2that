# Quality and release engineer

## Mission
- Guard correctness with tests, fixtures, and release hygiene so migrations stay stable across
  versions.

## Scope
- Test strategy: unit tests for registry/parsers/mapping/renderers, streaming order checks, golden
  fixtures per agent pair.
- CI wiring for `make lint` and `make test`; coverage expectations and flake management.
- Regression safety: doc version diffs, warning coverage, before/after examples.
- Release notes and troubleshooting guidance; artifact validation for CLI and FastMCP server.

## Outputs
- Pytest suites with snapshot/golden fixtures for core paths and edge cases.
- CI/config docs describing lint/test commands and expected environment.
- Regression dashboards or checklists for new agent additions or ontology updates.
- Troubleshooting guide covering detection failures, streaming issues, and plugin misconfigurations.

## Inputs needed
- Feature surfaces from platform, registry, parser, and renderer owners.
- Target success metrics from product (accuracy, timing, zero data loss).
- Plugin interface expectations to cover third-party extensions in tests.

## Collaboration signals
- Pair with mapping engineer on golden fixtures and downgrade warnings.
- Pair with platform engineer to validate CLI/stdio behavior under load.
- Provide QA sign-off criteria to product before releases.

## Risks to watch
- Snapshot churn due to non-deterministic ordering or timestamps.
- Coverage gaps on plugin paths and Kiro multi-file flows.
- CI drift vs. documented `make` commands.
