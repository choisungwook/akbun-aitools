# Architecture

## Responsibility

Own the loop "change one unit → run the repository's verification → keep or revert" and the filter that decides which changes reach a human. The skill does not own what a good refactoring looks like for a given language; it owns the gate and the report.

## Boundary

- Refactoring means changing something already in use while preserving behavior and meaning. Creating new things or adding features is out of scope, and the skill must not widen the user's stated range.
- "Verified" means a command the repository already uses (or a listed standard tool already installed) returned pass. A change with no such command is never reported as verified; it becomes a human item. This is the invariant that keeps the human report trustworthy.
- Human items are defined by the fixed table in `SKILL.md` section 5. Anything outside that table that passes verification is only counted, never listed.
- Baseline failures (failing before any change) are recorded, never fixed, so the diff stays attributable to the refactoring.
- The only question the skill asks is the report channel, once at the start. All other ambiguity becomes an assumption recorded as a human item. This keeps the skill usable in non-interactive runs where the default channel is stdout.
- Passing verification by editing tests, expectations, snapshots, lint rules, or the verification scope does not count as passing; it is reported as `검증 우회`.
- Delivery adapters are intentionally thin: stdout is the default and the fallback; GitHub PR body and issue are updated in place when a previous report exists; a file path is written as Markdown.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Ask the channel once → fix the scope and the working-tree state → build the verification matrix from repository-defined checks first (catalog order) → run everything once for the baseline → for each change unit: change, verify, fix own cause, revert after three failures → classify each unit against the human-item table → write the report in the fixed template order → deliver through the chosen channel, falling back to stdout with the reason on the first line.

## Terminology

- **change unit (변경 단위)**: one purpose per change; the granularity at which verification runs and classification happens.
- **verification (검증)**: a pass/fail command needing no human; anything else is not verification.
- **baseline (기준선)**: the verification result before the first change.
- **human item (사람 항목)**: a unit or fact matching the section-5 table.
- **channel (채널)**: `stdout`, `github-pr`, `github-issue`, `file:<path>`.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary, channel question, loop, classification table, report order.
- [`references/verification-catalog.md`](../references/verification-catalog.md): where to look for repository-defined checks and the standard-tool fallbacks per artifact type; owns the baseline recording rule.
- [`references/report-template.md`](../references/report-template.md): the fixed report layout and the per-channel placement; change it together with `SKILL.md` section 6.
