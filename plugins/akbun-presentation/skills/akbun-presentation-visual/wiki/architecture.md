# Architecture

## Responsibility

Creates akbun-style 16:9 raster visuals for presentation slides from a visual brief or a source figure.

## Boundary

Owns raster visual abstraction, generation, and visual QA. It does not own deck structure, editable PowerPoint shapes, speaker scripts, or slide assembly; those remain with `akbun-presentation`.

The skill remains eligible for implicit invocation because `akbun-presentation` uses it as a runtime dependency.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Normalize the visual brief, preserve source facts and provenance, choose the light-sandwich or dark-step variant, compose or regenerate the image, visually inspect it, and return the image with any source or assumption label.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`references/visual-style.md`](../references/visual-style.md): canonical raster composition, palette, and prompt contract.
- [`akbun-presentation`](../../akbun-presentation/SKILL.md): upstream deck workflow that may request and place the generated visual.
