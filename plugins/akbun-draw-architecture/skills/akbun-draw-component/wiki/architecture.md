# Architecture

## Responsibility

Turns code or component descriptions into a single English prompt for a high-level architecture relationship image.

## Boundary

Preserve only the big picture: three to eight independently meaningful components, labeled relationships, and dashed logical boundaries; do not draw file, class, or function detail.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Identify the system message, collapse implementation detail into meaningful components, select essential relationships and boundaries, then return one image-generation prompt plus a short Korean explanation.

## Stable language

- A reference image supplies reusable layout and style cues; it is never a pixel target or a source of subjects to copy.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
