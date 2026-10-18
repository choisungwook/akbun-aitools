# akbun-aitools 리뷰 지침

## 이 지침의 구조

- 이 파일에는 저장소 전체에 적용되는 규칙만 둔다.
- 특정 경로나 주제에만 적용되는 규칙은 `.github/instructions/<주제>.instructions.md`에 둔다. 파일 맨 위 `applyTo`에 적용할 경로 glob을 적는다.
- 주제 파일은 모두 같은 틀을 쓴다: `## 적용 대상`(언제 이 파일을 적용하는지 한두 줄) → `## 지적한다`(필요하면 `###` 소주제로 나눔) → `## 지적하지 않는다`.
- 규칙은 한 줄에 하나, "무엇이 있으면/없으면 지적한다" 형태로 쓴다. 판단에 숫자가 필요하면 숫자를 적는다.
- 새 기준이 생기면 맞는 주제 파일에 한 줄을 더한다. 맞는 주제가 없으면 같은 틀로 새 주제 파일을 만들고 아래 목록에 한 줄을 더한다. 파일 이름·숫자로 판정할 수 있는 기준은 여기가 아니라 `scripts/`의 검사로 간다.

| 주제 파일 | 다루는 것 |
|---|---|
| `style-skills.instructions.md` | 그림·영상 스타일 skill의 참고 자료 흔적, 모방, 모델 독립성 |
| `video-rendering.instructions.md` | 영상을 렌더하거나 편집기 타임라인에 놓는 skill의 출력 형식·fps·원본 보존 |
| `skill-scripts.instructions.md` | skill 스크립트의 의존성, 자체 검사, 프레임 처리 |
| `repo-config.instructions.md` | workflow, 검사 스크립트, agent 규칙 문서 같은 리스크 등급 높음 경로 |

## 리뷰 방식

- 리뷰 코멘트는 한국어로 쓴다.
- 요약 첫 줄은 지적 건수다. 예: "지적 2건(중요 1, 사소 1)". 고칠 것이 없으면 "고칠 것 없음"이라고 쓴다.
- 지적마다 근거를 파일과 줄로 든다. 근거를 못 대는 추측("~일 수도 있음", "확인해 보세요")은 쓰지 않는다.
- 지적마다 등급을 하나 붙인다. `중요`: 머지 전에 고쳐야 함. `사소`: 안 고쳐도 됨, PR당 3개까지. `기존`: 이 PR이 만든 문제가 아님. 기존 문제를 중요로 올리지 않는다.
- 같은 부류의 문제가 여러 곳이면 부류를 한 번 설명하고 위치를 전부 나열한다. 한 곳만 지적하고 나머지를 남기지 않는다.
- 이미 올린 지적을 새 커밋에서 반복하지 않는다. 재리뷰는 마지막 리뷰 이후 커밋의 diff만 본다.
- 스타일·취향·정리 제안·이름 바꾸기 제안은 쓰지 않는다. `imgs/`와 이미지·영상 바이너리는 보지 않는다.

## 이 저장소에서 버그란

이 저장소는 Claude Code·Codex 플러그인 skill 모음이다. 실행 지침의 원본은 각 `plugins/<plugin>/skills/<skill>/SKILL.md`다. 문서가 주 산출물이므로 버그는 코드가 아니라 문서가 틀리는 모양으로 나타난다.

- `SKILL.md`가 거짓말한다: 설명하는 옵션·키·단계가 같은 skill의 `scripts/`·`references/`에 없거나 다르게 동작하면 지적한다.
- 문서끼리 어긋난다: 같은 값이 표와 본문에서 다르거나, `README.md`·`docs/`가 `SKILL.md`와 다른 이름·흐름을 말하면 지적한다.
- PR 본문이 diff와 다르다: 아래 `## PR 본문`.
- `Validate PR`·`Validate editvideo` CI가 이미 검사하는 것(manifest version 일치와 +1, frontmatter `name`, `README.md` 목록, PR 본문 구조·등급, `akbun-editvideo`의 깨진 로컬 링크)은 다시 지적하지 않는다. 다른 plugin의 깨진 로컬 링크는 CI가 보지 않으므로 지적한다. CI가 못 보는 의미상의 어긋남에 집중한다.

## PR 본문

PR 본문은 `.github/pull_request_template.md` 구조(`# 구현`, `# 구조`, `# 검증`, `# 리스크`)다. diff와 대조한다.

- `# 구현` 첫 줄이 diff에서 가장 큰 변경과 다르면 지적한다. 예: 본문은 설명 수정이라는데 diff는 스크립트 동작을 바꿈.
- `# 구조`의 mermaid 노드가 저장소에 없는 파일을 가리키거나, diff에서 바뀐 주요 파일(스크립트, SKILL.md, workflow)이 그림에 없으면 지적한다. 노드가 12개를 넘거나 `changed` 표시가 diff와 다르면 지적한다.
- `# 검증` 표의 대상·방법이 diff에서 바뀐 것과 안 맞으면 지적한다.
- diff에 `scripts/**/*.py`나 skill의 `scripts/` 파일이 있는데 `# 검증`에 그 검사(`--selftest`, `test_*.py`)를 돌린 줄이 없으면 지적한다.
- diff가 `SKILL.md`의 동작·수치·흐름을 바꿨는데 `# 검증`에 실제 입력으로 실행한 줄이 없고 "검증하지 않음"도 없으면 지적한다.
- `# 검증` 표의 결과 칸이 "통과", "확인함"처럼 출력 없이 판정만이면 지적한다.
- `# 리스크`의 못 보는 것 줄이 "없음"인데 diff가 `SKILL.md`의 동작·수치·흐름을 바꿨으면 지적한다. 동작 변경은 실행해야만 알 수 있는 것이 남는다.

## skill 추가·삭제·이동

- 새 `SKILL.md` frontmatter에 `disable-model-invocation: true`가 없으면 지적한다. 다른 skill이 참조하는 기준 skill이거나 PR 본문에 자동 호출을 허용한 이유가 있으면 예외다.
- skill을 추가했는데 그 plugin의 `.codex-plugin/plugin.json` `interface.defaultPrompt`에 그 skill을 부르는 예시 한 줄이 없으면 지적한다.

## 플러그인별 규칙

플러그인마다 따로 지켜야 하는 규칙이다. 새 플러그인 규칙은 이 목록에 한 줄로 더한다.

- `akbun-editvideo`: skill의 동작·흐름이 바뀌었는데 `docs/manual_editvideo.md`와 `docs/terms_editvideo.md`가 같은 PR에서 바뀌지 않았으면 지적한다.
- `akbun-draw`: SVG `<text>`의 `font-family`에 SIL OFL이 아닌 글꼴(유료·상용·라이선스 불명)이 있으면 지적한다.

## Markdown

- H1(`#`)은 문서 맨 위 제목 하나만 쓴다. 나머지 섹션은 H2(`##`)부터 시작한다. `.github/pull_request_template.md`와 PR 본문은 예외다.
- 코드블록 바로 위에 그 코드가 무엇인지 설명하는 문장이 없으면 지적한다.
- 코드블록에 언어(`bash`, `json`, `yaml`, `python`, `text` 등)가 없으면 지적한다.

## 개인정보

- 사용자 홈 절대 경로(`/Users/<이름>/`, `/home/<이름>/`, `C:\Users\<이름>\`), 이메일 주소, API 키·토큰이 skill·문서·스크립트에 들어가면 지적한다. 경로는 `~/`나 `<작업명>` 같은 자리표시자로 쓴다.
