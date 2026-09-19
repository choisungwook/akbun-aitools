# Architecture

## Responsibility

Own three things: the proposal gate (what will be modified, deleted, or created, with evidence, accepted by a human before any edit), the loop "change one unit → run the repository's verification → keep or revert", and the filter that decides which changes reach a human. The skill does not own what a good refactoring looks like for a given language; it owns the gates and the report.

The motivation lives in `SKILL.md` ("동기와 기대") because the agent must weigh it at runtime: faster implementation does not make human understanding faster, so the skill removes humans from repeated review only while leaving verifiable evidence, and keeps product-intent and quality-bar decisions with humans.

## Boundary

- Refactoring means changing something already in use while preserving behavior and meaning. Creating new things or adding features is out of scope, and the skill must not widen the user's stated range.
- "Verified" means a command the repository already uses (or a listed standard tool already installed) returned pass. A change with no such command is never reported as verified; it becomes a human item. This is the invariant that keeps the human report trustworthy.
- Human items are defined by the fixed table in `SKILL.md` section 5. Anything outside that table that passes verification is only counted, never listed.
- Baseline failures (failing before any change) are recorded, never fixed, so the diff stays attributable to the refactoring.
- The skill asks exactly two things: the report channel once at the start, and acceptance of the proposal before editing. All other ambiguity becomes an assumption recorded as a human item. Non-interactive runs default the channel to stdout and, with no acceptance, end by reporting the proposal only; nothing is edited without acceptance.
- Deletion is in scope and must be proposed boldly when something has no references, does not serve the contract, contradicts the code, or duplicates something else. Accepted deletions are still reported as human items.
- `SKILL.md` is kept under about 1000 Korean characters (whitespace excluded); the tables and per-step rules live in `references/procedure.md`, which `SKILL.md` marks as mandatory reading.
- Passing verification by editing tests, expectations, snapshots, lint rules, or the verification scope does not count as passing; it is reported as `검증 우회`.
- Delivery adapters are intentionally thin: stdout is the default and the fallback; GitHub PR body and issue are updated in place when a previous report exists; a file path is written as Markdown.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Ask the channel once → fix the scope, the contract, and the working-tree state → build the verification matrix from repository-defined checks first (catalog order) → run everything once for the baseline → propose modifications, deletions, and creations with evidence and wait for acceptance → for each accepted unit: change, verify, fix own cause, revert after three failures → classify each unit against the human-item table → write the report in the fixed template order (each human item starts with before/after) → deliver through the chosen channel, falling back to stdout with the reason on the first line.

## Terminology

- **change unit (변경 단위)**: one purpose per change; the granularity at which verification runs and classification happens.
- **verification (검증)**: a pass/fail command needing no human; anything else is not verification.
- **baseline (기준선)**: the verification result before the first change.
- **contract (계약)**: the behavior, invariants, and data read/write actors that must hold after the refactoring; the reference point for "does this serve the intent" and for deletion proposals.
- **proposal (제안)**: the pre-edit list of modify/delete/create actions with evidence; nothing is edited until accepted.
- **human item (사람 항목)**: a unit or fact matching the section-5 table.
- **channel (채널)**: `stdout`, `github-pr`, `github-issue`, `file:<path>`.

## Resources

- [`SKILL.md`](../SKILL.md): motivation, terminology, the six-step flow, and the do-not list; intentionally short.
- [`references/procedure.md`](../references/procedure.md): per-step rules and tables (channel table, contract, matrix, proposal template and deletion criteria, loop, human-item table); the runtime detail `SKILL.md` delegates to.
- [`references/verification-catalog.md`](../references/verification-catalog.md): where to look for repository-defined checks and the standard-tool fallbacks per artifact type; owns the baseline recording rule.
- [`references/report-template.md`](../references/report-template.md): the fixed report layout and the per-channel placement; change it together with `SKILL.md` section 6.
