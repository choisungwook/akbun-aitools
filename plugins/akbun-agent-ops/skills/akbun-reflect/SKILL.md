---
name: akbun-reflect
description: 이 세션의 transcript를 리뷰어 3개(판단·도구·발산)가 병렬로 읽고, 다음 agent의 시간을 아낄 학습을 골라 기존 SKILL.md 수정 제안으로 라우팅한다. 사용자가 승인한 행만 적용한다. 디렉터리 구조나 AGENTS.md 읽기 순서는 정하지 않는다. "reflect", "이 세션에서 배운 걸 skill에 남겨", "self-improving" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-reflect

세션에서 배운 것 중 다음 agent의 시간을 아낄 것만 골라, 그 학습이 살아야 할 SKILL.md에 넣는다. 기록은 별도 wiki가 아니라 실행 경로에 있는 SKILL.md 자체에 남긴다. 실행 경로에 없는 문서는 읽히지 않고, 읽히지 않는 문서는 갱신되지 않는다.

세션을 끝내기 전에 사용자가 부른다. 사소한 세션, 주제를 벗어난 세션, 기존 skill을 그대로 따라 끝난 세션이면 "남길 것 없음"으로 끝낸다. 한 번 일어난 일은 학습이 아니다.

## 하지 않는 것

- 디렉터리 구조와 AGENTS.md 읽기 순서를 만들거나 바꾸지 않는다. 구조는 프로젝트마다 다르고 `akbun-memory-setup`이 프로젝트에서 도출한다. 이 skill의 제안이 "새 디렉터리를 만들자"로 나오면 기각한다.
- 사용자 승인 없이 파일을 고치지 않는다. skill 수정은 이후 모든 세션에 영향을 준다.
- 작업 로그, SHA, 현재 파일 경로, 버전 번호처럼 코드가 바뀌면 틀려지는 사실을 남기지 않는다.

## 1. transcript를 찾는다

Claude Code는 `~/.claude/projects/<slug>/*.jsonl`에 세션을 저장한다. `<slug>`는 프로젝트 절대 경로의 `/`를 `-`로 바꾼 것이다. 수정 시각이 가장 최근인 파일이 보통 현재 세션이다. 첫 `user` 줄의 내용이 이 대화의 첫 요청과 일치하는지 확인해 고른다. 다른 프로젝트 디렉터리는 뒤지지 않는다.

경로를 못 찾으면 이 세션의 요약(요청, 결정, 교정, 산출물)을 직접 써서 transcript 대신 넘긴다.

## 2. 리뷰어 3개를 병렬로 띄운다

Agent 도구로 한 메시지에 3개를 띄운다. 읽기 전용이다. 각 리뷰어는 `references/`의 프롬프트를 그대로 받고 transcript 경로(또는 요약)만 채운다.

| 렌즈 | 찾는 것 | 프롬프트 |
|---|---|---|
| 판단 | 사건 뒤의 일반 원칙, 사용자의 교정과 선호, 반복된 수작업 | `references/reviewer-judgment.md` |
| 도구 | 명령·플래그·경로·라이브러리 특성처럼 다음 agent가 다시 알아내야 할 기술 사실, 사용자가 손으로 준 맥락 중 agent가 스스로 찾을 수 있었던 것 | `references/reviewer-tooling.md` |
| 발산 | 다른 두 리뷰어가 놓칠 것. 운 좋게 통과한 결정, 건너뛴 검증, 2차 효과, 불렸어야 하는데 안 불린 skill | `references/reviewer-divergent.md` |

리뷰어의 발견은 이 세션이 실제로 읽은 skill(transcript에서 `SKILL.md`를 Read한 기록)이나 실제로 쓴 도구에만 라우팅한다. 읽지 않은 skill로의 라우팅은 추측이다. skill이 있었는데 트리거되지 않은 경우만 `tune description: <skill 경로>`로 라우팅한다.

## 3. 종합한다

Agent 하나에 `references/synthesizer.md`와 리뷰어 3개의 출력을 넘긴다. 결과는 Accepted / Rejected / Backlog 표다. 기준은 프롬프트에 있다. 6개월 뒤에도 참인가, 다음 agent의 행동을 바꾸는가, 2명 이상이 같은 걸 봤는가, 기존 skill이 이미 말하고 있지 않은가, 스크립트나 lint로 강제할 수 있지 않은가.

## 4. 구조로 보낼 것을 가른다

Accepted 중 lint, 검증 스크립트, 메타데이터, 런타임 검사로 더 확실히 강제되는 항목은 Backlog로 옮긴다. 텍스트 지시는 읽는 agent의 협조에 의존하고, 구조는 협조 없이 작동한다. 같은 지시가 두 번째로 나오고 있다면 그 지시는 텍스트가 아니라 구조로 갈 신호다.

## 5. 사용자에게 보이고 승인을 받는다

Accepted / Rejected / Backlog 전체를 보이고 기다린다. 사용자가 적용할 행을 고르고 라우팅을 바꿀 수 있다. 승인된 행만 적용한다.

- 한 줄 추가, 문장 조임, 틀린 사실 교정: 직접 고친다.
- 새 절이나 10줄 넘는 변경: skill 작성 규칙(skill-creator가 있으면 그것)을 따라 초안·검토 순으로 고친다.
- `tune description`: 해당 skill의 description만 고친다.
- `new skill`: 드물다. 기존 skill이 진짜 집이 아닐 때만, 사용자 확인 뒤 만든다.

plugin 아래 skill을 고쳤으면 그 plugin의 두 manifest 버전을 이 저장소 규칙대로 올린다. Backlog는 사용자가 쓰는 트래커가 있으면 거기에, 없으면 보고에만 남긴다.

## 6. 보고

개조식, 서두 없이.

- 적용한 수정: `<skill 경로>`. 무엇이 바뀌었는지 한 줄씩
- 만든 skill: 있으면 한 줄씩
- Backlog: 제목과 제안한 메커니즘
- 기각: 원칙 한 줄과 기각 이유 태그
