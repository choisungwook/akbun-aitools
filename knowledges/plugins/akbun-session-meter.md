---
type: Claude Code Plugin
title: akbun-session-meter
description: "Claude Code mod — session ID, estimated cost, tokens, context window usage, the agent list and a git diff view in panes and the status line"
resource: ../../mods/akbun-session-meter/
tags: [plugin, mod]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-18T09:27:50Z }
stale_after: 2027-02-18T00:00:00Z
sources:
  - id: manifest
    resource: ../../mods/akbun-session-meter/.claude-plugin/plugin.json
    title: akbun-session-meter Claude manifest
    last_modified: 2026-11-18T09:27:50Z
  - id: readme
    resource: ../../mods/akbun-session-meter/README.md
    title: akbun-session-meter README
    last_modified: 2026-11-18T09:27:50Z
---

Claude Code mod (hooks module, not skills) that shows session ID, estimated cost, context tokens, context window usage, the session's agent list and a git diff view in panes and the status line[^manifest]

## Where

- Hooks module: [mods/akbun-session-meter/hooks/register.tsx](../../mods/akbun-session-meter/hooks/register.tsx); git diff reading and parsing in `hooks/diff.ts`. Install (marketplace or `--plugin-dir`/`CLAUDE_CODE_PLUGIN_DIRS` folder), update, uninstall and test commands in its README[^readme]
- Diff view is git based (`git diff HEAD` plus untracked files), like the desktop app's diff panel; outside a git repo it shows nothing.
- Lives under `mods/`, not `plugins/`: Claude Code only, so it has one manifest (`.claude-plugin`) and is listed only in `.claude-plugin/marketplace.json`. `scripts/validate_plugins.py` and the Antigravity install loop read `plugins/*` alone, so they skip it.
- Rejected: placing it in `plugins/` with Codex and Antigravity manifests that would install nothing usable there.
- Checks: `claude plugin validate` and `claude plugin test` on the folder.

[^manifest]: akbun-session-meter Claude manifest
[^readme]: akbun-session-meter README
