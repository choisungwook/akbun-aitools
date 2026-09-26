# 여행 브이로그 편집 오케스트레이터는 색보정 workflow skill 하나다

Scope: akbun-editvideo / akbun-davinciresolve-workflow

## Decision

전체 파이프라인 오케스트레이터(`davinciresolve-video-editor`)를 삭제하고 그 마커 등록표·기본 원칙·작업 순서·검증·로그 형식·`references/agent-api.md`를 색보정 전용이던 `akbun-davinciresolve-workflow`에 합쳤다. 이 skill이 컷부터 렌더까지 전체 순서를 맡고, 하위 skill 전부가 이 skill의 기본 원칙과 마커 등록표를 참조한다.

- 편집은 항상 `akbun-davinciresolve-timeline-chrono`로 촬영 시간순 타임라인 A를 만드는 것으로 시작한다. 유일한 예외는 사용자가 원본 타임라인의 순서를 의도했다고 말한 경우다.
- 하늘(`SKY` 노드, `akbun-davinciresolve-sky`)은 workflow 밖의 단독 skill이다.
- 하위 skill은 모두 `disable-model-invocation: true`라 오케스트레이터가 Skill 도구로 부르지 않고 각 `SKILL.md`를 읽어 절차와 스크립트를 직접 수행한다.

## Reason

두 skill은 원본 불변·클립 식별자·작업 로그 규칙을 공유했고 색보정 workflow가 오케스트레이터의 4단계로 들어가 있어 순서·완료 조건이 두 문서에 나뉘어 있었다. 한 문서로 합치면 순서를 바꿀 때 한 곳만 고친다. 대신 "workflow"라는 이름이 색보정보다 넓은 범위를 뜻하게 됐고, 이름·단계 번호를 참조하는 형제 skill 17개를 함께 고쳐야 했다.

촬영 시간순을 첫 단계로 고정한 이유는 Resolve 스크립팅 API에 클립 이동 함수가 없어 순서를 타임라인 생성 시점에만 정할 수 있기 때문이다. 컷 뒤에 재배치하는 선택지는 없다.

하늘을 뺀 이유는 하늘 없는 클립이 많아 매 편집에 도는 단계로 두기엔 조건부 작업이고, 노드 준비 점검(`workflow.py nodes`)의 필요 라벨을 단순하게 유지하기 위해서다. 필요할 때 단독 호출한다.
