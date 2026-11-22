# Decisions

* [0002 Reference image is not a pixel target](0002-reference-image-is-not-pixel-target.md) - Reference images/videos are only a style source; done is judged by rule checks, not pixel similarity
* [0004 Notion sync prefers CLI, MCP as fallback](0004-md-to-notion-cli-first.md) - Use the Notion CLI first; MCP only for what the CLI cannot do
* [0005 YouTube output is a transcript-grounded script](0005-youtube-transcript-is-grounded.md) - Produce a chronological Markdown transcript, not a summary
* [0006 Travel vlog orchestrator is the color workflow skill](0006-travel-vlog-orchestrator-is-color-workflow.md) - akbun-davinciresolve-workflow owns the full order from cut to render
* [0008 Explainer SVG reduced to the chalkboard skill](0008-explainer-svg-reduced-to-chalkboard.md) - Replace the akbun-draw-explainer-svg router with the akbun-draw-chalkboard skill and delete the other tokens
* [0009 diagram-haru picks a layout from the relation; color only on role label chips](0009-diagram-haru-spec-assembled-prompt-and-color-roles.md) - Relation-first layout incl. sequence, work-folder shapes/palettes, ink lines and text, color only on label chips
