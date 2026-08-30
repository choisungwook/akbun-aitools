# Architecture

## Responsibility

Creates a vertical one-cut essay-toon page with top narration and one emotional whale-mascot scene.

## Boundary

Use warm off-white space, one bold handwritten narration block, and one scene; the standard whale appearance comes from `akbun-mascot-whale`.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Condense the input to one emotional sentence and scene, pose the mascot, balance narration and negative space, then produce the prompt and editable-text SVG.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
