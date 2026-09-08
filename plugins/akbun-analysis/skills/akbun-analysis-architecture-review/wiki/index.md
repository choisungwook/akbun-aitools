# akbun-analysis-architecture-review Wiki

This is the maintenance context the next agent reads before changing this skill. Runtime behavior remains in [SKILL.md](../SKILL.md).

## Purpose

Adversarially reviews a current architecture from user-provided context and an active interview, then proposes better structures with evidence, quantified effects (security and operational toil are mandatory lenses), trade-offs, migration order, and mermaid diagrams when structure or call order changes.

## Read order

1. Read [architecture.md](architecture.md) for boundaries, flow, and resource ownership.
2. Read [development.md](development.md) before editing or validating the skill.
3. Read [SKILL.md](../SKILL.md) and only the supporting resources needed for the requested change.

## Documents

| Document | Purpose |
|---|---|
| [architecture.md](architecture.md) | Stable behavior, boundaries, flow, terminology, and resource ownership |
| [development.md](development.md) | Maintenance sequence, validation, and wiki upkeep |
