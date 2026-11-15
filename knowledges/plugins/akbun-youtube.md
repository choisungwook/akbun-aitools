---
type: Claude Code Plugin
title: akbun-youtube
description: "YouTube skills written as YAML for people and AI — a channel settings sheet that follows official YouTube documentation, Codex computer-use skills that set an uploaded video's metadata and register AI-translated titles and descriptions (English, Japanese, French, Simplified Chinese), analysis of your own videos' metrics and style, and a storyboard (editable pptx) and script from an idea or quote"
resource: ../../plugins/akbun-youtube/
tags: [plugin]
generated: { by: claude-code/claude-fable-5-2, at: 2026-11-15T03:25:00Z }
stale_after: 2027-02-13T00:00:00Z
sources:
  - id: manifest
    resource: ../../plugins/akbun-youtube/.claude-plugin/plugin.json
    title: akbun-youtube Claude manifest
    last_modified: 2026-11-15T03:25:00Z
  - id: readme
    resource: ../../README.md
    title: README plugin list
    last_modified: 2026-11-15T03:25:00Z
  - id: dami-decisions
    resource: ../../plugins/akbun-youtube/skills/akbun-youtube-storyboard-dami/references/decisions.md
    title: akbun-youtube-storyboard-dami design decisions
    last_modified: 2026-11-15T03:25:00Z
---

YouTube skills written as YAML for people and AI — a channel settings sheet that follows official YouTube documentation, Codex computer-use skills that set an uploaded video's metadata and register AI-translated titles and descriptions (English, Japanese, French, Simplified Chinese), analysis of your own videos' metrics and style, and a storyboard (editable pptx) and script from an idea or quote[^manifest]

## Where

- Skills: [plugins/akbun-youtube/skills/](../../plugins/akbun-youtube/skills/)
- Three manifests (`.claude-plugin`, `.codex-plugin`, `.antigravity-plugin`), same `version`. Rules: [plugin-versioning](../policies/plugin-versioning.md)
- Skill list and when to use each: README `## plugin 목록` → `### akbun-youtube` table (source of truth)[^readme]
## akbun-youtube-storyboard-dami design (2026-11-15)

Turns an idea or a quote into a storyboard and a script for a faceless channel (IT hands-on, IT concept explainers, talking vlog, daily log, travel vlog), edited in DaVinci Resolve.[^dami-decisions]

- The skill's philosophy lives in its own file, `references/philosophy.md`, read first and edited before any rule changes. Principles 1–3 come from the owner and answer three drop-off points: (1) opening — a curiosity-raising scene before any background explanation; (2) mid-video — nothing unrelated to the awaited answer, and a short close once the answer lands; (3) weak reactions — one empathy element or question that makes viewers tell their own experience or share. `check` enforces proxies: hook length ≤ genre `hook_max`, cut 1 is not a `title-card`, time after `answer_cut` ≤ 20% of the total, and a required `reaction` {cut, text}. The 20% is a starting value, not measured. `answer_cut` means the cut where the hook's promise is actually seen on screen, not where the idea is first explained; a fresh-context review flagged this as a judgment call.
- Single source is `storyboard.json`. The model writes only the spec; `scripts/dami_storyboard.py` checks it, assembles sketch prompts, and builds `storyboard.pptx` and `script.md`. Timecodes are never written in the spec, only per-cut `dur`.
- The script draws the frame; the image model draws only a text-free 16:9 pencil sketch per cut. Rejected: generating whole storyboard pages as images (text and frames cannot be edited, Korean lettering breaks, one cut cannot be redrawn alone).
- Output is pptx because the creator edits it by hand: overview → timeline read like a Resolve timeline (part markers, V2 overlay, V1 cuts, A1 live, A2 ADR, A3 BGM, A4 SFX, each block a separate shape) → sound and ADR tables → three cuts per slide with sketch, description, intent and narration.
- `SKILL.md` only routes. Detailed rules live in `references/` (`story.md`, `sound.md`, `sketch.md`, `spec.md`, `deck.md`, `genres.jsonl`, `shots.jsonl`, `moves.jsonl`). This was an explicit request from the repo owner.
- No image tool, model name, CLI command or music service appears in the skill, and no font name goes into prompts or the spec. The pptx itself uses one commercially usable open-license font (Pretendard, SIL OFL 1.1). BGM and SFX are described by mood, genre, BPM, instruments and energy, with both library search keywords and a generation prompt, so the spec is not tied to one service.
- ADR (post-recorded voice) is a per-cut `voice` value with a required reason, and shows as its own timeline track.
- Real outputs are kept as PNGs in the skill's `examples/<topic>/` (spec, script.md, one PNG per slide). They are overwritten in the same change whenever the skill changes, so git shows before/after; no separate `before/` folders (owner's request).
- First trial finding: with the first cut attached as a style reference, hands from that cut leaked into most other sketches. The prompt now says to copy only line weight and shading, and people/hands are drawn only when the scene asks.
- Only the overview is length-limited (one slide). The timeline continues on further slides every 120 seconds, and sound tables and storyboard slides grow freely (owner's request). pptx files are gitignored; `scripts/slides_to_png.py` (macOS Quick Look, notes stripped because they hang it) exports the example PNGs.
- Not recorded as a `docs/adr` entry: the choices are reversible, so they stay in the skill's `references/decisions.md`.
- Open at creation time: sketch style was tested with one image model only, and `hook_max`/`cut_dur` per genre are starting values chosen without measurement.

[^manifest]: akbun-youtube Claude manifest
[^dami-decisions]: akbun-youtube-storyboard-dami design decisions
[^readme]: README plugin list
