# akbun-aitools

akbun(악분)이 매일 쓰는 AI agent skill을 Claude Code와 Codex plugin으로 묶은 저장소다. 글을 쓰고, 그림 프롬프트를 만들고, 코드를 이해하고, agent를 세션 넘어 운영하는 방식을 skill로 고정해 두었다. 모든 skill은 한국어로 답하고, 입력에 있는 사실만 쓰고, 확인하지 못한 것은 `확인 필요`로 남긴다.

## 한눈에 보기

plugin 9개, skill 51개. 하고 싶은 일에서 plugin을 찾고, 아래 `plugin 목록`에서 skill을 고른다.

| 하고 싶은 일 | plugin | 대표 skill |
|---|---|---|
| 공부한 것을 akbun 스타일 한국어 기술 글로 쓰기, 문서 교정, 운영 작업 공지 | [akbun-writing](#akbun-writing) | `akbun-writing`, `akbun-docs-review`, `akbun-it-infra-change-notice` |
| 고정 스타일의 이미지 생성 프롬프트와 Figma/Canva용 SVG(웹툰·카드뉴스·삽화·아키텍처 그림) | [akbun-draw](#akbun-draw) | `akbun-draw-webtoon-c`, `akbun-draw-cardnews-cream`, `akbun-draw-system-architecture` |
| AWS VPC·Kubernetes 네트워크 draw.io 다이어그램 | [akbun-draw-architecture](#akbun-draw-architecture) | `akbun-drawio-aws-vpc`, `kubernets-network-drawio` |
| akbun 스타일 pptx 덱과 발표 대본, 삽입 시각자료 | [akbun-presentation](#akbun-presentation) | `akbun-presentation` |
| 알고리즘 과외, 영상 자막 대본, 발음 가이드, Anki, 학습지 | [akbun-learning](#akbun-learning) | `akbun-algorithm-tutor`, `akbun-studysheet` |
| 코드베이스 관계 분석, 병목 예측, 아키텍처 적대 리뷰, PR의 왜와 어떻게, 머지 영향 범위 | [akbun-analysis](#akbun-analysis) | `akbun-analysiscode`, `akbun-analysis-git-whyandhow`, `akbun-analysis-gitdiff-blast-radius` |
| 이미 쓰는 코드·문서를 자동 검증에 걸어 리팩토링, 사람이 판단할 것만 보고 | [akbun-refactoring](#akbun-refactoring) | `akbun-refactoring-autoverify` |
| agent 기억 구조 설정, 세션 시작 때 맥락 복원, 세션에서 배운 것을 skill에 반영 | [akbun-agent-ops](#akbun-agent-ops) | `akbun-memory-setup`, `akbun-recall`, `akbun-reflect` |
| 매일 GitHub·Readwise 활동을 복습 문서로, 기간별 결과를 주간회의 브리프로 | [akbun-pulse](#akbun-pulse) | `github-daily-pulse`, `github-period-pulse`, `readwise-daily-pulse` |

## 빠른 시작

Claude Code에서 marketplace를 등록하고 plugin 하나를 설치한 뒤 skill 이름으로 호출한다. 전체 설치 명령과 Codex는 아래 `설치 방법`에 있다.

```bash
/plugin marketplace add choisungwook/akbun-aitools
/plugin install akbun-writing@akbun-aitools
/reload-plugins
```

설치 뒤 예시 요청:

```text
/akbun-writing 이 실습 노트를 블로그 글로 정리해줘
```

대부분의 skill은 사용자가 이름을 불러야 실행된다(`disable-model-invocation: true`). 모델이 알아서 끼어들지 않게 하려는 선택이다.

## plugin 목록

설치 가능한 plugin과 각 plugin이 제공하는 skill이다. plugin이나 skill을 추가/삭제하면 이 목록도 함께 갱신한다(`AGENTS.md`의 플러그인 변경 규칙 참고).

### akbun-writing

글쓰기, 리뷰, 블로그 발행 지원 skill 모음.

| skill | 설명 |
|---|---|
| [akbun-writing](./plugins/akbun-writing/skills/akbun-writing/) | akbun 스타일 한국어 기술 글 작성. 설명 모드 고정, 문장 규칙 4층(상위 규칙·독자 지향·한 문장 한 생각·오독 제거), naturalize 호출로 마무리 |
| [akbun-writing-with-question](./plugins/akbun-writing/skills/akbun-writing-with-question/) | 질문 기반 akbun 스타일 학습형 블로그 작성 |
| [akbun-writing-persuasive](./plugins/akbun-writing/skills/akbun-writing-persuasive/) | 독자가 끝까지 읽고 납득하도록 설득식 구조로 akbun 스타일 블로그 작성 |
| [akbun-docs-review](./plugins/akbun-writing/skills/akbun-docs-review/) | 이미 쓴 한국어 기술 문서의 용어 표기 통일과 근거 있는 사실 교정. 맞춤법·문장은 naturalize를 호출해 처리하고 원본에 덮어씀 |
| [akbun-writing-naturalize](./plugins/akbun-writing/skills/akbun-writing-naturalize/) | 원문 목소리와 구조를 보존하며 한국어 맞춤법과 기계적인 문체 교정. 다른 skill이 호출 모드로 재사용 |
| [akbun-markdown-to-html-pandoc](./plugins/akbun-writing/skills/akbun-markdown-to-html-pandoc/) | Obsidian markdown을 pandoc으로 HTML 변환(블로그 업로드) |
| [akbun-md-to-notion](./plugins/akbun-writing/skills/akbun-md-to-notion/) | Obsidian markdown을 Notion Tasks DB로 전송 |
| [akbun-writing-style-warm](./plugins/akbun-writing/skills/akbun-writing-style-warm/) | 겁먹은 초보 독자를 위한 해요체 경험 고백 말투로 쓰기 |
| [akbun-writing-easy](./plugins/akbun-writing/skills/akbun-writing-easy/) | 원본 자료를 초보자용 기초 레이어 글로 바꾸는 개조식 쉬운 설명 작성 |
| [akbun-voice-diary](./plugins/akbun-writing/skills/akbun-voice-diary/) | 음성 채팅으로 말한 하루를 고정 규격 일기(한 줄·있었던 일·힘들었던 것·공부하면 좋은 것)로 저장(기본 ~/Downloads, Apple Notes·Google Docs 선택)하고 공부 주제를 이번 주 주말 Apple Calendar에 등록 |
| [akbun-thumbnail-review](./plugins/akbun-writing/skills/akbun-thumbnail-review/) | 유튜브 썸네일을 6항목(TV 친화 50% 테스트·질문·감정 유발·레퍼런스 메커니즘·잡동사니 제거·문제 부각·문구 변주)으로 리뷰하고 제안마다 이유를 설명 |
| [akbun-it-infra-change-notice](./plugins/akbun-writing/skills/akbun-it-infra-change-notice/) | 스테이징 검증이 끝난 인프라 변경을 운영에 적용하기 전 개발자용 작업 공지 초안(영향·해야 할 일 → 왜 → 변경 → 기대 효과 → 확인 항목 붙은 절차 → 시간 → 롤백과 불가 지점 → 비용 계산식 → 리스크 → 스테이징 증거). 수치는 측정/인용/추정 라벨, 없으면 확인 필요 |

### akbun-draw

이미지 그리기 skill 모음. 소재·글·코드를 akbun 고정 스타일의 이미지 생성 프롬프트와 Figma/Canva 편집용 SVG로 만든다.

| skill | 설명 |
|---|---|
| [akbun-generateimage-code](./plugins/akbun-draw/skills/akbun-generateimage-code/) | 코드 설명용 블로그 figure의 이미지 생성 프롬프트 작성 |
| [akbun-draw-webtoon-b](./plugins/akbun-draw/skills/akbun-draw-webtoon-b/) | 이미지·글로 파스텔 치비 동물 캐릭터 웹툰 페이지의 이미지 생성 프롬프트 + Figma/Canva용 텍스트 SVG 작성 |
| [akbun-draw-webtoon-c](./plugins/akbun-draw/skills/akbun-draw-webtoon-c/) | 글·이미지로 세로형 1컷 에세이툰(상단 내레이션+고래 마스코트 단일 장면) 페이지의 이미지 생성 프롬프트 + Figma/Canva용 텍스트 SVG 작성 |
| [akbun-draw-webtoon-d](./plugins/akbun-draw/skills/akbun-draw-webtoon-d/) | 실제 경험담을 인스타 세로형(3:4) 흑백 다큐툰(거친 잉크 낙서선+하단 자막 내레이션+얼굴 없는 실루엣 군중)의 장면별 이미지 생성 프롬프트로 작성 |
| [akbun-draw-sketchbook-card](./plugins/akbun-draw/skills/akbun-draw-sketchbook-card/) | 개념을 연필 스케치북 카드(손글씨 제목·체크리스트+일러스트)로 그리는 이미지 생성 프롬프트 작성 |
| [akbun-draw-storytellingimage](./plugins/akbun-draw/skills/akbun-draw-storytellingimage/) | 이야기를 장면별 손그림 마커 스케치 삽화의 이미지 생성 프롬프트로 작성 |
| [akbun-draw-quiet-pencil](./plugins/akbun-draw/skills/akbun-draw-quiet-pencil/) | 아무 순간을 크림 배경+넓은 여백+회색 연필 소재+틸 소품 하나의 조용한 연필 스케치 장면 스타일로 그리는 이미지 생성 프롬프트 작성 |
| [akbun-draw-book-illustration](./plugins/akbun-draw/skills/akbun-draw-book-illustration/) | 소재·문구를 monogray 삽화 스타일 + 고정 레이아웃 5종(아이콘 스트립·확대·대화·흐름·포스터)과 상하좌우 간격으로 배치한 이미지 생성 프롬프트와 Figma/Canva용 SVG 작성 |
| [akbun-draw-cartoon-b](./plugins/akbun-draw/skills/akbun-draw-cartoon-b/) | 아무 상황을 회색 그라데이션+베이지 테두리+낙서풍 고래 캐릭터+올리브 포인트 하나의 이슈 카드뉴스 스타일로 그리는 이미지 생성 프롬프트와 Figma/Canva용 SVG 작성 |
| [akbun-draw-cardnews-cream](./plugins/akbun-draw/skills/akbun-draw-cardnews-cream/) | 아무 개념을 크림 배경+손글씨 제목·본문+낙서 다이어그램+파란 빗금 포인트 하나의 설명형 카드뉴스 스타일로 그리는 이미지 생성 프롬프트와 Figma/Canva용 SVG 작성 |
| [akbun-mascot-whale](./plugins/akbun-draw/skills/akbun-mascot-whale/) | akbun 마스코트 고래 캐릭터의 표준 외형 스펙(다른 그리기 skill이 참조) |
| [akbun-draw-system-architecture](./plugins/akbun-draw/skills/akbun-draw-system-architecture/) | 시스템 설명·코드·문서를 진회색 프레젠테이션 스타일의 시스템 아키텍처 이미지·생성 프롬프트·편집 가능한 PPTX로 변환 |
| [akbun-draw-learning-mono](./plugins/akbun-draw/skills/akbun-draw-learning-mono/) | 논문·책·문서·개념을 흰 배경 흑백 미니멀 16:9 학습용 설명 이미지(주제별 분할 + 한국어 발표 대본)로 변환 |

아래는 각 skill로 만든 예시다.

| skill | 이미지 |
|---|---|
| `akbun-mascot-whale` | <img src="./imgs/akbun-mascot-whale.png" alt="akbun-mascot-whale" width="320"> |
| `akbun-draw-webtoon-c` | <img src="./imgs/akbun-draw-webtoon-c.png" alt="akbun-draw-webtoon-c" width="320"> |
| `akbun-draw-cartoon-b` | <img src="./imgs/akbun-draw-cartoon-b.png" alt="akbun-draw-cartoon-b" width="320"> |

### akbun-draw-architecture

아키텍처 그리기 skill 모음. AWS/Kubernetes draw.io 다이어그램을 만든다.

| skill | 설명 |
|---|---|
| [akbun-drawio-aws-vpc](./plugins/akbun-draw-architecture/skills/akbun-drawio-aws-vpc/) | draw.io로 AWS VPC 기초 다이어그램 생성 |
| [kubernets-network-drawio](./plugins/akbun-draw-architecture/skills/kubernets-network-drawio/) | draw.io로 Kubernetes 네트워크 다이어그램 생성 |

### akbun-presentation

akbun 발표자료 스타일 skill 모음.

| skill | 설명 |
|---|---|
| [akbun-presentation](./plugins/akbun-presentation/skills/akbun-presentation/) | 주제·원본 자료를 akbun 스타일 pptx 덱 + 슬라이드별 상세 발표 대본(md)으로 생성 — 발표 시간·청중·언어 설정을 받아 분량을 맞추고, 라이트 샌드위치(기본)/다크 스텝 스타일과 질문 훅 스토리를 따름 |
| [akbun-presentation-visual](./plugins/akbun-presentation/skills/akbun-presentation-visual/) | 발표 내용·슬라이드 브리프·원본 Figure를 akbun 스타일의 16:9 삽입용 시각자료 이미지로 생성 |

아래는 skill로 만든 예시다.

| skill | 이미지 |
|---|---|
| `akbun-presentation` | <img src="./imgs/akbun-presentation.png" alt="akbun-presentation 예시 슬라이드" width="480"> |

### akbun-learning

언어·학습 보조 skill 모음.

| skill | 설명 |
|---|---|
| [akbun-algorithm-tutor](./plugins/akbun-learning/skills/akbun-algorithm-tutor/) | 학습자 눈높이에 맞춘 알고리즘 문제 풀이·복잡도 과외 |
| [akbun-describe-twitter-transcript](./plugins/akbun-learning/skills/akbun-describe-twitter-transcript/) | x.com post 영상을 한국어 Markdown 대본으로 정리 |
| [akbun-describe-youtube-transcript](./plugins/akbun-learning/skills/akbun-describe-youtube-transcript/) | 유튜브 자막을 한국어 보고서로 정리 |
| [akbun-driven-learning](./plugins/akbun-learning/skills/akbun-driven-learning/) | 가설 검증형 학습자를 위한 기술 개념 설명 스타일(판정 우선·구조 시각화·연쇄 질문 대응) |
| [akbun-learning-english](./plugins/akbun-learning/skills/akbun-learning-english/) | 한국어 학습자용 영어 발음·읽기 가이드 |
| [akbun-learning-japanese](./plugins/akbun-learning/skills/akbun-learning-japanese/) | 한국어 학습자용 일본어 발음·읽기 가이드 |
| [akbun-make-anki-japanese](./plugins/akbun-learning/skills/akbun-make-anki-japanese/) | 일본어 교재 이미지/PDF를 Anki 덱으로 변환 |
| [akbun-studysheet](./plugins/akbun-learning/skills/akbun-studysheet/) | 주제·글·코드를 문제 상황 → 원리 → 구조 이해 → 핸즈온 흐름의 인터랙티브 HTML 학습지(20장 미만, 전체 light theme akbun 라이트 스타일)로 생성 |

### akbun-analysis

코드베이스 분석 skill 모음. 어떤 비즈니스를 위해 코드가 쓰였는지를 file:line 근거가 있는 JSON으로 저장하고, 인터랙티브 HTML과 선택적 draw.io 관계도를 생성·증분 갱신한다.

| skill | 설명 |
|---|---|
| [akbun-analysiscode](./plugins/akbun-analysis/skills/akbun-analysiscode/) | 비즈니스 흐름·API·서비스 관계를 근거 기반 JSON으로 분석하고, 비즈니스·서비스·API 관계도를 가진 인터랙티브 HTML·draw.io로 시각화·증분 갱신 |
| [akbun-analysis-bottleneck](./plugins/akbun-analysis/skills/akbun-analysis-bottleneck/) | 트래픽 증가 시 병목 후보를 file:line 근거로 예측하고 측정 항목·장애 시 확인 순서·해결책 선택지·개선 뒤 새 문제를 mermaid 아키텍처와 함께 문서화 |
| [akbun-analysis-architecture-review](./plugins/akbun-analysis/skills/akbun-analysis-architecture-review/) | 넘겨준 문맥과 인터뷰로 현재 아키텍처를 적대적으로 평가하고, 보안·운영 부담(toil) 관점 필수로 발견→대안→수치 효과 표→감수할 것→이행 순서를 mermaid 컴포넌트·시퀀스와 함께 제안 |
| [akbun-analysis-token-credential](./plugins/akbun-analysis/skills/akbun-analysis-token-credential/) | 토큰·API 키 같은 자격 증명을 보안 관점에서 볼 때 발급 주체·읽는 주체·허용 범위를 묻는 질문 한 줄. 인증·인가 분석 의도를 AI에게 전달하는 용도 |
| [akbun-analysis-adversarial-review](./plugins/akbun-analysis/skills/akbun-analysis-adversarial-review/) | 사용자가 구현한 코드·주장을 옹호하지 않고 숨은 가정과 예외를 의심해 깨지는 반례를 근거와 함께 드는 적대적 리뷰 지침 두 줄 |
| [akbun-analysis-git-whyandhow](./plugins/akbun-analysis/skills/akbun-analysis-git-whyandhow/) | 코드·PR을 why → how 순서로 이해. git·gh CLI·저장소 문서만으로(MCP 미사용) 동기를 확신 등급·인용과 함께 조사하고, 그 제약(Preserve/Change/Avoid/Risk)을 안고 동작을 온보딩 수준으로 설명 |
| [akbun-analysis-gitdiff-blast-radius](./plugins/akbun-analysis/skills/akbun-analysis-gitdiff-blast-radius/) | PR·diff를 머지하면 diff 밖 어디가 깨지고 내 다음 작업과 어디서 만나는지 찾고, 안전한 이유인 사실 하나를 실행 스크립트로 증명(확신 사다리 5단). 옵션으로 gh CLI로 PR 코멘트 |

### akbun-refactoring

리팩토링 skill 모음. 이미 사용 중인 코드·문서·설정·인프라 코드를 고칠 때 모든 변경을 자동 검증에 통과시키고, 사람이 판단할 변경만 골라 보고한다.

| skill | 설명 |
|---|---|
| [akbun-refactoring-autoverify](./plugins/akbun-refactoring/skills/akbun-refactoring-autoverify/) | 이미 사용 중인 코드·문서·설정을 무엇을 어떤 근거로 수정·삭제·생성할지 먼저 제안해 수락받고, 작은 단위로 고치며 매번 저장소의 자동 검증(테스트·린트·타입·빌드·문서 검사)을 통과시킨 뒤, 사람이 결정할 변경(동작·인터페이스 변경·삭제·보안·되돌림·기준선 실패)만 변경 전후·증거와 함께 보고. 보고 채널은 시작 시 한 번 질문(stdout 기본, GitHub PR body, GitHub issue, 파일) |

### akbun-agent-ops

agent 운영 skill 모음. 프로젝트의 기억 구조를 최초 1회 설계하고, 세션 시작 때 작업 맥락을 복원하고, 세션에서 배운 것을 승인 뒤 SKILL.md에 남긴다.

| skill | 설명 |
|---|---|
| [akbun-memory-setup](./plugins/akbun-agent-ops/skills/akbun-memory-setup/) | 프로젝트를 훑어 agent 기억 디렉터리(디렉터리마다 "언제 읽는가")와 AGENTS.md 읽기 순서·CLAUDE.md 포인터를 최초 1회 생성. 매 세션 쓰는 맥락은 AGENTS.md 인라인, 반복 지시는 스크립트로 |
| [akbun-recall](./plugins/akbun-agent-ops/skills/akbun-recall/) | 세션 시작 때 AGENTS.md가 가리키는 기억, git·PR 상태, 이전 세션 transcript를 읽고 대조해 캡슐·상태 태그 스레드·반복 문제·다음 행동 1개의 브리프로 복원 |
| [akbun-reflect](./plugins/akbun-agent-ops/skills/akbun-reflect/) | 세션 transcript를 저비용 모델 리뷰어 3개(판단·도구·발산)가 읽고 학습을 코드베이스가 이미 가진 기억 구조(관련 SKILL.md, 프로젝트 wiki·결정 기록, AGENTS.md)의 맞는 자리에 수정 제안(Accepted/Rejected/Backlog)으로 라우팅, 사용자 승인 행만 적용. 새 구조는 만들지 않음 |

### akbun-pulse

펄스 skill 모음. 오늘 GitHub에서 일어난 일과 어제 Readwise에 들어온 글을 복습 문서로, 기간 동안 끝낸 일을 주간회의 브리프로 만들어 사용자 손에 바로 넣는다.

| skill | 설명 |
|---|---|
| [github-daily-pulse](./plugins/akbun-pulse/skills/github-daily-pulse/) | 오늘 00:00부터 실행 시각까지 접근 가능한 모든 repo의 issue·discussion·merged PR·open/draft PR을 한글 복습 문서(시간·핵심작업·모든 작업)로 만들고 Gmail로 나에게 전송, 실패 시 Apple Notes 저장(Google Docs·md 파일 지정 가능) |
| [readwise-daily-pulse](./plugins/akbun-pulse/skills/readwise-daily-pulse/) | 어제 Readwise Reader에 저장된 문서(new·later·feed)·하이라이트를 changelog(유형 표시)·읽을 것·나머지로 분류한 한글 개조식 요약을 Gmail 초안으로 생성. 프로필·관심 주제·받는 주소·토큰은 변수로 받아 루틴에서는 변수명만 지정 |
| [github-period-pulse](./plugins/akbun-pulse/skills/github-period-pulse/) | 하루·1주·날짜 범위 동안 내가 GitHub에서 끝낸 것을 주간회의 보고용 브리프로. gh CLI만 사용, 결과(사용자에게 달라진 것, PR body 구현 첫 줄 재사용)·진행 중·막힌 것·다음 기간·수치 한 줄, 항목마다 PR·issue 링크 |

## skill 연관관계

일부 skill은 다른 skill의 정의를 참조한다. 참조 대상 skill을 바꾸면 참조하는 skill의 결과물도 함께 바뀐다.

- `akbun-memory-setup`(akbun-agent-ops): AGENTS.md 읽기 순서를 만든다. `akbun-recall`이 그 순서를 따라 기억을 읽고, `akbun-reflect`는 그 구조 안의 기존 문서(SKILL.md·wiki·AGENTS.md)에만 쓰고 구조를 바꾸지 않는다.
- `akbun-writing`(akbun-writing): 글쓰기 기준 skill. `akbun-writing-with-question`, `akbun-writing-persuasive`가 모든 기본 규칙을 참조로 상속하고 각자 한 축(질문 구조, 설득 장치)만 더한다. `akbun-writing-easy`는 tokenops 규칙을 참조한다. 마무리에 `akbun-writing-naturalize`를 호출 모드로 적용한다.
- `akbun-presentation-visual`(akbun-presentation): `akbun-presentation`이 슬라이드에 삽입할 래스터 시각자료를 생성한다.
- `akbun-mascot-whale`(akbun-draw): akbun 마스코트 고래의 표준 외형을 정의하는 기준 skill. 캐릭터를 그리는 아래 skill들이 이 스펙을 참조한다.
  - 캐릭터로 직접 사용: `akbun-draw-cartoon-b`, `akbun-draw-webtoon-c`

## 설치 방법

### Claude Code

Claude Code에서 아래를 차례로 실행한다. 필요한 plugin만 골라 설치해도 된다.

```bash
/plugin marketplace add choisungwook/akbun-aitools
/plugin install akbun-writing@akbun-aitools
/plugin install akbun-draw@akbun-aitools
/plugin install akbun-draw-architecture@akbun-aitools
/plugin install akbun-learning@akbun-aitools
/plugin install akbun-presentation@akbun-aitools
/plugin install akbun-analysis@akbun-aitools
/plugin install akbun-pulse@akbun-aitools
/plugin install akbun-refactoring@akbun-aitools
/plugin install akbun-agent-ops@akbun-aitools
/reload-plugins
```

### Codex

Codex에서 아래를 차례로 실행한다.

```bash
codex plugin marketplace add choisungwook/akbun-aitools --json
codex plugin add akbun-learning@akbun-aitools --json
codex plugin add akbun-writing@akbun-aitools --json
codex plugin add akbun-draw@akbun-aitools --json
codex plugin add akbun-draw-architecture@akbun-aitools --json
codex plugin add akbun-presentation@akbun-aitools --json
codex plugin add akbun-analysis@akbun-aitools --json
codex plugin add akbun-pulse@akbun-aitools --json
codex plugin add akbun-refactoring@akbun-aitools --json
codex plugin add akbun-agent-ops@akbun-aitools --json
```

#### Codex 업그레이드 (hard reset)

third-party marketplace는 자동 갱신되지 않는다. 업그레이드는 제거 후 재설치(hard reset)로 한다. Codex에게 아래처럼 요청하면 된다.

```text
akbun-aitools Codex plugin을 hard reset하세요.
```

직접 실행할 때의 hard reset 명령어

```bash
codex plugin remove akbun-writing@akbun-aitools --json
codex plugin remove akbun-draw@akbun-aitools --json
codex plugin remove akbun-draw-architecture@akbun-aitools --json
codex plugin remove akbun-learning@akbun-aitools --json
codex plugin remove akbun-presentation@akbun-aitools --json
codex plugin remove akbun-analysis@akbun-aitools --json
codex plugin remove akbun-pulse@akbun-aitools --json
codex plugin remove akbun-refactoring@akbun-aitools --json
codex plugin remove akbun-agent-ops@akbun-aitools --json

rm -rf ~/.codex/plugins/cache/akbun-aitools
rm -rf ~/.codex/.tmp/marketplaces/akbun-aitools

codex plugin marketplace add choisungwook/akbun-aitools --json
codex plugin add akbun-writing@akbun-aitools --json
codex plugin add akbun-draw@akbun-aitools --json
codex plugin add akbun-draw-architecture@akbun-aitools --json
codex plugin add akbun-learning@akbun-aitools --json
codex plugin add akbun-presentation@akbun-aitools --json
codex plugin add akbun-analysis@akbun-aitools --json
codex plugin add akbun-pulse@akbun-aitools --json
codex plugin add akbun-refactoring@akbun-aitools --json
codex plugin add akbun-agent-ops@akbun-aitools --json

codex plugin list --json
```

## 저장소 구조와 기여

- `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`: skill의 실행 지침. 이 파일이 원본이다.
- `plugins/<plugin-name>/.claude-plugin/plugin.json`, `plugins/<plugin-name>/.codex-plugin/plugin.json`: plugin manifest. 두 파일의 `version`은 항상 같다.
- `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`: Claude Code·Codex marketplace 목록.
- `AGENTS.md`: agent가 이 저장소에서 일할 때 따르는 규칙(읽는 순서, 버전 규칙, PR 형식).
- `docs/guide_deploy_plugins.md`: plugin 생성·배포 절차.
- `docs/adr/`: 되돌리기 어려운 설계 결정 기록.
