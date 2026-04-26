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
$ codex plugin marketplace add choisungwook/akbun-aitools
$ vi ~/.codex/config.toml
[plugins."akbun-learning@akbun-aitools"]
enabled = true

[plugins."akbun-writing@akbun-aitools"]
enabled = true
```

Codex plugin 업그레이드

```bash
codex plugin marketplace upgrade
```

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
| `readonce` | 같은 세션에서 변경되지 않은 파일의 반복 Read를 차단 |
