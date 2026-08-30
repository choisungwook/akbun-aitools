# Architecture

## Responsibility

Creates a first-day system onboarding document from code, documentation, and a focused interview when explicitly requested.

## Boundary

Separate verified system behavior from interview-only business rules and mark unknowns instead of inventing missing operational context.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Inspect available sources, map overview, business flows, architecture, dependencies, infrastructure, operations, access, and caveats, then interview only for consequential gaps.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
