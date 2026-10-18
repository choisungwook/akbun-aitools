---
applyTo: ".github/**,AGENTS.md,CLAUDE.md,scripts/**,.claude/**,.claude-plugin/**,.agents/**"
---

# 저장소 규칙·CI 리뷰 지침

## 적용 대상

- GitHub Actions workflow, PR·Issue 템플릿, 리뷰 지침, agent 규칙(`AGENTS.md`, `CLAUDE.md`, `.claude/`), 저장소 검사 스크립트, marketplace manifest.
- 이 경로는 리스크 등급 높음이다. 한 번 틀리면 이후 모든 PR이 영향을 받는다.

## 지적한다

### workflow

- `permissions`가 없거나, job이 쓰지 않는 `write` 권한이 있으면 지적한다.
- `pull_request_target`을 쓰면 지적한다.
- PR 제목·본문·브랜치 이름 같은 `${{ github.event.* }}` 값을 `run:`에 직접 보간하면 지적한다. `env:`로 받아 변수로 써야 한다.
- action 참조가 `@main`·`@master`처럼 움직이는 ref면 지적한다.
- 검사 step에 `continue-on-error: true`가 있으면 지적한다.
- 새 검사를 추가했는데 PR `# 검증`에 일부러 틀린 입력으로 실패시킨 기록이 없으면 지적한다.

### 검사 스크립트

- 검사 조건을 지우거나 약하게 바꿨는데 PR 본문에 이유가 없으면 지적한다.
- 검사 스크립트가 보는 경로 목록(리스크 등급 경로, 검사 대상 glob)이 `AGENTS.md`의 표와 다르면 지적한다.
- 검사를 추가·수정했는데 `test_*.py`에 실패 입력 케이스가 없으면 지적한다.

### 규칙 문서

- 새 규칙에 판정 기준(파일 이름, 숫자, 조건)이 없어 리뷰어마다 다르게 읽히면 지적한다.
- 파일 이름과 숫자로 판정할 수 있는 규칙을 `scripts/` 검사 대신 `AGENTS.md`나 리뷰 지침에 글로만 추가했으면 지적한다.
- 같은 규칙이 `AGENTS.md`, `.github/copilot-instructions.md`, `.github/pull_request_template.md`에 다른 말로 있으면 지적한다.

## 지적하지 않는다

- 한국어 문체, 문장 길이, 주석 안내문의 표현.
- `AGENTS.md`의 절 순서.
