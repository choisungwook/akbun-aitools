---
name: akbun-md-to-notion
description: >
  Transfer an Obsidian markdown file to a Notion "Tasks" database using the
  Notion MCP. Reads the markdown content, parses YAML frontmatter for metadata,
  sets database properties (Tags, Start & End Date, Status), and creates a new
  page with the content. If a page with the same title already exists, asks
  before overwriting. Use this skill whenever the user mentions Notion in the
  context of transferring, uploading, or syncing content — even if they just
  say "send this to Notion" or "노션에 올려줘" without specifying the file format.
  Also triggers when the user wants to create a Notion page from any markdown
  content. Triggers on: "notion", "send to notion", "md to notion",
  "obsidian to notion", "transfer to notion", "sync to notion", "upload to notion",
  "노션", "노션에 보내줘", "노션에 올려줘", "노션 페이지 만들어줘", or any request
  involving moving written content into a Notion database.
allowed-tools:
  - Bash(echo:*)
  - mcp__notion__notion-search
  - mcp__notion__notion-fetch
  - mcp__notion__notion-create-pages
  - mcp__notion__notion-update-page
  - mcp__notion__notion-update-data-source
---

# Markdown to Notion

## 개요

Notion MCP를 통해 Obsidian markdown 파일을 Notion "Tasks" 데이터베이스로 전송한다.
Obsidian의 `![[image]]` 문법은 plain text로 유지된다(Notion은 로컬 이미지를 렌더링할 수 없다).

## 사전 요구사항

- Claude Code에 Notion MCP 연결
- `~/.zshrc`에 `$OBSIDIAN_VAULT` 환경변수 설정
- `~/.zshrc`에 `$NOTION_TASKS_DATASOURCE_ID` 환경변수 설정

## Notion 데이터베이스 정보

- **데이터베이스**: Tasks
- **Data Source ID**: `$NOTION_TASKS_DATASOURCE_ID` 환경변수에서 읽는다

## 워크플로우

1. Obsidian markdown 파일을 **읽는다**
2. YAML frontmatter에서 `name`, `created` 날짜, `tags`를 **파싱**한다
3. 동일한 제목의 페이지가 있는지 Notion에서 **검색**한다
   - 있으면: 덮어쓰기 전에 **사용자에게 확인**한다 (`replace_content`로 `notion-update-page` 사용)
   - 없으면: 새 페이지를 **생성**한다
4. 속성과 콘텐츠로 Notion 페이지를 **생성/업데이트**한다

## 속성 매핑

| Notion 속성 | 값 |
|---|---|
| Name | **중요**: `.md` 확장자를 제외한 Obsidian 파일명을 사용한다. frontmatter의 `name` 필드는 무시한다 |
| Tags | 콘텐츠에서 자동 생성 (가능하면 기존 Notion 태그 옵션 재사용) |
| Start & End Date | Start = Obsidian `created` 날짜, End = 오늘 날짜 |
| Status | "In progress" |
| Related to Areas | 비워둔다 (사용자가 직접 설정) |
| Related Projects | 비워둔다 |
| Release | 비워둔다 |

## 속성 형식 (notion-create-pages용)

`notion-create-pages`에 전달할 속성 형식이다.

```json
{
  "Name": "page title",
  "Tags": "[\"tag1\", \"tag2\"]",
  "Status": "In progress",
  "date:Start & End Date:start": "2026-02-15",
  "date:Start & End Date:end": "2026-02-15",
  "date:Start & End Date:is_datetime": 0
}
```

## 콘텐츠 규칙

- Notion에 전송하기 전에 YAML frontmatter(`---...---`)를 제거한다
- Obsidian `![[image]]` 문법은 그대로 유지한다 (plain text 마커)
- 그 외 모든 markdown(헤더, 코드 블록, 목록, 굵은 글씨, 링크)은 그대로 유지한다
- Notion enhanced markdown 형식 사용 (불확실하면 첫 사용 전에 `notion://docs/enhanced-markdown-spec`을 fetch한다)

## 줄 바꿈 규칙

Notion은 빈 줄을 자동으로 제거한다. 빈 줄을 표시하려면 `<empty-block/>` 태그를 사용한다:

- **문단 뒤**: 각 문단 다음 줄에 `<empty-block/>`를 추가한다
- **코드 블록 뒤**: 닫는 ` ``` ` 다음 줄에 `<empty-block/>`를 추가한다
- **코드 블록 앞**: Notion이 자동으로 간격을 처리한다
- **이미지 마커 뒤** (`![[...]]`): 각 이미지 마커 다음 줄에 `<empty-block/>`를 추가한다

아래는 적용 예시다.

```text
문단 내용.
<empty-block/>
다음 문단 내용.
<empty-block/>
` ``bash
code here
` ``
<empty-block/>
이어지는 내용.
```

## 기존 태그 참고

데이터베이스에 이미 있는 공통 태그: AI, aws, Kubernetes, EKS, terraform,
claude, tools, git, linux, ebpf, Cilium, MLOps, kubeflow, OIDC, oauth,
security, vpn, skills, notion, blog, study.

새 태그를 만들기보다 기존 태그를 재사용하는 것을 우선한다.
