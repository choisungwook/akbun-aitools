# Changelog

## 2026-05-25 #10

- `kubernets-network-drawio` 스킬의 YAML 설명을 정정했다.
- YAML 입력은 `example.yaml`을 읽는 것이 아니라, 사용자가 넘긴 YAML 파일 또는 YAML 형식 텍스트를 읽도록 명확히 했다.
- `example.yaml`은 실제 입력이 아니라 작성 예시로만 참고한다고 정리했다.
- `akbun-writing` plugin manifest 버전을 마지막 버전 `1.0.8`에서 `1.0.9`로 올렸다.

## 2026-05-25 #9

- `kubernets-network-drawio` 스킬에서 어색한 한국어 기술 용어를 자연스러운 영어 표현으로 정리했다.
- `작업 루프`를 `Workflow`로 바꾸고, `topology`, `export`, `validation`, `assumptions`, `boundary`, `external system` 표현을 사용하도록 조정했다.
- `akbun-writing` plugin manifest 버전을 마지막 버전 `1.0.7`에서 `1.0.8`로 올렸다.

## 2026-05-25 #8

- `kubernets-network-drawio` 스킬 본문을 한국어 중심으로 변경했다.
- `agents/openai.yaml` 표시 이름, 짧은 설명, 기본 프롬프트를 한국어로 변경했다.
- 이전에 고정한 frontmatter `description: draw kubernetes network with draw.io`는 유지했다.
- `akbun-writing` plugin manifest 버전을 마지막 버전 `1.0.6`에서 `1.0.7`로 올렸다.

## 2026-05-25 #7

- `kubernets-network-drawio` 스킬을 `grill-with-docs` 스타일처럼 `<what-to-do>`와 `<supporting-info>` 구조로 다듬었다.
- 자연어, 사진, YAML, 기존 draw.io 입력을 모두 topology로 통합하고, 가능한 경우 파일 생성까지 진행하도록 운영 루프를 정리했다.
- 입력이 불완전해도 보수적 가정과 `확인 필요`를 분리해 다이어그램 생성을 막지 않도록 ambiguity 처리 규칙을 추가했다.
- `agents/openai.yaml` 기본 프롬프트에 자연어, 사진, YAML 입력을 반영했다.

## 2026-05-25 #6

- `kubernets-network-drawio` 스킬의 입력 모드를 자연어, 사진, YAML로 명확히 했다.
- 사진 입력 시 topology와 레이아웃을 해석하고, 불명확한 텍스트나 edge 방향은 `확인 필요`로 묻도록 규칙을 추가했다.
- 기본 산출물 위치를 `~/Downloads/<name>.drawio`와 `~/Downloads/<name>.drawio.png`로 명시했다.

## 2026-05-25 #5

- `kubernets-network-drawio` 스킬의 YAML 입력을 선택 사항으로 명확히 하고 `example.yaml`을 추가했다.
- workload가 지정되면 Pod를 생략할 수 있도록 intake, 레이아웃 규칙, 검증 스크립트를 수정했다.
- ingress controller 이름, 여러 actor 구분, LB domain 매핑 규칙을 추가했다.

## 2026-05-24 #4

- `kubernets-network-drawio` 스킬 추가: draw.io Desktop CLI로 Kubernetes 서비스 네트워크 아키텍처를 `.drawio`로 만들고 PNG/SVG/PDF로 export한다.
- 외부 호출 `User -> LB -> optional ingress controller -> Service -> Pod` 흐름과 Pod 외부 호출을 그리는 레이아웃 규칙을 추가했다.
- draw.io 공식 XML validation checklist를 반영한 정적 검증 스크립트와 기준 템플릿을 추가했다.

## 2026-05-23 #5

- `akbun-drawio-aws-vpc` 스킬을 기준 이미지 유사도 검증 중심에서 재사용 가능한 AWS VPC 레이아웃 가이드 중심으로 재정리했다.
- `a.png`는 복제 대상이 아니라 스타일/구조 참고 예시로만 다루도록 명시했다.
- 사용자가 검증 이미지를 제공하지 않아도 XML 정적 검증, draw.io CLI export, PNG 육안 확인으로 완료할 수 있게 작업 순서를 바꿨다.
- 일본어 plain text 라벨, 48x48 AWS icon, group nesting, orthogonal edge, full background, Managed Services/VPC Endpoint 배치 규칙을 reference에 추가했다.
- reference PNG 비교 스크립트를 제거하고, XML 검증 스크립트가 배경, group size, icon size, edge style, plain label 규칙을 검사하도록 수정했다.
- `akbun-writing` plugin manifest 버전을 `1.0.8`로 올렸다.

## 2026-05-23 #4

- `akbun-drawio-aws-vpc` 스킬 추가: draw.io Desktop CLI와 AWS icon pack으로 AWS VPC 아키텍처 XML을 만들고 PNG로 export한다.
- 공식 draw.io XML/CLI 문서에서 필요한 내용만 한국어 reference로 정리했다.
- XML 검증, CLI export, PNG 유사도 비교 스크립트와 AWS VPC 템플릿을 추가했다.
- 사용자 기준 PNG와 비교하는 검증 게이트를 필수화하고 self-compare를 실패 처리한다.
- `a.png` 기준 구조에 맞춰 multi-AZ AWS VPC 템플릿을 보강하고, foreground 기반 유사도 점수로 검증했다.
- 번호 동그라미와 Route53을 제거하고, 같은 subnet 내부 컴포넌트의 위쪽 정렬/동일 크기, 직선 화살표, 라벨 겹침 방지 규칙을 추가했다.
- 기존 기준 PNG에서 의도적으로 제거한 영역만 제외하는 `--ignore-rect` 비교 옵션과 draw.io 렌더링 오차용 `--tolerance` 옵션을 추가하고 95% 검증 기준으로 상향했다.
- `akbun-writing` plugin manifest 버전을 `1.0.7`로 올렸다.

## 2026-05-17 #3

- `akbun-md-to-notion` 스킬을 `ntn api` 우선, Notion MCP fallback 구조로 정리했다.
- Codex automation 무인 실행을 위해 파일 조회, hash 계산, state 저장, `ntn` 호출 관련 allowed-tools를 추가했다.
- `notion_sync`/`notion_page_id` 메타데이터와 payload hash 기반 skip 규칙을 추가했다.
- 자동화 실행에서는 `notion_sync: true` 파일의 기존 Notion page 덮어쓰기를 사용자 승인 없이 진행하도록 명시했다.
- `akbun-writing` plugin manifest 버전을 `1.0.5`로 올렸다.

## 2026-05-10 #2

- `akbun-learning-language-blog` 스킬 추가: 영어공부/일본어공부 노트를 한국어 개인 일기형 학습 기록 초안으로 정리한다.
- trigger는 명시적인 영어공부/일본어공부 정리 요청으로 좁게 유지한다. 일반 게시/업로드, 기술블로그, 발음, 번역, 회사명/수업명/기관명 기반 요청은 제외한다.
- `요약`, `목차`, `마무리`, `참고자료` 없이 공부 날짜가 먼저 보이는 일기형 출력을 위해 템플릿과 스타일 가이드를 추가한다.

## 2026-04-19 #1

- akbun-writing SKILL.md: 따옴표 누락(여는 따옴표), 문단 규칙 중복/어색 표현, `# 참고자료` 섹션의 "이유는 두 가지다" 누락된 두 번째 이유 정리
- akbun-writing SKILL.md: 안티패턴 6개 중 5개에 비포/애프터 한 줄 예시 추가 (Opus 격식 디폴트 교정)
- akbun-writing SKILL.md: 1인칭 소유권 섹션에 모델 디폴트 교정 한 줄, 미완성 인정 섹션에 좋은 예 한 줄 추가
