---
name: akbun-analysis-git-whyandhow
description: 코드·PR·서브시스템을 두 단계로 이해한다. 먼저 why(왜 이렇게 만들었나)를 git 이력·gh CLI의 PR·이슈·리뷰·저장소 문서에서 인용과 확신 등급을 붙여 조사하고, 그 제약을 안고 how(어떻게 동작하나)를 온보딩 수준으로 설명한다. MCP 도구는 쓰지 않고 GitHub는 gh CLI만 쓴다. "왜 이렇게 됐고 어떻게 동작해", "이 PR 이해시켜줘", "코드 바꾸기 전에 파악", "회귀 원인 배경" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-analysis-git-whyandhow

코드를 바꾸거나 PR을 판단하기 전에 두 질문에 순서대로 답한다. **why가 먼저다.** 동기와 제약을 모르고 동작만 읽으면 "고쳐도 되는 것"과 "지켜야 하는 것"이 구분되지 않는다. why가 낸 제약을 안고 how를 읽어야 다음 작업에서 무엇을 건드리면 안 되는지가 남는다.

읽기 전용이다. 파일을 만들거나 고치지 않는다. **MCP 도구를 쓰지 않는다.** 증거는 로컬 git, `gh` CLI, 저장소 안의 문서에서만 가져온다. 이 셋이 없는 범주는 "보지 않았다"로 기록하고 사람에게 물을 대상으로 넘긴다.

## 원칙

- 코드는 자기 동기의 증거가 아니다. "코드가 X를 하니 작성자가 X를 원했다"는 증거가 아니라 해석이다. 동기는 커밋 메시지, PR 본문과 리뷰, 이슈, 문서에만 있다.
- 모든 주장에 확신 등급을 붙인다. `[Direct]` 작성자가 글로 썼다. `[Supported]` 간접 증거 여럿이 수렴한다. `[Inferred]` 내 해석이다. `[Speculative]` 다른 설명도 똑같이 맞는다. `[Unknown]` 찾아봤는데 없다. `because`, `~하려고 설계했다`는 Direct·Supported에만 쓴다. Inferred는 `~로 보인다`, `~와 일치한다`.
- 검색한 것을 기록한다. "모른다"가 아니라 "이 파일을 건드린 PR 6개와 이슈 검색어 A, B를 봤는데 없었다"까지 쓴다. 그래야 다음 사람이 어디서 시작할지 안다.
- 사용자의 가설("성능 때문이지?")은 조사 대상이지 결론이 아니다. 증거가 지지하면 인용과 함께 말하고, 아니면 증거가 지지하는 것을 말한다.
- 모순되는 증거는 둘 다 보인다. 티켓과 PR 본문이 다르게 말하면 둘 다 인용하고 판단은 사용자에게 넘긴다.

## 1. 앵커를 고정한다

대상이 모호하면 대화 맥락(열린 파일, 최근 수정, 언급된 PR)에서 가장 그럴듯한 대상을 골라 한 줄로 되돌려 말하고 진행한다.

앵커에 담을 것: 파일 경로와 줄 범위, 핵심 심볼, 최근 커밋, PR 번호, 이슈 번호. 아래 명령으로 모은다.

```bash
git blame -L <start>,<end> <file>
git log --oneline -20 -- <file>
git log --follow -p -- <file>
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews
gh issue view <number> --json title,body,comments
gh pr list --search "<symbol or keyword>" --state all --limit 20
```

PR 하나를 이해하는 요청이면 앵커는 그 PR의 diff가 만지는 파일·심볼 전체다.

## 2. why를 조사한다

조사자 3개를 Agent 도구로 한 메시지에 띄운다. 저비용 모델, 읽기 전용, 각자 소스 하나. 프롬프트는 `references/investigator.md`에 앵커·질문·소스를 채워 넘긴다.

| 조사자 | 소스 | 잘 드러내는 것 |
|---|---|---|
| 소스 컨트롤 | `git log`, `git blame`, 커밋 메시지, 커밋에 함께 바뀐 테스트 | 구현 시점의 이유, 함께 바뀐 것 |
| GitHub | `gh pr view`·`gh pr list`·`gh issue view`·`gh search issues`. 본문, 리뷰 코멘트, 연결 이슈, 디스커션 | 리뷰에서 나온 제약, 제품·운영 쪽 요구 |
| 저장소 문서 | `docs/`, `docs/adr/`, README, 코드 주석, 설계 문서, 런북, CHANGELOG | 글로 남긴 설계 이유, 되돌리기 어려운 결정 |

조사자는 결론을 내지 않는다. 원문 인용과 정확한 위치(커밋 해시, PR·이슈 번호, `file:line`), 검색한 쿼리, 못 찾은 것, 모순, 다른 소스로 넘길 단서만 돌려준다.

대상이 방어 코드(널 체크, 재시도, 타임아웃, rate limit, feature flag)면 세 조사자 모두에게 "이 코드가 막으려던 장애·버그 보고"를 추가로 찾게 한다. 이슈 라벨 `bug`·`incident`, 커밋 메시지의 `fix`·`hotfix`·`revert`, 되돌려진 커밋이 단서다.

## 3. why를 종합한다

Agent 하나에 `references/synthesizer-why.md`, 앵커, 질문, 조사자 3개의 출력을 넘긴다. 부모 세션 모델을 쓴다. 판단이 여기서 갈린다. synthesizer는 인용을 spot-check하고 아래를 낸다.

- 찾은 것(`[Direct]`·`[Supported]`, 인용 포함)
- 추론한 것(`[Inferred]`, 추론 사슬 명시)
- 경쟁 가설(증거가 여러 이야기에 맞을 때만)
- 모르는 것(질문, 검색한 곳과 쿼리, 볼 수 없었던 소스, 물어볼 사람)
- 본 소스 목록(소스별 한 줄, 안 본 것도 이유와 함께)
- **제약 세트.** Preserve(지켜야 할 동작·불변식) / Change(바꿔도 되는 것) / Avoid(과거에 시도했다 되돌린 것) / Risk(증거가 얇아 확인이 필요한 것)

## 4. how를 읽는다

why의 제약 세트를 들고 동작을 읽는다. 복잡도로 경로를 정한다. 애매하면 단순 경로.

- **단순**(모듈 하나, 함수 하나): explainer 1개가 탐색과 설명을 한 번에. 부모 세션 모델.
- **복잡**(여러 파일·서비스, 횡단 기능): explorer 2~4개를 저비용 모델로 병렬. 각자 다른 각도(진입점과 트리거, 데이터 흐름과 변환, 핵심 타입과 소유, 다른 서브시스템과의 경계) 하나만 깊게. 프롬프트는 `references/explorer.md`. 그 뒤 explainer 1개(부모 세션 모델)가 `references/explainer.md`로 합친다.

explorer는 이름으로 추측하지 않고 코드를 읽는다. 못 추적한 것은 "못 추적했다"고 쓴다. explainer는 겹치는 것을 병합하고 모순은 코드를 다시 읽어 해소한다. why의 제약 세트에서 Preserve·Avoid에 해당하는 지점이 코드 어디인지 `file:line`으로 짚는다.

## 5. 보고

한국어 개조식. 순서는 why → how → 제약. explainer와 synthesizer의 확신 표현은 고치지 않는다.

1. **질문.** 사용자의 질문 한두 줄과 앵커.
2. **Why.** 찾은 것, 추론한 것, 경쟁 가설(있으면), 모르는 것, 본 소스 목록.
3. **How.** 개요, 핵심 개념, 동작 흐름(구성요소 3개 이상이면 mermaid 시퀀스나 흐름도 하나), 파일 위치, 함정. 함정에는 why에서 온 제약이 코드 어디에 걸리는지를 넣는다.
4. **제약 세트.** Preserve / Change / Avoid / Risk. 다음 작업 계획의 입력이다.
5. **확신 요약.** 두 문장. 무엇이 근거가 튼튼하고 무엇이 추론인가.

주장마다 출처를 같은 문장에 붙인다. 커밋 해시, PR·이슈 번호, `file:line`, 문서 경로. 없는 출처는 만들지 않는다.
