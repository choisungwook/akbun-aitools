# akbun-readonce 작업 가이드

- Claude Code가 같은 세션에서 동일한 파일을 반복 읽는 것을 방지하는 플러그인.
- 파일의 mtime과 sha256을 추적하여, 변경되지 않은 파일은 Read를 차단하고 이전 컨텍스트를 사용하도록 안내한다.

## 설계 방향

세션별 고유 캐시 파일(JSON)에 읽은 파일의 mtime/sha256을 기록한다.

- **첫 읽기**: 정상 통과 후 캐시에 기록
- **재읽기 (미변경)**: Read 차단 + "이전에 읽은 내용을 사용하세요" 메시지 반환
- **재읽기 (변경됨)**: 정상 통과 후 캐시 갱신

캐시 파일 경로는 transcript 경로에서 파생되어 세션마다 고유하다.

```
~/.claude/projects/<encoded-cwd>/<session-id>-read-cache.json
```

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

## 작업 히스토리

작업 내역은 `docs/changelog.md`에 날짜별로 기록되어 있다. 작업 시작 전에 읽고 현재 상태를 파악한다.

## 작업 후 검증

코드를 수정한 후 반드시 단위 테스트를 실행한다.

```bash
./plugins/akbun-readonce/tests/test-hooks.sh
```

모든 테스트가 PASS여야 하며, 결과 요약에서 "N passed, 0 failed"로 전체 통과를 확인한다. 현재 기준: 12 passed, 0 failed.
