# Notion Sync Prefers CLI With MCP Fallback

## Decision

Use the Notion CLI first and MCP only when the CLI cannot perform the required operation. Detect changes with a payload hash; an automation may update the same previously approved Notion page without asking again.

## Reason

CLI execution is reproducible and retryable. MCP remains necessary for operations that the CLI cannot express without making it the default path.

