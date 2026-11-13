---
type: Policy
title: Risk tiers
description: "Changed paths set the PR risk tier; agents never merge high-tier PRs"
tags: [policy]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-05-13T00:00:00Z
sources:
  - id: agents
    resource: ../../AGENTS.md
    title: AGENTS.md
    last_modified: 2026-11-13T15:00:00Z
  - id: checker
    resource: ../../scripts/check_pr_body.py
    title: check_pr_body.py
    last_modified: 2026-11-13T13:29:35Z
---

Changed paths set the PR risk tier; agents never merge high-tier PRs.

## Rules

| Tier | Paths |
|---|---|
| low (낮음) | README.md, docs/, imgs/, other docs |
| medium (중간) | plugins/** |
| high (높음) | .github/**, AGENTS.md, CLAUDE.md, scripts/**, .claude/**, .claude-plugin/**, .agents/** |

Mixed PRs take the highest tier.[^agents] Paths not in the table (including knowledges/) fall through to low; `risk_tier` in check_pr_body.py computes it.[^checker]

[^agents]: AGENTS.md
[^checker]: check_pr_body.py
