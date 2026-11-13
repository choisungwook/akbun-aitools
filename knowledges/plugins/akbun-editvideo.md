---
type: Claude Code Plugin
title: akbun-editvideo
description: "Video editing skills — plan and run DaVinci Resolve vlog edits: speech-free travel vlogs (cut/stabilize, chronological timeline, color-grading workflow (Log LUT, exposure, white balance, contrast, saturation on labeled nodes), four separate creative looks on new LOOK nodes, and a city montage cut style, face mosaic, Gmarket Sans subtitles, vertical YouTube Shorts) and faceless talking developer vlogs (dialogue/keyword subtitles, project style guide, plus shot sketches)"
resource: ../../plugins/akbun-editvideo/
tags: [plugin]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
stale_after: 2027-02-13T00:00:00Z
sources:
  - id: manifest
    resource: ../../plugins/akbun-editvideo/.claude-plugin/plugin.json
    title: akbun-editvideo Claude manifest
    last_modified: 2026-11-13T14:10:15Z
  - id: readme
    resource: ../../README.md
    title: README plugin list
    last_modified: 2026-11-13T14:10:15Z
---

Video editing skills — plan and run DaVinci Resolve vlog edits: speech-free travel vlogs (cut/stabilize, chronological timeline, color-grading workflow (Log LUT, exposure, white balance, contrast, saturation on labeled nodes), four separate creative looks on new LOOK nodes, and a city montage cut style, face mosaic, Gmarket Sans subtitles, vertical YouTube Shorts) and faceless talking developer vlogs (dialogue/keyword subtitles, project style guide, plus shot sketches)[^manifest]

## Where

- Skills: [plugins/akbun-editvideo/skills/](../../plugins/akbun-editvideo/skills/)
- Three manifests (`.claude-plugin`, `.codex-plugin`, `.antigravity-plugin`), same `version`. Rules: [plugin-versioning](../policies/plugin-versioning.md)
- Skill list and when to use each: README `## plugin 목록` → `### akbun-editvideo` table (source of truth)[^readme]
- Manual and glossary: [docs/manual_editvideo.md](../../docs/manual_editvideo.md), [docs/terms_editvideo.md](../../docs/terms_editvideo.md)
- Extra check: [validate-editvideo](../checks/validate-editvideo.md)
- Decisions: [0006](../decisions/0006-travel-vlog-orchestrator-is-color-workflow.md)

[^manifest]: akbun-editvideo Claude manifest
[^readme]: README plugin list
