# Architecture

## Responsibility

Synchronizes Markdown or Obsidian files to Notion with CLI-first execution and an MCP fallback.

## Boundary

Use payload hashes to avoid unnecessary updates, prefer reproducible CLI operations, and use MCP only when the CLI cannot perform the required Notion action.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Identify sync metadata and target, compute whether content changed, run the Notion CLI, fall back to MCP when necessary, then report the resulting page and sync state.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
