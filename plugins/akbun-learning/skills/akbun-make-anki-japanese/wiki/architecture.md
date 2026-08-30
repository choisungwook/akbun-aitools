# Architecture

## Responsibility

Converts Japanese textbook images or PDFs into an Anki deck for Korean beginner learners.

## Boundary

Cards retain Japanese source text, reading, Korean meaning, and a usable audio experience; do not silently invent unreadable source content.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Extract and verify source items, normalize fields, build cards and media, package the deck, then check representative cards.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`scripts/`](../scripts/): supporting resources retained outside the maintenance wiki.
