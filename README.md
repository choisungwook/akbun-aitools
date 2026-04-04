# akbun-aitools

This repository manages AI tools used by akbun.

## Install

```bash
/plugin marketplace add choisungwook/akbun-aitools
/plugin install akbun-skills@akbun-aitools
```

## Scripts

### install_aitools.sh

플러그인을 로컬 환경에 설치하는 스크립트. 두 가지 방법을 제공한다.

- **Plugin install**: Claude Code `/plugin` 명령어 안내 (권장)
- **Direct install**: `plugins/akbun-skills/`의 skills, agents, hooks, rules를 `~/.claude/`로 직접 복사

```bash
./install_aitools.sh
```

### sync_to_repo.sh

`~/.claude/`에서 개발한 skill과 agent를 이 repo로 동기화하는 스크립트. **akbun 본인만 사용한다.**

`akbun-` prefix가 붙은 항목만 `plugins/akbun-skills/`로 복사한다. 워크플로우: `~/.claude/`에서 로컬 개발/테스트 후, 이 스크립트로 repo에 반영하고 git push로 배포한다.

```bash
./sync_to_repo.sh
```
