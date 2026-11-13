---
type: Validation Script
title: check_pr_body.py
description: "Checks the PR body verification table, risk tier line and 40-line limit"
resource: ../../scripts/check_pr_body.py
tags: [check, ci]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-05-13T00:00:00Z
sources:
  - id: script
    resource: ../../scripts/check_pr_body.py
    title: check_pr_body.py
    last_modified: 2026-11-13T16:00:00Z
  - id: workflow
    resource: ../../.github/workflows/validate-pr.yml
    title: validate-pr.yml
    last_modified: 2026-10-24T06:16:56Z
---

Checks the PR body verification table, risk tier line and 40-line limit.[^script]

## Run

Run the same check locally:

```bash
PR_BODY="$(cat body.md)" uv run --python 3.12 scripts/check_pr_body.py --files changed.txt
```

## Self-test and CI

- Self-test: [test_check_pr_body.py](../../scripts/test_check_pr_body.py)
- CI: validate-pr.yml runs it on every PR.[^workflow]

[^script]: check_pr_body.py
[^workflow]: validate-pr.yml
