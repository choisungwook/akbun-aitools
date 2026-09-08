# Architecture

## Responsibility

Produces a DR plan document: BIA, a recommended DR strategy and verification method that the user confirms, per-scenario analysis sheets, an exercise plan (with a facilitator script for tabletop), and a gap list.

## Boundary

The skill writes documents only. It does not build DR infrastructure, generate IaC, or run failover. It recommends one strategy and one verification method but never finalizes them without user confirmation; the user's choice wins even when it differs from the recommendation.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Terminology

| Term | Meaning in this skill |
|---|---|
| DR strategy | Recovery architecture: Backup & Restore, Pilot Light, Warm Standby, Multi-site Active-Active |
| Verification method | How the strategy is exercised: tabletop, simulation (isolated failover), live failover |
| Tabletop | Discussion-based exercise driven by injects; the user's "말로만" |
| Scenario | A concrete failure situation for this system, not a generic disaster category |
| Failback | Returning to the primary environment after recovery, including reverse data sync |

DR strategy and verification method are two independent axes. A request that mixes them ("build or just talk") is split before any recommendation.

## Flow

Fill target scope and BIA from sources (an `akbun-it-onboarding` document is accepted as input), recommend strategy and verification method from RTO/RPO, stop for user confirmation, then list and prioritize scenarios, write one analysis sheet per scenario, and finish with the exercise plan and gaps.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
- Related: `plugins/akbun-writing/skills/akbun-it-onboarding/` supplies optional input; this skill does not depend on it at runtime.
