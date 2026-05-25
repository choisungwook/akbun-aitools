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
- language study blog: 영어공부/일본어공부 정리 요청에만 쓰는 일기형 학습 기록이다. 일반 기술 블로그, 발음, 번역, 게시/업로드 요청과 구분한다.
