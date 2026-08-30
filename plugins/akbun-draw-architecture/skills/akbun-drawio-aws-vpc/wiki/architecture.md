# Architecture

## Responsibility

Creates and exports a draw.io AWS VPC foundation diagram containing VPCs, Availability Zones, subnet tiers, CIDRs, and optional Internet or NAT Gateways.

## Boundary

Complete topology intake before XML work and keep workloads, load balancers, endpoints, hybrid links, managed services, and application traffic outside this skill.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Collect required topology, copy the reusable draw.io foundation, apply VPC and AZ layout rules, validate XML, export with draw.io Desktop, and visually inspect the PNG.

## Stable language

- Topology is the normalized network structure independent of whether the input arrived as prose, YAML, an image, or an existing diagram.
- A reference image is style and structure evidence, not a pixel-level completion target.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`agents/`](../agents/): supporting resources retained outside the maintenance wiki.
- [`assets/`](../assets/): supporting resources retained outside the maintenance wiki.
- [`example.yaml`](../example.yaml): supporting document retained outside the maintenance wiki.
- [`README.md`](../README.md): supporting document retained outside the maintenance wiki.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
- [`scripts/`](../scripts/): supporting resources retained outside the maintenance wiki.
