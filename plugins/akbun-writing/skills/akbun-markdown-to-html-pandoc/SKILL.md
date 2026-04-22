---
name: akbun-markdown-to-html-pandoc
description: >
  Obsidian markdown을 pandoc으로 HTML로 변환한다. Tistory 같은 블로그 플랫폼에 업로드할 때 사용한다.
  Obsidian 이미지 문법(![[...]])은 plain text 마커로 보존되어 수동으로 이미지를 삽입할 위치를 알 수 있다.
  헤더, 코드 블록 등 일반 markdown 요소는 정상적으로 HTML로 변환된다.
  Triggers on: "markdown to html", "pandoc convert", "tistory", "obsidian to html",
  "blog upload", "블로그 업로드", "HTML 변환", "마크다운 변환".
allowed-tools:
  - Read
---

# Pandoc으로 Markdown을 HTML로 변환

## 문제

Tistory 같은 블로그 플랫폼은 API 업로드를 지원하지 않아 내용을 수동으로 붙여넣어야 한다.
Obsidian은 로컬 이미지 문법(`![[path/to/image.png]]`)을 사용하는데, 이는 표준 markdown이 아니라 pandoc이 `<img>` 태그로 렌더링할 수 없다.

대신 pandoc은 `![[...]]`을 HTML 출력에 plain text로 남긴다. 이 텍스트 마커가 블로그 에디터에서 이미지를 수동으로 삽입할 위치를 알려준다.

그 외 모든 markdown 요소(헤더, 코드 블록, 목록, 굵은 글씨, 링크 등)는 정상적으로 HTML로 변환된다.

## 사전 요구사항

- Homebrew로 `pandoc` 설치 (`brew install pandoc`)
- `~/.zshrc`에 `$OBSIDIAN_VAULT` 환경변수 설정:

아래 내용을 `~/.zshrc`에 추가한다.

```bash
export OBSIDIAN_VAULT="your obsidian path"
```

경로는 `~/vault/post.md` 형식의 `~` 상대 경로를 사용한다.

## 사용법

Obsidian 파일 경로를 인자로 스크립트를 실행한다.

```bash
bash scripts/md-to-html.sh "$OBSIDIAN_VAULT/my-post.md"
```

출력 파일은 `~/Downloads/<파일명>.html`에 저장된다.

## 스크립트 동작

1. markdown을 standalone HTML로 변환 — `pandoc -s`를 실행해 `<html>`, `<head>`, `<body>` 태그를 포함한 완전한 HTML 문서를 생성한다(`-s`/`--standalone` 플래그로 HTML 파편이 아닌 유효한 파일을 출력한다)
2. 줄 바꿈 보존 — `-f markdown+hard_line_breaks`로 단일 개행을 `<br />` 태그로 변환해 Obsidian의 줄 바꿈 동작을 그대로 유지한다
3. 이미지 마커 보존 — Obsidian `![[...]]` 문법을 plain text로 남겨 수동 이미지 삽입 위치 표시자로 활용한다
4. `~/Downloads`에 출력 — 블로그 에디터에 바로 복사·붙여넣기할 수 있다

## 변환 후

1. 생성된 HTML을 브라우저나 텍스트 에디터로 열기
2. 내용을 복사해 블로그 에디터(HTML 모드)에 붙여넣기
3. `![[...]]` 텍스트 마커를 찾아 해당 위치에 이미지를 수동으로 업로드

## 스크립트 위치

`scripts/md-to-html.sh` — 각 플래그와 단계에 대한 자세한 설명은 스크립트 주석을 참고한다.
