# Architecture

## Responsibility

Provide a single question that frames a credential from the security perspective: issuer, reader, and permitted scope.

## Boundary

The skill is intentionally one line. It does not scan code, list secrets, or produce a report; the other `akbun-analysis` skills own analysis output. Unlike the rest of this plugin it omits `disable-model-invocation` on purpose so the model can apply it automatically when a credential appears.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

A credential appears in the context → the model or user invokes the skill → the question is applied to that credential.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
