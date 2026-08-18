---
name: akbun-make-troubleshootingstruture-foragents
description: 장애 조사를 여러 세션에 걸쳐 이어가도록 incident/ 상태 디렉터리와 AGENTS.md의 트러블슈팅 규칙을 만든다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-make-troubleshootingstruture-foragents

세션이 바뀔 때마다 agent가 처음부터 추리하는 걸 막는 게 목적이다. 대화를 기억시키는 게 아니라 **조사의 상태**(확정 사실 / 가설 / 증거 / 다음 할 일)를 파일로 분리해 남긴다. 이 skill은 그 뼈대만 만들고 조사는 하지 않는다.

## 1. incident/ 생성

각 파일은 헤더와 짧은 작성 예시만 담은 빈 뼈대로 만든다. 실제 장애 내용은 넣지 않는다.

```text
incident/
├── CURRENT.md        # 확정된 사실만. Symptom / Known / Unknown / Next Actions
├── HYPOTHESES.md     # 가설. H-001 형식, 상태 머신으로 관리
├── EVIDENCE.md       # 관측값만. E-001 형식, 해석은 금지
├── SEARCH_INDEX.md   # 증상 → 관련 가설·증거·code path 로 내려가는 색인
└── investigations/   # 축별 조사 노트. code-paths.md 는 기본 포함
```

각 파일의 작성 형식:

```markdown
## H-001 {가설 문장}
Status: new | investigating | supported | rejected
Confidence: low | medium | high
Expected: {이 가설이 맞다면 무엇이 관측돼야 하는가}
Evidence: {지지 E-ID} / 반증: {반증 E-ID}
Next: {검증할 다음 한 가지}

## E-017
Time: {시각}
Observation: {수치만}
Related: {H-ID}

## CP-003 {이름}
Entry: {진입점}
Path: {호출 경로}
Potential cost: {DB 호출·반복·직렬화 등}
Related hypothesis: {H-ID}
```

## 2. AGENTS.md에 규칙 추가

AGENTS.md에는 조사 **방법**만 적는다. 현재 상황·가설·관측값은 incident/ 파일이 갖는다. 이렇게 나눠야 AGENTS.md가 몇 달 뒤에도 그대로 재사용된다. 아래 5개를 `## Troubleshooting Rules` 섹션으로 넣는다.

1. **정상 구간과 장애 구간을 항상 비교한다.** 높은 시점만 보면 원인이 안 보인다. 절대값(CPU 80%)이 아니라 단위 작업당 비용(CPU/request, DB queries/request, DB time/request, rows scanned/request)을 두 구간에서 비교하고, 그 사이에 **달라진 변수**부터 판다.
2. **증거를 가설보다 먼저 기록한다.** 관측과 해석을 섞지 않는다. "DB CPU 79%"는 증거, "DB가 CPU를 잡아먹는다"는 해석이다. 모든 결론은 E-ID를 참조한다.
3. **가설은 중복 생성하지 않는다.** 새로 만들기 전에 HYPOTHESES.md를 먼저 검색하고, rejected 가설은 다시 조사하지 않는다.
4. **repo 전체를 다시 훑지 않는다.** 진입점 → 실행 경로 → 비싼 연산(쿼리·반복·직렬화·락·재시도·외부 호출·캐시 미스) 순으로 추적하고 결과를 code-paths.md에 남긴다. 다음 세션은 기록된 경로에서 이어서 관련 파일만 확인한다.
5. **세션 종료 시 구체적인 next action 1~3개를 남긴다.** "로그 더 보기", "DB 확인" 같은 건 아무 정보가 없다. "E-017과 E-018의 endpoint 분포 비교", "CP-003의 루프 여부 확인"처럼 대상이 특정된 것만 남긴다.

## 3. 마무리

CLAUDE.md가 없으면 AGENTS.md를 읽고 따르라는 지시만 담아 만든다. 이미 있으면 건드리지 않는다.
