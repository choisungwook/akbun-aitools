---
type: Architecture Decision Record
title: "0002 Reference image is not a pixel target"
description: "Reference images/videos are only a style source; done is judged by rule checks, not pixel similarity"
resource: ../../docs/adr/0002-drawio-aws-vpc-reference-image-is-not-pixel-target.md
tags: [decision]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
sources:
  - id: adr
    resource: ../../docs/adr/0002-drawio-aws-vpc-reference-image-is-not-pixel-target.md
    title: ADR 0002
    last_modified: 2026-11-13T11:12:21Z
---

Scope: repo (draw skills, style tokens)

## Decision

Reference images/videos are only a style source; done is judged by rule checks, not pixel similarity. Subjects, scenes and text from the reference are never copied into outputs.[^adr]

[^adr]: ADR 0002
