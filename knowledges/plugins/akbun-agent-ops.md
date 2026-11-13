---
type: Claude Code Plugin
title: akbun-agent-ops
description: "Agent operations skills — set up a project's memory layout once, rebuild working context at session start, and turn each session's lessons into approved edits to the memory structure the codebase already has"
resource: ../../plugins/akbun-agent-ops/
tags: [plugin]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-02-13T00:00:00Z
sources:
  - id: manifest
    resource: ../../plugins/akbun-agent-ops/.claude-plugin/plugin.json
    title: akbun-agent-ops Claude manifest
    last_modified: 2026-11-08T01:23:16Z
  - id: readme
    resource: ../../README.md
    title: README plugin list
    last_modified: 2026-11-13T14:10:15Z
---

Agent operations skills — set up a project's memory layout once, rebuild working context at session start, and turn each session's lessons into approved edits to the memory structure the codebase already has[^manifest]

## Where

- Skills: [plugins/akbun-agent-ops/skills/](../../plugins/akbun-agent-ops/skills/)
- Three manifests (`.claude-plugin`, `.codex-plugin`, `.antigravity-plugin`), same `version`. Rules: [plugin-versioning](../policies/plugin-versioning.md)
- Skill list and when to use each: README `## plugin 목록` → `### akbun-agent-ops` table (source of truth)[^readme]

[^manifest]: akbun-agent-ops Claude manifest
[^readme]: README plugin list
