Below is a **product architecture breakdown** grounded in MCP/FastMCP concepts (Tools/Resources/Prompts) and the real-world config discovery patterns (e.g., Codex layering via `AGENTS.md`). ([FastMCP][1])

---

When implementing any component, pick the matching role brief in `docs/roles/` and consult
`docs/tasks/task_roles.md` to align responsibilities and risks.

## 1) High-level architecture (layers)

### A. CLI Layer (your product’s executable)

**Responsibility:** user-facing command, file IO, streaming output.

* `agentcfg migrate --from claude --to codex --input CLAUDE.md --output AGENTS.md`
* Streams *each output file* to stdout / target path **incrementally** (section-by-section or file-by-file).
* Handles workspace detection (repo root, subdir, etc.).

**CLI syntax (initial)**

* Command: `agentcfg migrate`
* Required flags: `--from <agent>` `--to <agent>` `--input <path>` `--output <path>`

### B. MCP Orchestrator Layer (FastMCP server)

**Responsibility:** expose “migration brain” as MCP tools/resources to any MCP client (Codex/Claude/Cursor/etc.).
FastMCP is designed to build MCP servers by decorating Python functions as tools/resources. ([FastMCP][1])

### C. Intelligence Layer (Doc-driven concept mapping)

**Responsibility:** convert source config → target config by:

1. fetching latest docs (Context7)
2. extracting concepts from source
3. mapping concepts into target structure
4. rendering target config(s)

Context7’s job is to inject up-to-date, version-specific docs into the LLM context. ([GitHub][2])

---

## 2) Core components (inside the MCP server)

### 2.1 Agent Registry

**What it stores**

* Supported agent IDs (claude, codex, gemini, kiro, …)
* For each agent: canonical config “artifacts” (filenames, folders, precedence rules)

  * Example: Codex discovers `AGENTS.md` in global and project scope with precedence and size limits. ([OpenAI Developers][3])

**Why it matters**

* Enables dynamic “agent mentioned by user” handling.
* Drives which parsers/renderers to load.

**Initial supported agents and normalization**

* Canonical IDs are lowercase: `claude`, `codex`, `gemini`, `kiro`.
* Normalization is case-insensitive and trims whitespace/punctuation.
* Accepted aliases map to canonical IDs:
  * `claude`: "claude", "claude code", "claude.md", "claude-md"
  * `codex`: "codex", "openai codex", "agents.md", "agents-md"
  * `gemini`: "gemini", "gemini cli", "gemini.md", "gemini-md"
  * `kiro`: "kiro", "kiro cli", "kiro.md", "kiro-md"

**Canonical config artifacts per agent**

* `claude`: `CLAUDE.md` (single-file instructions)
* `codex`: `AGENTS.md` (root and nested overrides per directory)
* `gemini`: `GEMINI.md` (single-file instructions)
* `kiro`: `.kiro/steering/*.md` (multi-file steering bundle)

**Supported migration modes**

* single-file -> single-file (phase 1)
* multi-file -> single-file (phase 1)
* single-file -> multi-file (phase 2)

---

### 2.2 Documentation Fetcher (Context7 integration)

**Responsibility**

* Given `{agent_name, topic=config/instructions, version?}`, retrieve the *latest* docs/snippets/examples.
* Cache results with TTL to reduce repeated calls.

**Two deployment patterns**

1. **Preferred**: MCP client connects to both servers:

   * Your `migrator-mcp` server + `context7-mcp` server
   * The LLM can call Context7 tools directly, while your server focuses on transformation logic.
2. **Optional**: your server embeds a Context7 “sub-client” (only if you want your server to call Context7 itself).

Context7 explicitly exists to pull latest docs “from the source” into the model context. ([GitHub][2])

---

### 2.3 Source Parser

**Responsibility**

* Parse origin config(s) into a **normalized intermediate representation (IR)**.
* Accept:

  * single markdown file (CLAUDE.md / GEMINI.md / AGENTS.md)
  * multi-file patterns (e.g., Kiro steering folder)

**Output: Config IR**
A structured object like:

* `identity`: agent, file path(s)
* `sections`: [{title, body, tags}]
* `directives`: normalized concepts (see section 3)

---

### 2.4 Concept Ontology + Normalizer

**Responsibility**
Transform “what the config means” into stable concepts.

Example concept families to normalize:

* **Project setup** (install/dev/test commands)
* **Code style** (formatting, linting, patterns)
* **Repository rules** (what not to touch, commit conventions)
* **Testing policy** (must run tests, specific commands)
* **Safety / security** (no secrets, env handling)
* **Tooling expectations** (allowed commands, required tools)

This is the “persist main concept” layer.

---

### 2.5 Mapping Engine (IR → Target IR)

**Responsibility**

* Use docs from Context7 (and known heuristics) to map normalized concepts into the target agent’s expected structure.
* Handle:

  * field mismatches
  * feature gaps
  * precedence differences

Example: if target is Codex, you must generate `AGENTS.md` and respect that Codex concatenates per-directory instructions with override behavior. ([OpenAI Developers][3])

---

### 2.6 Target Renderer

**Responsibility**
Render Target IR into one or more output files:

* `AGENTS.md` for Codex (and often works for others)
* `CLAUDE.md` for Claude
* `GEMINI.md` for Gemini (or `AGENTS.md` if configured)
* `.kiro/steering/*.md` if you choose Kiro-native layout

AGENTS.md is also a documented open format for guiding agents. ([Agents][4])

---

### 2.7 Streaming Output Manager

**Responsibility**

* Produce output **file-by-file**, and within a file **section-by-section**.
* Emits “chunks” to the CLI layer so you never bundle everything into one response.

---

## 3) MCP surface area (what your FastMCP server exposes)

MCP servers expose **Tools**, **Resources**, and optionally **Prompts**. ([FastMCP][1])

### Tools (actions)

* `detect_agent_config(workspace_path) -> candidates`
* `parse_config(agent, files) -> config_ir`
* `fetch_agent_doc(agent, topic) -> snippets` *(or rely on Context7 server directly)*
* `map_config(source_ir, target_agent, doc_snippets) -> target_ir`
* `render_target(target_ir) -> streamed_chunks`

### Resources (read-only context objects)

* `resource://agent-registry`
* `resource://concept-ontology`
* `resource://mapping-rules/{from}/{to}`

### Prompts (user-controlled workflows)

Expose a reusable workflow prompt like:

* `migrate_config_prompt(from, to, input_path)`
  Prompts are a first-class MCP concept for reusable templates. ([MCP Protocol][5])

---

## 4) End-to-end runtime flow

1. **CLI** reads inputs (`--from`, `--to`, file paths)
2. CLI calls **MCP tool** `parse_config` → Source IR
3. LLM obtains **latest docs** via Context7 (directly or via your fetcher) ([GitHub][2])
4. `map_config` builds Target IR
5. `render_target` streams chunks:

   * `BEGIN FILE: AGENTS.md`
   * section 1
   * section 2
   * …
   * `END FILE: AGENTS.md`
6. CLI writes output incrementally

---

## 5) Data stores & caching

* **Doc cache** (Context7 results, TTL)
* **Mapping cache** (from/to/version signatures → mapping result)
* **Telemetry (optional)**: warnings for unmapped concepts, size limits, etc.

  * Useful because Codex has a max bytes limit for project docs by default. ([OpenAI Developers][3])

---
