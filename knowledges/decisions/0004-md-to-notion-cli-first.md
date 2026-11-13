---
type: Architecture Decision Record
title: "0004 Notion sync prefers CLI, MCP as fallback"
description: "Use the Notion CLI first; MCP only for what the CLI cannot do"
resource: ../../docs/adr/0004-md-to-notion-sync-prefers-cli-with-mcp-fallback.md
tags: [decision]
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T14:20:00Z }
sources:
  - id: adr
    resource: ../../docs/adr/0004-md-to-notion-sync-prefers-cli-with-mcp-fallback.md
    title: ADR 0004
    last_modified: 2026-09-19T15:58:54Z
---

Scope: akbun-writing / akbun-md-to-notion

## Decision

Use the Notion CLI first; MCP only for what the CLI cannot do. Detect changes by payload hash.[^adr]

[^adr]: ADR 0004
