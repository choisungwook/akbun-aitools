---
type: Validation Script
title: validate_plugins.py
description: "Checks the three manifest versions match and bump +1, SKILL.md frontmatter name, README list and tables, and the manual_draw list"
resource: ../../scripts/validate_plugins.py
tags: [check, ci]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-05-13T00:00:00Z
sources:
  - id: script
    resource: ../../scripts/validate_plugins.py
    title: validate_plugins.py
    last_modified: 2026-11-08T01:23:16Z
  - id: workflow
    resource: ../../.github/workflows/validate-pr.yml
    title: validate-pr.yml
    last_modified: 2026-10-24T06:16:56Z
---

Checks the three manifest versions match and bump +1, SKILL.md frontmatter name, README list and tables, and the manual_draw list.[^script]

## Run

Run the same check locally:

```bash
uv run --python 3.12 scripts/validate_plugins.py --base origin/main
```

## Self-test and CI

- Self-test: [test_validate_plugins.py](../../scripts/test_validate_plugins.py)
- CI: validate-pr.yml runs it on every PR and every push to main.[^workflow]

[^script]: validate_plugins.py
[^workflow]: validate-pr.yml
