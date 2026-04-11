# akbun-aitools

Claude Code plugin marketplace for akbun tools.

## Plugin 설치

marketplace를 등록한 후 원하는 plugin을 설치한다.

```bash
/plugin marketplace add choisungwook/akbun-aitools
```

사용 가능한 plugin 목록:

```bash
/plugin install akbun-writing@akbun-aitools
/plugin install akbun-learning@akbun-aitools
```

설치 후 세션을 새로고침한다.

```bash
/reload-plugins
```

## Hook 설치

plugin이 아닌 hook 방식으로 배포되는 도구는 `install_hook.sh`로 설치한다.

```bash
git clone https://github.com/choisungwook/akbun-aitools.git
cd akbun-aitools
bash install_hook.sh
```

사용 가능한 hook 목록:

| hook | 설명 |
|---|---|
| `readonce` | 같은 세션에서 변경되지 않은 파일의 반복 Read를 차단 |
