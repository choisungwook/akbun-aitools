# Development

## Change sequence

1. Read [index.md](index.md), [architecture.md](architecture.md), and the affected section of [SKILL.md](../SKILL.md).
2. Read only the supporting resources involved in the change: `references/procedure.md` for step rules, `references/verification-catalog.md` for detection or tool changes, `references/report-template.md` for report layout changes.
3. Keep `SKILL.md` short (about 1000 Korean characters excluding whitespace). Put new rules or tables in `references/procedure.md` and only a one-line pointer in `SKILL.md`. Step numbers in `procedure.md` must match `SKILL.md`.
4. Keep the human-item list (`SKILL.md` step 5), the table in `procedure.md` section 5, and `report-template.md` consistent; a new item kind needs all three.
5. Keep `disable-model-invocation: true`; the skill runs verification commands, deletes files after acceptance, and writes to GitHub, so it must stay user-invoked.
6. Update this wiki when responsibility, boundaries, terminology, resource ownership, or a lasting caveat changes.
7. Add an ADR under `wiki/adr/` only when the decision is difficult to reverse, looks surprising without context, and involved a real trade-off.

## Validation

Run the repository's skill validator from the repository root:

```bash
uv run --python 3.12 --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/akbun-refactoring/skills/akbun-refactoring-autoverify
```

Check both plugin manifests parse and share one version:

```bash
python3 -c 'import json; a=json.load(open("plugins/akbun-refactoring/.claude-plugin/plugin.json")); b=json.load(open("plugins/akbun-refactoring/.codex-plugin/plugin.json")); assert a["version"]==b["version"], (a["version"], b["version"]); print(a["version"])'
```

Observable checks:

- Every code block in `SKILL.md` and `references/*.md` has a language tag (the repository hook enforces this on edit).
- `SKILL.md` body length stays in range: `python3 -c 'import sys; s=open(sys.argv[1]).read().split("---",2)[2]; print(len("".join(s.split())))' plugins/akbun-refactoring/skills/akbun-refactoring-autoverify/SKILL.md`
- The report template's section order matches `SKILL.md` step 6 and `procedure.md` section 6.
- A dry read of the flow with no acceptance answer ends at the proposal report and edits nothing.
- A dry read of `SKILL.md` for a repository with no tests yields all changes as human items, never as verified.

## Do not record

Do not use this wiki as a changelog, task log, temporary debugging notebook, copy of `SKILL.md`, or storage for generic documentation.
