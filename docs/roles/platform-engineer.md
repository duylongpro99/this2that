# Platform engineer

## Mission
- Stand up the CLI and FastMCP server surfaces so migrations run reliably from dev shells or MCP
  clients.

## Scope
- CLI command shape (`--from`, `--to`, `--input`, `--output`, dry-run, verbose/json flags).
- FastMCP server bootstrap, stdio transport, tool/resource registration.
- Process-level concerns: logging hooks, config loading, env handling, exit codes.
- Developer ergonomics: Makefile targets, local run scripts, packaging guidance.

## Outputs
- Executable CLI entrypoint callable from repo root or subfolders.
- FastMCP server that declares capabilities and starts cleanly over stdio.
- Clear error surfaces for invalid agent names, files, or arguments.
- Minimal build/run docs wired into README/Makefile.

## Inputs needed
- Supported agent list and naming normalization from the registry owner.
- Streaming requirements from the renderer owner (chunking, delimiting).
- Logging/telemetry expectations from the product owner.

## Collaboration signals
- Pair with the registry engineer to validate agent lookups and metadata.
- Pair with the mapping/renderer engineer to integrate streaming output.
- Loop QA early on flag validation and error pathways.

## Risks to watch
- Non-deterministic output ordering when piping to other tools.
- Stdio transport misconfigurations that break MCP discovery.
- Flag creep—keep CLI surface narrow and documented.
