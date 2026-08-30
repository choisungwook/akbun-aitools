# Architecture

## Responsibility

Creates an akbun-style PowerPoint deck and a detailed per-slide Markdown speaker script from a topic or source material.

## Boundary

Fit slide count and script length to talk duration and audience, preserve the selected light-sandwich or dark-step design system, and keep slides and script synchronized. Raster visual generation is delegated to `akbun-presentation-visual`; editable slide composition remains here.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Analyze source and settings, build a question-led story, write the speaker script, request raster visuals where they improve explanation, assemble the editable PPTX, and verify both outputs.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`design.md`](../design.md): supporting document retained outside the maintenance wiki.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
- [`akbun-presentation-visual`](../../akbun-presentation-visual/SKILL.md): raster visual generation contract used by this deck workflow.
