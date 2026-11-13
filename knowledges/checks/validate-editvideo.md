---
type: Validation Script
title: validate_editvideo.py
description: "Checks akbun-editvideo frontmatter, manual, glossary, links, manifest and defaultPrompt consistency"
resource: ../../scripts/validate_editvideo.py
tags: [check, ci]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-05-13T00:00:00Z
sources:
  - id: script
    resource: ../../scripts/validate_editvideo.py
    title: validate_editvideo.py
    last_modified: 2026-10-25T02:55:38Z
  - id: workflow
    resource: ../../.github/workflows/validate-editvideo.yml
    title: validate-editvideo.yml
    last_modified: 2026-09-27T08:28:13Z
---

Checks akbun-editvideo frontmatter, manual, glossary, links, manifest and defaultPrompt consistency.[^script]

## Run

Run the same check locally:

```bash
uv run --python 3.12 scripts/validate_editvideo.py
```

## Self-test and CI

- Self-test: [test_validate_editvideo.py](../../scripts/test_validate_editvideo.py)
- CI: validate-editvideo.yml runs it only when the workflow's listed paths change (akbun-editvideo, docs, README, AGENTS.md, ...).[^workflow]

[^script]: validate_editvideo.py
[^workflow]: validate-editvideo.yml
