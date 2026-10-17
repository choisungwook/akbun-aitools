# Claude Code mods

Claude Code의 동작을 바꾸는 mod(function hooks plugin) 모음이다. skill이나 marketplace plugin이 아니라 파일 묶음이라 `install.sh`로 `~/.claude/mods/`에 복사해 쓴다.

| mod | 하는 일 | 트리거 |
|---|---|---|
| [akbun-memory-sync](./akbun-memory-sync/) | 턴이 끝날 때 사용자 지시에서 반복 규칙을 뽑아 `AGENTS.md`와 그 파일이 참조하는 문서에 반영하는 턴을 제안·자동 실행 | 매 턴 종료, `/memory-sync` |
| [akbun-decision-log](./akbun-decision-log/) | 대안 비교 끝에 내린 결정을 감지해 `docs/adr/`에 ADR 파일과 색인 행을 추가 | 매 턴 종료, `/decision` |
| [akbun-diagram](./akbun-diagram/) | 세션에서 다룬 구조를 Mermaid로 그려 `docs/diagrams/`에 저장, pane 표시, 클립보드 복사 | `/diagram`, 파일 3개 이상 수정 후 제안 띠 |

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

Claude Code를 다시 시작한 뒤 `/` 를 입력하면 명령 목록에 `/memory-sync`, `/decision`, `/diagram`이 나타난다. 나타나지 않으면 `claude --debug`로 시작해 로그에서 mod 이름과 거부 사유를 찾는다.

## 공통 동작

- 세 mod 모두 세션의 작업 디렉터리(`$.session.root()`) 기준으로 파일을 읽고 쓴다. 저장소 밖에서는 동작하지 않거나 빈 결과를 낸다.
- 턴 종료 감지(`turn.complete`)는 메인 대화만 본다. 서브에이전트 턴은 건너뛴다.
- 감지 결과는 프롬프트 위 띠(AbovePrompt)에 뜨고 `반영`·`기록`·`다이어그램` 버튼을 누를 때만 파일을 쓰거나 턴을 큐에 넣는다. `무시`를 누르면 사라진다.
- 모델 호출: 감지는 `haiku` 1회(`$.model.complete`), 초안 작성은 현재 대화를 fork한 1회(`$.model.fork`)다. 토큰은 세션 계정에서 쓴다.

## 개발

mod를 고친 뒤에는 검증과 테스트를 돌린다.

```bash
claude plugin validate mods/akbun-memory-sync
claude plugin test mods/akbun-memory-sync
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
