---
okf_version: "0.2"
---

# akbun-aitools knowledge bundle

Agent-facing summary of this repo's plugins, rules, decisions and checks as an [OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) bundle. Source of truth stays in each `SKILL.md` and `AGENTS.md`; concepts here summarize and link.

## How to read

* `generated` = who wrote it and when. `verified` = who confirmed it. No `verified` → unverified; a `human:` actor → human-reviewed.
* Past `stale_after` → re-check against the source before relying on it.
* `status: deprecated` → history only.

## Bundle

* [Plugins](plugins/) - role, location and related docs per plugin
* [Policies](policies/) - versioning, README, image, verification, risk and PR rules from AGENTS.md
* [Decisions](decisions/) - docs/adr summaries and supersession
* [Checks](checks/) - check scripts run locally and in CI
