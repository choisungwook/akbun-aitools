# akbun-session-meter

Claude Code 세션의 상태를 pane과 status line에 표시하는 mod입니다. skill이 아니라 Claude Code 화면을 바꾸는 hooks module이라 Claude Code에서만 동작합니다.

## 표시하는 값

| 항목 | 내용 |
|---|---|
| Session | 현재 세션 ID |
| Cost | `/cost`와 같은 예상 비용(USD). 로컬 계산값이라 실제 청구액과 다를 수 있습니다 |
| Tokens | 마지막 응답 기준 컨텍스트 토큰 / 컨텍스트 윈도우 크기 |
| Context | 컨텍스트 윈도우 사용률. 60% 이상 노랑, 80% 이상 빨강 |
| Agents | 이 세션의 subagent·teammate 목록. 실행 중인 것이 위에 오고, 상태·이름·타입·토큰·비용을 표시합니다 |

status line에는 한 줄 요약이 표시됩니다.

```text
abcdef12 | ~$1.23 | 45.2k/200.0k (23%) | agents 1
```

## 설치

Claude Code 입력창에서 marketplace를 등록하고 mod를 설치하는 명령입니다.

```bash
/plugin marketplace add choisungwook/akbun-aitools
/plugin install akbun-session-meter@akbun-aitools
/reload-plugins
```

터미널에서 설치하는 명령입니다. 설치 뒤 Claude Code를 다시 시작합니다.

```bash
claude plugin marketplace add choisungwook/akbun-aitools
claude plugin install akbun-session-meter@akbun-aitools
```

저장소를 받아 설치 없이 한 번만 써 보려면 폴더를 지정해 Claude Code를 실행합니다.

```bash
git clone --depth 1 https://github.com/choisungwook/akbun-aitools
claude --plugin-dir akbun-aitools/mods/akbun-session-meter
```

## 사용

- 세션이 시작되면 pane이 자동으로 열립니다. 데스크톱 앱은 작은 widget, 터미널은 너비 110칸 이상이면 대화 오른쪽, 그보다 좁으면 입력창 위에 표시됩니다.
- pane을 닫았으면 `/session-meter`로 다시 엽니다.
- 비용·토큰·컨텍스트는 턴이 끝날 때마다, 에이전트 목록은 2초마다 갱신됩니다.

## 재설치

최신 버전으로 다시 받는 터미널 명령입니다. 끝나면 Claude Code에서 `/reload-plugins`를 실행합니다.

```bash
claude plugin uninstall akbun-session-meter@akbun-aitools
claude plugin marketplace update akbun-aitools
claude plugin install akbun-session-meter@akbun-aitools
```

## 삭제

mod를 지우는 터미널 명령입니다.

```bash
claude plugin uninstall akbun-session-meter@akbun-aitools
```

## 개발

| 파일 | 내용 |
|---|---|
| `hooks/register.tsx` | hook 본체. 측정값 저장, 에이전트 목록 갱신, pane 그리기 |
| `types/index.d.ts` | `$.state`에 저장하는 값의 타입 |
| `tests/register.test.tsx` | pane·status line 표시 테스트 |

검사와 테스트를 실행하는 명령입니다.

```bash
claude plugin validate mods/akbun-session-meter
claude plugin test mods/akbun-session-meter
```
