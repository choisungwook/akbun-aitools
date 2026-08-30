# Architecture

## Responsibility

Turns learning material into minimal black-and-white 16:9 explainer images with a Korean talk track.

## Boundary

One visual explains one concept on white with black and dark-gray hierarchy; split complex material instead of crowding a slide.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Segment the source by concept, choose a minimal explanatory composition for each segment, generate prompts or images, and pair each with a Korean explanation.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
