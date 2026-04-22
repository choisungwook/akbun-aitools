# Agent Guide

## requirements

만약 너가 claude.ai에 실행한 claude code라면 plugin을 설치하여 skills을 확인하고 설치한다. claude.ai가 아닌 로컬이라면 plugin이 설치되어 있다고 가정한다.

```bash
/plugin marketplace add choisungwook/akbun-aitools
/plugin install akbun-writing@akbun-aitools
```

## 플러그인 이력관리

- 플러그인 작업 내용은 ./plugins/{플러그인이름}/{plugin resource, ex: skills}/docs/changelog.md에 있다. 만약 없다면 아래 규칙으로 작성해라. 작업내용은 리스트형식으로 5개를 넘지 않도록 한다.

```sh
## {날짜} #{번호}

- 작업내용 1
- 작업내용 2
```

## hook 생성 규칙

- hook은 `hooks/{hook이름}/` 디렉터리에 생성한다.
- `hooks/{hook이름}/install/settings.json`에 사용자가 `~/.claude/settings.json`에 추가할 hook 설정을 정의한다.
- `hooks/{hook이름}/scripts/`에 hook이 실행할 shell 스크립트를 배치한다. `install_claude_hook.sh`는 이 디렉터리의 `.sh` 파일을 `$HOME/.claude/hooks/{hook이름}/`으로 복사한다.

## 코드 규칙

- 코드 작성 규칙은 `.claude/rules/`에 정의되어 있다.
