# Diagram Inputs Are Normalized to Topology

## Decision

Normalize prose, images, YAML, and existing draw.io files into one topology instead of maintaining separate input modes. Continue with conservative assumptions when possible and record unresolved ambiguity as `확인 필요`.

## Reason

Topology is the stable model the diagram needs. Requiring a strict input format blocks useful work without improving the resulting network semantics.

