# Architecture

## Responsibility

Creates a blog-figure image prompt that visually explains the important point in supplied code.

## Boundary

Explain the code's idea rather than reproduce a screenshot; keep labels and relationships readable as one focused figure.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Read the code and explanation goal, extract one mechanism or contrast, map it to a simple visual model, then write the image prompt.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
