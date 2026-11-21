# Update log

## 2026-11-21

* **Updated**: akbun-draw-diagram-haru adds `blocked` edge, `split` gap has no divider, group names get top padding and arrows avoid text; akbun-draw 1.1.7.

## 2026-11-18

* **Created**: akbun-session-meter mod concept (mods/ folder, Claude marketplace only, git diff pane, folder install guide).

## 2026-11-16

* **Updated**: akbun-draw-diagram-haru arrows straight by default, `split` layout gets per-half top-left `titles`; akbun-draw 1.1.6.

## 2026-11-15

* **Updated**: akbun-youtube gains akbun-youtube-storyboard-dami-detail (detail mode: per-cut beats, recording steps and AI video prompts on the summary spec, one slide per cut); summary skill now offers it after a run; manifest version 1.0.3.
* **Updated**: akbun-youtube gains akbun-youtube-storyboard-dami (idea → editable pptx storyboard with a Resolve-style timeline, plus script.md); design decisions recorded in the plugin concept; manifest version 1.0.2.
* **Updated**: akbun-youtube-storyboard-dami keeps its philosophy in `references/philosophy.md` (three owner-given drop-off principles first) and real outputs as PNGs in `examples/` for before/after; pptx is gitignored (`*.pptx`, `storyboard-output/`); timeline splits into 120-second slides.
* **Updated**: knowledges must be updated before push/PR. AGENTS.md reading-order item 5 rewritten and `.claude/hooks/check-knowledges-before-push.sh` added (PreToolUse on `git push` / `gh pr create` only); verification policy and AGENTS.md `last_modified` refreshed.

## 2026-11-14

* **Updated**: akbun-draw gains akbun-draw-gaon (fine-line street drawing prompts with a day/night inversion); manifest version 1.0.56.

## 2026-11-13

* **Updated**: tracking-Issue step removed; pull-request policy rewritten, AGENTS.md/template/check_pr_body.py `last_modified` refreshed.
* **Updated**: AGENTS.md line 38 rewritten for ADR 0008 (chalkboard skill); refreshed AGENTS.md `last_modified` in policies.
* **Created**: bundle with 11 plugins, 6 policies, 6 decisions (0007 deprecated), 3 checks, filled from the codebase.
