# Development

## Change sequence

1. Read [index.md](index.md), [architecture.md](architecture.md), and the affected section of [SKILL.md](../SKILL.md).
2. Read only the scripts involved in the change.
3. Keep invocation scope and runtime behavior in `SKILL.md`; keep stable maintenance context and terminology in this wiki.
4. When changing the diary format, update the template block, the writing principles, and the completion checklist in `SKILL.md` together.
5. If `create_apple_note.py` changes, apply the same change to the copy under `plugins/akbun-pulse/skills/github-daily-pulse/scripts/`.
6. Update this wiki when responsibility, boundaries, terminology, resource ownership, or a lasting caveat changes.
7. Add an ADR under `wiki/adr/` only when the decision is difficult to reverse, looks surprising without context, and involved a real trade-off.

## Validation

Run the repository's skill validator from the repository root:

```bash
uv run --python 3.12 --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/akbun-writing/skills/akbun-voice-diary
```

Compile the scripts and check the non-macOS exit code:

```bash
python3 -m py_compile plugins/akbun-writing/skills/akbun-voice-diary/scripts/*.py
python3 plugins/akbun-writing/skills/akbun-voice-diary/scripts/create_calendar_event.py "t" 2026-01-03; echo $?
```

On macOS, create one event in a throwaway calendar and run the same command twice; the second run must print `exists`. Verify that both plugin manifests use the release version required by the root AGENTS.md.

## Do not record

Do not use this wiki as a changelog, task log, temporary debugging notebook, copy of `SKILL.md`, or storage for generic documentation.
