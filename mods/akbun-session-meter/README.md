# akbun-session-meter

Claude Code 세션의 상태를 pane과 status line에 표시하는 mod입니다. skill이 아니라 Claude Code 화면을 바꾸는 hooks module이라 Claude Code에서만 동작합니다.

## 표시하는 값

`Session meter` pane(세션 시작 시 자동으로 열림):

| 항목 | 내용 |
|---|---|
| Session | 현재 세션 ID |
| Cost | `/cost`와 같은 예상 비용(USD). 로컬 계산값이라 실제 청구액과 다를 수 있습니다 |
| Tokens | 마지막 응답 기준 컨텍스트 토큰 / 컨텍스트 윈도우 크기 |
| Context | 컨텍스트 윈도우 사용률. 60% 이상 노랑, 80% 이상 빨강 |
| Changes | 변경 파일 수와 추가·삭제 줄 수. 누르거나 `d`를 누르면 `Changes` pane이 열립니다 |
| Agents | 이 세션의 subagent·teammate 목록. 실행 중인 것이 위에 오고, 상태·이름·타입·토큰·비용을 표시합니다 |

`Changes` pane(Claude Desktop의 diff 화면과 비슷한 화면):

- `git diff HEAD`와 새로 만든(untracked) 파일 기준으로 변경 파일 목록과 파일별 `+`/`-` 줄 수를 표시합니다.
- 파일을 누르면 그 파일의 diff를 색으로 구분해 표시합니다. 처음에는 첫 파일이 선택됩니다.
- Edit·Write·Bash 같은 도구가 끝날 때마다 갱신됩니다. `r` 또는 `새로고침`으로 직접 갱신합니다.
- git 저장소가 아니면 diff를 표시하지 않습니다. 파일 50개, 파일당 diff 400줄까지 표시하고, 넘는 파일 수는 `외 N개`로 표시합니다. 이름을 바꾼 파일은 삭제와 추가로 나눠 표시합니다.

status line에는 한 줄 요약이 표시됩니다.

```text
abcdef12 | ~$1.23 | 45.2k/200.0k (23%) | agents 1
```

## 설치

두 방법 중 하나를 고릅니다.

| 방법 | 설치 위치 | 이럴 때 |
|---|---|---|
| marketplace 설치 | `~/.claude/plugins/` | Claude Code가 플러그인을 관리하게 할 때 |
| 디렉터리 지정 | 내가 받은 폴더 | `~/.claude`에 설치하지 않고 폴더를 직접 관리할 때 |

### marketplace 설치

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

### 디렉터리 지정

저장소를 원하는 폴더에 받는 명령입니다. 아래 예시는 `~/tools`에 받습니다.

```bash
git clone --depth 1 https://github.com/choisungwook/akbun-aitools ~/tools/akbun-aitools
```

실행할 때마다 폴더를 지정하는 명령입니다.

```bash
claude --plugin-dir ~/tools/akbun-aitools/mods/akbun-session-meter
```

매번 지정하지 않으려면 셸 설정 파일(`~/.zshrc`, `~/.bashrc`)에 환경 변수를 넣습니다. 여러 폴더는 `:`(Windows는 `;`)로 구분합니다. 셸 설정 파일의 변수는 터미널에서 실행한 Claude Code만 읽습니다.

```bash
export CLAUDE_CODE_PLUGIN_DIRS="$HOME/tools/akbun-aitools/mods/akbun-session-meter"
```

데스크톱 앱은 셸 설정 파일을 읽지 않으므로 `~/.claude/settings.json`의 `env`에 넣습니다. JSON에서는 `$HOME`이 풀리지 않으니 `~`나 절대 경로를 씁니다.

```json
{
  "env": {
    "CLAUDE_CODE_PLUGIN_DIRS": "~/tools/akbun-aitools/mods/akbun-session-meter"
  }
}
```

## 사용

- 세션이 시작되면 `Session meter` pane이 자동으로 열립니다. 데스크톱 앱은 작은 widget, 터미널은 너비 110칸 이상이면 대화 오른쪽, 그보다 좁으면 입력창 위에 표시됩니다.
- `/session-meter`: `Session meter` pane을 다시 엽니다.
- `/session-diff`: `Changes` pane을 엽니다.
- 비용·토큰·컨텍스트는 응답마다, 에이전트 목록은 2초마다 갱신됩니다.

## 업데이트

marketplace로 설치했다면 최신 버전으로 다시 받는 터미널 명령입니다. 끝나면 Claude Code에서 `/reload-plugins`를 실행합니다.

```bash
claude plugin marketplace update akbun-aitools
claude plugin update akbun-session-meter@akbun-aitools
```

디렉터리를 지정했다면 받은 폴더를 갱신하고 Claude Code를 다시 시작합니다.

```bash
git -C ~/tools/akbun-aitools pull
```

## 설치 해제

marketplace로 설치했다면 mod를 지우는 터미널 명령입니다. 끝나면 Claude Code를 다시 시작합니다.

```bash
claude plugin uninstall akbun-session-meter@akbun-aitools
```

이 저장소의 다른 plugin도 쓰지 않을 때만 marketplace 등록을 지웁니다. 등록을 지우면 이 marketplace에서 설치한 다른 plugin도 함께 지워집니다.

```bash
claude plugin marketplace remove akbun-aitools
```

Claude Code 입력창에서 지울 때는 아래 명령입니다.

```bash
/plugin uninstall akbun-session-meter@akbun-aitools
/reload-plugins
```

디렉터리를 지정했다면 `--plugin-dir` 옵션을 빼고 실행합니다. 환경 변수를 넣었다면 셸 설정 파일에서 `CLAUDE_CODE_PLUGIN_DIRS` 줄을 지운 뒤 새 터미널을 엽니다. 받은 폴더가 더 필요 없으면 지웁니다.

```bash
rm -rf ~/tools/akbun-aitools
```

## 개발

| 파일 | 내용 |
|---|---|
| `hooks/register.tsx` | hook 본체. 측정값 저장, 에이전트 목록 갱신, pane 그리기 |
| `hooks/diff.ts` | `git diff` 실행과 출력 파싱 |
| `types/index.d.ts` | `$.state`에 저장하는 값의 타입 |
| `tests/register.test.tsx` | pane·status line·diff 표시 테스트 |
| `tests/diff.test.ts` | 실제 git 출력으로 만든 diff 파싱 경계 사례 테스트 |

검사와 테스트를 실행하는 명령입니다.

```bash
claude plugin validate mods/akbun-session-meter
claude plugin test mods/akbun-session-meter
```
