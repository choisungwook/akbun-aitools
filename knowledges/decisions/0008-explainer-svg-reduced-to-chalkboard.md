---
type: Architecture Decision Record
title: "0008 Explainer SVG reduced to the chalkboard skill"
description: "Replace the akbun-draw-explainer-svg router with the akbun-draw-chalkboard skill and delete the other tokens"
resource: ../../docs/adr/0008-explainer-svg-router-reduced-to-chalkboard-skill.md
tags: [decision]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-22T00:00:00Z }
sources:
  - id: adr
    resource: ../../docs/adr/0008-explainer-svg-router-reduced-to-chalkboard-skill.md
    title: ADR 0008
    last_modified: 2026-11-22T00:00:00Z
---

Scope: akbun-draw / akbun-draw-chalkboard

## Decision

Replace the akbun-draw-explainer-svg router with the akbun-draw-chalkboard skill and delete the other tokens. The style is a design token that fixes colors, lines, fonts, effects and margins, never composition.[^adr]

[^adr]: ADR 0008
