# Architecture

## Responsibility

Creates an incident state layout that lets troubleshooting continue across sessions without performing the investigation itself.

## Boundary

Keep confirmed facts, hypotheses, observations, search routing, and code paths separate; scaffold state only and never invent incident content.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Create the incident files and investigation index, define stable IDs and state transitions, then add conditional troubleshooting read and write rules to AGENTS.md.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
