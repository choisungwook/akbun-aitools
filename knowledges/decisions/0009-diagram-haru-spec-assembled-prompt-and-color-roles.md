---
type: Architecture Decision Record
title: "0009 diagram-haru assembles prompts from a spec; text is ink, accent only on arrows"
description: "Model writes only a spec, the script assembles the prompt from jsonl libraries; all text ink, accent on arrows only, one focus fill color"
resource: ../../docs/adr/0009-diagram-haru-spec-assembled-prompt-and-color-roles.md
tags: [decision]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-22T00:00:00Z }
sources:
  - id: adr
    resource: ../../docs/adr/0009-diagram-haru-spec-assembled-prompt-and-color-roles.md
    title: ADR 0009
    last_modified: 2026-11-22T00:00:00Z
---

Scope: akbun-draw / akbun-draw-diagram-haru

## Decision

The model writes only a diagram spec; `haru_prompt.py` assembles and scores the prompt from `references/*.jsonl`, and layout routing lives in `layouts.jsonl` fields. All text (names, labels, notes, titles, step numbers) is ink in every palette; accent is only for arrow lines, heads, `blocked` X strokes and step circles. A palette's `focus` fill is one color painted identically on every focus shape, at most one per panel. Arrows are straight and bend once only around a shape; failures use `blocked`.[^adr]

## Rejected

Accent-colored labels (text flipped between blue and black across images), two alternating yellows (uneven yellow within one image), per-layout node keys hardcoded in the script, half names repeated in every label.[^adr]

[^adr]: ADR 0009
