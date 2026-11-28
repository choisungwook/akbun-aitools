# Update log

## 2026-11-26

* **Created**: akbun-thinking plugin 1.0.0 collects short thinking principles as `akbun-thinking-<proper noun>` skills: akbun-thinking-holmes (evidence leads the conclusion, not the other way) and akbun-thinking-dennett (principle of charity before judging). 결정 없음: 새 plugin 추가뿐이고 삭제로 되돌릴 수 있음.

## 2026-11-25

* **Updated**: bundle upgraded from OKF v0.2 to v0.3 (`okf_version: "0.3"`, root `title`/`description`, spec link moved to open-knowledge-format; How to read notes file-relative paths, current-only `verified` and `superseded_by`); existing paths were already file-relative; `../../` repo paths stay external under OKF and are opened from the checkout; akbun-draw actor and 0009 index entry fixed. 결정 없음: 스펙 버전 추종이고 index.md 한 줄로 되돌릴 수 있음.

## 2026-11-24

* **Updated**: akbun-draw gains shared composition rules (`akbun-draw-template-cartoon/references/composition.jsonl`: focal, depth, lines, room, bubble, camera) assembled into the cartoon, maru, comedy, dotori and wash prompts; new reference skill `akbun-draw-camera` is the single source of camera values; cartoon panels require `camera` and the other four accept it, placed right after FORMAT as FRAMING (inside each PANEL on multi-panel sheets); maru, cartoon and dotori no longer draw short straight lines around faces; new agent `akbun-draw-review-loupe` judges composition from result images; akbun-draw 1.1.15. 결정 없음: 프롬프트 문장과 검사 추가뿐이고 되돌리기 쉬움.

## 2026-11-23

* **Created**: akbun-draw-folk builds naive folk-art painting prompts (thick impasto relief, even near-black outline around every shape and every repeated dab, flat frontal shapes without perspective, one local color per shape, no people) from a spec via `folk_prompt.py`; palettes `cobalt`/`terracotta`/`dusk`, canvas `16:9`/`3:4`; akbun-draw 1.1.14. 결정 없음: 새 skill 추가뿐이고 삭제로 되돌릴 수 있음.

## 2026-11-22

* **Updated**: akbun-reflect rewritten as one short list-based pass usable in any project (three reviewers, synthesizer and `references/` removed); approval table `번호 | local repo | remote repo | 수정 내용`, installed plugin caches edited only as copies, no PR or push, Backlog stays in the report and asks where to record it; akbun-agent-ops 1.1.0. 결정 없음: skill 문구 재작성이고 되돌리기 쉬움.
* **Updated**: akbun-agentops-cleancomment renamed to akbun-agentops-prune-comments (verb-first, natural English); akbun-agent-ops 1.0.5. 결정 없음: 이름 변경뿐이고 되돌리기 쉬움.
* **Updated**: akbun-agentops-cleancomment no longer names this repo's doc paths; it finds design docs and decision records through the target project's AGENTS.md or README; akbun-agent-ops 1.0.4. 결정 없음: 문구 일반화뿐이고 되돌리기 쉬움.
* **Updated**: akbun-agent-ops gains akbun-agentops-cleancomment (fresh-context subagent finds comments that conflict with design docs, decision records or the code; parent verifies and deletes, offers encodings for constraint comments); akbun-agent-ops 1.0.3. 결정 없음: 새 skill 추가뿐이고 삭제로 되돌릴 수 있음.
* **Updated**: akbun-draw-mermaid-database-garam wraps GRANT SQL labels in `<code>` so the theme draws them as plain text above the arrow (Mermaid leaves no edge id on labels); akbun-draw 1.1.13. 결정 없음: 테마 CSS 조정이고 되돌리기 쉬움.
* **Created**: akbun-draw-mermaid-database-garam draws DB permission labs as Mermaid `flowchart LR` (DB subgraph, schema.table + owner nodes, real GRANT SQL on solid arrows, SQL to verify on dotted arrows, results left blank, fixed frontmatter theme); akbun-draw 1.1.12. 결정 없음: 새 skill 추가뿐이고 삭제로 되돌릴 수 있음.
* **Updated**: akbun-draw-diagram-haru uses no shade color by default; label chips only when the figure compares roles or cases, and a single chip color fails the check; ADR 0009 updated; akbun-draw 1.1.11.
* **Updated**: akbun-draw-diagram-haru starts from the relation to show and maps it to a layout, adds `sequence` (lifelines, `wait`, `spans`, edge notes), lets the work folder define shapes/palettes, and replaces accent/focus colors with ink lines plus role label chips (`pastel`); ADR 0009 rewritten; akbun-draw 1.1.10.
* **Updated**: push/PR hook now also requires a decision in `knowledges/decisions/` (or `결정 없음: <reason>` in the log) and runs from Claude Code, Codex (`.codex/hooks.json`) and Antigravity (`.agents/hooks.json`); decision 0009 records diagram-haru's spec-assembled prompt and color roles.
* **Updated**: akbun-draw-diagram-haru writes all text in ink (accent only on arrow lines, heads, step circles) and `mono-yellow` uses one yellow for every focus shape; superseded ADR 0007 deleted and 0008 stands alone; akbun-draw 1.1.9.

## 2026-11-21

* **Updated**: AGENTS.md requires running triggered workflow commands locally before a PR and all `gh pr checks` green before merge, including pre-existing main failures; editvideo test fixture now copies `mods/`.
* **Updated**: akbun-draw-diagram-haru moves layout routing into `layouts.jsonl` fields, adds `stack` layout and `mono-yellow` palette (`focus`, `same`, per-panel steps); README gets a haru layout section; akbun-draw 1.1.8.
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
