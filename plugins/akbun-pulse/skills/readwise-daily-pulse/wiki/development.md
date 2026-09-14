# Development

## Change sequence

1. Read [index.md](index.md), [architecture.md](architecture.md), and the affected section of [SKILL.md](../SKILL.md).
2. Read only the supporting resource involved in the change.
3. Keep invocation scope and runtime behavior in `SKILL.md`; keep stable maintenance context and terminology in this wiki.
4. If the collection window or filter semantics change, update `collect_readwise.py`, `references/mcp-collection.md`, and SKILL.md sections 1-2 in the same change.
5. If the mail layout changes, update SKILL.md section 6 and `check_draft.py` together.
6. Never add profile text, an email address, or a token to any file in this skill. Add a variable instead.
7. Update this wiki when responsibility, boundaries, terminology, resource ownership, or a lasting caveat changes.
8. Add an ADR under `wiki/adr/` only when the decision is difficult to reverse, looks surprising without context, and involved a real trade-off.

## Validation

Compile the scripts and exercise the checker with a passing and a failing body:

```bash
python3 -m py_compile plugins/akbun-pulse/skills/readwise-daily-pulse/scripts/*.py
python3 plugins/akbun-pulse/skills/readwise-daily-pulse/scripts/check_draft.py /tmp/pulse-body.md
```

Run the collector against a real token with a narrow day (the token stays in the environment):

```bash
READWISE_TOKEN=... python3 plugins/akbun-pulse/skills/readwise-daily-pulse/scripts/collect_readwise.py --date 2026-01-01 --with-content --out /tmp/pulse.json
```

Check that `range` matches the intended local day, `stats.excluded_by_date` is non-zero when the account has older updated documents, every document has `output_url` or none, and both plugin manifests carry the same version required by the root AGENTS.md.

## Do not record

Do not use this wiki as a changelog, task log, temporary debugging notebook, copy of `SKILL.md`, or storage for generic documentation.
