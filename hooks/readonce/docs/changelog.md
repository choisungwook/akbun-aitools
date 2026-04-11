# Changelog

## 2026-04-11 #2

- 플러그인 → hook 배포 방식 전환: `plugins/akbun-readonce/` → `hooks/readonce/`
- `install_hook.sh` 대화형 설치 스크립트 추가, settings.json은 수동 안내 방식
- hook 규격 정의: `install/settings.json` + `scripts/` 구조로 통일

## 2026-04-11 #1

- readonce hook 생성: 미변경 파일 재읽기 방지 (mtime/sha256 기반 캐싱)
- Hook 3개 구현: PreToolUse(Read), PostToolUse(Read), SessionStart
- /clear, compact 시 캐시 초기화, startup 시 7일 이상 된 캐시 정리
