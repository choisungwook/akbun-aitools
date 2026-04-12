# akbun-readonce work guide

## Language

All code comments, documentation, and written content must be in **English**.

## Overview

A hook that prevents Claude Code from re-reading the same file within the same session.
Tracks mtime and sha256 of each file. If unchanged, blocks the Read and instructs Claude to use the previously loaded context.

## Design

Stores mtime/sha256 of read files in a per-session cache JSON file.

- **First read**: passes through and writes to cache
- **Re-read (unchanged)**: Read blocked + "use previously read content" message returned
- **Re-read (changed)**: passes through and updates cache

Cache file path is derived from the transcript path and is unique per session.

```
~/.claude/projects/<encoded-cwd>/<session-id>-read-cache.json
```

## Hook configuration

| Hook | Script | Role |
|---|---|---|
| PreToolUse(Read) | `scripts/pre-read.sh` | Check cache and decide allow/block |
| PostToolUse(Read) | `scripts/post-read.sh` | Write to cache after successful read |
| PreCompact | `scripts/pre-compact.sh` | Delete cache before compact |
| SessionStart | `scripts/session-start.sh` | Delete cache on /clear; purge stale caches on startup |

## Change detection order

1. Compare mtime (fast)
2. If mtime differs, compare sha256 (handles touch-only changes)
3. If sha256 also differs, treat as changed → allow Read

## Cache reset conditions

| Event | Action |
|---|---|
| `/clear` | SessionStart(source=clear) → delete current session cache |
| compact | PreCompact hook → delete current session cache |
| startup (new session) | SessionStart(source=startup) → delete cache files older than 7 days |

## Work history

Work history is recorded in `docs/changelog.md`. Read it before starting to understand the current state.

## Verification after changes

Always run unit tests after modifying code.

```bash
./hooks/readonce/tests/test-hooks.sh
```

All tests must pass. Confirm with "N passed, 0 failed" in the summary. Current baseline: 19 passed, 0 failed.
