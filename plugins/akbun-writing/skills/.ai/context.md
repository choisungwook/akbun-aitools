# AI Context

## 작업 맥락

akbun-writing은 한국어 글쓰기·리뷰·발행·Notion 동기화 skill 모음이다. 이미지와 아키텍처 작업은 각각 akbun-draw와 akbun-draw-architecture가 맡는다. 새 skill 설명은 호출 의도와 산출물을 좁게 적고, 작업 이력은 남기지 않는다.

## 용어 정리

- trigger: skill이 선택될 사용자 표현이다. 명시적이고 좁은 의도에 맞춘다.
- akbun style: 입력에 없는 경험을 만들지 않고 `무엇 -> 원리 -> 헷갈리는 점 -> 실제 사용`으로 쓰는 한국어 기술 블로그 스타일이다.
- 문체 자연화: 한국어 원문의 사실·논지·장르·목소리·Markdown을 보존하며 맞춤법과 기계적인 문체만 국소 교정한다. 사용자 규칙은 삭제 목록이 아니라 AI스러운 조건과 사람다운 수정 방향을 합의해 누적한 커스텀 기준이다. skill: `akbun-writing-naturalize`.
- 확인 필요: 의미를 추측하지 않고 원문을 유지한 불확실성을 표시한다.
- Notion sync: CLI(`ntn`) 우선, MCP fallback으로 Markdown을 Notion에 동기화한다.
- onboarding doc: 맥락 없는 사람이 시스템 전체를 이해하는 문서다. 코드·문서로 확인할 수 없는 업무 규칙과 제약은 인터뷰로 보완한다. skill: `akbun-it-onboarding`.
- question style: 관통 질문과 질문형 섹션으로 전개하는 1인칭 공부 정리다. skill: `akbun-writing-with-question`.
- 기초 레이어: 초보자가 `전체 그림 -> 구성 요소 -> 동작 순서 -> 헷갈리는 지점`을 잡는 개조식 글이다. skill: `akbun-writing-easy`.
