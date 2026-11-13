---
type: Policy
title: Plugin versioning
description: "Changing a skill or agent under plugins/ bumps that plugin's version once, from origin/main"
tags: [policy]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-05-13T00:00:00Z
sources:
  - id: agents
    resource: ../../AGENTS.md
    title: AGENTS.md
    last_modified: 2026-11-13T15:30:00Z
  - id: deploy
    resource: ../../docs/guide_deploy_plugins.md
    title: Plugin deploy guide
    last_modified: 2026-11-08T01:23:16Z
---

Changing a skill or agent under plugins/ bumps that plugin's version once, from origin/main.

## Rules

- The three manifest `version` values are always equal.[^agents]
- Patch +1 by default; minor +1 when behavior changes a lot or breaks compatibility.
- Bump once per PR from the origin/main value, no matter how many edits.
- A new skill adds one example line to the manifest's `interface.defaultPrompt`.
- Deploy steps: the deploy guide.[^deploy]
- Checked by [validate-plugins](../checks/validate-plugins.md).

[^agents]: AGENTS.md
[^deploy]: Plugin deploy guide
