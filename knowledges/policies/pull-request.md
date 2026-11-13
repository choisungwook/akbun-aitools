---
type: Policy
title: Pull request format
description: "PR body has three H1s (구현, 검증, 리스크), Korean bullet style, at most 40 lines"
tags: [policy]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-05-13T00:00:00Z
sources:
  - id: agents
    resource: ../../AGENTS.md
    title: AGENTS.md
    last_modified: 2026-11-13T16:00:00Z
  - id: template
    resource: ../../.github/pull_request_template.md
    title: PR template
    last_modified: 2026-11-13T16:00:00Z
---

PR body has three H1s (구현, 검증, 리스크), Korean bullet style, at most 40 lines.

## Rules

- Format source of truth: the PR template.[^template]
- No tracking Issue. Why goes in a `이유:` line under 구현, rejected options in a `버린 대안:` line, completion criteria in the 검증 table's 대상 cells; hard-to-reverse decisions go to docs/adr.[^agents]
- 검증 is a single `| 대상 | 방법 | 결과 |` table; checks not run say "검증하지 않음" with a reason.
- Checked by [check-pr-body](../checks/check-pr-body.md).

[^agents]: AGENTS.md
[^template]: PR template
