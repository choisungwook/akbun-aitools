# akbun-aitools 리뷰 지침

## 이 지침의 구조

- 이 파일에는 저장소 전체에 적용되는 규칙만 둔다.
- 특정 경로나 주제에만 적용되는 규칙은 `.github/instructions/<주제>.instructions.md`에 둔다. 파일 맨 위 `applyTo`에 적용할 경로 glob을 적는다.
- 주제 파일은 모두 같은 틀을 쓴다: `## 적용 대상`(언제 이 파일을 적용하는지 한두 줄) → `## 지적한다`(필요하면 `###` 소주제로 나눔) → `## 지적하지 않는다`.
- 규칙은 한 줄에 하나, "무엇이 있으면/없으면 지적한다" 형태로 쓴다. 판단에 숫자가 필요하면 숫자를 적는다.
- 새 기준이 생기면 맞는 주제 파일에 한 줄을 더한다. 맞는 주제가 없으면 같은 틀로 새 주제 파일을 만들고 아래 목록에 한 줄을 더한다.

| 주제 파일 | 다루는 것 |
|---|---|
| `style-skills.instructions.md` | 그림·영상 스타일 skill의 참고 자료 흔적, 모방, 모델 독립성 |
| `video-rendering.instructions.md` | 영상을 렌더하거나 편집기 타임라인에 놓는 skill의 출력 형식·fps·원본 보존 |
| `skill-scripts.instructions.md` | skill 스크립트의 의존성, 자체 검사, 프레임 처리 |

## 공통

- 리뷰 코멘트는 한국어로 쓴다.
- 이 저장소는 Claude Code·Codex 플러그인 skill 모음이다. 실행 지침의 원본은 각 `plugins/<plugin>/skills/<skill>/SKILL.md`다. 문서가 주 산출물이므로 문서끼리, 문서와 스크립트가 어긋나는 것도 버그로 지적한다.
- CI가 이미 검사하는 형식 오류(frontmatter 키, README 목록 누락, 깨진 로컬 링크)보다 CI가 잡지 못하는 의미상의 어긋남에 집중한다.

## 플러그인 버전

- `plugins/<plugin>/` 아래 skill·agent·script·reference가 바뀌었는데 `plugins/<plugin>/.claude-plugin/plugin.json`과 `plugins/<plugin>/.codex-plugin/plugin.json`의 `version`이 그대로면 지적한다.
- 두 manifest의 `version`이 서로 다르면 지적한다.
- 한 PR에서 base 브랜치 값보다 patch를 2 이상 올렸으면 지적한다(예: `1.0.15` → `1.0.17`). 한 PR은 한 번만 올린다.

## skill 추가·삭제·이동

- 새 `SKILL.md` frontmatter에 `disable-model-invocation: true`가 없으면 지적한다. 다른 skill이 참조하는 기준 skill이면 예외다.
- frontmatter `name`이 skill 디렉터리 이름과 다르면 지적한다.
- skill을 추가·삭제·이동했는데 `README.md`의 `## plugin 목록` 표가 함께 바뀌지 않았으면 지적한다.
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
