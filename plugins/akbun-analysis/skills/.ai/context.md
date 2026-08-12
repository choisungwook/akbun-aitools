# AI Context

## 작업 맥락

akbun-analysis skills는 코드베이스의 서비스·컴포넌트 관계를 repo 바깥에 영구 저장하고 시각화한다. `analysis.json`만 분석 원본이며 self-contained HTML과 선택적 draw.io는 JSON에서 생성한다. 이후 구조·역할·영향 가능성 질문은 JSON을 먼저 읽고, 코드 변경은 file:line 근거와 소유 경로를 이용해 증분 반영한다.

## 용어 정리

- 분석 원본: 프로젝트별 `analysis.json`. SQLite와 wiki는 사용하지 않는다.
- 파생 산출물: `analysis.json`에서 생성하는 `analysis.html`과 선택적 `analysis.drawio`. draw.io 변경은 JSON으로 역동기화하지 않는다.
- 활용 모드: JSON을 먼저 읽어 질문에 답하는 기본 모드. 최초 분석과 증분 갱신에서만 코드를 탐색한다.
- project-id: repo이름 slug + git remote(없으면 절대경로) sha256 앞 8자리. 같은 repo는 항상 같은 저장소로 이어진다.
- 영향 가능성: 관계 방향과 종류로 계산한 도달 가능성. 장애 범위나 실제 리스크를 의미하지 않는다.
