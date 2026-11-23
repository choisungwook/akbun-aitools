---
type: Claude Code Plugin
title: akbun-writing
description: "Writing, review, and blog support skills by akbun"
resource: ../../plugins/akbun-writing/
tags: [plugin]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-23T00:00:00Z }
stale_after: 2027-02-13T00:00:00Z
sources:
  - id: manifest
    resource: ../../plugins/akbun-writing/.claude-plugin/plugin.json
    title: akbun-writing Claude manifest
    last_modified: 2026-11-13T14:10:15Z
  - id: readme
    resource: ../../README.md
    title: README plugin list
    last_modified: 2026-11-13T14:10:15Z
---

Writing, review, and blog support skills by akbun[^manifest]

## Where

- Skills: [plugins/akbun-writing/skills/](../../plugins/akbun-writing/skills/)
- Three manifests (`.claude-plugin`, `.codex-plugin`, `.antigravity-plugin`), same `version`. Rules: [plugin-versioning](../policies/plugin-versioning.md)
- Agents: [plugins/akbun-writing/agents/](../../plugins/akbun-writing/agents/). `akbun-style-reviewer` checks akbun style; `akbun-cold-reader` reads only the draft file, without writer context, and is called at the end of akbun-writing
- akbun-writing templates: [references/templates/](../../plugins/akbun-writing/skills/akbun-writing/references/templates/), default `tech-blog`; user templates in `~/.config/akbun-writing/templates/` win on the same name
- Skill list and when to use each: README `## plugin 목록` → `### akbun-writing` table (source of truth)[^readme]
- Decisions: [0004](../decisions/0004-md-to-notion-cli-first.md)

[^manifest]: akbun-writing Claude manifest
[^readme]: README plugin list
