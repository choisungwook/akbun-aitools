# AI Context

## 작업 맥락

akbun-analysis skills는 코드베이스 분석 결과를 repo 바깥의 영구 지식 저장소로 남기고 재사용하는 skill 모음이다. 첫 분석에서 서비스 관계 그래프(SQLite)와 LLM wiki를 만들고, 이후 구조·역할·영향도 질문은 코드 대신 저장소를 먼저 읽어 입력 토큰을 줄인다. 저장소 경로·스키마 같은 계약은 `references/storage.md`에 고정하고, 분석 방법 자체는 agent 판단에 맡긴다.

## 용어 정리

- 지식 저장소(knowledge store): OS 표준 데이터 경로 아래 프로젝트별로 쌓이는 분석 산출물 전체(graph.sqlite + wiki + meta.json).
- LLM wiki: 사람이 아니라 다음 LLM agent가 읽는 것을 전제로 쓴 문서 묶음. index-first로 탐색한다.
- 활용 모드: 저장소를 먼저 읽어 질문에 답하는 기본 모드. 분석 모드는 저장소가 없거나 전면 재분석이 필요할 때만 수행한다.
- project-id: repo이름 slug + git remote(없으면 절대경로) sha256 앞 8자리. 같은 repo는 항상 같은 저장소로 이어진다.
