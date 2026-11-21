---
type: Policy
title: Verification
description: "Run the checks matching the changed paths while editing and put commands and output in the PR verification table"
tags: [policy]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-21T07:00:00Z }
stale_after: 2027-05-13T00:00:00Z
sources:
  - id: agents
    resource: ../../AGENTS.md
    title: AGENTS.md
    last_modified: 2026-11-21T07:00:00Z
---

Run the checks matching the changed paths while editing and put commands and output in the PR verification table.

## Rules

- plugins/, README, docs/manual_draw.md → validate_plugins.py --base origin/main.[^agents]
- akbun-editvideo, docs/ → validate_editvideo.py.
- Before a PR, a subagent without the authoring context reviews the diff; the result goes in the verification table.
- Before `git push` or `gh pr create`, knowledges/ must be updated when plugins/, docs/adr/, scripts/ or AGENTS.md changed; `.claude/hooks/check-knowledges-before-push.sh` blocks the command otherwise (Claude Code only, other tools check by hand).
- Before opening a PR, run locally every `.github/workflows/` command that the changed paths trigger; before merging, `gh pr checks <n>` must be all pass. A red check that already fails on main is not waved through as pre-existing: it is fixed in the same PR or in a fix PR merged first. Rejected: merging with a PR comment that blames main — main stayed red after #380 and every later PR inherited the failure.
- Checks: [validate-plugins](../checks/validate-plugins.md), [validate-editvideo](../checks/validate-editvideo.md), [check-pr-body](../checks/check-pr-body.md).

[^agents]: AGENTS.md
