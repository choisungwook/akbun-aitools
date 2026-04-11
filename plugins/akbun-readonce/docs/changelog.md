# Changelog

## 2026-04-11

- ReadOnce plugin 생성: 미변경 파일 재읽기 방지 (mtime/sha256 기반 캐싱)
- Hook 3개 구현: PreToolUse(Read), PostToolUse(Read), SessionStart
- 캐시 저장소: transcript 경로 기반 세션별 고유 JSON 파일
- /clear, compact 시 캐시 자동 초기화, startup 시 7일 이상 된 캐시 정리
