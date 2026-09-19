# Development

## Change sequence

1. Read [index.md](index.md), [architecture.md](architecture.md), and [SKILL.md](../SKILL.md).
2. Keep `SKILL.md` to the stance sentences; add supporting resources only if the skill grows a real procedure.
3. Keep `disable-model-invocation: true` unless the user asks for automatic invocation.
4. Update this wiki when responsibility, boundaries, or a lasting caveat changes.
5. Add an ADR under `wiki/adr/` only when the decision is difficult to reverse, looks surprising without context, and involved a real trade-off.

## Validation

Run the repository's skill validator from the repository root:

```bash
uv run --python 3.12 --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/akbun-analysis/skills/akbun-analysis-adversarial-review
```

Confirm the frontmatter has `name`, `description`, and `disable-model-invocation`, and that both plugin manifests use the release version required by the root AGENTS.md.

## Do not record

Do not use this wiki as a changelog, task log, temporary debugging notebook, copy of `SKILL.md`, or storage for generic documentation.
