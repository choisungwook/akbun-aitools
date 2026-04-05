# Claude plugin 배포 정리

Claude Code plugin을 배포할 때 필요한 작업을 정리합니다.

## 배포 설정

- marketplace entry는 `strict: true`로 유지

## 1. 처음 생성

새 plugin을 처음 만들 때 순서:

1. plugin root 생성

```text
plugins/<plugin-name>/
├── .claude-plugin/plugin.json
├── skills/
└── agents/   # option
```

2. `plugin.json` 작성

최소 필드:

- `name`
- `description`
- `version`
- `author`
- `repository`
- `license`

3. skill, agent 파일 배치

- skill: `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
- agent: `plugins/<plugin-name>/agents/<agent-name>.md`

4. `.claude-plugin/marketplace.json`에 plugin 추가

예시:

```json
{
  "name": "akbun-writing",
  "source": "./plugins/akbun-writing",
  "description": "Writing, review, blog, and publishing support skills",
  "strict": true
}
```

5. 로컬 검증

```bash
claude plugin validate .
claude --plugin-dir ./plugins/<plugin-name>
```

6. 커밋 후 push

사용자는 아래 순서로 설치한다.

```bash
/plugin marketplace add choisungwook/akbun-aitools
/plugin install <plugin-name>@akbun-aitools
/reload-plugins
```

## 2. 버전 업데이트

기존 plugin 내용을 수정해 다시 배포할 때 순서:

1. 해당 plugin root 아래 리소스 수정

- plugin 내용 수정
- 필요 시 marketplace description 수정

2. plugin 버전 증가

수정 대상:

```text
plugins/<plugin-name>/.claude-plugin/plugin.json
```

3. 검증 후 커밋, push

```bash
claude plugin validate .
```

사용자 반영 방식:

```bash
claude plugin marketplace update akbun-aitools
claude plugin update <plugin-name>@akbun-aitools
```

주의:

- third-party marketplace는 auto-update가 기본 비활성화다.
- repo를 push했다고 해서 사용자 쪽 plugin이 자동 반영되지는 않는다.
