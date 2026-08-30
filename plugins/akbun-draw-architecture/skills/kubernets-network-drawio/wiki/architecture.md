# Architecture

## Responsibility

Creates a draw.io and PNG view of a Kubernetes service network from prose, images, YAML, an existing diagram, or a combination of inputs.

## Boundary

Normalize every input into one topology, continue with conservative assumptions when meaning is stable, and mark unresolved ambiguity as `확인 필요` instead of forcing an input mode.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Read the drawing rules, merge inputs into topology, edit the template, validate XML, export PNG, visually inspect network semantics and alignment, then report artifacts and assumptions.

## Stable language

- Topology is the normalized network structure independent of input format.
- `확인 필요` marks uncertainty that could not be safely resolved without blocking all otherwise meaningful work.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`agents/`](../agents/): supporting resources retained outside the maintenance wiki.
- [`assets/`](../assets/): supporting resources retained outside the maintenance wiki.
- [`example.yaml`](../example.yaml): supporting document retained outside the maintenance wiki.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
- [`scripts/`](../scripts/): supporting resources retained outside the maintenance wiki.
