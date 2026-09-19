# Architecture

## Responsibility

Set an adversarial stance toward the user's implementation and claims: look for hidden assumptions and unhandled exceptions, and produce counterexamples backed by evidence (`file:line` or a reproducing input).

## Boundary

The skill is intentionally two sentences. It does not define a report format, a lens list, or a finding limit; `akbun-analysis-architecture-review` owns structured architecture evaluation, and this skill targets code and claims the user presents as done. It keeps `disable-model-invocation: true` so the model challenges the user only on request.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

The user presents code or a claim and invokes the skill → the model doubts it instead of agreeing → each doubt is turned into a counterexample with evidence.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
