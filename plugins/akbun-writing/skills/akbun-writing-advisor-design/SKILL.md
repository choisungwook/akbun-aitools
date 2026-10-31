---
name: akbun-writing-advisor-design
description: AI로 만든 UI 화면(스크린샷·Figma·HTML/CSS 코드)에서 AI가 만든 티를 찾아 효과·여백·글자 계층·부품 규칙으로 피드백하거나 고친다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# UI 디자인 자문

AI가 한두 번 돌려 만든 화면은 효과가 과하고, 색이 흩어지고, 여백과 글자 크기에 우선순위가 없다. 이 skill은 그 티를 규칙 파일로 찾아 고친다. 규칙은 전부 `references/*.jsonl`에 있고 이 문서는 어느 파일을 언제 읽는지만 정한다.

## 입력

- 화면 이미지, Figma 링크, HTML·CSS·React 코드 중 하나. Figma 링크는 Figma MCP로 읽는다.
- 대시보드·관리자 화면인지 먼저 정한다. 규칙의 `scope`가 `all`이면 모든 화면, `dashboard`이면 대시보드에만 적용한다. 밝은 테마와 어두운 테마 모두에 쓴다.

## 규칙 라우팅

| 볼 것 | 파일 |
|---|---|
| 그림자·glow·그라디언트·색 수·배경 대비 | [effect-rules.jsonl](references/effect-rules.jsonl) |
| 여백·묶음·정렬·카드 배치·표 열 | [layout-rules.jsonl](references/layout-rules.jsonl) |
| 글자 크기·굵기·단위·반복 문구 | [type-rules.jsonl](references/type-rules.jsonl) |
| 선·버튼·아이콘·hover 영역·모서리·배지·검색창·부품 재사용 | [component-rules.jsonl](references/component-rules.jsonl) |

규칙을 뽑은 참고자료는 [sources.jsonl](references/sources.jsonl)에 한 줄씩(`url`, `title`, `added`, 그 자료에서 나온 `rules` id) 쌓는다. 실행 때는 읽지 않는다.

규칙 파일 네 개를 모두 읽는다. 각 줄은 JSON 객체 하나다. `signals`로 해당 여부를 보고, `exceptions`를 먼저 확인한 뒤 `fix` 방향으로 고친다. `example`의 수치는 방향을 보이는 예이고, 화면의 기존 값 단계에 맞춰 고른다. 규칙을 추가할 때는 같은 키로 한 줄을 해당 파일에 넣고, `source`에 그 규칙을 뽑은 참고자료 URL을 넣는다.

## 순서

1. 화면에서 가장 중요한 정보 하나를 정한다. 이후 모든 판단의 기준이다.
2. effect 규칙으로 효과·그라디언트·색을 걷는다.
3. layout·type 규칙으로 여백과 글자 계층을 다시 잡는다.
4. component 규칙으로 부품을 정리하고, 1에서 정한 정보만 emphasis-by-size와 one-guide의 예외로 다시 강조한다.

## 결과

- 이미지·Figma: 고칠 곳을 중요한 순서로 나열한다. 한 줄에 `규칙 id`, 위치, 지금 값 → 고칠 값.
- 코드: 사용자가 고쳐 달라고 하면 코드를 고치고 바꾼 규칙 id 목록을 보고한다. 피드백만 원하면 이미지와 같은 목록을 준다.
- 화면에서 값을 읽을 수 없으면(이미지의 정확한 px) 추정이라고 표시한다.
