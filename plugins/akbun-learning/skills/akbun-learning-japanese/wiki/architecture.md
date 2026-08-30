# Architecture

## Responsibility

Guides Japanese reading and pronunciation for Korean learners.

## Boundary

Pair Japanese text with the reading and Korean meaning needed by a beginner while preserving distinctions that Korean approximation can hide.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Segment the expression, provide reading and meaning, explain pronunciation or grammar traps, then give a practice sequence.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
