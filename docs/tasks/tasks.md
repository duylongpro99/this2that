Great — I’ll deliver **all three** in a clean, execution-ready form, aligned with a **Product Owner / Platform team** workflow.

---

# 1️⃣ Jira-Ready User Stories (with Acceptance Criteria)

Before starting any task, pick the matching role brief in `docs/roles/` and follow its scope,
inputs, and risks while you work.

See `docs/tasks/task_roles.md` for the task-to-role map covering all items.

I’ll structure these so they can be **directly imported into Jira**.

---

## EPIC: MCP-based Coding Agent Config Migrator

---

### STORY MCP-01 — CLI Command for Agent Config Migration

**As a** developer
**I want** a CLI command to migrate config from one coding agent to another
**So that** I can switch agents without rewriting instructions manually

**Acceptance Criteria**

* CLI supports `--from`, `--to`, `--input`, `--output`
* CLI validates supported agent names
* CLI exits with clear error messages on invalid input
* CLI works from repo root or subdirectories

---

### STORY MCP-02 — Streamed Output Generation

**As a** developer
**I want** migrated config files to be streamed incrementally
**So that** large configs do not exceed context or memory limits

**Acceptance Criteria**

* Output is streamed section-by-section
* Each file is clearly delimited (`BEGIN FILE` / `END FILE`)
* No bundled full-file response is returned
* Streaming works for single and multi-file targets

---

### STORY MCP-03 — FastMCP Server Initialization

**As a** platform engineer
**I want** a FastMCP server exposing migration capabilities
**So that** multiple MCP clients can consume it

**Acceptance Criteria**

* Server starts via stdio transport
* MCP capabilities are declared correctly
* Tools, resources, and prompts are registered
* Server is discoverable by MCP-compatible clients

---

### STORY MCP-04 — Agent Registry & Detection

**As a** system
**I want** to recognize agent config formats automatically
**So that** users don’t need to manually specify files

**Acceptance Criteria**

* Registry includes Claude, Codex, Gemini, Kiro
* System detects known config files in workspace
* Detection returns ordered candidates with confidence
* Unknown agents are rejected with explanation

---

### STORY MCP-05 — Context7 Documentation Retrieval

**As a** migration engine
**I want** to fetch the latest agent documentation dynamically
**So that** migrations are always accurate and up to date

**Acceptance Criteria**

* Context7 MCP tools are invoked dynamically
* Docs include config format, constraints, examples
* Results are cached with TTL
* Failures fall back gracefully with warnings

---

### STORY MCP-06 — Source Config Parsing

**As a** system
**I want** to parse agent configs into a neutral representation
**So that** they can be mapped consistently

**Acceptance Criteria**

* Markdown sections are parsed correctly
* Multi-file configs (Kiro) are merged
* Original ordering is preserved
* Unrecognized sections are retained verbatim

---

### STORY MCP-07 — Concept Ontology & Normalization

**As a** product
**I want** configs normalized into stable concepts
**So that** intent survives across agents

**Acceptance Criteria**

* Concepts include setup, style, testing, rules, safety
* Each section maps to ≥1 concept
* Raw text is preserved
* Ontology is versioned

---

### STORY MCP-08 — Mapping Engine (Source → Target)

**As a** system
**I want** to map normalized concepts into target agent structure
**So that** output is compliant and meaningful

**Acceptance Criteria**

* Mapping rules exist per agent pair
* Unsupported concepts produce warnings
* Target constraints are enforced
* No silent data loss

---

### STORY MCP-09 — Target Renderer

**As a** developer
**I want** valid target config files generated
**So that** the target agent can immediately use them

**Acceptance Criteria**

* Correct filenames per agent
* Markdown formatting follows target conventions
* Deterministic ordering
* Supports single or multi-file output

---

### STORY MCP-10 — Validation & Regression Safety

**As a** product owner
**I want** migrations to be reliable across versions
**So that** updates don’t break users

**Acceptance Criteria**

* Golden fixtures exist for major agent pairs
* Snapshot tests pass
* Size and precedence constraints validated
* Clear migration warnings logged

---

# 2️⃣ PRD + Milestone Plan

---

## Product Requirements Document (PRD)

### Product Name

**AgentCfg Migrator MCP**

### Problem

Each coding agent CLI uses incompatible configuration formats, causing friction when switching tools.

### Solution

A CLI + MCP server that **automatically migrates agent configs** using:

* dynamic documentation (Context7)
* concept-based normalization
* streamed output

### Target Users

* AI-first developers
* Platform teams
* Open-source maintainers
* Tooling teams

### Success Metrics

* Migration accuracy ≥ 95%
* Time to migrate < 10 seconds
* Zero manual rewrite required
* New agent added without core rewrite

---

## Milestones

### Milestone 1 — MVP (Weeks 1–2)

* CLI command
* FastMCP server
* Claude ↔ Codex support
* Single-file configs
* Streaming output

### Milestone 2 — Multi-Agent Support (Weeks 3–4)

* Gemini + Kiro
* Context7 full integration
* Concept ontology v1
* Validation & warnings

### Milestone 3 — Extensibility (Weeks 5–6)

* Plugin architecture
* Multi-file rendering
* Regression suite
* Documentation & examples

---

# 3️⃣ Task Dependency Graph (Build Order)

```
CLI Interface
   ↓
FastMCP Server
   ↓
Agent Registry ──→ Context7 Docs
   ↓                  ↓
Source Parser        Doc Normalizer
   ↓                  ↓
Concept Normalizer ←──┘
   ↓
Mapping Engine
   ↓
Target Renderer
   ↓
Streaming Output
   ↓
Validation & Regression
```

**Critical Path**

> MCP Server → Registry → Parser → Concept Ontology → Mapping → Renderer → Streaming

---

## Next steps (your choice)

I can now:

* 🔧 Convert this into **Jira tickets (CSV / JSON)**
* 📐 Produce a **technical design doc (TDD)** with data models
* 🧩 Define **IR schemas & MCP tool signatures**
* 🗺️ Create a **plugin SDK spec** for third-party agents

Just tell me which one to do next.
