# Architecture

## Responsibility

Locally corrects Korean spelling and mechanical AI-like prose while preserving the existing author's voice and document structure.

## Boundary

Do not change facts, argument, genre, voice, or Markdown; treat accumulated rules as conditional symptoms and human editing directions, not unconditional deletion patterns.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Read common and user rules, diagnose only matching prose problems, make local edits, preserve uncertainty, and update user rules only from explicit feedback.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
