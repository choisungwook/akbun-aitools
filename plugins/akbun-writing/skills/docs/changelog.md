# Changelog

## 2026-05-17 #3

- `akbun-md-to-notion` 스킬을 `ntn api` 우선, Notion MCP fallback 구조로 정리했다.
- Codex automation 무인 실행을 위해 파일 조회, hash 계산, state 저장, `ntn` 호출 관련 allowed-tools를 추가했다.
- `notion_sync`/`notion_page_id` 메타데이터와 payload hash 기반 skip 규칙을 추가했다.
- 자동화 실행에서는 `notion_sync: true` 파일의 기존 Notion page 덮어쓰기를 사용자 승인 없이 진행하도록 명시했다.
- `akbun-writing` plugin manifest 버전을 `1.0.5`로 올렸다.

## 2026-05-10 #2

- `akbun-learning-language-blog` 스킬 추가: 영어공부/일본어공부 노트를 한국어 개인 일기형 학습 기록 초안으로 정리한다.
- trigger는 명시적인 영어공부/일본어공부 정리 요청으로 좁게 유지한다. 일반 게시/업로드, 기술블로그, 발음, 번역, 회사명/수업명/기관명 기반 요청은 제외한다.
- `요약`, `목차`, `마무리`, `참고자료` 없이 공부 날짜가 먼저 보이는 일기형 출력을 위해 템플릿과 스타일 가이드를 추가한다.

## 2026-04-19 #1

- akbun-writing SKILL.md: 따옴표 누락(여는 따옴표), 문단 규칙 중복/어색 표현, `# 참고자료` 섹션의 "이유는 두 가지다" 누락된 두 번째 이유 정리
- akbun-writing SKILL.md: 안티패턴 6개 중 5개에 비포/애프터 한 줄 예시 추가 (Opus 격식 디폴트 교정)
- akbun-writing SKILL.md: 1인칭 소유권 섹션에 모델 디폴트 교정 한 줄, 미완성 인정 섹션에 좋은 예 한 줄 추가
