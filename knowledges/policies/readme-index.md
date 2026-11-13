---
type: Policy
title: README skill index
description: "Adding or removing a skill updates the README plugin table in the same change"
tags: [policy]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-05-13T00:00:00Z
sources:
  - id: agents
    resource: ../../AGENTS.md
    title: AGENTS.md
    last_modified: 2026-11-13T16:00:00Z
  - id: readme
    resource: ../../README.md
    title: README
    last_modified: 2026-11-13T14:10:15Z
---

Adding or removing a skill updates the README plugin table in the same change.

## Rules

- Tables live under README `## plugin 목록`.[^readme]
- Header is `| skill | 이럴 때 쓰세요 |`; each row describes the situation and ends with "때".[^agents]
- akbun-draw skills also update the situation table in docs/manual_draw.md.
- No plugin/skill counts in README.
- Checked by [validate-plugins](../checks/validate-plugins.md).

[^agents]: AGENTS.md
[^readme]: README
