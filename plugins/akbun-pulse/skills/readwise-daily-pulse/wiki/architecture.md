# Architecture

## Responsibility

Turns one day of Readwise intake into a short Korean mail draft a person can scan in a few minutes, ranked by relevance to a reader profile that the skill itself does not know.

## Boundary

- Everything personal is a variable (`PULSE_PROFILE`, `PULSE_INTERESTS`, `PULSE_CANDIDATE_TOPICS`, `PULSE_TO`) and the API token is environment-only. The skill files are published in a public repository, so no profile text, address, or token may ever be written into `SKILL.md`, references, scripts, or evals. Defaults stay generic (`엔지니어`, no interests).
- "Yesterday" is the half-open local-day interval in `PULSE_TZ`, filtered on `saved_at` / `highlighted_at`. The Readwise API only filters on `updated_at`, so the client-side date filter is mandatory and the collector owns it.
- Collection is read-only. The skill never edits Reader documents or highlights, and it creates a Gmail draft, never sends mail.
- URL handling is intentionally simple: `source_url` if it is HTTP(S), else the Reader URL. Gmail rewraps links when a draft is sent, so redirect unwrapping and post-creation link verification were dropped on purpose; do not reintroduce them.
- The mail layout (count line, highlights, `## changelog`, `## 읽을 것`, `## 나머지`, one continuous numbering) is fixed and enforced by `scripts/check_draft.py`.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Resolve variables (call text, then environment, then defaults); compute the local-day window; collect documents and highlights either through `collect_readwise.py` (API) or the Readwise MCP procedure in `references/mcp-collection.md`; read bodies; classify and write the digest; validate the body with `check_draft.py`; create the Gmail draft (Markdown file fallback); report counts and defaulted variables in chat.

## Terminology

- **pulse**: the digest for one local day.
- **changelog item**: a document whose body confirms a concrete product change; always carries exactly one English type suffix.
- **worth reading (읽을 것)**: incident/security and technical-analysis items with a stated, concrete link to the profile; 5-7 targeted, never padded.
- **the rest (나머지)**: everything else, grouped by site_name, no recommendation.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary, variables, and runtime instructions.
- [`references/mcp-collection.md`](../references/mcp-collection.md): MCP tool call sequence for `PULSE_SOURCE=mcp`; must stay in sync with the collector's window and filter semantics.
- [`scripts/collect_readwise.py`](../scripts/collect_readwise.py): owns the time window, pagination, date filter, dedupe, body fetch, and the JSON shape the digest is written from.
- [`scripts/check_draft.py`](../scripts/check_draft.py): owns the mail-format invariants; change it together with SKILL.md section 6.
