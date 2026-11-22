---
type: Architecture Decision Record
title: "0009 diagram-haru picks a layout from the relation; color only on role label chips"
description: "Spec-only model output assembled from jsonl; relation-first layout choice including sequence; work-folder shapes/palettes; ink lines and text, color only on label chips"
resource: ../../docs/adr/0009-diagram-haru-spec-assembled-prompt-and-color-roles.md
tags: [decision]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-22T12:00:00Z }
sources:
  - id: adr
    resource: ../../docs/adr/0009-diagram-haru-spec-assembled-prompt-and-color-roles.md
    title: ADR 0009
    last_modified: 2026-11-22T12:00:00Z
---

Scope: akbun-draw / akbun-draw-diagram-haru

## Decision

The model writes only a spec; `haru_prompt.py` assembles and scores the prompt from `references/*.jsonl`. Before the spec, decide the relation the reader must see and pick the matching layout; time-ordered messages between the same participants use `sequence` (lifelines, `wait` gaps, `spans` brackets). Missing shapes or palettes are defined as new ids in the work folder's `shapes.jsonl`/`palettes.jsonl` (merged, never overriding); missing layouts are proposed for `layouts.jsonl`. Lines, arrows, step numbers and text are all ink; color appears only as a pale chip behind labels whose role must be told apart, same role same chip. `focus` fills and accent-arrow palettes were removed.[^adr]

## Rejected

Accent arrows (text color drifted between blue and black), `focus` yellow fills (color spread to shapes), faking sequences with `column`, inventing shapes inside the spec.[^adr]

[^adr]: ADR 0009
