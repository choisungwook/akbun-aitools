# Negative instruction detection

When writing or editing any of these files:

- `CLAUDE.md`
- `.claude/rules/*.md`
- `.claude/skills/*/SKILL.md`
- `.claude/agents/*.md`

If the content includes negative language such as `never`, `don't`, `do not`, `must not`, `should not`, `avoid`, `prohibited` — stop and do the following:

1. Warn the user: tell them that negative instructions are better enforced as hooks, not written as passive rules.
2. Start an interview by asking these questions one at a time:
  - What specific behavior should be blocked or checked?
  - When should it trigger? (e.g., after writing a file, before a tool runs)
  - What should happen on violation? (block with error / warn only)
3. Use the answers to build a hook in `.claude/settings.json` and a script in `.claude/scripts/` instead.
