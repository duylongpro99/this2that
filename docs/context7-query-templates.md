# Context7 query templates

## Purpose

- Provide consistent prompts for fetching config format, precedence, and examples.
- Ensure doc snippets are versioned, source-linked, and scoped to agent config behavior.
- Keep Context7 calls predictable for downstream normalization.

## Template inputs

- `agent_name`: Human-facing agent name (e.g., Claude, Codex, Gemini, Kiro).
- `agent_id`: Canonical registry ID (e.g., `claude`, `codex`, `gemini`, `kiro`).
- `config_scope`: Optional scope hint (project, global, nested, multi-file).

## Templates

### Config format

Use when extracting filenames, structure, supported sections, and limits.

```text
Find the official, up-to-date documentation for {agent_name} configuration files.
Return the canonical filename(s), expected location(s), and required structure.
Include any size limits, required headings, or reserved sections.
Provide citations and the doc version or last-updated date when available.
```

### Instruction precedence

Use when determining load order and override behavior across scopes.

```text
Find the official documentation for {agent_name} instruction precedence.
Describe how global, project, and nested config files are discovered and merged.
Include the exact precedence order, override rules, and any special cases.
Provide citations and the doc version or last-updated date when available.
```

### Examples

Use when looking for canonical examples or recommended layouts.

```text
Find official example configurations for {agent_name}.
Return a minimal example and a full example if available.
Include headings, section ordering, and any recommended best practices.
Provide citations and the doc version or last-updated date when available.
```

## Expected response fields

- Source URL(s) and version or last-updated date.
- Canonical filenames and expected locations.
- Precedence and merge rules across scopes.
- Example snippets that match the documented format.
