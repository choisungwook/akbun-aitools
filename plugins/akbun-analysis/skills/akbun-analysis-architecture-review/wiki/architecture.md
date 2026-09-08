# Architecture

## Responsibility

Inventory the context the user provided, interview to fix the evaluation criteria, attack the current architecture lens by lens with cited evidence, propose the smallest effective alternative per finding with a quantified effect table, and draw current/after diagrams when they change structure or call order.

## Boundary

Document only: no code or infrastructure changes, no penetration or load tests. Findings without evidence (`file:line`, document location, or interview answer) are dropped. Numbers are counted, measured, or explicitly estimated with a formula; unsourced percentages are forbidden. The user decides which alternative to take.

Scalability is handed to `akbun-analysis-bottleneck`; this skill stays at the structural level.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Terminology

| Term | Meaning in this skill |
|---|---|
| Context | Anything the user handed over: code, architecture docs, infra code, ops material, scale numbers, constraints |
| Lens | One evaluation perspective; security and operational toil are mandatory, the rest conditional |
| Finding (F#) | A concrete "how to break this" scenario with evidence, impact, and likelihood |
| Toil | Repeated manual operational work: deploy steps, hand-managed config, human-handled alarms |
| Counted / measured / estimated | The three allowed sources of a number in the effect table |
| Migration order | Stepwise path from current to proposed with a rollback per step |

## Flow

Context inventory (reuse `akbun-analysiscode` stored analysis when present) → interview up to 3 rounds, confirm criteria table → adversarial findings per lens, 3-7 total, ordered by impact × likelihood → 1-2 alternatives per finding with effect table and one security line and one toil line each → diagrams only when structure or sequence changes → single Markdown document → user decides.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`references/review-lenses.md`](../references/review-lenses.md): lens table with breaking questions, STRIDE-style security branches, interview question bank, and the metric catalog the effect table draws from. Add a metric only with a counting method.
- Related: `plugins/akbun-analysis/skills/akbun-analysiscode/scripts/locate_analysis.py` is reused read-only for the current architecture.
- Related: `plugins/akbun-analysis/skills/akbun-analysis-bottleneck/` owns traffic-scaling analysis.
