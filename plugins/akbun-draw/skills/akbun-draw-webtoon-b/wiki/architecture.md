# Architecture

## Responsibility

Turns images and text into pastel watercolor chibi-animal webtoon prompts plus editable-text SVG page layouts.

## Boundary

Preserve character continuity and soft watercolor styling while keeping all user-editable wording as SVG text rather than raster lettering.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Extract story beats and character traits, plan pages and panels, write per-page prompts, then create matching editable SVG layouts.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
