# Architecture

## Responsibility

Creates an image prompt and editable SVG in the monogray book-illustration style using one of five fixed layouts.

## Boundary

Keep the shared ink, gray, orange, and off-white style while selecting only icon strip, zoom, dialog, flow, or poster-card layout with its defined spacing.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Interpret the subject, choose a fixed layout, compose concise text when needed, write the image prompt and editable-text SVG, then report the layout and orange accent.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`assets/`](../assets/): supporting resources retained outside the maintenance wiki.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
