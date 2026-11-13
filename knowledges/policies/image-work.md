---
type: Policy
title: Image work
description: "From reference images extract only the style; never copy subjects, scenes or text"
tags: [policy]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-05-13T00:00:00Z
sources:
  - id: agents
    resource: ../../AGENTS.md
    title: AGENTS.md
    last_modified: 2026-11-13T15:00:00Z
---

From reference images extract only the style; never copy subjects, scenes or text.

## Rules

- Record layout, spacing, color, line and typography as subject-independent rules (ratios, coordinates, color values).[^agents]
- Test draw skills with at least two different models.
- SVG fonts must be free-license fonts such as SIL OFL.
- Decision: [0002](../decisions/0002-reference-image-is-not-pixel-target.md).

[^agents]: AGENTS.md
