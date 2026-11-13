---
type: Architecture Decision Record
title: "0005 YouTube output is a transcript-grounded script"
description: "Produce a chronological Markdown transcript, not a summary"
resource: ../../docs/adr/0005-describe-youtube-transcript-output-is-transcript-grounded.md
tags: [decision]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
sources:
  - id: adr
    resource: ../../docs/adr/0005-describe-youtube-transcript-output-is-transcript-grounded.md
    title: ADR 0005
    last_modified: 2026-09-19T15:58:54Z
---

Scope: akbun-learning / akbun-describe-youtube-transcript

## Decision

Produce a chronological Markdown transcript, not a summary. Cleaned captions are primary input; raw VTT is fallback evidence.[^adr]

[^adr]: ADR 0005
