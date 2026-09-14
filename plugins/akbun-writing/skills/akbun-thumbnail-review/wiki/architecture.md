# Architecture

## Responsibility

Diagnoses a YouTube thumbnail with six fixed checks (TV-friendly 50% test, question/emotion, references and mechanism, clutter, problem prominence, text variants) and produces improvement proposals, each paired with the reason it affects clicks.

## Boundary

Every recommendation must carry a reason grounded in viewer behavior or interface layout; a bare "do this" is out of spec. Relevance alone never passes check 2. The thumbnail's protagonist is the problem the video addresses, never a person; a face or logo that reads before the problem fails check 5. References are transferred by mechanism, never by copying composition or wording. Channel metrics come only from user input. The skill does not generate final thumbnail images; it stops at directions, element lists, and text candidates.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Parse the video topic and thumbnail elements, run the six checks with verdict/evidence/proposal/reason, branch into question-and-emotion brainstorming when no thumbnail exists or check 2 fails, branch into the reference worksheet when requested or check 3 fails, then emit text variants and next actions.

## Terminology

- **50% test**: cover the bottom half; the top half alone must convey the topic and invite a scroll.
- **Mechanism**: the concrete device by which a reference creates a question or emotion; the transferable unit.
- **Outlier**: a video that over-performs its own channel's average (internal = user's channel, external = other channels).
- **Model channel**: same video format, different subject matter.
- **Problem prominence**: check 5; the single problem phrase must be the first element a viewer perceives.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
