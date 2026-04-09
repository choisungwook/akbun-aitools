---
name: akbun-make-questions
description: "기술 노트를 읽고 질문을 생성하거나, 열린 질문을 관리한다. Trigger on: '질문 만들어줘', '질문 생성', 'generate questions', '궁금한 점', '더 공부할 것', '질문 정리', 'question from note', or any request to create study questions from technical content."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# akbun 질문 생성

기술 노트를 읽고 깊은 질문을 만든다. 질문은 공부의 시작점이다 -- 좋은 질문은 "왜?"와 "만약?"에서 나온다.

## 질문 생성 원칙

질문 깊이를 3단계로 구분한다. 표면적인 what 질문보다 구조적인 why 질문이 3개월 후에도 의미가 있기 때문이다.

1. **what 질문** -- "이 설정의 기본값은 뭔가?" 검색하면 바로 답이 나오므로 기록하지 않는다.
2. **why 질문** -- "왜 이 기본값을 선택했을까?" 설계 의도를 파고들며, 답을 찾는 과정에서 배운다.
3. **what-if 질문** -- "만약 이 값을 바꾸면 어떤 사이드이펙트가 있을까?" 실험이나 경험이 필요하다. 가장 가치 있다.

what 질문은 메모만 해두고, why와 what-if 질문을 question 노트로 만든다.

## 질문 생성 워크플로

사용자가 노트 경로를 주거나 주제를 말하면 다음 순서로 진행한다.

1. 노트를 읽는다
2. 핵심 개념을 추출한다
3. 각 개념에 대해 아래 5가지 유형의 질문을 시도한다
4. why/what-if 질문만 남긴다
5. 사용자에게 질문 목록을 보여주고 어떤 것을 노트로 만들지 묻는다

### 5가지 질문 유형

| 유형 | 설명 | 예시 |
|---|---|---|
| 설계 의도 | 왜 이렇게 만들었는가? | "왜 kubelet은 lease API를 10초 간격으로 갱신하는가?" |
| 트레이드오프 | 이 선택의 대가는? | "Readiness Probe에 DB 상태를 넣으면 뭘 얻고 뭘 잃는가?" |
| 경계 조건 | 극단적 상황에서 어떻게 되는가? | "모든 node가 동시에 not ready가 되면 pod은 어디로 가는가?" |
| 비교 | 비슷한 것과 뭐가 다른가? | "Gateway API는 Ingress와 뭐가 다르고 왜 만들었는가?" |
| 연결 | 다른 개념과 어떻게 이어지는가? | "eBPF로 kube-proxy를 대체하면 conntrack에 어떤 영향이 있는가?" |

## question 노트 저장

노트를 생성하기 전에 사용자에게 저장 경로를 묻는다. 사용자가 응답하지 않거나 경로를 지정하지 않으면 `~/Downloads/{YYMMDDhh}-questions-byakbun.md`에 생성한다. 예: `26041014-questions-byakbun.md`

프로젝트의 CLAUDE.md나 템플릿에 저장 경로나 frontmatter 규칙이 정의되어 있으면 그것을 우선한다.

## question 노트 구조

본문 구조:

```markdown
## Question

> {why 또는 what-if 질문}

## Context

{이 질문이 왜 생겼는지. 원본 노트의 어떤 내용에서 출발했는지 기술한다.}

## Research

{조사한 내용을 여기에 기록한다. 생성 시점에는 비워둔다.}

## Resolution

{답을 찾으면 여기에 정리한다. 생성 시점에는 비워둔다.}

# 참고자료

- {원본 노트 경로 또는 링크}
```

## 질문 관리

### 열린 질문 현황 확인

사용자가 "질문 현황", "open questions" 같은 요청을 하면:

1. 사용자에게 question 노트가 저장된 경로를 확인한다
2. 해당 경로의 `.md` 파일을 읽는다
3. frontmatter나 본문의 상태 표기(open/resolved 등)로 분류한다
4. 태그별로 집계하여 표로 보여준다

### 질문 해결

사용자가 질문에 답을 찾으면:

1. Research 섹션에 조사 내용을 기록한다
2. Resolution 섹션에 답을 정리한다
3. 상태를 resolved로 변경한다

## 제약

- what 질문은 노트로 만들지 않는다 -- 검색으로 바로 답이 나오는 질문은 노트로 관리할 필요가 없다.
- 질문이 넓으면 쪼갠다 -- "kubernetes 네트워킹은 어떻게 되는가?"보다 "kube-proxy가 iptables 규칙을 어떻게 생성하는가?"가 답을 찾기 쉽다.
- 한 노트에서 질문은 2~3개로 제한한다 -- 5개 이상이면 핵심이 흐려진다.
