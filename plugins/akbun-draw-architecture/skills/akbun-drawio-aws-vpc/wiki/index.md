# akbun-drawio-aws-vpc Wiki

This is the maintenance context the next agent reads before changing this skill. Runtime behavior remains in [SKILL.md](../SKILL.md).

## Purpose

Creates and exports a draw.io AWS VPC foundation diagram containing VPCs, Availability Zones, subnet tiers, CIDRs, and optional Internet or NAT Gateways.

## Read order

1. Read [architecture.md](architecture.md) for boundaries, flow, and resource ownership.
2. Read [development.md](development.md) before editing or validating the skill.
3. Read [SKILL.md](../SKILL.md) and only the supporting resources needed for the requested change.
4. Read the domain or decision documents below only when the change touches them.

## Documents

| Document | Purpose |
|---|---|
| [architecture.md](architecture.md) | Stable behavior, boundaries, flow, and resource ownership |
| [development.md](development.md) | Maintenance sequence, validation, and wiki upkeep |
| [domain-language.md](domain-language.md) | Migrated domain language and boundaries |
| [adr/0001-reference-image-is-not-pixel-target.md](adr/0001-reference-image-is-not-pixel-target.md) | Decision and reasoning that remain relevant to this skill |
