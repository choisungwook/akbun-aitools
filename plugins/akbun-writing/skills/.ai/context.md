# AI Context

## 작업 맥락

akbun-writing은 한국어 기술 글쓰기, 문서 리뷰, 블로그 업로드, Notion 동기화, draw.io 다이어그램 생성을 돕는 skill 모음이다. 새 skill이나 agent 설명은 실제 호출 의도와 산출물을 좁고 명확하게 적는다. 작업 이력은 changelog로 남기지 않고, 다음 agent에게 필요한 용어와 중요한 결정만 이 context와 `docs/decisions/`에 남긴다.

## 용어 정리

- trigger: skill이 자동으로 선택될 사용자 표현이다. 너무 넓게 잡지 않고, 명시적인 요청이나 좁은 의도에 맞춘다.
- akbun style: 실제 글에서 추출한 판단 기준 기반의 한국어 기술 블로그 스타일이다. 입력에 없는 동기·경험·감정을 만들지 않고 `무엇 -> 원리 -> 헷갈리는 점 -> 실제 사용` 흐름을 따른다.
- topology: 자연어, 사진, YAML, 기존 다이어그램에서 추출한 네트워크 구성과 연결 관계이다. 다이어그램 skill은 입력 형식보다 topology 정규화를 우선한다.
- reference image: 그대로 복제할 대상이 아니라 레이아웃, 스타일, 구조를 판단하는 참고 이미지이다.
- 확인 필요: 가정으로 처리하기 어렵거나 다음 작업자가 다시 확인해야 하는 불확실성을 표시하는 말이다.
- Notion sync: Markdown to Notion은 CLI(`ntn`)를 우선하고 MCP를 fallback으로 둔다. `notion_sync`와 payload hash로 반복 업로드를 줄인다.
- book illustration layout(책 삽화 레이아웃): `akbun-draw-poster-monogray`와 같은 팔레트(진회색 잉크+플랫 회색+오렌지 포인트 하나+off-white)를 쓰되, 구도를 자유롭게 두지 않고 참고 이미지에서 뽑은 고정 레이아웃 5종(flow-stack, zoom-detail, poster-card, dialog-scene, icon-strip)과 상하좌우 간격에 맞춰 배치한다. `akbun-draw-book-illustration`이 담당하며, 산출물은 이미지 프롬프트와 편집 가능한 SVG 두 가지다. 스타일만 필요하고 구도가 자유로우면 monogray, 정해진 레이아웃·간격이 필요하면 이 skill을 쓴다.
- question style(질문식): "질문이 글을 끌고 간다"는 골격으로 쓰는 akbun 공부 정리 글이다. `도입 훅(상황 + 관통 질문) -> 질문으로 여는 섹션 -> 마무리 종합` 흐름으로 궁금증을 유발해 끝까지 읽히게 한다. 인터뷰·대담이 아니라 글쓴이 한 명의 정리이며, 화자를 지어내지 않는다. 질문은 why·what-if로 잡는다. self-contained skill: `akbun-writing-with-question`(톤·포맷 규칙을 자체 포함).
- essay-toon(에세이툰): 가로형(16:10) 1컷 페이지 형식으로, 상단의 굵은 손글씨 내레이션이 이야기를 끌고 그림은 감정 한 장면만 보여준다. 주인공은 플랫 채색한 akbun 고래 마스코트, 배경 인물은 채색 없는 선화 실루엣이다. `akbun-draw-webtoon-c`가 담당한다(a: 3~4컷 스틱피겨, b: 세로형 파스텔 치비와 구분).
