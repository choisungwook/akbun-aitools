---
type: Architecture Decision Record
title: "0009 diagram-haru picks a layout from the relation; shade chips only for comparisons"
description: "Spec-only model output assembled from jsonl; relation-first layout choice including sequence; work-folder shapes/palettes; ink lines and text, shade chips only when comparing"
resource: ../../docs/adr/0009-diagram-haru-spec-assembled-prompt-and-color-roles.md
tags: [decision]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-22T15:00:00Z }
sources:
  - id: adr
    resource: ../../docs/adr/0009-diagram-haru-spec-assembled-prompt-and-color-roles.md
    title: ADR 0009
    last_modified: 2026-11-22T15:00:00Z
---

Scope: akbun-draw / akbun-draw-diagram-haru

## Decision

The model writes only a spec; `haru_prompt.py` assembles and scores the prompt from `references/*.jsonl`. Before the spec, decide the relation the reader must see and pick the matching layout; time-ordered messages between the same participants use `sequence` (lifelines, `wait` gaps, `spans` brackets). Missing shapes or palettes are defined as new ids in the work folder's `shapes.jsonl`/`palettes.jsonl` (merged, never overriding); missing layouts are proposed for `layouts.jsonl`. Lines, arrows, step numbers and text are all ink; shade colors are off by default and appear only as pale chips behind labels when the figure compares two or more roles or cases, one color per compared item (a single chip color fails the check). `focus` fills and accent-arrow palettes were removed.[^adr]

## Rejected

Laying chips whenever roles differ (user feedback: shade spread into ordinary figures), accent arrows (text color drifted between blue and black), `focus` yellow fills (color spread to shapes), faking sequences with `column`, inventing shapes inside the spec.[^adr]

[^adr]: ADR 0009
