# Development

## Change sequence

1. Read [index.md](index.md), [architecture.md](architecture.md), and the affected section of [SKILL.md](../SKILL.md).
2. Read only the script involved in the change.
3. Keep invocation scope and runtime behavior in `SKILL.md`; keep stable maintenance context and terminology in this wiki.
4. If the JSON shape produced by `collect_github_activity.py` changes, update the field names in `SKILL.md` section 1 and 2 in the same change.
5. Update this wiki when responsibility, boundaries, terminology, resource ownership, or a lasting caveat changes.
6. Add an ADR under `wiki/adr/` only when the decision is difficult to reverse, looks surprising without context, and involved a real trade-off.

## Validation

Run the skill validator from the repository root:

```bash
uv run --python 3.12 --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/akbun-pulse/skills/github-daily-pulse
```

Compile the scripts and run the collector against a real `gh` login with a narrow window:

```bash
python3 -m py_compile plugins/akbun-pulse/skills/github-daily-pulse/scripts/*.py
python3 plugins/akbun-pulse/skills/github-daily-pulse/scripts/collect_github_activity.py --since "$(date +%F)T00:00:00" --out /tmp/pulse.json
```

Check that `items` contain the four kinds (issue, merged PR, open/draft PR, discussion) when the account has such activity, that `errors` is empty, and that both plugin manifests carry the same version required by the root AGENTS.md.

## Do not record

Do not use this wiki as a changelog, task log, temporary debugging notebook, copy of `SKILL.md`, or storage for generic documentation.
