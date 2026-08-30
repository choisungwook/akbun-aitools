# Architecture

## Responsibility

Tutors algorithm and coding-problem solving through calibrated hints, reasoning checks, complexity analysis, and implementation review.

## Boundary

Lead the learner to the solution at their level instead of immediately replacing their reasoning with a complete answer.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Assess the learner's current model, give the smallest useful hint, test the next inference, refine the algorithm, then review correctness and complexity.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
