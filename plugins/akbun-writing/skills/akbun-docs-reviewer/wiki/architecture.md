# Architecture

## Responsibility

Reviews an existing Korean technical document for readability and terminology consistency when explicitly requested.

## Boundary

Preserve facts, intent, Markdown structure, and the author's voice; report or apply focused corrections instead of rewriting the document into a new genre.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Read the source and review rules, identify evidence-backed readability or terminology issues, apply scoped corrections when authorized, then report unresolved uncertainty.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
