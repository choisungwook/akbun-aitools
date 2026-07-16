# AI Context

## 작업 맥락

akbun-writing은 한국어 기술 글쓰기, 문서 리뷰, 블로그 업로드, Notion 동기화를 돕는 skill 모음이다. 이미지 그리기 skill은 akbun-draw plugin으로, 아키텍처·다이어그램 skill은 akbun-draw-architecture plugin으로 분리했다. 새 skill이나 agent 설명은 실제 호출 의도와 산출물을 좁고 명확하게 적는다. 작업 이력은 changelog로 남기지 않고, 다음 agent에게 필요한 용어와 중요한 결정만 이 context와 `docs/decisions/`에 남긴다.

## 용어 정리

- trigger: skill이 자동으로 선택될 사용자 표현이다. 너무 넓게 잡지 않고, 명시적인 요청이나 좁은 의도에 맞춘다.
- akbun style: 실제 글에서 추출한 판단 기준 기반의 한국어 기술 블로그 스타일이다. 입력에 없는 동기·경험·감정을 만들지 않고 `무엇 -> 원리 -> 헷갈리는 점 -> 실제 사용` 흐름을 따른다.
- 확인 필요: 가정으로 처리하기 어렵거나 다음 작업자가 다시 확인해야 하는 불확실성을 표시하는 말이다.
- Notion sync: Markdown to Notion은 CLI(`ntn`)를 우선하고 MCP를 fallback으로 둔다. `notion_sync`와 payload hash로 반복 업로드를 줄인다.
- question style(질문식): "질문이 글을 끌고 간다"는 골격으로 쓰는 akbun 공부 정리 글이다. `도입 훅(상황 + 관통 질문) -> 질문으로 여는 섹션 -> 마무리 종합` 흐름으로 궁금증을 유발해 끝까지 읽히게 한다. 인터뷰·대담이 아니라 글쓴이 한 명의 정리이며, 화자를 지어내지 않는다. 질문은 why·what-if로 잡는다. self-contained skill: `akbun-writing-with-question`(톤·포맷 규칙을 자체 포함).
