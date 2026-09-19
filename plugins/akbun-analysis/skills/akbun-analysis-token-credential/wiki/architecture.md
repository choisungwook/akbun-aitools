# Architecture

## Responsibility

Provide a single question that frames a credential from the security perspective: issuer, reader, and permitted scope.

## Boundary

The skill is intentionally one line. It does not scan code, list secrets, or produce a report; the other `akbun-analysis` skills own analysis output. Like the rest of this plugin it sets `disable-model-invocation: true`. The user invokes it to hand the model the intent of an authentication or authorization analysis; the model does not apply it on its own when a credential appears.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

The user starts an authentication or authorization analysis → the user invokes the skill → the question is applied to every credential in scope.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
