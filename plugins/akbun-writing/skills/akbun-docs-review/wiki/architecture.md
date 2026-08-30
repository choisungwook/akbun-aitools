# Architecture

## Responsibility

Correct language and terminology, improve readability, and fix evidence-backed factual errors in existing Korean technical documents.

## Boundary

Preserve the document's intent, voice, layout, and code. Do not create or restructure sections, impose a writing style, or modify code, commands, settings, and paths. Report uncertain claims and errors that require code changes instead of guessing.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Read the source as a text document, preserve its structure and voice, apply language and terminology corrections, fix factual errors supported by sufficient evidence, then report unresolved uncertainty or code-related errors.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
