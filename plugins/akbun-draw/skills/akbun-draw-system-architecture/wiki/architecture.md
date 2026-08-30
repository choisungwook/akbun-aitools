# Architecture

## Responsibility

Creates a dark presentation-style system architecture image, prompt, or editable PowerPoint slide from code or a system description.

## Boundary

Use a 16:9 charcoal canvas, white structural lines, limited yellow and red emphasis, and only system relationships needed for the message.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Extract system boundaries and key flows, select the necessary components, compose the presentation diagram, and render the requested image or editable slide output.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
