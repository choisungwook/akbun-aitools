---
type: Claude Code Plugin
title: akbun-draw
description: "Image drawing skills by akbun — image-generation prompts and editable SVGs in fixed akbun styles"
resource: ../../plugins/akbun-draw/
tags: [plugin]
generated: { by: claude-code, at: 2026-11-22T00:00:00Z }
stale_after: 2027-02-13T00:00:00Z
sources:
  - id: manifest
    resource: ../../plugins/akbun-draw/.claude-plugin/plugin.json
    title: akbun-draw Claude manifest
    last_modified: 2026-11-16T00:00:00Z
  - id: readme
    resource: ../../README.md
    title: README plugin list
    last_modified: 2026-11-13T14:10:15Z
---

Image drawing skills by akbun — image-generation prompts and editable SVGs in fixed akbun styles[^manifest]

## Where

- Skills: [plugins/akbun-draw/skills/](../../plugins/akbun-draw/skills/)
- Three manifests (`.claude-plugin`, `.codex-plugin`, `.antigravity-plugin`), same `version`. Rules: [plugin-versioning](../policies/plugin-versioning.md)
- Skill list and when to use each: README `## plugin 목록` → `### akbun-draw` table (source of truth)[^readme]
- Choosing a draw skill: [docs/manual_draw.md](../../docs/manual_draw.md)
- `akbun-draw-diagram-haru`: arrows are straight (a bend is allowed only where a straight line would cross another shape); the `split` layout requires `titles` (`left`·`right`), drawn at the top-left of each half, with an empty gap and no divider line between halves; failure paths use the `blocked` edge (dashed accent line with an X) instead of borrowing `sync`, keeping the 3-color palette. Rejected: putting the half name in every shape `label` — it repeats the same word and spends the 12-character label limit. Layout routing lives in `references/layouts.jsonl` (`pick` says when to choose, `key`/`values`/`where` the per-shape slot, `title` panel titles, `same` the same-component marker) and the script reads only those fields, so adding a layout is one jsonl line; `stack` (top/bottom panels with solid panel outlines, left-to-right inside) and the `mono-yellow` palette (black arrows, one identical pale yellow `focus` fill per panel) were added this way, with per-panel step restarts allowed. All text (names, labels, notes, titles, step numbers) is ink in every palette; accent is only for arrow lines, heads and step circles, because accent-colored labels made text drift between black and blue across images. Rejected: hardcoding each layout's node key in the script — every new layout needed code, SKILL.md and selftest edits in three places.
- Decisions: [0002](../decisions/0002-reference-image-is-not-pixel-target.md), [0008](../decisions/0008-explainer-svg-reduced-to-chalkboard.md)

[^manifest]: akbun-draw Claude manifest
[^readme]: README plugin list
