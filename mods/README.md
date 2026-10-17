# Claude Code mods

Claude Code의 동작을 바꾸는 mod(function hooks plugin) 모음이다. skill이나 marketplace plugin이 아니라 파일 묶음이라 `install.sh`로 `~/.claude/mods/`에 복사해 쓴다.

세 mod는 같은 틀로 돈다. 턴이 끝날 때마다 `haiku` 한 번이 "더 할 일이 있는가"를 판정하고, 있을 때만 현재 대화를 fork한 모델(`$.model.fork`)이 결과를 JSON으로 돌려주고, mod가 파일을 쓰거나 pane을 그린다. 메인 세션은 멈추지 않는다.

| mod | 하는 일 | 트리거 |
|---|---|---|
| [akbun-memory-sync](./akbun-memory-sync/) | 사용자 지시에서 반복 규칙을 찾아 `AGENTS.md`와 그 파일이 참조하는 문서의 섹션 끝에 줄을 덧붙임. 띠에 `+N · 파일`, pane에 기록, `되돌리기` | 매 턴 종료(haiku 판정), `/memory-sync now` |
| [akbun-decision-log](./akbun-decision-log/) | Claude가 선택지를 묻는 질문으로 답을 끝내면 선택지·장단점·추천을 pane에 정리하고, 고른 안을 `docs/adr/`에 ADR과 색인 행으로 기록 | 질문으로 끝난 턴(정규식 + haiku), `/decision` |
| [akbun-diagram](./akbun-diagram/) | 답의 Mermaid 블록을 pane에 고정하고, 몇 턴마다 작업 지도(파일·컴포넌트·단계)를 상자와 간선으로 그림. `/diagram save`로 `docs/diagrams/`에 저장 | 3턴마다(haiku 게이트), `/diagram` |

## 설치

저장소 루트에서 아래 명령을 실행하면 `mods/*`를 `~/.claude/mods/<mod>`로 복사한다.

```bash
mods/install.sh
```

항상 로드하려면 `--settings`를 붙인다. `~/.claude/settings.json`의 `env.CLAUDE_CODE_PLUGIN_DIRS`에 복사한 경로를 합치고, 기존 파일은 `.bak.<시각>`으로 백업한다.

```bash
mods/install.sh --settings
```

특정 mod만 설치하려면 이름을 나열한다.

```bash
mods/install.sh akbun-diagram akbun-decision-log
```

이번 세션에서만 써 보려면 복사 없이 저장소 경로를 직접 준다.

```bash
claude --plugin-dir mods/akbun-memory-sync --plugin-dir mods/akbun-decision-log --plugin-dir mods/akbun-diagram
```

복사 대상 디렉터리는 `CLAUDE_MODS_DIR` 환경 변수로 바꿀 수 있다. 로드 방법의 원본은 Claude Code 문서의 `--plugin-dir`, `CLAUDE_CODE_PLUGIN_DIRS` 항목이다.

## 설치 확인

Claude Code를 다시 시작한 뒤 `/` 를 입력하면 명령 목록에 `/memory-sync`, `/decision`, `/diagram`이 나타난다. 터미널이 144열 이상이면 `Memory`, `Diagrams` pane이 오른쪽에 열린다. 나타나지 않으면 `claude --debug`로 시작해 로그에서 `hooks module akbun-` 줄과 거부 사유를 찾는다.

## 공통 동작

- 세 mod 모두 세션의 작업 디렉터리(`$.session.root()`) 기준으로 파일을 읽고 쓴다. 저장소 밖에서는 동작하지 않거나 빈 결과를 낸다.
- 턴 종료 감지(`turn.complete`)는 메인 대화의 정상 종료만 본다. 서브에이전트 턴과 중단된 턴은 건너뛴다.
- 판정은 `haiku` 1회(`$.model.complete`), 초안은 현재 대화를 fork한 1회(`$.model.fork`)다. fork는 도구를 쓰지 않고 JSON으로만 답하며, 파일은 mod 코드가 쓴다. 토큰은 세션 계정에서 쓴다.
- 판정과 fork는 턴이 끝난 뒤 백그라운드로 돈다. `claude -p`처럼 턴이 끝나면 종료되는 환경에서는 `AKBUN_MEMORY_SYNC_WAIT=1`, `AKBUN_DECISION_WAIT=1`, `AKBUN_DIAGRAM_WAIT=1`로 기다리게 한다. `-p`에서는 pane과 명령이 없다.
- pane은 세션 시작 때 열린다(`akbun-decision-log`는 질문이 감지될 때). 터미널이 144열보다 좁으면 자동으로 열리지 않고, 해당 명령을 치면 폭과 무관하게 열린다.

## 개발

mod를 고친 뒤에는 검증과 테스트를 돌린다. 테스트는 모델·파일·시계를 mock으로 바꿔 hook 흐름과 pane 내용을 확인한다.

```bash
claude plugin validate mods/akbun-memory-sync
claude plugin test mods/akbun-memory-sync
```

실제 동작은 `--plugin-dir`로 띄워 본다. 헤드리스로 확인할 때는 저장소 사본에서 돌린다.

```bash
AKBUN_MEMORY_SYNC_WAIT=1 claude -p --plugin-dir mods/akbun-memory-sync "앞으로 커밋 메시지는 한국어로 써줘"
```

파일 구조는 모든 mod가 같다.

| 파일 | 역할 |
|---|---|
| `.claude-plugin/plugin.json` | 이름, 버전, 설명, 타입 계약 경로 |
| `hooks/hooks.json` | 로드할 hooks module 경로 |
| `hooks/register.tsx` | hook 본체 |
| `hooks/register.test.ts` | `claude plugin test`가 돌리는 테스트 |
| `types/index.d.ts` | `$.state`에 두는 값의 타입 계약 |
| `README.md` | 사용 매뉴얼 |

`install.sh`는 `*.test.ts`와 엔진이 생성하는 `.claude-plugin/types/`를 복사하지 않는다.
