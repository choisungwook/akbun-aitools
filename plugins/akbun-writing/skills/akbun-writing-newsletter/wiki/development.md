# Development

## Change sequence

1. Read [index.md](index.md), [architecture.md](architecture.md), and the affected section of [SKILL.md](../SKILL.md).
2. Read only the supporting references involved in the change.
3. Keep invocation scope and runtime behavior in `SKILL.md`; keep stable maintenance context and terminology in this wiki.
4. Keep `SKILL.md` and `references/newsletter-layout.md` in sync on module order and card lines.
5. Update this wiki when responsibility, boundaries, terminology, resource ownership, or a lasting caveat changes.
6. Add an ADR under `wiki/adr/` only when the decision is difficult to reverse, looks surprising without context, and involved a real trade-off.

## Validation

Run the repository's skill validator from the repository root:

```bash
uv run --python 3.12 --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/akbun-writing/skills/akbun-writing-newsletter
```

Check Markdown links, confirm that every code block has a language tag, confirm that no paywall or CTA instruction leaked into `SKILL.md`, and verify that both plugin manifests use the release version required by the root AGENTS.md.

## Do not record

Do not use this wiki as a changelog, task log, temporary debugging notebook, copy of `SKILL.md`, or storage for generic documentation.
