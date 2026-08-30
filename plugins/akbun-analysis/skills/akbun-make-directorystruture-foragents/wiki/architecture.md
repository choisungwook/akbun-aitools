# Architecture

## Responsibility

Creates a small, retrieval-oriented project memory layout plus AGENTS.md and a minimal CLAUDE.md pointer when explicitly requested.

## Boundary

Organize only recurring context and tell agents when to read it; do not create a broad archive or duplicate AGENTS.md inside CLAUDE.md.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Inspect recurring context needs, create the minimum memory directories, encode conditional read order in AGENTS.md, and make CLAUDE.md point to AGENTS.md.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
