# akbun-readonce

Claude Code가 같은 세션에서 동일한 파일을 반복 읽는 것을 방지하는 hook.

## 동작 원리

세션별 고유 캐시 파일(JSON)에 읽은 파일의 mtime/sha256을 기록한다.

- **첫 읽기**: 정상 통과 후 캐시에 기록
- **재읽기 (미변경)**: Read 차단 + "이전에 읽은 내용을 사용하세요" 메시지 반환
- **재읽기 (변경됨)**: 정상 통과 후 캐시 갱신

## Hook 구성

| Hook | 스크립트 | 역할 |
|---|---|---|
| PreToolUse(Read) | `scripts/pre-read.sh` | 캐시 확인 후 차단/허용 판단 |
| PostToolUse(Read) | `scripts/post-read.sh` | 읽기 성공 후 캐시 기록 |
| SessionStart | `scripts/session-start.sh` | /clear, compact 시 캐시 초기화 |

## 변경 감지 순서

1. mtime 비교 (빠름)
2. mtime이 다르면 sha256 비교 (touch만 한 경우 대응)
3. sha256도 다르면 변경된 것으로 판단 → Read 허용

## 캐시 초기화 조건

| 이벤트 | 동작 |
|---|---|
| `/clear` | 현재 세션 캐시 삭제 |
| `compact` (컨텍스트 압축) | 현재 세션 캐시 삭제 |
| `startup` (새 세션) | 7일 이상 된 캐시 파일 정리 |

## 설치

리포지토리 루트에서 설치 스크립트를 실행한다.

```bash
bash install_hook.sh
```

스크립트가 `$HOME/.claude/hooks/readonce/`에 hook 스크립트를 복사하고, `~/.claude/settings.json`에 hook 설정을 자동 추가한다.

## 제거

리포지토리 루트에서 설치 스크립트를 실행한 후 "제거"를 선택한다.

```bash
bash install_hook.sh
```

스크립트가 `$HOME/.claude/hooks/readonce/` 디렉터리를 삭제하고, `~/.claude/settings.json`에서 readonce 관련 hook 설정을 자동 제거한다.

## 환경변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `READ_ONCE_DISABLED` | `0` | `1`로 설정하면 hook 비활성화 |
| `READ_ONCE_MODE` | `deny` | `deny`: 재읽기 차단 (exit 2), `warn`: 읽기 허용 + 경고 메시지 |

## 부분 읽기 (offset/limit)

offset이나 limit 파라미터가 있는 부분 읽기는 캐싱하지 않고 항상 허용한다. 같은 파일의 다른 구간을 읽을 때 잘못 차단되는 것을 방지한다.

## 의존성

- `jq`: JSON 파싱/쓰기
- `shasum`: sha256 해시 계산
