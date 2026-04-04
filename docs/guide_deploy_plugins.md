# Claude marketplace에 plugin 배포하기

> ref: <https://code.claude.com/docs/en/plugin-marketplaces>

## plugin이란

plugin은 skills, subagents, MCP servers, hooks를 묶어서 배포하는 단위다.
`/plugin` 명령어로 설치하거나 비활성화할 수 있다.

## plugin.json vs marketplace.json

| | plugin.json | marketplace.json |
|---|---|---|
| 위치 | `.claude-plugin/plugin.json` (plugin root) | `.claude-plugin/marketplace.json` (repo root) |
| 역할 | plugin 1개의 메타데이터 | plugin 카탈로그 (여러 plugin 목록) |
| 비유 | 앱 1개의 정보 | 앱스토어 |
| 필수 여부 | plugin마다 1개 | GitHub 배포 시 필요 |

## plugin 디렉토리 구조

```
my-marketplace/                         ← marketplace root
├── .claude-plugin/
│   └── marketplace.json                ← 카탈로그: plugin 목록과 위치 정의
├── plugins/
│   └── my-plugin/                      ← plugin root
│       ├── .claude-plugin/
│       │   └── plugin.json             ← plugin 메타데이터 (name, version, author)
│       ├── skills/<name>/SKILL.md      ← skills
│       ├── agents/<name>.md            ← subagents
│       └── hooks/
│           ├── hooks.json              ← hook 설정
│           └── *.sh                    ← hook 스크립트
```

컴포넌트(`skills/`, `agents/`, `hooks/`)는 반드시 **plugin root**에 위치해야 한다. `.claude-plugin/` 안에 넣으면 안 된다.

## strict mode

marketplace.json의 plugin entry에서 `strict` 필드로 컴포넌트 정의 권한을 제어한다.

| 값 | 동작 |
|---|---|
| `true` (기본값) | `plugin.json`이 컴포넌트를 정의한다. marketplace entry는 보충만 가능 |
| `false` | marketplace entry가 전체를 정의한다. plugin.json에 컴포넌트가 있으면 충돌 에러 |

대부분의 경우 `strict: true`(기본값)를 사용하면 된다. plugin이 자체 `plugin.json`을 가지고 있으면 marketplace entry에서 skills/hooks/agents 경로를 지정할 필요가 없다.

## plugin marketplace

누구나 marketplace를 호스팅할 수 있다. `.claude-plugin/marketplace.json`이 포함된 git repo면 된다.

marketplace.json 예시:

```json
{
  "name": "my-marketplace",
  "owner": { "name": "your-name" },
  "metadata": { "description": "My plugins", "version": "1.0.0" },
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./plugins/my-plugin",
      "description": "What this plugin does"
    }
  ]
}
```

## marketplace에서 설치

```bash
/plugin marketplace add user-or-org/repo-name
/plugin install plugin-name@marketplace-name
```

## 업데이트

```bash
claude plugin marketplace update marketplace-name
claude plugin update plugin-name@marketplace-name
```

## 로컬 테스트

```bash
claude plugin validate .
claude --plugin-dir ./plugins/my-plugin
```

## 참고 문서

- plugin 만들기: <https://code.claude.com/docs/en/plugins>
- plugin 레퍼런스: <https://code.claude.com/docs/en/plugins-reference>
- marketplace 배포: <https://code.claude.com/docs/en/plugin-marketplaces>
