# Architecture

## Responsibility

Converts Markdown to blog-ready HTML through the bundled Pandoc workflow.

## Boundary

Preserve document semantics and code blocks while applying only the publishing transformations defined by the conversion script.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Validate the input path, run the bundled conversion, inspect generated HTML for structural issues, and return the output path.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`scripts/`](../scripts/): supporting resources retained outside the maintenance wiki.
