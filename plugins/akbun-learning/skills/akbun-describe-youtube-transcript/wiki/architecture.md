# Architecture

## Responsibility

Fetches YouTube captions and converts the spoken content into a cleaned Markdown transcript.

## Boundary

The deliverable is a chronological transcript, not a short summary; cleaned captions are primary and raw VTT is only fallback evidence.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Fetch captions, clean rolling and karaoke duplication, preserve speech order and meaning, then write the Markdown transcript.

## Stable language

- A cleaned transcript removes automatic-caption overlap and karaoke tags while preserving utterance content and order.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`scripts/`](../scripts/): supporting resources retained outside the maintenance wiki.
