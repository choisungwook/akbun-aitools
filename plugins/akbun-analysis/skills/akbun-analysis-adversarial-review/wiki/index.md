# akbun-analysis-adversarial-review Wiki

This is the maintenance context the next agent reads before changing this skill. Runtime behavior remains in [SKILL.md](../SKILL.md).

## Purpose

Holds a two-sentence adversarial stance for reviewing the user's own code and claims: doubt hidden assumptions and unhandled exceptions, then give counterexamples with evidence. Manual-only so it applies when the user explicitly asks to be challenged.

## Read order

1. Read [architecture.md](architecture.md) for boundaries, flow, and resource ownership.
2. Read [development.md](development.md) before editing or validating the skill.
3. Read [SKILL.md](../SKILL.md) and only the supporting resources needed for the requested change.

## Documents

| Document | Purpose |
|---|---|
| [architecture.md](architecture.md) | Stable behavior, boundaries, flow, and resource ownership |
| [development.md](development.md) | Maintenance sequence, validation, and wiki upkeep |
