---
name: readwise-daily-pulse
description: 어제(기준 시간대 00:00~24:00) Readwise Reader에 저장된 문서(new·later·feed)와 하이라이트를 모아 changelog·읽을 것·나머지로 분류한 한글 개조식 요약을 Gmail 초안으로 만든다. 독자 프로필·관심 주제·받는 주소·API 토큰은 변수로 받아 루틴에서는 변수명만 넘긴다. "어제 Readwise 정리", "리더 데일리 펄스", "어제 저장한 글 요약해서 메일 초안으로", "readwise-daily-pulse 실행" 같은 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# readwise-daily-pulse

어제 Readwise Reader에 들어온 문서와 하이라이트를 **오늘 아침 5분 안에 훑을 수 있는 메일 초안**으로 만드는 skill이다. 판단 기준(누가 읽는지, 무엇에 관심 있는지, 어디로 보내는지)은 SKILL.md에 박아 두지 않고 변수로 받는다. 이 파일은 공개 저장소에 올라가므로 개인 정보와 토큰은 절대 여기 적지 않는다.

## 0. 변수

값은 아래 우선순위로 정한다. 루틴(스케줄 프롬프트)은 값을 본문에 쓰지 않고 변수명만 언급해도 된다.

1. 호출 문장에 `KEY=value` 형태로 준 값
2. 환경 변수 `$KEY`
3. 기본값

| 변수 | 용도 | 기본값 |
|---|---|---|
| `PULSE_SOURCE` | `mcp`(Readwise MCP) 또는 `cli`(번들 스크립트 + API) | `mcp`. Readwise MCP가 없으면 `cli` |
| `READWISE_TOKEN` | Readwise API 토큰. `cli`일 때만 필요 | 없음 |
| `PULSE_TO` | 초안 받는 주소 | Gmail 계정 본인 주소. 없으면 `git config user.email` |
| `PULSE_PROFILE` | 독자 역할 한 줄. 관련성·운영 영향 판단 기준 | `엔지니어` |
| `PULSE_INTERESTS` | 관심 주제, 쉼표 구분 | 없음 |
| `PULSE_CANDIDATE_TOPICS` | 후보 주제, 쉼표 구분. 상단 선정 시 관심 주제보다 낮은 우선순위 | 없음 |
| `PULSE_TZ` | 기준 시간대(IANA) | `Asia/Seoul` |
| `PULSE_SUBJECT_PREFIX` | 메일 제목 접두 | `[Reader]` |

규칙:

- `READWISE_TOKEN`은 환경 변수로만 받는다. 호출 문장에 들어 있어도 채팅·메일·로그·파일에 다시 쓰지 않는다.
- `PULSE_INTERESTS`가 없으면 관련성 제외를 하지 않고 품질 기준(5절)만으로 선정한다. 있으면 관심 주제와 무관한 글은 품질과 무관하게 상단에서 제외한다.
- 변수가 비어 있어도 사용자에게 묻지 않는다. 기본값으로 진행하고 마지막 보고에 어떤 변수를 기본값으로 썼는지 한 줄 남긴다.

루틴 예시:

```text
readwise-daily-pulse 실행. PULSE_PROFILE, PULSE_INTERESTS, PULSE_TO는 환경 변수 값을 사용.
```

## 1. 시간 계산

실행 시점을 기준으로 `PULSE_TZ`에서 다음 값을 먼저 계산하고 채팅에 한 줄로 적는다.

- `yesterday_start_local`: 어제 00:00:00
- `today_start_local`: 오늘 00:00:00
- `yesterday_start_utc`, `today_start_utc`: 위 두 값을 UTC로 변환

이후 "어제"는 `saved_at` 또는 `highlighted_at`이 `yesterday_start_local` 이상 `today_start_local` 미만인 반개구간만 뜻한다. API 필터는 `updated_at` 기준이라 범위 밖 문서가 섞여 들어오므로 이 계산을 건너뛰면 결과가 틀린다.

## 2. 수집

### cli 모드

번들 스크립트가 시간 계산·페이지네이션·날짜 필터·중복 제거·본문 로드를 모두 처리해 JSON을 만든다.

```bash
python3 <skill-dir>/scripts/collect_readwise.py --tz "$PULSE_TZ" --with-content --out /tmp/readwise-daily-pulse.json
```

- `--date YYYY-MM-DD`로 어제 대신 다른 날을 지정할 수 있다.
- JSON의 `range`(시간 계산 결과), `stats`(전체 수집·날짜 필터 제외·저장·RSS·본문 로드 실패 건수), `documents[]`, `highlights[]`를 그대로 쓴다. 각 문서에는 `output_url`(source_url 우선, 없으면 Reader url)과 `content`(본문 텍스트) 또는 `content_error`가 들어 있다.
- exit 2는 토큰 없음, exit 3은 API 실패다. 두 경우 모두 초안을 만들지 않고 원인만 한 줄 보고한다.

### mcp 모드

Readwise MCP로 같은 결과를 만든다. 호출 순서와 필드는 [references/mcp-collection.md](references/mcp-collection.md)를 따른다. 핵심은 세 가지다.

- `location=feed, new, later` 각각 `limit=100`, `updated_after=yesterday_start_utc`로 호출하고 `nextPageCursor`가 없을 때까지 페이지를 넘긴다. 세 location 모두 끝나기 전에는 수집 완료로 보지 않는다.
- 받은 문서의 `saved_at`을 `PULSE_TZ`로 바꿔 1절 반개구간 안의 것만 남긴다. 나머지는 "날짜 필터 제외 건수"에 센다. 문서 ID로 중복을 제거한다.
- 하이라이트는 `readwise_list_highlights`를 `highlighted_at_gt=yesterday_start_utc`로 끝까지 넘기고 `highlighted_at`을 같은 방식으로 필터한다.

### 공통

- 집계: 저장 수(new+later), RSS 수(feed), 전체 수집 건수(필터·중복 제거 전), 날짜 필터 제외 건수.
- 처리 대상 문서와 하이라이트가 모두 없으면 본문이 "어제 들어온 항목 없음"인 초안만 만들고 끝낸다.

## 3. URL 확정

메일에 넣을 URL은 문서마다 하나만 쓴다.

1. `source_url`이 `http://` 또는 `https://`로 시작하면 그것을 쓴다.
2. 아니면 Reader `url`을 쓴다.
3. 둘 다 없으면 URL 줄을 생략한다.
4. 하이라이트의 `book_source_url`, URL 형태의 `site_name`도 같은 규칙이다. `site_name`이 URL이면 도메인만 표시한다.

Gmail은 초안을 보낼 때 본문 링크를 자체 리디렉션으로 다시 감싼다. 그래서 초안을 다시 읽어 링크를 검사하거나 리디렉션을 풀어 쓰는 작업은 의미가 없고, 여기서는 하지 않는다.

## 4. 본문 확인

- cli 모드는 JSON의 `content`를 쓴다. mcp 모드는 처리 대상 문서만 `reader_get_document_details`를 각 1회 호출한다.
- 본문을 못 읽은 문서는 제목과 `summary`로 정리하고 제목 옆에 "본문 로드 실패"를 붙인다. 실패 건수를 센다.

작성 스타일(메일 전체 공통, 개조식):

- 짧고 직접적인 문장. 한 문장에 사실 하나.
- 핵심 기능·변경점·수치·영향 중심. 배경·수식어·접속어는 뺀다.
- "다룸/설명함/소개함"처럼 내용 없는 종결을 쓰지 않는다.
- 가능하면 "무엇이 바뀌었는지 → 운영 영향" 순서.
- 본문에서 확인하지 못한 내용은 쓰지 않는다.

## 5. 분류와 선정

관련성은 `PULSE_PROFILE`, `PULSE_INTERESTS`, `PULSE_CANDIDATE_TOPICS` 기준으로 판단한다. "영향"과 "운영 영향"은 항상 이 프로필의 작업·도구·운영 환경 기준으로 쓴다.

**A. changelog**: 기능 출시·수정, 기본값·동작·호환성 변경, 성능 개선, 버그·보안 수정, hotfix, 가격 변경, deprecation, 리전 추가, 버전 릴리스.

- 제목 끝에 유형 하나만 붙인다: `(new feature)` `(update)` `(hotfix)` `(bugfix)` `(security fix)` `(deprecation)` `(pricing)` `(region)` `(release)`. 유형 구분이 어려운 릴리스는 `(release)`.
- 본문에서 실제 변경을 확인한 경우에만 changelog다. 유형을 추측하지 않는다. 확인 못 하면 일반 문서로 둔다.
- 단순 홍보에는 유형을 붙이지 않는다. 제목에 이미 유형이 있어도 영문 유형을 추가한다.
- 우선순위: 운영 영향 큰 new feature > 기본값·API·호환성·성능·가격 update > security fix·hotfix·bugfix > deprecation > release > 단순 region.
- 업무 관련성·운영 영향 순으로 정렬한다. 같은 변경을 다룬 중복 문서는 원본에 가까운 것 하나만 남긴다.

**B. 장애·실패·보안**: 원인이 밝혀진 장애·실패, 보안 사고·취약점·권한·비밀 유출, 재현 조건·영향 범위·방지법이 구체적인 글.

**C. 기술 분석·설계**: 통념 반박·수정, 깊이 있는 분석, 아키텍처·성능·비용·운영 트레이드오프, 글·발표 소재.

우선순위 하향: 개인 프로젝트 홍보, Show HN·Show GN류, 단순 질문, 무관한 시사·스포츠, 중복 기사, 핵심 변경점 없는 홍보성 발표.

상단(읽을 것)은 5~7건이 목표지만 억지로 채우지 않는다. changelog는 이 목표 수에 넣지 않고 별도 영역에 둔다.

## 6. 메일 구성

순서: 하이라이트 → `## changelog` → `## 읽을 것` → `## 나머지`. 번호는 메일 전체에서 1부터 연속이다.

하이라이트(있으면 최상단):

```text
인용문 한 문장
- 표시한 이유: 독자가 표시했을 구체적 이유
원본 URL
```

`## changelog` 항목:

```text
1. ▶ 제품명 또는 제목 (변경 유형)
- 핵심 기능·변경점
- 기존과의 차이
- 운영 영향: 프로필의 작업·도구·운영 환경 기준
- 수치·조건: 버전, 가격, 성능, 적용 조건
원본 URL 또는 Reader URL
```

changelog 규칙: "출시됨/업데이트됨"만 쓰지 않는다. new feature는 무엇을 가능하게 하는지, update는 무엇이 달라졌는지, fix는 대상·조건·영향, deprecation은 대상·시점, pricing은 전후 가격 또는 과금 단위를 쓴다. 정보 없는 줄은 생략한다. 단순 region은 하단에 둔다.

`## 읽을 것` (장애·실패·보안 → 기술 분석·설계 순):

```text
2. ▶ 제목
- 핵심 내용: 확인된 원인, 주장, 설계
- 영향: 프로필의 작업·운영 환경에 미치는 구체적 영향
- 수치·조건
원본 URL 또는 Reader URL
```

연관성을 구체적으로 설명하지 못하면 상단에서 뺀다. "흥미롭다/유익하다" 같은 추상 평가는 쓰지 않는다.

`## 나머지` (site_name별 묶음):

```text
3. 제목 · site_name · reading_time
- 핵심 내용
- 수치·조건
원본 URL 또는 Reader URL
```

- 추천 판단을 붙이지 않는다. site_name이 URL이면 도메인만 표시한다.
- 본문 미로드 문서는 "본문 로드 실패"를 붙인다.
- changelog는 여기 두지 않고 전부 `## changelog`에 둔다.

## 7. 검증

본문을 파일로 저장하고 번들 검사기를 돌린다. 통과(exit 0)할 때만 초안을 만든다.

```bash
python3 <skill-dir>/scripts/check_draft.py /tmp/readwise-daily-pulse.md
```

검사 항목: 백틱 없음, 첫 줄 집계 형식, `## changelog` → `## 읽을 것` → `## 나머지` 순서, changelog 제목마다 유형 표시, `## 나머지`에 유형 표시 제목 없음, 번호 1부터 연속, URL 줄은 단독 한 줄. 실패하면 메시지대로 본문을 고치고 다시 돌린다. 최대 3회 수정 후에도 실패하면 초안을 만들지 않고 실패 원인을 보고한다.

## 8. Gmail 초안

Gmail MCP `create_draft`로 `PULSE_TO`에게 보내는 플레인 텍스트 초안을 만든다. `htmlBody`는 쓰지 않는다.

- 본문 첫 줄: `변경사항 {N}건 · 읽을 것 {N}건 · 나머지 {N}건 (저장 {N} · RSS {N}) · 하이라이트 {N}개`
- 제목: `{PULSE_SUBJECT_PREFIX} {어제 M/D} · 변경사항 {N}건 · 읽을 것 {N}건`
- 규칙: 전체 개조식, 긴 문단 금지, 백틱 금지, URL은 단독 한 줄, 원본 URL 우선.

Gmail MCP가 없거나 `create_draft`가 실패하면 본문을 `~/readwise-daily-pulse/YYYY-MM-DD.md`에 저장하고 그 사실을 보고한다. 어디로 보낼지 사용자에게 묻지 않는다.

## 9. 응답

채팅에는 초안 본문을 먼저 보여주고 마지막에 한 줄 보고를 적는다: 전체 수집 건수, 날짜 필터 제외 건수, 본문 로드 실패 건수, changelog 수와 유형별 건수, 상단 선정 기준(프로필·관심 주제), 기본값으로 쓴 변수, 초안 생성 결과. 토큰과 받는 주소 전체는 적지 않는다.
