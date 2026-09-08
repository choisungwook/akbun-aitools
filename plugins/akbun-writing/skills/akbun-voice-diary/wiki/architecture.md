# Architecture

## Responsibility

Listen with minimal interruption, write the diary in the fixed four-section format, always save a local Markdown file, optionally mirror to Apple Notes or Google Docs, and create one Apple Calendar event per detected study topic on the coming weekend.

## Boundary

The diary contains only what the user said. The skill never adds comfort, advice, or inferred facts to the diary body. Study-topic detection is the one place the skill interprets rather than transcribes, and each topic must cite the diary situation that produced it.

Voice context drives reply length: one sentence while listening, three lines at the end. The skill never asks where to save.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Terminology

| Term | Meaning in this skill |
|---|---|
| Listening | The phase before the user's end signal; replies are one sentence or less, at most one follow-up question |
| End signal | "끝", "저장해", "오늘은 여기까지", "일기 써 줘", or an equivalent wrap-up phrase |
| Fixed format | H1 date, then `한 줄`, `오늘 있었던 일`, `힘들었던 것`, `나중에 공부하면 좋은 것`, optional `내일` |
| Study topic | Something to learn later, from a direct cue or an indirect one (long struggle, solved by someone else, unknown term); max 3 scheduled per week, the rest marked `보류` |
| Coming weekend | Mon-Fri → this Saturday; Sat → this Sunday; Sun → next Saturday |

## Flow

Listen until the end signal → write the diary → naturalize in place → write `~/Downloads/YYYY-MM-DD.md` (or the user's path; append a `## 추가 (HH:MM)` section if the file exists) → mirror to Apple Notes / Google Docs only when requested → one calendar event per study topic via `create_calendar_event.py` → three-line spoken-style reply.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- Related: `plugins/akbun-writing/skills/akbun-writing-naturalize/references/*.jsonl` are read during the naturalize pass; this skill does not modify them.
- [`scripts/create_apple_note.py`](../scripts/create_apple_note.py): Markdown to Apple Notes HTML subset; macOS only. Copied from `plugins/akbun-pulse/skills/github-daily-pulse/scripts/` because plugins install independently; keep the two in sync when fixing bugs.
- [`scripts/create_calendar_event.py`](../scripts/create_calendar_event.py): creates one Apple Calendar event with title, date, start, duration, calendar name, and notes; creates the calendar if missing; returns `exists` instead of duplicating a same-title event on the same day. macOS only.

## Caveat

The naturalize pass runs between writing and saving, reusing `akbun-writing-naturalize` rules and procedure but overriding its output rule: one diary file, no `-v1` copy. It strips the assistant's own phrasing only; the user's spoken wording and endings are protected. Keep this override in `SKILL.md` if the naturalize skill's output rule changes.

Both scripts exit 2 off macOS. The skill must degrade to the local Markdown file and report the failure in one line, never fail the whole run.
