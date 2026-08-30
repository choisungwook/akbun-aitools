# Reference Image Is Not a Pixel Target

## Decision

Use a reference image only for reusable style and structure. Completion depends on static XML validation, draw.io export, and visual PNG inspection rather than pixel similarity.

## Reason

The skill creates reusable VPC layouts, not replicas. Pixel matching would overfit one example and conflict with topology-driven output.

