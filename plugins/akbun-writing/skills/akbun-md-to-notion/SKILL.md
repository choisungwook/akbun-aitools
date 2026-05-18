---
name: akbun-md-to-notion
description: >
  Transfer an Obsidian markdown file to a Notion "Tasks" database using the
  Notion CLI (`ntn`) first and the Notion MCP as a fallback. Reads the markdown
  content, parses YAML frontmatter for metadata, skips uploads when the Notion
  payload hash has not changed, sets database properties (Tags, Start & End
  Date, Status), and creates or updates the same Notion page using
  `notion_page_id`. Use this skill whenever the user mentions Notion in the
  context of transferring, uploading, or syncing content — even if they just
  say "send this to Notion" or "노션에 올려줘" without specifying the file format.
  Also triggers when the user wants to create a Notion page from any markdown
  content. Triggers on: "notion", "send to notion", "md to notion",
  "obsidian to notion", "transfer to notion", "sync to notion", "upload to notion",
  "노션", "노션에 보내줘", "노션에 올려줘", "노션 페이지 만들어줘", or any request
  involving moving written content into a Notion database.
allowed-tools:
  - Bash(echo:*)
  - Bash(pwd:*)
  - Bash(ls:*)
  - Bash(cat:*)
  - Bash(test:*)
  - Bash(find:*)
  - Bash(rg:*)
  - Bash(sed:*)
  - Bash(awk:*)
  - Bash(jq:*)
  - Bash(shasum:*)
  - Bash(stat:*)
  - Bash(date:*)
  - Bash(mktemp:*)
  - Bash(mkdir:*)
  - Bash(mv:*)
  - Bash(cp:*)
  - Bash(printf:*)
  - Bash(ntn:*)
  - mcp__notion__notion-search
  - mcp__notion__notion-fetch
  - mcp__notion__notion-create-pages
  - mcp__notion__notion-update-page
  - mcp__notion__notion-update-data-source
---

# Markdown to Notion

## 개요

markdown 파일을 Notion 데이터베이스로 동기화한다.

## 사전 요구사항

- `$OBSIDIAN_VAULT` 환경변수 설정.
- `$NOTION_TASKS_DATASOURCE_ID` 환경변수 설정. 만약 NOTION_TASKS_DATASOURCE_ID가 설정되어 있지 않으면 중단하고, 사용자에게 아래 오류 메세지를 알린다.

```log
NOTION_TASKS_DATASOURCE_ID 환경변수가 설정되어 있지 않습니다. 이 스킬을 사용하려면 Notion Tasks 데이터베이스의 datasource ID를 환경변수로 설정해야 합니다.
```

- (옵션) ntn CLI를 사용하려면 `NOTION_API_TOKEN` 환경변수 설정
- fallback을 위해 Codex 또는 Claude Code에 Notion MCP 연결

## Notion 도구 사용 우선순위

`ntn` CLI로 먼저 시도하고, 실패하면 Notion MCP로 fallback한다.

1. `ntn api` + `NOTION_API_TOKEN`
  - Codex automation처럼 사람이 자리에 없는 실행은 이 경로를 우선한다.
  - `NOTION_API_TOKEN`이 있으면 `ntn login`으로 Keychain에 저장된 인증보다 우선한다.
2. `ntn api` + `ntn login` Keychain 인증
  - 로컬 수동 실행에서만 사용한다.
3. Notion MCP
  - `ntn`이 없거나 인증이 없거나, markdown content replace를 안전하게 수행하기 어렵다면 fallback으로 사용한다.

## Obsidian frontmatter

마크다운에 아래 frontmatter가 있으면, obsidian으로 취급한다. notion과 동기화가 되었는지 기록하는 메타데이터이다.

```yaml
notion_sync: false
notion_page_id: ""
```

- `notion_sync`: 자동화 대상 여부. true/false상관 없이 notion 업로드가 된 적이 있는 파일은 true로 간주한다. 업로드 성공 시 자동으로 true로 설정한다. false는 한번도 notion에 sync된 적이 없는 파일로 간주한다.
- `notion_page_id`: 이미 생성된 Notion page를 다시 업데이트할 때 사용하는 고정 ID.

## 워크플로우

1. 입력받은 마크다운 파일을 읽는다.
2. YAML frontmatter에서 `created` 날짜, `tags`, `notion_sync`, `notion_page_id`가 있으면 해당 frontmatter를 파싱한다.
4. Notion에 보낼 payload를 만든다.
  - YAML frontmatter는 콘텐츠에서 제거한다。
  - `.md` 확장자를 제외한 파일명을 Notion `Name`으로 사용한다。
  - 속성 payload와 본문 payload를 합쳐 canonical hash를 계산한다。
5. `notion_page_id`가 있으면 해당 페이지를 업데이트한다。`notion_page_id`가 없으면 제목으로 기존 페이지를 검색한다。
  - 찾으면 해당 page id를 사용한다.
  - 없으면 새 페이지를 만든다.
6. 첫 업로드 또는 page id 발견 시 Obsidian frontmatter에 `notion_sync: true`, `notion_page_id`를 설정한다。
7. 업로드 성공 후 state 파일에 최신 hash, page id, sync time을 저장한다。

## 업로드 방식

### 1순위: `ntn api`

- `ntn --version`으로 CLI 존재를 확인한다.
- `NOTION_API_TOKEN`이 있으면 무인 자동화 경로로 간주한다.
- `ntn api`로 검색, page 생성, page 속성 업데이트, block children 교체/추가를 수행한다.
- markdown을 Notion blocks JSON으로 안전하게 변환할 수 없는 경우에는 `ntn` 경로를 실패로 보고 MCP fallback을 사용한다.

### 2순위: Notion MCP fallback

- `notion-search`로 기존 page를 찾는다.
- 생성은 `notion-create-pages`를 사용한다.
- 업데이트는 `notion-update-page`의 `replace_content`를 사용한다.
- 자동화 실행에서는 기존 페이지가 있어도 사용자 확인을 묻지 않는다. `notion_sync: true`가 명시된 파일은 덮어쓰기 승인으로 간주한다.

## 속성 매핑

| Notion 속성 | 값 |
|---|---|
| Name | 중요: `.md` 확장자를 제외한 Obsidian 파일명을 사용한다. frontmatter의 `name` 필드는 무시한다 |
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

- 문단 뒤: 각 문단 다음 줄에 `<empty-block/>`를 추가한다
- 코드 블록 뒤: 닫는 ` ``` ` 다음 줄에 `<empty-block/>`를 추가한다
- 코드 블록 앞: Notion이 자동으로 간격을 처리한다
- 이미지 마커 뒤 (`![[...]]`): 각 이미지 마커 다음 줄에 `<empty-block/>`를 추가한다

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
