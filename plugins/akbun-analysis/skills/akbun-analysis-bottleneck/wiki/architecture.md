# Architecture

## Responsibility

Turns code evidence into an ordered list of traffic bottleneck candidates and, for each, the sequence a developer experiences: measure, choose among fixes, apply, then face the new problem the fix creates.

## Boundary

The skill predicts and documents; it never modifies code, runs load tests, or judges code quality. Every candidate needs a `file:line` or config location or it is dropped. The final choice, the incident-time change scope, and acceptance of new risks are explicitly handed to the developer rather than decided by the skill. Adding infrastructure is always the last option in a solution table.

Terminology: a **bottleneck** is a cost that grows with traffic or touches a capped shared resource; a **secondary problem** is what the recommended fix creates; the **next bottleneck** is where load moves after the fix.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Reuse `akbun-analysiscode`'s stored `analysis.json` when `locate_analysis.py` reports it (flows are request paths, `origin.type == database` components are shared resources); otherwise trace entry points minimally. Match observations against the pattern catalog, rank candidates by traffic-proportional cost and shared-resource caps, fill the five fixed sections per candidate, draw current and post-fix mermaid diagrams, and emit one Markdown document.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`references/bottleneck-catalog.md`](../references/bottleneck-catalog.md): pattern table (code signal, mechanism, metrics, fixes, secondary problems) and where bottlenecks move after each fix type. Add a row only when the code signal is observable in source or config.
- `plugins/akbun-analysis/skills/akbun-analysiscode/scripts/locate_analysis.py`: read-only dependency for reusing stored analysis; this skill does not own or write that store.
