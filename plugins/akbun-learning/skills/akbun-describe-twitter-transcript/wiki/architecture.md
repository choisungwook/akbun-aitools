# Architecture

## Responsibility

Fetches or transcribes a video attached to an X post and converts the spoken content into a cleaned Markdown transcript.

## Boundary

The transcript is grounded in speech order; remove technical caption duplication but do not add a summary or unsupported explanation.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Fetch available media or captions, fall back to local transcription when required, clean rolling duplication, and write the ordered Markdown transcript.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`scripts/`](../scripts/): supporting resources retained outside the maintenance wiki.
