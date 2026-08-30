# Architecture

## Responsibility

Analyzes business flows and their supporting code with file-and-line evidence, then stores one reusable JSON source and renders HTML or draw.io views from it.

## Boundary

`analysis.json` is the only analysis source of truth; HTML and draw.io files are derived artifacts, and ordinary follow-up questions reuse or incrementally refresh the stored JSON.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Locate the project analysis and choose initial, reuse, incremental, or full mode; collect business-first evidence; validate and commit JSON; render requested views; answer impact questions from stored relationships.

## Stable language

- A business domain groups related work such as orders or payments; a flow is one entry-driven business scenario with ordered steps.
- A module is a meaningful step in a flow, not every class or function. Layers are limited to entrypoint, application, domain, infrastructure, and external.
- Origin distinguishes repository, database, and current-code ownership. Impact means graph reachability, not proven outage scope or risk.
- Capacity is a per-replica manifest observation when available. Fan-out is greater than one only when repetition is visible in code; propagated load remains an estimate, not measured sizing.
- A project ID combines the repository slug with the first eight characters of a SHA-256 over the Git remote, or absolute path when no remote exists.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`examples/`](../examples/): supporting resources retained outside the maintenance wiki.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
- [`schemas/`](../schemas/): supporting resources retained outside the maintenance wiki.
- [`scripts/`](../scripts/): supporting resources retained outside the maintenance wiki.
- [`tests/`](../tests/): supporting resources retained outside the maintenance wiki.
