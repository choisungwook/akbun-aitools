# akbun-aitools

akbun tools for both Claude Code and Codex plugin workflows.

## Claude Code

Claude Code marketplace metadata lives in:

- `.claude-plugin/marketplace.json`
- `plugins/<plugin-name>/.claude-plugin/plugin.json`

기존 설치 방식은 그대로 유지한다.

```bash
/plugin marketplace add choisungwook/akbun-aitools
/plugin install akbun-writing@akbun-aitools
/plugin install akbun-learning@akbun-aitools
/reload-plugins
```

## Codex

Codex plugin 설치 명령어

```bash
codex plugin marketplace add choisungwook/akbun-aitools --json
codex plugin add akbun-learning@akbun-aitools --json
codex plugin add akbun-writing@akbun-aitools --json
```

Codex plugin 업그레이드

아래 예시는 `akbun-writing` 기준이다. 다른 plugin은 plugin selector만 바꾼다.

옵션 1: marketplace snapshot을 먼저 갱신하고 plugin을 다시 추가한다. 일반적인 업데이트에는 이 방법을 우선 사용한다.

```bash
codex plugin marketplace upgrade akbun-aitools --json
codex plugin add akbun-writing@akbun-aitools --json
```

- 장점: 설치 상태를 크게 흔들지 않고 최신 marketplace 기준으로 plugin을 다시 맞춘다.
- 단점: 기존 설치 상태(에: 캐시)가 꼬여 있으면 문제가 남을 수 있다.

옵션 2: 기존 plugin을 제거한 뒤 다시 추가한다. 설치 상태가 꼬였거나 옵션 1로 반영되지 않을 때 사용한다.

```bash
codex plugin remove akbun-writing@akbun-aitools --json
codex plugin add akbun-writing@akbun-aitools --json
```

- 장점: plugin cache와 local config를 깨끗하게 다시 만든다.
- 단점: 기존 plugin 설정이 제거될 수 있다.

Codex plugin metadata lives in:

- `.agents/plugins/marketplace.json`
- `plugins/<plugin-name>/.codex-plugin/plugin.json`

## Hook 설치

plugin이 아닌 hook 방식으로 배포되는 도구는 GitHub Release에서 다운로드하여 설치한다.

```bash
curl -L https://github.com/choisungwook/akbun-aitools/releases/latest/download/akbun-hooks.tar.gz -o akbun-hooks.tar.gz
tar xzf akbun-hooks.tar.gz
bash install_claude_hook.sh
```

사용 가능한 hook 목록:

| hook | 설명 |
|---|---|
| `readonce` (deprecated) | 같은 세션에서 변경되지 않은 파일의 반복 Read를 차단 |
