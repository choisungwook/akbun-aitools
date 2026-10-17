# akbun-decision-log

대안을 비교한 끝에 내린 결정을 감지해 `docs/adr/`에 결정 기록(ADR)으로 남긴다. 결정은 Issue나 대화 속에 묻히기 쉬운데, 이 mod는 턴이 끝날 때 결정 여부를 묻고 버튼 한 번으로 파일과 색인 행을 쓴다.

## 해결하는 문제

- "A와 B 중 A로 간다"는 결론이 대화에만 남고 `docs/adr/`에 기록되지 않는다.
- 결정을 나중에 적으면 버린 대안과 이유가 빠진다.

## 동작

1. `prompt.submit`에서 사용자 발화를 모은다.
2. 메인 대화의 턴이 정상 종료하면 사용자 발화와 어시스턴트 답변을 `haiku`에 보내 결정 여부를 판정한다. 기준은 대안 2개 이상, 하나를 고름, 이유가 드러남 3가지다.
3. 결정이면 프롬프트 위 띠에 제목을 띄운다. `기록`을 누르면 파일을 쓴다. `무시`를 누르면 버린다.
4. 파일 번호는 `docs/adr/` 안의 `NNNN-*.md` 중 가장 큰 번호 +1이다. `docs/adr/README.md`가 있으면 표 끝에 행을 추가한다.

## 사용법

턴이 끝난 뒤 띠가 뜨면 버튼을 고른다.

```text
결정 감지: Notion 동기화는 CLI 우선  [기록] [무시]
```

감지되지 않은 결정을 직접 기록하려면 한 줄을 준다. 현재 대화를 fork해 초안을 만들고 바로 파일을 쓴다.

```text
/decision Notion 동기화는 CLI 우선, MCP는 대체
```

인자 없이 부르면 띠에 떠 있는 감지 결과를 기록한다.

```text
/decision
```

기존 기록 목록을 본다.

```text
/decision list
```

## 결과

`docs/adr/0007-notion-sync-cli-first.md`가 아래 형식으로 생긴다.

```markdown
# Notion 동기화는 CLI 우선

Scope: akbun-md-to-notion

## Decision

CLI를 먼저 쓰고 MCP는 대체로 둔다.

## Reason

CLI가 빠르고 재현 가능하다.

## Rejected alternatives

- MCP 단독: 느리고 인증이 자주 끊긴다

## Source

- 2025-10-09 Claude Code 세션 sess-1
```

`docs/adr/README.md` 표 끝에 행이 하나 붙는다.

```markdown
| [0007](0007-notion-sync-cli-first.md) | akbun-md-to-notion | Notion 동기화는 CLI 우선 |
```

명령으로 기록하면 응답에 경로와 결정 요약이 함께 나온다.

```text
akbun-decision-log: docs/adr/0007-notion-sync-cli-first.md 작성

Notion 동기화는 CLI 우선
CLI를 먼저 쓰고 MCP는 대체로 둔다.
```

## 한계

- 감지는 `haiku` 한 번이라 작은 선택을 결정으로 볼 수 있다. 띠에서 `무시`로 거른다.
- 파일 본문은 모델이 쓴 초안이다. 쓴 뒤 읽고 다듬는다. `AGENTS.md`의 결정 기록 조건(되돌리기 어렵고 트레이드오프가 있었던 결정)에 맞지 않으면 지운다.
- `docs/adr/`가 없으면 만들어 쓴다. 색인 `README.md`는 있을 때만 갱신한다.
