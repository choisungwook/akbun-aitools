# Architecture

## Responsibility

Produces an install manual document in a fixed 7-chapter order: product intro, structure (Mermaid), prerequisites, cautions, install steps, verification, cleanup. The document is meant to be followed top to bottom by someone who has never used the product.

## Boundary

The skill writes documents only. It does not run the installation, provision infrastructure, or generate IaC. Commands and paths come from official docs, user-provided material, or observed execution; unverified values are marked `확인 필요`, never invented.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Terminology

| Term | Meaning in this skill |
|---|---|
| Step | One numbered unit: 1-2 lines of explanation + exactly one code block (+ optional "expected output" line) |
| Prerequisite | Anything the reader must have before step 1 (spec, tools, firewall ports, IP/domain, accounts, keys); everything step 5 demands must appear here |
| Caution | A check item the reader must confirm before installing (hard-to-change values, destructive commands, version compatibility, unsafe defaults) |
| Masking | Secrets inside code blocks are written as `XXX`; user-specific non-secret values use `<자기-값>` |
| Cleanup | Reverse-order removal of everything the manual created, including prerequisites the reader set up |

## Design intent

Explanation is minimized on purpose; the reader is expected to learn by executing. Length limits apply to prose, not to install steps. Steps must be complete because a skipped step breaks the walkthrough.

## Flow

Confirm product, version, environment, and install method with the user; gather official docs and user material; write chapters 1-4 (intro, diagrams, prerequisites, cautions); write install steps; write verification with expected output and a short failure table; write cleanup in reverse order with a final "everything gone" check; run the completion checklist.

## Caveat

Step prose (chapters 5-7) uses `-음`/`-함` clause endings on purpose, to read as a checklist rather than an instruction from above; only chapter 1 uses `합니다`.

The final naturalize pass reuses `akbun-writing-naturalize` rules and procedure but overrides its output rule: the manual file is overwritten in place, no `-v1` copy is created, and the `-음` endings are preserved. Keep this override in `SKILL.md` if the naturalize skill's output rule changes.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
- Related: `plugins/akbun-writing/skills/akbun-writing-naturalize/references/*.jsonl` are read during the final naturalize pass; this skill does not modify them.
- Related: `plugins/akbun-writing/skills/akbun-it-onboarding/` covers understanding an existing system; this skill covers installing a product. They do not share resources.
