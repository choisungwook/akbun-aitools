# akbun-refactoring-autoverify Wiki

This is the maintenance context the next agent reads before changing this skill. Runtime behavior remains in [SKILL.md](../SKILL.md).

## Purpose

Refactors things already in use (code, docs, config, infrastructure code) in small units: proposes modify/delete/create actions with evidence and waits for acceptance, gates every accepted unit behind the repository's own automated verification, and reports only the changes a human must judge, each with before/after and evidence. The report channel is asked once at the start and defaults to stdout.

## Read order

1. Read [architecture.md](architecture.md) for boundaries, flow, and resource ownership.
2. Read [development.md](development.md) before editing or validating the skill.
3. Read [SKILL.md](../SKILL.md) and only the supporting resources needed for the requested change.
4. Read domain or ADR documents only when the change touches them.

## Documents

| Document | Purpose |
|---|---|
| [architecture.md](architecture.md) | Stable behavior, boundaries, flow, and resource ownership |
| [development.md](development.md) | Maintenance sequence, validation, and wiki upkeep |
