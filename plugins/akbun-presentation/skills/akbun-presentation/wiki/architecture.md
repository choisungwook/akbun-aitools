# Architecture

## Responsibility

Creates an akbun-style PowerPoint deck and a detailed per-slide Markdown speaker script from a topic or source material.

## Boundary

Fit slide count and script length to talk duration and audience, preserve the selected light-sandwich or dark-step design system, and keep slides and script synchronized.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Analyze source and settings, build a question-led story, design each slide with the shared visual language, generate the PPTX, write the speaker script, and verify both outputs.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`design.md`](../design.md): supporting document retained outside the maintenance wiki.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
