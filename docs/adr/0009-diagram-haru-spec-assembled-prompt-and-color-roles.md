# diagram-haru는 spec을 스크립트가 조립하고, 글자는 검정·강조색은 화살표에만 쓴다

Scope: akbun-draw / akbun-draw-diagram-haru

## Decision

- 모델은 다이어그램 spec(JSON)만 쓰고, 영어 프롬프트는 `scripts/haru_prompt.py`가 `references/*.jsonl`(style·palettes·layouts·shapes·edges·groups) 문장으로 조립하고 채점한다. 배치 라우팅(`pick`·`key`·`values`·`title`·`same`)도 `layouts.jsonl` 필드에 두어 새 배치는 jsonl 한 줄로 더한다.
- 글자(도형 이름·화살표 라벨·메모·판 제목·번호)는 팔레트와 무관하게 모두 `ink`(검정)다. 강조색 `accent`는 화살표 선·머리·`blocked`의 X 획·번호 원에만 쓴다.
- `focus` 강조 채움은 팔레트마다 한 색이고(`mono-yellow`는 `#FFF5C9`), 모든 `focus` 도형을 같은 농도로 칠한다. 개수는 판마다 하나까지다.
- 화살표는 직선이고, 직선이 다른 도형을 가로지를 때만 한 번 휜다. 실패 경로는 `sync`를 빌리지 않고 `blocked`를 쓴다.

## Reason

모델이 프롬프트 문장을 직접 쓰면 장마다 그림체가 달라져, 문장을 라이브러리로 고정했다. 화살표 라벨·메모를 강조색으로 쓰던 때는 `ink-blue` 장은 파란 글자, `mono-yellow` 장은 검은 글자가 되어 연속 장면에서 글자 색이 바뀌었다. 노랑을 두 색(`#FFF5C9`, `#F8E9A7`)으로 번갈아 칠하던 때는 한 그림 안에서 노랑 농도가 달라 보였다.

버린 대안: 판 이름을 도형 `label`마다 붙이기(같은 낱말 반복, 12자 한도 소모), 배치별 노드 키를 스크립트에 하드코딩(새 배치마다 코드·SKILL.md·selftest 세 곳 수정), 라벨만 강조색 유지(팔레트가 바뀌면 글자 색이 다시 흔들림).

트레이드오프: 화살표 라벨이 검정이라 어느 화살표의 라벨인지 색으로 구분되지 않고, 위치(선 바로 옆)로만 구분된다. 강조 도형 두 개를 색으로 구분할 수 없고 판 위치로만 구분한다.
