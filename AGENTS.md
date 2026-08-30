# AGENTS.md

## 목적

Agent는 skill을 수정하면서 다음 agent가 덜 헤매도록 각 skill의 LLM wiki에 안정적인 맥락과 중요한 결정만 최소한으로 남긴다.

## 파일 구조

각 skill은 자체 LLM wiki를 둔다. 새 wiki는 `templates/llm-wiki/`를 기준으로 만든다.

```text
plugins/<plugin-name>/skills/<skill-name>/
  SKILL.md
  wiki/
    index.md
    architecture.md
    development.md
    adr/                 # 조건을 충족하는 결정이 있을 때만 생성
      0001-slug.md
```

wiki는 사람이 읽는 사용자 문서가 아니라 다음 agent가 skill을 유지보수하기 위한 맥락이다. 모든 wiki 문서는 간결한 영어로 작성한다. 실행 시 지침의 원본은 항상 `SKILL.md`이며, wiki가 실행 지침을 복제하거나 일반 사용자 요청에서 반드시 로드되도록 만들지 않는다.

## 플러그인 변경 규칙

`plugins/<plugin-name>/` 아래에서 skill이나 agent를 추가, 수정, 삭제하면 사용자가 따로 말하지 않아도 해당
plugin의 버전을 올린다. 사용자에게 버전 업데이트 여부를 묻지 않는다.

- 버전을 올리는 파일: `plugins/<plugin-name>/.claude-plugin/plugin.json`, `plugins/<plugin-name>/.codex-plugin/plugin.json`
- 두 파일의 `version`은 항상 동일하게 맞춘다.
- 기본은 patch 증가(예: `1.0.14` -> `1.0.15`). 새 skill/agent 추가도 patch로 본다. 동작이 크게 바뀌거나
  호환이 깨지면 minor 증가.
- 버전은 **배포된 마지막 버전에서 +1** 한 값이다. 한 PR/작업 안에서 같은 plugin을 여러 번 고쳐도 매번
  올리지 않는다. 기준점은 `origin/main`의 현재 `version`이며, 그 값에서 한 번만 올린다(예: main이 `1.0.20`
  이면 이번 작업은 몇 번을 수정하든 `1.0.21`). 이미 이번 작업에서 올려둔 상태로 추가 수정이 생기면 번호를
  더 올리지 말고 그대로 둔다.
- skill을 새로 추가하면, 해당 plugin manifest의 `interface.defaultPrompt`에 그 skill을 부르는 예시 한 줄을 추가한다.
- skill을 새로 만들면 `SKILL.md` frontmatter에 `disable-model-invocation: true`를 기본으로 넣는다. 모델이
  알아서 부르지 않고 사용자가 직접 호출할 때만 실행되게 한다. 다른 skill이 참조하는 기준 skill이거나
  사용자가 자동 호출을 요청한 경우에만 뺀다.
- plugin을 추가/삭제하거나 plugin 아래 skill을 추가/삭제하면 `README.md`의 `## plugin 목록` 섹션도 함께 갱신한다.
  plugin이 추가되면 해당 plugin의 `### <plugin-name>` 하위 섹션과 skill 표를 만들고, 삭제되면 그 섹션을 지운다.
  skill이 추가/삭제되면 해당 plugin 표에서 한 줄짜리 설명 행을 추가/삭제한다. `docs/` 같이 `SKILL.md`가 없는 디렉터리는 목록에 넣지 않는다.
- marketplace의 description/category가 바뀐 경우에만 `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`도 함께 수정한다.
- 배포 절차 상세는 `docs/guide_deploy_plugins.md`를 따른다.

## 이미지 작업 규칙

사용자가 참고 이미지를 주며 그리기(프롬프트·SVG·일러스트 등)를 요청하면, 목표는 **원본을 따라 그리는 것이
아니라 스타일을 찾아내는 것**이다.

- 참고 이미지에서 재사용 가능한 스타일 요소를 추출한다: 레이아웃과 상하좌우 간격, 색 팔레트, 선·형태의
  그림 언어, 타이포그래피, 여백.
- 추출한 스타일은 어떤 주제가 와도 적용할 수 있는 일반 규칙(비율, 좌표, 색 값 등)으로 기록한다.
- 원본의 피사체·장면·문구를 복제하지 않는다. 예시가 필요하면 원본과 다른 주제로 만든다.
- 산출물(skill, 문서 등)에 참고 이미지 자체나 그 출처 맥락을 넣지 않는다.
- "~를 그려줘" 요청을 처리하는 skill을 새로 만들 때도 같은 원칙으로 설계한다. 특정 구도가 아니라
  그림체·색감(스타일)을 고정하고, 무엇을 그릴지(소재·구도)는 입력에 맞춰 자유롭게 정하도록 만든다.
  gold reference 예시는 참고 이미지와 다른 구도로 만들어 스타일이 소재와 무관하게 재사용됨을 보인다.
- Figma/Canva 편집이 필요하면 이미지 프롬프트와 함께, 기본 요소만 쓰고 텍스트를 편집 가능한 `text`로
  남긴 SVG를 만든다. SVG 폰트는 저작권 없는 폰트를 사용한다(예: SIL OFL).

## Pull Request 작성 규칙

- PR 설명은 한국어로 쓴다.
- `.github/pull_request_template.md`의 H1 구조(`# 구현`, `# 어려웠던 점`, `# 리스크`)를 따른다.
- 개조식으로 쓰고 문장은 명사 또는 `-음`, `-함`으로 끝낸다.
- `구현`과 기록용 Issue 링크는 항상 남긴다. 내용이 없는 `어려웠던 점`과 `리스크`는 헤더째 삭제한다.
- 목표와 의사결정은 기록용 Issue에 두고 PR에는 링크만 남긴다. PR에는 실제 구현에서 겪은 어려움과 감수하는 리스크만 적는다.
- 각 섹션은 요약 한 줄과 필요한 경우 근거 목록 하나까지만 사용한다.

## 시작 절차

skill 작업을 시작할 때 해당 skill의 `wiki/index.md`를 먼저 읽는다.

읽는 순서:

1. `/AGENTS.md`
2. `plugins/<plugin-name>/skills/<skill-name>/wiki/index.md`
3. `index.md`가 안내하는 `architecture.md`, `development.md`
4. 관련 결정 기록과 domain 문서, 변경에 필요할 때만
5. `SKILL.md`와 변경 대상 supporting resource

`wiki/index.md`가 없는 기존 skill은 `templates/llm-wiki/`로 wiki를 만든 뒤 작업한다. wiki 전체를 무조건 읽지 않고 `index.md`의 read order와 현재 변경 범위에 따라 필요한 문서만 읽는다.

## 세션 중 원칙

### 용어 충돌 확인

사용자 표현이 skill wiki의 용어와 충돌하면 즉시 지적한다. 질문하지 말고 충돌 내용을 명확히 적고, repo 기준의 권장 용어를 제시한다.

예:

```text
용어 정리에서는 cancellation을 주문 전체 취소로 정의한다. 현재 설명은 주문 항목 취소에 가깝다. 권장 용어는 order item cancellation이다.
```

### 모호한 용어 정리

사용자가 모호하거나 여러 의미로 쓰이는 단어를 사용하면 표준 용어를 제안한다. 확정 가능한 경우 해당 skill의 `wiki/architecture.md` 또는 별도 domain 문서에 바로 반영한다.

예:

```text
account는 의미가 모호하다. 결제 주체는 Customer, 로그인 주체는 User로 구분한다.
```

### 구체적 시나리오로 검증

도메인 관계, 경계, 예외 처리가 모호하면 구체적 시나리오로 검증한다. 결과는 질문이 아니라 권장 해석과 가정으로 정리한다.

예:

```text
시나리오: 주문은 생성됐지만 결제 승인에 실패했다. 이 경우 주문 실패가 아니라 결제 실패 상태의 주문으로 보는 것이 자연스럽다.
```

### 코드와 교차 확인

사용자가 동작 방식을 설명하면 코드, 설정, 문서가 같은지 확인한다. 충돌하면 바로 말하고 repo 기준의 권장 해석을 제시한다.

예:

```text
코드는 주문 전체 취소만 지원한다. 부분 취소 가능하다는 설명과 충돌한다. 현재 기준은 주문 전체 취소로 본다.
```

### 질문 최소화

self-improving 목적에서는 질문보다 repo 근거, 코드 확인, 가정 명시를 우선한다.

질문하지 않는 경우:

- repo에서 확인 가능
- 코드 기준으로 판단 가능
- 안전한 가정을 명시하고 진행 가능
- 용어 정리만 필요한 경우

질문하는 경우:

- 작업 진행이 불가능함
- 선택에 따라 결과가 크게 달라짐
- repo와 사용자 요구가 충돌하고 임의 선택이 위험함

## LLM wiki 작성 규칙

기본 문서 역할:

- `index.md`: wiki 목적, 읽는 순서, 문서 색인
- `architecture.md`: skill 책임, 경계, 안정적인 흐름, resource 소유 관계, 확정된 용어
- `development.md`: 수정 순서, 검증 방법, wiki 갱신 조건
- 추가 domain 문서: `architecture.md`가 과도하게 길어질 때만 생성
- `adr/`: 결정 기록 조건을 모두 충족할 때만 생성

규칙:

- 영어로 작성한다.
- 확정된 책임, 경계, 용어, resource 관계와 장기 caveat만 기록한다.
- `SKILL.md`, `references/`, `design.md`, `README.md` 내용을 복제하지 않고 링크한다.
- 스펙, 작업 로그, 구현 세부사항, 임시 메모, 일반 지식은 넣지 않는다.
- runtime behavior가 바뀌면 `SKILL.md`를 먼저 수정하고 wiki가 그 변경과 충돌하지 않게 갱신한다.

## 결정 기록 규칙

중요한 결정은 관련 skill의 `wiki/adr/`에 둔다. 첫 결정 기록이 필요할 때만 디렉터리를 만든다.

파일명:

```text
0001-slug.md
0002-slug.md
```

결정 기록은 아래 3개가 모두 참일 때만 만든다.

1. 되돌리기 어렵다.
2. 맥락 없이는 이상해 보인다.
3. 실제 트레이드오프가 있었다.

하나라도 아니면 결정 기록을 만들지 않는다.

결정 기록 형식:

```md
# {결정 제목}

## Decision

{결정을 간결한 영어로 작성}

## Reason

{이유와 실제 trade-off를 간결한 영어로 작성}
```

## Self-Improving 규칙

작업 중 또는 작업 종료 시 다음을 판단한다.

skill wiki 갱신 조건:

- 새 용어 확정
- 기존 용어 의미 변경
- 사용자 표현과 repo 용어 충돌 발견
- 다음 agent가 헷갈릴 가능성이 높은 용어 발견
- skill 책임, 경계, 안정적인 흐름, resource 소유 관계가 변경
- 다음 작업에도 남는 caveat가 발생

결정 기록 생성 조건:

- 되돌리기 어려움
- 맥락 없이는 이상해 보임
- 실제 트레이드오프 존재

갱신하지 않는 조건:

- 일회성 작업
- 단순 문구 수정
- 구현 세부사항
- 임시 디버깅 기록
- 다음 작업에 영향 없는 사실

## 압축 규칙

wiki 압축 조건:

- 용어 정리 20개 초과
- 오래된 용어 포함
- 중복 정의 포함
- `SKILL.md`나 supporting resource 설명을 반복

압축 방법:

1. 현재 유효한 용어만 유지
2. 중복 용어 병합
3. 구현 세부사항 삭제
4. 실행 지침은 `SKILL.md`로, 상세 규칙은 기존 supporting resource로 연결
5. 중요한 결정은 조건 충족 시 `wiki/adr/`로 분리

## 완료 전 확인

- 모호한 용어를 그대로 넘기지 않았는가?
- 코드와 사용자 설명의 충돌을 확인했는가?
- 확정된 용어와 바뀐 경계를 해당 skill wiki에 반영했는가?
- `SKILL.md`와 wiki가 충돌하지 않는가?
- 결정 기록은 세 조건을 모두 만족할 때만 만들었는가?
