# Notion Sync Prefers CLI With MCP Fallback

Markdown to Notion skill은 자동화 실행과 재시도 가능성을 위해 Notion CLI를 우선 사용하고, CLI로 처리하기 어려운 경우 Notion MCP를 fallback으로 사용한다. Notion 동기화가 명시된 파일은 payload hash로 변경 여부를 판단하며, 자동화에서는 같은 Notion page 업데이트를 사용자 재승인 없이 진행한다.
