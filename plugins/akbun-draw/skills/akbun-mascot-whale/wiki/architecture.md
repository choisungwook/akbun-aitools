# Architecture

## Responsibility

Defines the canonical appearance of the akbun whale mascot for other drawing skills.

## Boundary

This is a shared character specification, not a free-standing scene layout; dependent skills may change pose and context but not identifying anatomy.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Provide the standard body, face, fins, proportions, and allowed expression guidance for another drawing prompt.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
