---
okf_version: "0.3"
title: akbun-aitools knowledge bundle
description: "Agent-facing map of this repo's plugins, rules, decisions and checks; read before changing plugins or repo rules"
---

# akbun-aitools knowledge bundle

Agent-facing summary of this repo's plugins, rules, decisions and checks as an [OKF v0.3](https://github.com/open-knowledge-format/open-knowledge-format/blob/main/SPEC.md) bundle. Source of truth stays in each `SKILL.md` and `AGENTS.md`; concepts here summarize and link.

## How to read

* `generated` = who wrote it and when. `verified` = who confirmed it. Only `verified` events at or after `generated.at` count: none → unverified; only non-`human:` actors → machine-confirmed; a `human:` actor → human-reviewed.
* Past `stale_after` → re-check against the source before relying on it.
* Paths without a leading `/` resolve from the file's own directory. `../../` paths point into this repo outside the bundle, so OKF treats them as external; open them from the repo checkout.
* `status: deprecated` → history only; `superseded_by` points to the replacement.

## Bundle

* [Plugins](plugins/) - role, location and related docs per plugin
* [Policies](policies/) - versioning, README, image, verification, risk and PR rules from AGENTS.md
* [Decisions](decisions/) - docs/adr summaries and supersession
* [Checks](checks/) - check scripts run locally and in CI
