# Architecture

## Responsibility

Explains technical concepts by judging the learner's current hypothesis and using follow-up questions to refine their model.

## Boundary

State whether the hypothesis is correct, partly correct, or incorrect before expanding the explanation; keep later answers chained to the learner's reconstructed model.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Restate and judge the hypothesis, visualize the relevant structure, explain the mismatch or missing mechanism, then invite and answer the next linked question.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
