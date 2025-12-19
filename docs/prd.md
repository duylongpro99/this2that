# Plan for a Multi-Agent CLI Config Migration Tool (FastMCP Approach)

## Introduction and Problem Overview

AI coding assistants like **Claude Code, OpenAI Codex, Google Gemini CLI, and Kiro CLI** each use their own project configuration files to guide the agent. For example, Claude Code auto-loads a **CLAUDE.md** file, Codex looks for **AGENTS.md**, Gemini CLI uses **GEMINI.md**, and Kiro CLI reads markdown files under a **.kiro/steering/** folder[\[1\]](https://pnote.eu/notes/agents-md/#:~:text=,roorules%2Frules)[\[2\]](https://kiro.dev/docs/cli/steering/#:~:text=What%20is%20steering%3F). These files contain persistent instructions such as coding conventions, build/test commands, and project context that shape the agent’s behavior. While the core ideas overlap (e.g. code style guidelines, common commands, testing instructions), the formats and naming differ per tool[\[3\]](https://pnote.eu/notes/agents-md/#:~:text=Context%20files%20were%20popularized%20by,request%20sent%20to%20the%20LLM)[\[1\]](https://pnote.eu/notes/agents-md/#:~:text=,roorules%2Frules). This fragmentation makes it challenging to **migrate** a project’s “AI config” from one agent to another.

When assigning work, pick the matching role brief in `docs/roles/` and use the task-to-role map in
`docs/tasks/task_roles.md` to keep scope, inputs, and risks aligned.

**Goal:** Build a CLI-based solution (an MCP-powered agent) that can **dynamically convert** an origin agent’s config file into the target agent’s config format, **preserving all key concepts and instructions**. For instance, given a project’s .claude (Claude config) and a target of .codex (Codex), the tool should produce an equivalent Codex **AGENTS.md** that retains the project’s rules and context. The system must be **dynamic** – it should handle any supported agent names provided by the user – and always use the **latest official documentation** of each agent’s config to perform the mapping. We will leverage *Context7* MCP tools for up-to-date docs and examples[\[4\]](https://fastmcp.me/#:~:text=Discover%20Context7%20MCP%2C%20a%20powerful,boosts%20developer%20productivity%20and%20confidence), ensuring the migration uses current, version-specific settings.

## Key Requirements

* **Dynamic Documentation Fetching:** The solution should automatically retrieve the latest config format and guidelines for both the origin and target agent. By using the Context7 MCP server (via FastMCP), the agent can pull in official documentation for the specified CLI tools on demand[\[4\]](https://fastmcp.me/#:~:text=Discover%20Context7%20MCP%2C%20a%20powerful,boosts%20developer%20productivity%20and%20confidence). This avoids relying on outdated knowledge and makes the tool adaptable to new or updated agents. The user will specify the agent names (e.g. “Claude” and “Codex”), and those will be used in context7 queries to fetch their config docs.

* **Bidirectional & Flexible:** It should handle *any pair* of supported agents (Claude↔Codex, Gemini→Codex, Codex→Gemini, Kiro→Claude, etc.), not just a single direction. Both the origin and target formats are considered – the tool will fetch and understand **both** configurations before mapping.

* **Preserve Key Concepts:** The migration must carry over all important instructions (“the main concept”) from the origin file to the target. This includes sections like project setup steps, core file references, coding style conventions, testing or deployment commands, repository etiquette, and any custom rules. In essence, everything the origin’s config was encoding about how the AI should behave on the project should persist in the target’s config, just translated to its syntax/structure.

* **CLI Integration:** The implementation will be CLI-based, aligning with how these agents operate (terminal tools). The MCP agent can be invoked as a command (or within an MCP-compatible IDE/CLI like Cursor or Claude Code) to perform the conversion. This makes it easy to integrate into developer workflows (for example, a script or command to convert .claude to .codex in a repo).

* **Streamed Output (Chunked Generation):** To handle large config content and avoid one monolithic response, the tool should output the converted file in a streamed or section-by-section manner. For instance, it can generate each section of the target config sequentially (perhaps one heading or file at a time) rather than bundling the entire file in one reply. This ensures the conversion can scale to lengthy configs without hitting context limits, and lets users review parts incrementally. If multiple files need to be produced (e.g. Kiro’s multiple steering files), it will output them one by one.

## Non-goals

* Convert or manage runtime binary configs (only markdown-based agent configs are in scope).
* Handle auth secrets, API keys, or credential storage (users must manage secrets separately).
* Rewrite application code or refactor repositories during migration (config-only scope).

With these requirements in mind, below is a step-by-step plan for building the migration tool using FastMCP and Context7.

## Solution Outline

### 1\. Identify Origin and Target Agent Settings

**Input Processing:** The agent will first parse the user’s request to determine the origin and target agent types. For example, if the user says “migrate from .claude to .codex,” the tool identifies **Claude Code** as the source format and **OpenAI Codex** as the target. It may normalize the names (e.g. .claude → “Claude Code”, .gemini → “Gemini CLI”) to match known documentation references. This step ensures we know *which* config docs to fetch.

**Validation:** The tool can confirm that it recognizes both agent names and possibly list supported ones if not (Claude, Codex, Gemini, Kiro, etc.). This prevents proceeding with unknown formats. Once confirmed, it proceeds to fetch documentation for each.

### 2\. Fetch Latest Documentation via Context7 MCP

Using the **Context7** MCP server, the agent will dynamically retrieve the official or up-to-date documentation about each agent’s configuration files and settings. We instruct the MCP agent (e.g., by appending “use context7” in the prompt or via a tool invocation) to gather details such as:

* **Origin format details:** How the origin agent loads its config, expected file name/location, and content structure. For instance, Context7 would pull data on Claude Code’s .claude system – e.g. that *Claude Code reads CLAUDE.md files in a hierarchy (global \~/.claude/CLAUDE.md, then project root, then subdirectories)*[\[5\]](https://dinanjana.medium.com/mastering-the-vibe-claude-code-best-practices-that-actually-work-823371daf64c#:~:text=Claude%20Code%20reads%20information%20from,specific%20codebase%2C%20conventions%2C%20and%20quirks). This tells us what the Claude config looks like and its role. Similarly, if origin is Gemini CLI, we’d find that *Gemini by default looks for a GEMINI.md file for guidance*[\[6\]](https://pnote.eu/notes/agents-md/#:~:text=,roorules%2Frules), or if origin is Kiro, that *Kiro uses multiple markdown steering files under a .kiro/ folder*[\[2\]](https://kiro.dev/docs/cli/steering/#:~:text=What%20is%20steering%3F).

* **Target format details:** The agent also fetches documentation for the target’s config. For Codex, for example, we get that *Codex CLI auto-loads AGENTS.md files before doing any work*[\[7\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=Give%20Codex%20additional%20instructions%20and,context%20of%20your%20project) and how it merges global vs project-specific files[\[8\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=1,closer%20to%20your%20current%20task). This gives the expected file name (e.g. AGENTS.md with an “S” for Codex[\[1\]](https://pnote.eu/notes/agents-md/#:~:text=,roorules%2Frules)) and best practices for its content. For Claude target, we’d get CLAUDE.md guidelines; for Gemini, GEMINI.md or how to configure it to use AGENTS.md[\[9\]](https://news.ycombinator.com/item?id=44381169#:~:text=I%20agree%20that%20we%20should,you%20configure%20the%20filename%3A); for Kiro, how to structure steering files or the fact that Kiro also supports the AGENTS.md standard[\[10\]](https://kiro.dev/docs/cli/steering/#:~:text=Kiro%20supports%20providing%20steering%20directives,md%20files%20are%20always%20included).

Using Context7 ensures these docs are *fresh and version-specific*, reflecting the latest changes in each tool[\[4\]](https://fastmcp.me/#:~:text=Discover%20Context7%20MCP%2C%20a%20powerful,boosts%20developer%20productivity%20and%20confidence). The MCP tool will insert the relevant snippets into the agent’s context. (Behind the scenes, Context7 likely fetches from official sources – e.g. Anthropic’s guide, OpenAI’s Codex docs, etc. – meaning our agent has authoritative info to work with[\[4\]](https://fastmcp.me/#:~:text=Discover%20Context7%20MCP%2C%20a%20powerful,boosts%20developer%20productivity%20and%20confidence).)

### 3\. Analyze the Origin Configuration

Next, the agent will **parse and understand the origin’s config content** (which may be provided as text or read from the user’s project). This involves extracting the key conceptual sections and instructions. For example, if the origin is a Claude CLAUDE.md, it might contain sections like:

* **Common Commands & Setup:** e.g. how to install or run the project (dev server, tests, etc.).

* **Code Style Guidelines:** conventions for formatting, language usage, naming, etc.

* **Project Structure/Core Files:** important files or directories the agent should know (perhaps listed or described).

* **Testing/Deployment Instructions:** how to run tests, build or deploy the app, CI/CD notes.

* **Prohibitions or “Don’t” rules:** things the AI should avoid doing in this codebase.

* **Hooks or Automation Rules:** e.g. “after any significant change, run the linter” as seen in some .claude files[\[11\]](https://www.linkedin.com/posts/daneschilling_using-claude-code-for-the-first-time-it-activity-7360004345947410432-8RAP#:~:text=you%20said%20about%20small%20changes,and%20start%20using%20git%20worktree).

* **Repository Etiquette & Process:** commit message guidelines, code review process, etc.

These concepts are typically present in one form or another. (Indeed, an Anthropic article suggests including items like *common bash commands, core utilities, style guidelines, testing instructions, repo etiquette, and dev environment setup* in CLAUDE.md[\[12\]](https://pnote.eu/notes/agents-md/#:~:text=LLM) – a good blueprint of what to look for.) If the origin is Kiro’s steering files, the content might be split across multiple markdown files (product overview, tech stack, etc.[\[13\]](https://kiro.dev/docs/cli/steering/#:~:text=Foundational%20steering%20files%20are%3A)[\[14\]](https://kiro.dev/docs/cli/steering/#:~:text=Product%20Overview%20%28%60product.md%60%29%20,aligned%20with%20your%20product%20goals)), but collectively they cover similar ground. The agent will gather all these pieces.

**Parsing Approach:** If the origin file text is given, the tool can programmatically split it by headings or known patterns (e.g. lines starting with “\#\#” in markdown) to identify sections. If not given explicitly, we might use context7 \+ the repository to locate it. In an interactive scenario, the agent could ask the user to provide the origin config text if needed. In any case, at the end of this step, we have an internal representation of the origin’s instructions (structured by concept).

### 4\. Map Concepts to Target Format

This is the core of the migration: **translating the content** from origin structure to target structure while preserving meaning. Using the documentation fetched for the target, the agent will map each concept to the appropriate place or format in the target’s config. Key considerations:

* **File Naming and Organization:** Ensure we use the correct file for the target. For Codex or Gemini, that likely means producing an **AGENTS.md** at the project root (Gemini CLI supports configuring the name; it defaults to GEMINI.md but can use AGENTS.md as a standard[\[6\]](https://pnote.eu/notes/agents-md/#:~:text=,roorules%2Frules)[\[9\]](https://news.ycombinator.com/item?id=44381169#:~:text=I%20agree%20that%20we%20should,you%20configure%20the%20filename%3A)). For Claude, it means a **CLAUDE.md** file. For Kiro, the target could be either adopting the single AGENTS.md (since Kiro will auto-include it[\[10\]](https://kiro.dev/docs/cli/steering/#:~:text=Kiro%20supports%20providing%20steering%20directives,md%20files%20are%20always%20included)) *or* creating the .kiro/steering/\*.md files. Our plan should favor the simpler approach unless specified – since AGENTS.md is emerging as a universal standard, we could choose to output an AGENTS.md for targets that support it (Codex, Gemini, Kiro, etc.), and only use tool-specific names if needed (Claude still expects CLAUDE.md, though one could also symlink AGENTS.md to CLAUDE.md[\[15\]](https://pnote.eu/notes/agents-md/#:~:text=For%20proprietary%20agents%20that%20don%E2%80%99t,old%20symlinks%20do%20the%20job)). The user’s request suggests using target-specific extension (like “to .codex”), so we’ll abide by the target’s convention by default.

* **Section Heading Conversion:** We will reuse or convert section titles as needed. For example, if Claude’s file had “\#\# Code Style” and Codex typically also would have a “\#\# Code style” section in AGENTS.md[\[16\]](https://agents.md/#:~:text=), we keep that. If any wording differences exist (say, one tool’s docs recommend a different phrasing), adjust to match the target’s style without changing the essence.

* **Content Translation:** Most of the actual content (lists of rules, commands, etc.) can be carried over verbatim, since they are user/project-specific details. The main task is to ensure formatting and context cues are correct for the target. For instance, Claude might have some instructions phrased for Claude specifically; if converting to Codex, we ensure none of the instructions refer to “Claude” or use Anthropic-specific slash commands. The Context7 docs help here: e.g., if Claude’s config used a certain annotation or if Gemini’s format allows certain JSON or context blocks (Gemini has a settings.json where one can reference AGENTS.md[\[17\]](https://github.com/google-gemini/gemini-cli/discussions/1471#:~:text=GitHub%20github,block%20above%20into%20.gemini%2Fsettings.json), but we focus on the markdown content itself). We’ll adjust any syntactic differences.

* **Agent-Specific Features:** Map any special features. For example, Claude Code supports “Stop hooks” and custom /init commands in CLAUDE.md[\[18\]](https://www.humanlayer.dev/blog/writing-a-good-claude-md#:~:text=,generate%20your%20%60CLAUDE.md). If those exist and the target has an equivalent (Codex has slash commands and an *Autofix CI* feature, Kiro has **hooks**[\[19\]](https://kiro.dev/cli/#:~:text=agents%2Fcreating%2F%29%20for%20your%20workflows.%20,completion%5D%28%2Fdocs%2Fcli%2Fautocomplete%2F%29%20with%20context%20awareness), etc.), translate accordingly. That might mean converting a CLAUDE.md instruction “run linter after changes” into a Codex context instruction (e.g. adding to AGENTS.md: “Always run npm run lint before committing” if not already present[\[20\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=)) or even into a hook configuration if the target exposes one via MCP or CLI config. We aim to **preserve functionality**: if the origin guided the AI to run tests or avoid certain files, the target config should do the same using its paradigms.

* **Omitting Incompatible Parts:** In rare cases where an origin instruction cannot be replicated (for example, if one agent had a concept the other doesn’t support at all), we will still carry over a note or comment about it so the intent isn’t lost. (For instance, if migrating *to* Claude and the origin had a multi-file hierarchy, we might condense it into one CLAUDE.md, since Claude doesn’t support nested AGENTS.md overrides beyond directory-level CLAUDE.md files).

Throughout this mapping, the agent uses the fetched docs as a reference. For example, OpenAI’s guide might say *“Add global instructions in \~/.codex/AGENTS.md and project-specific ones in repo’s AGENTS.md”*[\[8\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=1,closer%20to%20your%20current%20task)[\[21\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=2.%20Create%20%60,preferences) – our tool will follow that by putting the content into the project’s AGENTS.md (assuming project-specific). The docs also give hints on style: e.g., *Codex suggests covering build/test commands, style, etc*[\[22\]\[16\]](https://agents.md/#:~:text=), which align with what we extracted, so we ensure those are present in clear sections. In essence, the mapping step is like using the origin as a template of *what to say*, and the target’s docs as a template of *how to say it*.

### 5\. Generate the Target Configuration Output

Now the agent will **compose the output file(s)** for the target format. We will do this in a structured way to ensure readability and correctness:

* **Proper Markdown Structure:** Use the appropriate top-level heading for the file (some projects might start AGENTS.md with a title line “\# AGENTS.md” or a brief intro – we saw an example snippet[\[22\]](https://agents.md/#:~:text=)). We’ll include all the migrated sections with \#\# or \#\#\# headings as needed, keeping formatting consistent. Lists of rules will remain as bullet points. We make sure any code commands remain fenced or backticked as in the origin. The goal is a clean, logically organized markdown that the target agent will parse or at least include as context.

* **Section-by-Section Streaming:** Instead of printing the entire file at once, the MCP agent can output one section at a time. For example, it might first output the “\#\# Setup commands” section with the list of commands[\[23\]](https://agents.md/#:~:text=), then stream the next “\#\# Code style” section, and so on. Each section will be a few lines (which fits the guideline of keeping paragraphs short and manageable). This approach prevents overwhelming the user (or the model) with a huge blob of text. The user can watch the file build up in real-time. If using a tool like Cursor or VSCode’s MCP client, this streaming could directly write into an open editor.

* **Multiple Files (if needed):** In cases like migrating *to* Kiro’s .kiro/steering, the agent might decide to output multiple files (e.g., product.md, tech.md, etc., as Kiro’s docs recommend foundational steering files[\[13\]](https://kiro.dev/docs/cli/steering/#:~:text=Foundational%20steering%20files%20are%3A)[\[14\]](https://kiro.dev/docs/cli/steering/#:~:text=Product%20Overview%20%28%60product.md%60%29%20,aligned%20with%20your%20product%20goals)). It would then stream each file content separately, clearly indicating the file name. However, since Kiro also accepts a single AGENTS.md, an alternative is to produce AGENTS.md for simplicity (or do both). This design decision would be based on user preference – the plan could make this configurable. For now, we assume one primary output file unless the target strictly requires splitting.

* **Preserve Comments/Explanations:** We might insert brief comments (as HTML comments or in a section) if certain context might need explanation. For example, “(The following rules were migrated from Claude’s config)” – though ideally, the content speaks for itself and such notes aren’t necessary in the final file, since the file is meant for the agent, not a person. We’ll keep the output clean for agent consumption.

**Example (Claude → Codex):** If the Claude .claude had a rule *“Don’t use class components (legacy codebase)”*, in Codex’s AGENTS.md under “\#\# Don’t Do This” we’d include that bullet. If Claude’s file had a project build command example, we’d ensure an equivalent “\#\# Setup” or “\#\# Build and Test” section in AGENTS.md has it. By the end of generation, the AGENTS.md should comprehensively reflect what the CLAUDE.md conveyed, just formatted for Codex.

Finally, the agent outputs (or saves, if integrated in an environment) the new config file. The user can then place this in their project (e.g., commit the AGENTS.md or replace the old config). We will have effectively **migrated the agent’s memory bank** from one format to another.

### 6\. Verification and Iteration

After generation, it’s wise to verify that the target agent indeed picks up the new file and that nothing critical was lost:

* The tool can suggest running a quick test, for instance: if the target is Codex CLI, run codex \--ask-for-approval never "Summarize the current instructions." as per OpenAI’s docs[\[24\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=,adding%20new%20production%20dependencies) to see if Codex lists the instructions from the new AGENTS.md. This confirms the file is correctly read. Similarly, for Claude, one might start Claude Code in that directory and confirm it acknowledges the CLAUDE.md content. Such verification could be offered as an optional step or instructions to the user.

* If any instruction didn’t translate well (say the origin had a very tool-specific note), the user or the agent may refine it. The plan includes using up-to-date best practices, so the agent might proactively adjust content (for example, the HumanLayer blog advises not to overload CLAUDE.md with too many minor rules[\[25\]](https://www.humanlayer.dev/blog/writing-a-good-claude-md#:~:text=It%20can%20be%20tempting%20to,We%20recommend%20against%20this)[\[26\]](https://www.humanlayer.dev/blog/writing-a-good-claude-md#:~:text=,applicability); if converting *to* Claude, the agent might consolidate redundant points).

This iterative refinement is part of ensuring the output is **comprehensive but concise**, following target guidelines. The Context7 docs and examples provide guidance on what an ideal file looks like for each agent, so we align with those (e.g., OpenAI’s Agents.md site gives examples of content and format[\[22\]\[16\]](https://agents.md/#:~:text=)).

## Conclusion

By combining the **Model Context Protocol** with context-fetching tools, we can create a robust migration agent that bridges the gap between different AI coding assistants. The plan ensures that all crucial project instructions – from coding style to build commands – are **persistently carried over** to the new format, maintaining the “memory” the AI needs about the project. Leveraging Context7 means the solution stays current with each tool’s evolving syntax and features[\[4\]](https://fastmcp.me/#:~:text=Discover%20Context7%20MCP%2C%20a%20powerful,boosts%20developer%20productivity%20and%20confidence), and using a streaming, section-wise output makes the process transparent and manageable. In essence, this tool will let developers easily switch their AI pair programmer from, say, Claude to Codex or Gemini, without losing any project-specific guidance. The result is a converted config (CLAUDE.md, GEMINI.md, AGENTS.md, etc. as appropriate) that empowers the target coding agent to immediately work with the same understanding of the project as the previous one[\[3\]](https://pnote.eu/notes/agents-md/#:~:text=Context%20files%20were%20popularized%20by,request%20sent%20to%20the%20LLM)[\[7\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=Give%20Codex%20additional%20instructions%20and,context%20of%20your%20project). This fosters a more unified ecosystem – moving us toward a world where, regardless of the AI agent chosen, it can tap into the same **AGENTS.md**\-style knowledge base for the project[\[27\]](https://pnote.eu/notes/agents-md/#:~:text=The%20bikeshed,AGENTS.md)[\[15\]](https://pnote.eu/notes/agents-md/#:~:text=For%20proprietary%20agents%20that%20don%E2%80%99t,old%20symlinks%20do%20the%20job).

**Sources:** The approach above references official and community insights on each tool’s configuration mechanism, including Anthropic’s Claude Code best practices, OpenAI’s Codex documentation, Google’s Gemini CLI notes, and Kiro’s docs, ensuring the migration uses validated patterns from each source. Key citations have been preserved throughout to indicate where practices and details were obtained, in line with the latest documentation.

---

[\[1\]](https://pnote.eu/notes/agents-md/#:~:text=,roorules%2Frules) [\[3\]](https://pnote.eu/notes/agents-md/#:~:text=Context%20files%20were%20popularized%20by,request%20sent%20to%20the%20LLM) [\[6\]](https://pnote.eu/notes/agents-md/#:~:text=,roorules%2Frules) [\[12\]](https://pnote.eu/notes/agents-md/#:~:text=LLM) [\[15\]](https://pnote.eu/notes/agents-md/#:~:text=For%20proprietary%20agents%20that%20don%E2%80%99t,old%20symlinks%20do%20the%20job) [\[27\]](https://pnote.eu/notes/agents-md/#:~:text=The%20bikeshed,AGENTS.md) AGENTS.md becomes the convention

[https://pnote.eu/notes/agents-md/](https://pnote.eu/notes/agents-md/)

[\[2\]](https://kiro.dev/docs/cli/steering/#:~:text=What%20is%20steering%3F) [\[10\]](https://kiro.dev/docs/cli/steering/#:~:text=Kiro%20supports%20providing%20steering%20directives,md%20files%20are%20always%20included) [\[13\]](https://kiro.dev/docs/cli/steering/#:~:text=Foundational%20steering%20files%20are%3A) [\[14\]](https://kiro.dev/docs/cli/steering/#:~:text=Product%20Overview%20%28%60product.md%60%29%20,aligned%20with%20your%20product%20goals) Steering \- CLI \- Docs \- Kiro

[https://kiro.dev/docs/cli/steering/](https://kiro.dev/docs/cli/steering/)

[\[4\]](https://fastmcp.me/#:~:text=Discover%20Context7%20MCP%2C%20a%20powerful,boosts%20developer%20productivity%20and%20confidence) FastMCP \- The AppStore for MCP Servers | Cursor, VS Code, Claude Desktop & More | FastMCP

[https://fastmcp.me/](https://fastmcp.me/)

[\[5\]](https://dinanjana.medium.com/mastering-the-vibe-claude-code-best-practices-that-actually-work-823371daf64c#:~:text=Claude%20Code%20reads%20information%20from,specific%20codebase%2C%20conventions%2C%20and%20quirks) Mastering the Vibe: Claude Code Best Practices That Actually Work | by Dinanjana Gunaratne | Medium

[https://dinanjana.medium.com/mastering-the-vibe-claude-code-best-practices-that-actually-work-823371daf64c](https://dinanjana.medium.com/mastering-the-vibe-claude-code-best-practices-that-actually-work-823371daf64c)

[\[7\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=Give%20Codex%20additional%20instructions%20and,context%20of%20your%20project) [\[8\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=1,closer%20to%20your%20current%20task) [\[20\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=) [\[21\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=2.%20Create%20%60,preferences) [\[24\]](https://developers.openai.com/codex/guides/agents-md/#:~:text=,adding%20new%20production%20dependencies) Custom instructions with AGENTS.md

[https://developers.openai.com/codex/guides/agents-md/](https://developers.openai.com/codex/guides/agents-md/)

[\[9\]](https://news.ycombinator.com/item?id=44381169#:~:text=I%20agree%20that%20we%20should,you%20configure%20the%20filename%3A) Can't we standardize on AGENTS.md instead of all these specific ...

[https://news.ycombinator.com/item?id=44381169](https://news.ycombinator.com/item?id=44381169)

[\[11\]](https://www.linkedin.com/posts/daneschilling_using-claude-code-for-the-first-time-it-activity-7360004345947410432-8RAP#:~:text=you%20said%20about%20small%20changes,and%20start%20using%20git%20worktree) First impressions of Claude Code: a new AI experience | Dane Schilling posted on the topic | LinkedIn

[https://www.linkedin.com/posts/daneschilling\_using-claude-code-for-the-first-time-it-activity-7360004345947410432-8RAP](https://www.linkedin.com/posts/daneschilling_using-claude-code-for-the-first-time-it-activity-7360004345947410432-8RAP)

[\[16\]](https://agents.md/#:~:text=) [\[22\]](https://agents.md/#:~:text=) [\[23\]](https://agents.md/#:~:text=) AGENTS.md

[https://agents.md/](https://agents.md/)

[\[17\]](https://github.com/google-gemini/gemini-cli/discussions/1471#:~:text=GitHub%20github,block%20above%20into%20.gemini%2Fsettings.json) AGENTS.md thought leadership · google-gemini gemini-cli \- GitHub

[https://github.com/google-gemini/gemini-cli/discussions/1471](https://github.com/google-gemini/gemini-cli/discussions/1471)

[\[18\]](https://www.humanlayer.dev/blog/writing-a-good-claude-md#:~:text=,generate%20your%20%60CLAUDE.md) [\[25\]](https://www.humanlayer.dev/blog/writing-a-good-claude-md#:~:text=It%20can%20be%20tempting%20to,We%20recommend%20against%20this) [\[26\]](https://www.humanlayer.dev/blog/writing-a-good-claude-md#:~:text=,applicability) Writing a good CLAUDE.md | HumanLayer Blog

[https://www.humanlayer.dev/blog/writing-a-good-claude-md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

[\[19\]](https://kiro.dev/cli/#:~:text=agents%2Fcreating%2F%29%20for%20your%20workflows.%20,completion%5D%28%2Fdocs%2Fcli%2Fautocomplete%2F%29%20with%20context%20awareness) CLI \- Kiro

[https://kiro.dev/cli/](https://kiro.dev/cli/)
