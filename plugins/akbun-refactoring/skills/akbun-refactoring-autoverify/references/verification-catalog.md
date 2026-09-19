# 검증 카탈로그

검증 매트릭스를 만들 때 대상별로 어떤 검증을 찾는지 정리한 표다. 저장소가 이미 정한 검증이 항상 우선이고, 이 표의 표준 도구는 저장소에 정해진 것이 없을 때만 쓴다.

## 찾는 순서

1. 저장소가 정한 것을 읽는다. 여기 있는 명령을 그대로 쓴다.
   - `.github/workflows/*.yml`의 `run:` 단계
   - `Makefile`, `justfile`, `Taskfile.yml`의 test·lint·check 타깃
   - `package.json`의 `scripts`(test, lint, typecheck, build)
   - `pyproject.toml`, `tox.ini`, `noxfile.py`, `setup.cfg`
   - `.pre-commit-config.yaml`
   - `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`의 검증·테스트 절
2. 없으면 아래 표준 도구 중 저장소에 설치·설정된 것을 쓴다. 설치되지 않은 도구를 새로 깔지 않는다.
3. 둘 다 없으면 `자동 검증 없음`이다.

## 대상별 후보

### 코드

| 감지 파일 | 언어 | 검증 | 명령 예 |
|---|---|---|---|
| `pyproject.toml`, `requirements*.txt` | Python | 테스트 · 린트 · 타입 | `pytest -q` · `ruff check .` · `mypy .` |
| `package.json` | JavaScript/TypeScript | 테스트 · 린트 · 타입 · 빌드 | `npm test` · `npm run lint` · `npx tsc --noEmit` · `npm run build` |
| `go.mod` | Go | 테스트 · 정적 검사 · 포맷 | `go test ./...` · `go vet ./...` · `gofmt -l .` |
| `Cargo.toml` | Rust | 테스트 · 린트 · 포맷 | `cargo test` · `cargo clippy` · `cargo fmt --check` |
| `pom.xml`, `build.gradle*` | Java/Kotlin | 테스트 · 빌드 | `mvn -q test` · `./gradlew test` |
| `*.sh` | Shell | 문법 · 정적 검사 | `bash -n <file>` · `shellcheck <file>` |

### 문서

| 대상 | 검증 | 명령 예 |
|---|---|---|
| `*.md` | 마크다운 규칙 | `markdownlint <path>` (`.markdownlint.json`이 있으면 그 설정) |
| `*.md` | 코드 블록 언어 표기 | 저장소 hook이 있으면 그 스크립트, 없으면 `` ^``` `` 뒤 언어 없는 줄 grep |
| `*.md` | 내부 링크 존재 | 링크 대상 파일·헤더가 존재하는지 확인. `lychee --offline <path>` 또는 스크립트 |
| 문서 사이트 | 빌드 | `mkdocs build --strict` · `npm run build` |

문서의 사실·수치·절차 순서가 맞는지는 자동 검증이 아니다. 그 변경은 사람 항목이다.

### 설정·인프라 코드

| 대상 | 검증 | 명령 예 |
|---|---|---|
| `*.json` | 파싱 | `python3 -c 'import json,sys; json.load(open(sys.argv[1]))' <file>` |
| `*.yaml`, `*.yml` | 파싱 | `python3 -c 'import yaml,sys; yaml.safe_load(open(sys.argv[1]))' <file>` |
| JSON/YAML + 스키마 | 스키마 검사 | `check-jsonschema --schemafile <schema> <file>` |
| `*.tf` | 문법 · 포맷 | `terraform validate` · `terraform fmt -check -recursive` |
| Kubernetes manifest | 스키마 · 서버 검사 | `kubeconform -strict <file>` · `kubectl apply --dry-run=client -f <file>` |
| `Dockerfile` | 린트 | `hadolint Dockerfile` |
| GitHub Actions | 문법 | `actionlint` |

### 이 저장소(akbun-aitools) 자체

| 대상 | 검증 | 명령 예 |
|---|---|---|
| `plugins/*/.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` | 파싱 · 두 파일 버전 일치 | JSON 파싱 후 `version` 비교 |
| `plugins/*/skills/*/SKILL.md` | frontmatter `name`·`description` 존재 | 저장소 `docs/`가 안내하는 validator |
| `*.md` | 코드 블록 언어 표기 | `.claude/hooks/check-codeblock-lang.sh`와 같은 awk 규칙 |

## 기준선 기록 규칙

- 검증마다 변경 전 결과를 `통과` · `실패 N건` · `실행 불가(이유)` 중 하나로 적는다.
- `실행 불가`는 도구 미설치, 네트워크 필요, 자격 증명 필요가 대표적이다. 이 경우 그 대상은 `자동 검증 없음`과 같이 취급한다.
- 기준선 실패는 사람 항목 `기준선 실패`로 옮기고 변경 대상에서 고치지 않는다.
