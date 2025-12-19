---
description: Execute a full Codex agent workflow from context intake to state update
argument-hint: "[TASK_ID=<id>] [MODE=solo|parallel|sync]"
---

Read `README.md` first to understand the current and up-to-date state of the system, including architecture, features, and known limitations.

Read `AGENTS.md` to understand existing agents, coordination rules, and ownership boundaries.

Check the task source of truth (e.g. `TASKS.md`, issues, or `/tasks/*.yaml`) to determine current task statuses and identify the next task to implement.
If `TASK_ID` is provided, focus exclusively on that task.

Analyze the selected task:
- Classify task type (feature, refactor, infra, test, docs, research)
- Identify impact radius, risk level, and dependencies
- Decide whether the task can run solo, in parallel, or requires synchronization
If `MODE` is provided, follow it explicitly.

Atomically claim the task by updating its status to `claimed`, recording the agent name and timestamp.
If running in parallel, explicitly list sibling tasks and coordination notes.

Before coding, design the solution:
- Define inputs, outputs, and failure modes
- Check backward compatibility against documented behavior
- Confirm alignment with the system architecture in `README.md`

Implement the task in small, focused commits:
- One concern per commit
- Clear, descriptive commit messages
- No silent scope expansion; record any scope changes in task notes

After implementation, perform a mandatory self-review:
- Mechanical review: build, lint, type checks, tests, dead code, performance issues
- Semantic review: task completeness, edge cases, architectural consistency, clarity for other agents
If confidence is below 0.8, mark the task as `review` instead of `done`.

Integrate changes with the target branch:
- Rebase or merge consciously
- Resolve conflicts by preferring documented behavior
- Re-run all checks after integration
Record any architectural disagreements or risks in `AGENTs.md`.

After successful integration, update system state:
- Update `README.md` to reflect the new system state, features, or limitations
- Update `AGENTs.md` with agent activity, coordination notes, and follow-ups
- Update task status to `done`, including a summary, technical debt notes, and suggested next tasks
