# Decisions

* [0002 Reference image is not a pixel target](0002-reference-image-is-not-pixel-target.md) - Reference images/videos are only a style source; done is judged by rule checks, not pixel similarity
* [0004 Notion sync prefers CLI, MCP as fallback](0004-md-to-notion-cli-first.md) - Use the Notion CLI first; MCP only for what the CLI cannot do
* [0005 YouTube output is a transcript-grounded script](0005-youtube-transcript-is-grounded.md) - Produce a chronological Markdown transcript, not a summary
* [0006 Travel vlog orchestrator is the color workflow skill](0006-travel-vlog-orchestrator-is-color-workflow.md) - akbun-davinciresolve-workflow owns the full order from cut to render
* [0007 Static draw styles are design tokens, not skills](0007-draw-styles-are-design-tokens.md) - (deprecated) Static SVG styles are one router skill plus one JSON design token per style
* [0008 Explainer SVG reduced to the chalkboard skill](0008-explainer-svg-reduced-to-chalkboard.md) - Replace the akbun-draw-explainer-svg router with the akbun-draw-chalkboard skill and delete the other tokens
