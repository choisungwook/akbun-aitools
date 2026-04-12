# Changelog

## 2026-04-12 #6

- [#22](https://github.com/choisungwook/akbun-aitools/issues/22) 한 세션에서 두 번째 이후 파일의 Read 해시가 캐시에 기록되지 않아 readonce 차단이 동작하지 않던 버그 수정 — `ensure_cache_file`을 `if`/`fi` 블록으로 재작성해 캐시 JSON이 이미 있을 때도 0을 반환하도록 수정
- 모든 hook 스크립트에 ERR trap 추가: `set -eE` + 스크립트별 exit code(post-read=10, pre-read=20, pre-compact=30, session-start=40)로 구분. 향후 어떤 명령이 실패해도 stderr에 `[readonce/xxx.sh] failed at line N (rc=..., code=...)` 진단이 남음
- 회귀 테스트 `test_post_read_consecutive_calls` 추가 (23 passed / 0 failed)

## 2026-04-12 #5

- compact 이후 캐시가 삭제되지 않는 버그 수정 (closes #20)
- PreCompact 훅 추가: `scripts/pre-compact.sh`
- `session-start.sh`의 동작하지 않던 compact 분기 제거
- `install/settings.json`에 PreCompact 엔트리 추가
- 테스트 교체: `test_session_start_clears_on_compact` → `test_pre_compact_clears_cache`

## 2026-04-11 #4

- offset/limit 부분 읽기 바이패스 추가 (캐싱/차단 대상에서 제외)
- `READ_ONCE_DISABLED=1` 환경변수로 hook 비활성화 지원
- `READ_ONCE_MODE=warn` 모드 추가 (읽기 허용 + JSON 경고 메시지)
- 차단 메시지에 토큰 절약량 표시 (~N 토큰 절약)
- 테스트 5개 추가 (총 19 passed)

## 2026-04-11 #3

- `install_hook.sh`에 설치/제거 선택 메뉴 추가
- jq로 `~/.claude/settings.json` 자동 설정: 설치 시 hook 항목 merge, 제거 시 해당 항목만 필터링 삭제
- 중복 설치 감지 및 settings.json 백업(.bak) 생성
- 기존 수동 안내 방식(`show_settings_snippet`, `show_uninstall_settings_snippet`) 제거
- README.md에 제거 가이드 섹션 추가

## 2026-04-11 #2

- 플러그인 → hook 배포 방식 전환: `plugins/akbun-readonce/` → `hooks/readonce/`
- `install_hook.sh` 대화형 설치 스크립트 추가, settings.json은 수동 안내 방식
- hook 규격 정의: `install/settings.json` + `scripts/` 구조로 통일

## 2026-04-11 #1

- readonce hook 생성: 미변경 파일 재읽기 방지 (mtime/sha256 기반 캐싱)
- Hook 3개 구현: PreToolUse(Read), PostToolUse(Read), SessionStart
- /clear, compact 시 캐시 초기화, startup 시 7일 이상 된 캐시 정리
