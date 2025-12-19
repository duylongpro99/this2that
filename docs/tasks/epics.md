Below is a **product-owner level task breakdown** derived directly from the **architecture** and **document-driven MCP design** we established.
I’ll structure this as a **hierarchical product backlog** (Epics → Stories → Tasks), written so it can be handed directly to engineering.

---

# Product Backlog – MCP-based Coding Agent Config Migrator

## EPIC 0 — Product Foundation & Scope

### Story 0.1 — Define Supported Agents & Migration Scope

**Goal:** Establish clear initial boundaries.

**Tasks**

* Identify initial supported agents (dynamic by name, but validated list): Claude, Codex, Gemini, Kiro
* Define supported config artifacts per agent:

  * Claude → `CLAUDE.md`
  * Codex → `AGENTS.md`
  * Gemini → `GEMINI.md` / `AGENTS.md`
  * Kiro → `.kiro/steering/*.md` and/or `AGENTS.md`
* Define migration modes:

  * single-file → single-file
  * multi-file → single-file
  * single-file → multi-file (optional phase 2)
* Define non-goals (e.g., runtime binary config, auth secrets)

---

## EPIC 1 — CLI Product Layer

### Story 1.1 — CLI Command Design

**Goal:** Provide a clean, predictable CLI interface.

**Tasks**

* Define CLI syntax:

  * `agentcfg migrate --from <agent> --to <agent> --input <path> --output <path>`
* Support stdin/stdout streaming
* Support workspace auto-detection (repo root)
* Add `--dry-run` mode
* Add `--verbose` and `--json-log` flags

---

### Story 1.2 — Streaming Output Implementation

**Goal:** Ensure output is streamed, not bundled.

**Tasks**

* Implement chunked stdout writer
* Support file headers:

  * `BEGIN FILE: <path>`
  * `END FILE: <path>`
* Stream per section (markdown heading–based)
* Handle multi-file streaming (future-compatible)

---

## EPIC 2 — MCP Server (FastMCP)

### Story 2.1 — FastMCP Server Bootstrap

**Goal:** Expose migration logic as MCP-compliant services.

**Tasks**

* Create FastMCP server entrypoint
* Register server metadata (name, version, capabilities)
* Enable stdio transport for CLI usage
* Add structured logging hooks

---

### Story 2.2 — MCP Tool Definitions

**Goal:** Define the public MCP surface area.

**Tasks**

* Define MCP tools:

  * `detect_agent_config`
  * `parse_config`
  * `map_config`
  * `render_target`
* Define MCP resources:

  * `agent_registry`
  * `concept_ontology`
* Define MCP prompt:

  * `migrate_config_prompt(from, to, input_path)`
* Validate MCP schemas against spec

---

## EPIC 3 — Agent Registry & Discovery

### Story 3.1 — Agent Registry Core

**Goal:** Central source of truth for agent metadata.

**Tasks**

* Create agent registry data model
* Store:

  * agent_id
  * known config filenames
  * directory patterns
  * precedence rules
* Add runtime validation for unknown agents
* Enable dynamic extension via config/plugin

---

### Story 3.2 — Workspace Detection Logic

**Goal:** Automatically locate origin config files.

**Tasks**

* Implement recursive search rules per agent
* Support:

  * root-level configs
  * nested overrides
  * multi-file folders (Kiro)
* Return ordered candidate list with confidence scores

---

## EPIC 4 — Context7 Documentation Integration

### Story 4.1 — Context7 MCP Integration

**Goal:** Always use latest agent documentation.

**Tasks**

* Define Context7 query templates:

  * config file format
  * instruction precedence
  * examples
* Implement doc-fetch orchestration strategy:

  * LLM calls Context7 directly (preferred)
  * fallback fetcher abstraction
* Add TTL-based caching layer

---

### Story 4.2 — Documentation Normalization

**Goal:** Convert raw docs into usable mapping hints.

**Tasks**

* Extract:

  * config filenames
  * structural expectations
  * constraints (size limits, precedence)
* Normalize docs into internal `AgentDocModel`
* Detect version differences and warn if breaking

---

## EPIC 5 — Source Config Parsing

### Story 5.1 — Markdown Parser

**Goal:** Parse configs into a neutral representation.

**Tasks**

* Implement markdown AST parsing
* Identify headings, lists, code blocks
* Preserve ordering and semantic grouping
* Support inline directives and comments

---

### Story 5.2 — Multi-file Parser (Kiro)

**Goal:** Handle Kiro-style steering folders.

**Tasks**

* Parse `.kiro/steering/*.md`
* Classify files by intent (product, tech, rules)
* Merge into unified Source IR with provenance

---

## EPIC 6 — Concept Ontology & Normalization

### Story 6.1 — Concept Ontology Definition

**Goal:** Define what “main concepts” are.

**Tasks**

* Define ontology categories:

  * setup_commands
  * code_style
  * testing_policy
  * repo_rules
  * safety_constraints
  * tool_usage
* Define required vs optional concepts
* Version ontology for future evolution

---

### Story 6.2 — Concept Extraction Engine

**Goal:** Convert parsed config into normalized concepts.

**Tasks**

* Map markdown sections → ontology concepts
* Handle ambiguous sections via heuristics
* Preserve raw text + semantic tags
* Emit warnings for unclassified sections

---

## EPIC 7 — Mapping Engine (Source → Target)

### Story 7.1 — Mapping Rule System

**Goal:** Translate concepts between agents.

**Tasks**

* Define mapping rules per agent pair
* Support:

  * 1→1 mappings
  * N→1 collapses
  * 1→N expansions
* Add fallback rules when target lacks feature

---

### Story 7.2 — Constraint & Mismatch Handling

**Goal:** Prevent silent loss of meaning.

**Tasks**

* Detect unsupported concepts
* Add comments or warnings in output
* Enforce target-specific limits (e.g., size caps)
* Provide downgrade strategies

---

## EPIC 8 — Target Rendering

### Story 8.1 — Markdown Renderer

**Goal:** Generate target-compliant config files.

**Tasks**

* Implement renderer per agent:

  * Claude renderer
  * Codex renderer
  * Gemini renderer
  * Kiro renderer
* Enforce target naming conventions
* Ensure deterministic ordering

---

### Story 8.2 — Streaming Renderer

**Goal:** Support incremental output.

**Tasks**

* Emit content per section
* Flush after each chunk
* Support resumable generation
* Integrate with CLI stream manager

---

## EPIC 9 — Quality, Safety & Validation

### Story 9.1 — Output Validation

**Goal:** Ensure target agents can consume output.

**Tasks**

* Validate markdown structure
* Validate filename correctness
* Validate agent-specific constraints
* Run simulated “agent read” checks

---

### Story 9.2 — Regression Fixtures

**Goal:** Prevent breaking migrations.

**Tasks**

* Create golden fixtures:

  * Claude → Codex
  * Gemini → Codex
  * Codex → Claude
* Snapshot test output
* Add doc-version-based regression tests

---

## EPIC 10 — Extensibility & Plugins

### Story 10.1 — Plugin Architecture

**Goal:** Enable new agents without core changes.

**Tasks**

* Define agent plugin interface
* Allow plugins to define:

  * registry entry
  * parser
  * renderer
  * mapping rules
* Document plugin authoring guide

---

## EPIC 11 — UX, Docs & Adoption

### Story 11.1 — Developer Documentation

**Goal:** Make product usable and trustworthy.

**Tasks**

* Write CLI usage docs
* Write migration examples
* Explain limitations & warnings
* Provide troubleshooting guide

---

### Story 11.2 — Example Repositories

**Goal:** Show real-world usage.

**Tasks**

* Create demo repos per agent
* Provide before/after configs
* Add CI check demonstrating migration

---

## EPIC 12 — Future Roadmap (Optional)

* Interactive diff viewer
* IDE plugin (Cursor / VS Code)
* Bidirectional sync mode
* Live agent introspection

---

If you want next:

* I can **convert this into Jira-ready user stories**, or
* generate a **PRD + milestone plan**, or
* create a **task dependency graph** (what must be built first).
