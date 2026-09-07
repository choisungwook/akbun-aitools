# Architecture

## Responsibility

Turns one day of GitHub activity into a Korean digest a person can re-read to recall what was decided and why, then places it where the person will see it.

## Boundary

- Collection is read-only. The skill never writes to GitHub.
- The time window is local 00:00 to invocation time unless the user names another range. The script owns the window; the digest reports it verbatim.
- Scope is every non-archived repository the `gh` account can access, not only items the user authored. The GitHub MCP fallback only reaches items the user is involved in, and the digest must say so.
- Delivery never asks the user which output to use. A named output wins; otherwise Gmail, then Apple Notes, then a Markdown file.
- The digest structure (`## 시간`, `## 핵심작업`, `## 모든 작업`) is fixed; the value is in intent and decisions, not in title lists.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Run `collect_github_activity.py` (gh CLI: repo list, issues endpoint with `since`, pull detail per PR, comments since window, discussions via GraphQL) to a JSON file; group items by topic and write the digest from bodies and comments; deliver via the requested or default channel; echo the digest and a one-line delivery result in chat.

## Terminology

- **pulse**: the daily digest document for one time window.
- **topic (주제)**: a group of related items (an issue and its PR count as one topic).
- **key work (핵심작업)**: 3-5 completed or decided items; merged PRs and decided issues/discussions rank first.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`scripts/collect_github_activity.py`](../scripts/collect_github_activity.py): owns the time window, repo enumeration, and the JSON shape the digest is written from.
- [`scripts/create_apple_note.py`](../scripts/create_apple_note.py): Markdown to Apple Notes HTML subset; macOS only.
