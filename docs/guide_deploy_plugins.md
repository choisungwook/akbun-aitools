# Claude/Codex plugin 배포 정리

이 저장소의 plugin을 Claude Code와 Codex 양쪽에 맞춰 배포할 때 필요한 작업을 정리합니다.

## 메타데이터 위치

### Claude Code

- repo marketplace: `.claude-plugin/marketplace.json`
- plugin manifest: `plugins/<plugin-name>/.claude-plugin/plugin.json`
- marketplace entry는 `strict: true`로 유지

### Codex

- repo marketplace: `.agents/plugins/marketplace.json`
- plugin manifest: `plugins/<plugin-name>/.codex-plugin/plugin.json`
- marketplace entry는 `policy.installation`, `policy.authentication`, `category`를 항상 포함

## 1. 처음 생성

새 plugin을 처음 만들 때 기본 구조:

```text
plugins/<plugin-name>/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── skills/
└── agents/   # option, currently Claude-oriented docs
```

### 공통 리소스 배치

- skill: `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
- agent: `plugins/<plugin-name>/agents/<agent-name>.md`

### Claude marketplace entry 추가

`.claude-plugin/marketplace.json` 예시:

```json
{
  "name": "akbun-writing",
  "source": "./plugins/akbun-writing",
  "description": "Writing, review, blog, and publishing support skills",
  "strict": true
}
```

### Codex marketplace entry 추가

`.agents/plugins/marketplace.json` 예시:

```json
{
  "name": "akbun-writing",
  "source": {
    "source": "local",
    "path": "./plugins/akbun-writing"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Writing"
}
```

### 로컬 검증

Claude Code 검증:

```bash
claude plugin validate .
claude --plugin-dir ./plugins/<plugin-name>
```

Codex 쪽은 우선 JSON 유효성과 경로 일관성을 확인한다:

- `plugins/<plugin-name>/.codex-plugin/plugin.json`
- `.agents/plugins/marketplace.json`

## 2. 버전 업데이트

기존 plugin 내용을 수정해 다시 배포할 때 순서:

1. 해당 plugin root 아래 리소스 수정
2. 필요하면 양쪽 manifest 버전도 같이 증가

수정 대상:

```text
plugins/<plugin-name>/.claude-plugin/plugin.json
plugins/<plugin-name>/.codex-plugin/plugin.json
```

3. marketplace description/category가 바뀌면 해당 marketplace 파일도 함께 수정
4. 검증 후 커밋, push

Claude 사용자 반영 방식:

```bash
claude plugin marketplace update akbun-aitools
claude plugin update <plugin-name>@akbun-aitools
```

주의:

- third-party marketplace는 auto-update가 기본 비활성화다.
- repo를 push했다고 해서 사용자 쪽 plugin이 자동 반영되지는 않는다.
