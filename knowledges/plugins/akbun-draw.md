---
type: Claude Code Plugin
title: akbun-draw
description: "Image drawing skills by akbun — image-generation prompts and editable SVGs in fixed akbun styles"
resource: ../../plugins/akbun-draw/
tags: [plugin]
generated: { by: claude-code, at: 2026-11-22T12:00:00Z }
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
- `akbun-draw-diagram-haru`: the model writes only a spec and `haru_prompt.py` assembles the prompt from `references/*.jsonl`; layout routing lives in `layouts.jsonl` fields, so a layout is one jsonl line plus script support only for new fields. The workflow starts from the relation the reader must see and maps it to a layout (`row`/`column`/`columns` steps, `hub`, `layers`, `split`/`stack` comparison, `loop`, `sequence` for time-ordered messages with lifelines, `wait` gaps and `spans` brackets). Missing shapes/palettes go in the work folder's `shapes.jsonl`/`palettes.jsonl` as new ids, merged at build/check. Lines, arrows and all text are ink; color is only a pale chip behind role labels (`chip`, palette `pastel`). Arrows are straight; failures use `blocked`; `split` has titles and no divider; `stack` uses panel outlines and `same`. Rejected: accent arrows and `focus` yellow fills (text color drifted, color leaked onto shapes), faking sequences with `column`, half names in every label, hardcoded per-layout keys. Decision: ADR 0009.
- Decisions: [0002](../decisions/0002-reference-image-is-not-pixel-target.md), [0008](../decisions/0008-explainer-svg-reduced-to-chalkboard.md)

[^manifest]: akbun-draw Claude manifest
[^readme]: README plugin list
