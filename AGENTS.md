# AGENTS.md

## 목적

Agent는 이 저장소의 plugin skill을 만들고 유지보수한다. 실행 지침의 원본은 항상 각 skill의 `SKILL.md`다. 세션에서 배운 것은 별도 문서가 아니라 실행 경로에 있는 문서, 즉 관련 `SKILL.md`와 이 파일에 남긴다. 실행 경로에 없는 문서는 읽히지 않고, 읽히지 않는 문서는 갱신되지 않는다.

## 읽는 순서

1. 이 파일 전체.
2. 작업 대상 skill의 `SKILL.md`와 그것이 참조하는 `references/`, `scripts/`.
3. `docs/adr/README.md`의 결정 표. 작업 대상 plugin·skill에 해당하는 결정이 있으면 그 파일까지 읽는다. 결정을 뒤집는 변경은 새 결정 기록 없이 하지 않는다.
4. plugin을 추가·배포하거나 manifest를 만질 때 `docs/guide_deploy_plugins.md`.

`README.md`의 `## plugin 목록`은 사람용 색인이다. 규칙의 원본이 아니다.

## 세션 시작과 끝

- 세션 시작 시 `docs/adr/README.md`를 읽어 이번 작업이 기존 결정과 충돌하는지 확인한다. 이전 작업을 이어갈 때는 `akbun-recall`(akbun-agent-ops)로 맥락을 복원한다. 설치돼 있지 않으면 git 로그와 열린 PR로 직접 복원한다.
- 세션을 끝내기 전에 남길 학습이 있으면 `akbun-reflect`(akbun-agent-ops)를 부른다. 학습의 자리는 셋이다. skill을 쓰다 드러난 빈틈은 그 `SKILL.md`, 매 세션 지켜야 할 규칙은 이 파일, 되돌리기 어려운 결정은 `docs/adr/`. 새 디렉터리나 새 문서를 만들어 남기지 않는다.
- 같은 지시를 두 번째로 쓰고 있다면 그 지시는 텍스트가 아니라 스크립트·검사로 갈 신호다. 규칙을 추가하기 전에 자동 검증으로 바꿀 수 있는지 먼저 본다.

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
- `akbun-editvideo` skill을 추가·수정·삭제하거나 스킬의 사용 흐름을 바꾸면 `docs/manual_editvideo.md`와 `docs/terms_editvideo.md`를 같은 변경에서 함께 갱신한다. 매뉴얼은 상황별 안내·해결하는 문제·동작 요약·스킬 링크를, 용어사전은 관련 용어와 정의를 실제 `SKILL.md`와 일치시킨다.
- `akbun-editvideo` 변경은 `uv run --python 3.12 scripts/validate_editvideo.py`로 frontmatter·문서 목록·링크·manifest·prompt를 검사한다. 공용 `quick_validate.py`가 `disable-model-invocation`을 거부하더라도 필수 키를 삭제하지 않는다.
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

## 작업 기록 흐름

Discussion, Issue, PR을 결정 단계로 나눠 쓴다. 완료 조건을 쓸 수 있으면 Issue, 못 쓰면 Discussion.

| | Discussion | Issue | PR |
|---|---|---|---|
| 단계 | 결정 전 | 결정 후, 작업 전 | 작업 후 |
| 답하는 질문 | 무엇이 문제인가, 대안은 무엇인가 | 왜 하나, 무엇이면 끝인가, 무엇을 골랐나 | 무엇이 달라졌나, 어떻게 증명했나 |
| 여는 조건 | 답을 모름, 대안 2개 이상, 의견이 필요함 | 완료 조건을 쓸 수 있음 | diff가 있음 |
| 끝나는 조건 | 결론이 나서 Issue로 넘어감, 또는 안 하기로 함 | 완료 조건 전부 참, PR 머지 | 머지 또는 닫힘 |
| 남는 것 | 비교 과정, 버린 논거 전체 | 결론 한 묶음(ADR) | 증거 |

Issue의 완료 조건 목록을 PR의 검증 절이 하나씩 답한다. 비교 과정 전체는 Discussion에 두고, Issue ADR에는 결론 한 묶음과 Discussion 링크만 둔다.

1. Discussion 열기. 문제와 후보 대안을 적는다. 카테고리는 아래 표에서 고른다. 완료 조건을 바로 쓸 수 있으면 이 단계를 건너뛴다.
2. 결론 내기. Q&A 카테고리면 답변 채택. 아니면 마지막 코멘트로 "결론:" 한 줄과 버린 대안을 남긴다.
3. Issue 만들기. `.github/ISSUE_TEMPLATE/work-record.md` 형식. Discussion에서 넘어왔으면 Discussion 화면의 "Create issue from discussion"을 쓰고 Why에 Discussion 링크를 둔다. PR보다 먼저 만든다.
4. PR. 본문 끝에 `Closes #<issue>`. `.github/pull_request_template.md` 형식.
5. 머지 후 정리. agent가 머지했으면 아래 규칙대로 Issue를 닫는다. Discussion이 있었으면 PR 링크를 코멘트로 남기고 resolved로 닫는다. 안 하기로 했으면 outdated로 닫고 이유 한 줄.

Discussion 카테고리:

| 카테고리 | 형식 | 용도 |
|---|---|---|
| RFC | Open-ended | 설계 대안 비교. 되돌리기 어려운 결정 전에. 템플릿은 `.github/DISCUSSION_TEMPLATE/rfc.yml` |
| Q&A | Question/Answer | 모르는 것 질문. 답변 채택으로 닫힘 |
| Ideas | Open-ended | 아직 문제 정의도 안 된 아이디어 |
| Weekly | Announcement | github-period-pulse 결과 게시. 주간 보고 누적 |
| Learning | Open-ended | 공부한 내용 기록. 나중에 akbun-writing의 입력 |

### 머지 후 Issue 닫기

agent가 PR을 머지하면 그 PR이 링크한 기록용 Issue를 같은 작업 안에서 닫는다. 사용자에게 닫을지 묻지 않는다.

- PR 본문의 `Closes #<issue>`로 자동으로 닫히는지 머지 직후 확인한다. 열려 있으면 `state_reason: completed`로 직접 닫는다.
- 완료 조건 중 참이 아닌 것이 남았으면 닫지 않고, Issue에 남은 조건을 코멘트로 적고 사용자에게 알린다.
- PR을 머지하지 않고 닫았으면 Issue는 `not_planned`로 닫고 이유 한 줄을 코멘트로 남긴다.
- Discussion에서 넘어온 작업이면 Discussion도 같은 작업 안에서 닫는다(5번).

## Pull Request 작성 규칙

- PR 설명은 한국어로 쓴다. PR body는 리뷰어가 diff를 옆에 두고 1분 안에 읽는 브리핑이고, squash 커밋 본문이 된다. 40줄 이내.
- `.github/pull_request_template.md`의 H1 구조(`# 구현`, `# 검증`, `# 어려웠던 점`, `# 리스크`)를 따른다. PR body는 `.claude/rules/markdown.md`의 헤더 규칙 대상이 아니다.
- 개조식으로 쓰고 문장은 명사 또는 `-음`, `-함`으로 끝낸다.
- `구현`, `검증`, 기록용 Issue 링크(`Closes #<issue>`)는 항상 남긴다. 내용이 없는 `어려웠던 점`과 `리스크`는 헤더째 삭제한다.
- `구현` 첫 줄은 사용자(또는 이 코드를 쓰는 동료)에게 무엇이 달라지는지 한 줄. 근거는 실제 파일·함수 이름 한 줄. 이름을 바꾸거나 옮겼으면 전후 이름 모두.
- `검증`은 실제로 돌린 것마다 "무엇을 → 결과" 한 줄. 수치는 전 → 후와 단위. Issue의 완료 조건을 하나씩 답한다. 돌리지 않은 것은 "검증하지 않음"으로 적는다. "통과"만 쓰지 않는다.
- `어려웠던 점`은 막힌 지점 한 줄. 버린 방법과 그 판단 근거가 된 수치를 근거 한 줄.
- `리스크`는 머지하면 감수하는 것 한 줄. 누가 언제 영향을 받는지, 문제를 어떻게 알아채고 되돌리는지 근거 한 줄.
- 왜 하는지와 의사결정은 기록용 Issue에 두고 PR에는 링크만 남긴다.
- 각 섹션은 요약 한 줄과 필요한 경우 근거 목록 하나까지만 사용한다.
- 쓰지 않는 것: 커밋 SHA 나열, 파일별 체크리스트, 로그·메트릭 표 붙여넣기, "완벽"·"문제없음" 같은 판정어, Summary·Test plan 보일러플레이트. diff와 실제로 돌린 결과에서만 쓰고 기억이나 계획으로 쓰지 않는다.

## 세션 중 원칙

### 용어 충돌 확인

사용자 표현이 해당 skill `SKILL.md`의 용어와 충돌하면 즉시 지적한다. 질문하지 말고 충돌 내용을 명확히 적고, repo 기준의 권장 용어를 제시한다.

예:

```text
용어 정리에서는 cancellation을 주문 전체 취소로 정의한다. 현재 설명은 주문 항목 취소에 가깝다. 권장 용어는 order item cancellation이다.
```

### 모호한 용어 정리

사용자가 모호하거나 여러 의미로 쓰이는 단어를 사용하면 표준 용어를 제안한다. 확정 가능한 경우 해당 skill의 `SKILL.md`(용어 절이 없으면 새 절)에 바로 반영한다.

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

질문보다 repo 근거, 코드 확인, 가정 명시를 우선한다.

질문하지 않는 경우:

- repo에서 확인 가능
- 코드 기준으로 판단 가능
- 안전한 가정을 명시하고 진행 가능
- 용어 정리만 필요한 경우

질문하는 경우:

- 작업 진행이 불가능함
- 선택에 따라 결과가 크게 달라짐
- repo와 사용자 요구가 충돌하고 임의 선택이 위험함

## 결정 기록 규칙

되돌리기 어려운 결정은 `docs/adr/NNNN-slug.md`에 둔다. 번호는 기존 최대값 +1이고, `docs/adr/README.md` 표에 한 줄을 추가한다.

결정 기록은 아래 3개가 모두 참일 때만 만든다.

1. 되돌리기 어렵다.
2. 맥락 없이는 이상해 보인다.
3. 실제 트레이드오프가 있었다.

하나라도 아니면 만들지 않는다. 형식:

```md
# {결정 제목}

Scope: {plugin / skill, 저장소 전체면 repo}

## Decision

{결정을 간결하게}

## Reason

{이유와 실제 trade-off}
```

## 완료 전 확인

- 모호한 용어를 그대로 넘기지 않았는가?
- 코드와 사용자 설명의 충돌을 확인했는가?
- 바뀐 동작이 `SKILL.md`에 있고, `references/`와 충돌하지 않는가?
- plugin manifest 두 파일의 버전을 올렸고 `README.md` 표를 갱신했는가?
- 결정 기록은 세 조건을 모두 만족할 때만 만들었는가?
- PR을 머지했다면 링크한 기록용 Issue(와 Discussion)를 닫았는가?
