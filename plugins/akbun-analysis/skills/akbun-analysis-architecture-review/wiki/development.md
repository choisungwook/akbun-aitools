# Development

## Change sequence

1. Read [index.md](index.md), [architecture.md](architecture.md), and the affected section of [SKILL.md](../SKILL.md).
2. Read `references/review-lenses.md` only when the change touches lenses, interview questions, or metrics.
3. Keep invocation scope and runtime behavior in `SKILL.md`; keep lens, question, and metric detail in the reference; keep stable maintenance context here.
4. When adding a lens, add its breaking question and metrics to the reference in the same change.
5. Update this wiki when responsibility, boundaries, terminology, resource ownership, or a lasting caveat changes.
6. Add an ADR under `wiki/adr/` only when the decision is difficult to reverse, looks surprising without context, and involved a real trade-off.

## Validation

Run the repository's skill validator from the repository root:

```bash
uv run --python 3.12 --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/akbun-analysis/skills/akbun-analysis-architecture-review
```

Check Markdown links, confirm every metric in the reference has a counting method, confirm the document structure block in `SKILL.md` matches the per-finding section list, and verify that both plugin manifests use the release version required by the root AGENTS.md.

## Do not record

Do not use this wiki as a changelog, task log, temporary debugging notebook, copy of `SKILL.md`, or storage for generic documentation.
