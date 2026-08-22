---
name: akbun-draw-system-architecture
description: >
  시스템 설명·코드·문서를 분석해 진회색 프레젠테이션 스타일의 시스템 아키텍처 이미지를 만든다.
  이미지 생성 기능이 있으면 직접 생성하고, 없으면 완성형 영어 프롬프트를 출력한다. 사용자가 PowerPoint를
  요청하면 같은 스타일의 편집 가능한 16:9 PPTX 슬라이드로 제공한다.
  Trigger on: "시스템 아키텍처 그려줘", "아키텍처 이미지", "구성도 그려줘", "system architecture diagram",
  or requests to visualize system components, boundaries, flows, bottlenecks, or failure paths.
---

# 시스템 아키텍처 그리기

입력에서 핵심 컴포넌트·경계·흐름을 추려 한눈에 읽히는 시스템 아키텍처 이미지로 만든다. 참고 이미지의
피사체, 문구, 구성을 복제하지 않고 아래의 시각 언어만 재사용한다.

## 출력 모드

사용자가 요구한 형식을 먼저 확인한다.

- `.pptx`, PowerPoint, PPT slide를 명시함: [PPTX 출력](references/pptx-output.md)을 읽고 같은 스타일의
  편집 가능한 슬라이드를 만든다. 이미지도 함께 요청한 경우에만 PNG를 추가로 만든다.
- PPTX 요청이 없고 이미지 생성 가능: 아래 규칙으로 영어 프롬프트를 조립해 이미지를 직접 생성하고,
  생성 이미지와 한국어 한 줄 설명을 반환한다.
- PPTX 요청이 없고 이미지 생성 불가: 이미지를 생성하려고 시도하지 않는다. 완성된 영어 프롬프트를 `text` 코드 블록 하나에 담고,
  한국어 한 줄 설명을 덧붙인다.

골든 이미지, 예시 이미지, SVG를 만들지 않는다. 사용자가 요구하지 않은 PPTX, 중간 분석, 초안 프롬프트도 출력하지 않는다.

## 아키텍처 추상화

- 제목과 핵심 메시지를 각각 한 줄로 정한다. 핵심 메시지는 구조가 초래하는 효과나 위험을 짧게 설명한다.
- 컴포넌트는 서비스, 프로세스, 데이터 저장소, 사용자·외부 시스템 같은 배포·실행 단위 3~7개로 줄인다.
- 함수, 클래스, 파일, 세부 설정은 컴포넌트로 그리지 않는다.
- 역할이 같은 인스턴스는 하나로 묶고 `x N`처럼 수량만 표시한다.
- 흐름은 구조 이해에 필요한 관계만 남긴다. 모든 연결을 그리지 않는다.
- 코드·문서에서 확인되지 않은 컴포넌트, 경계, 관계, 장애는 만들지 않는다.
- 사용자가 강조할 문제를 주면 정상 경로와 문제 경로를 구분한다. 문제가 없으면 실패 표시를 억지로 추가하지 않는다.
- 모든 선과 라벨은 겹치지 않게 배치한다. 연결선 교차를 줄이는 방향으로 top-down 또는 left-right를 선택한다.

## 시각 스타일

참고 이미지에서 추출한 재사용 가능한 스타일 규칙이다. 소재와 실제 배치는 입력에 맞게 바꾼다.

- 캔버스: 가로 16:9, 무광에 가까운 균일한 차콜 배경 `#242424`. 질감, 그라데이션, 그림자 없음.
- 여백: 바깥쪽 안전 여백 4~6%. 상단 텍스트 영역과 아래 다이어그램 영역 사이에 큰 간격을 둔다.
- 제목: 좌상단, 큰 흰색 또는 옅은 회색 산세리프, medium weight. 장식 없이 한 줄.
- 핵심 메시지: 제목 아래에 작은 불릿 한 개로 배치한 옅은 회색 문장. 최대 두 줄.
- 컴포넌트: 채움 없는 직각 사각형, 1~2px 옅은 회색 선. 이름은 중앙 정렬한 단정한 산세리프.
- 경계: 채움 없는 흰색 파선 사각형. 경계 이름은 선의 좌상단 가까이에 작게 둔다.
- 기본 연결: 얇은 흰색 실선과 작은 삼각형 화살촉. 짧은 라벨은 선 위나 가까운 곳에 둔다.
- 강조 연결: 병목, 재시도, 실패 전파처럼 주의가 필요한 흐름만 빨강 `#F01818`으로 표시한다.
- 단계 배지: 중요한 순서가 있을 때만 작은 원형 배지를 쓴다. 첫 핵심 단계는 노랑 `#FFC400`, 위험 단계는
  빨강 `#F01818`. 원 안에는 숫자 하나만 넣는다.
- 문제 표식: 영향을 받는 컴포넌트 근처에 작은 빨간 X와 2~5단어의 짧은 문제 라벨을 둔다.
- 팔레트: 차콜, 흰색·옅은 회색, 노랑, 빨강만 쓴다. 노랑과 빨강은 전체 면적의 5% 미만으로 제한한다.
- 전체 인상: 기술 발표 슬라이드처럼 절제되고 선명하며, 멀리서도 구조와 문제 지점이 바로 보인다.
- 금지: 로고, 제품 아이콘, 3D, 입체 효과, 네온, 장식 패턴, 사진, 캐릭터, 워터마크, 범례.

## 텍스트 규칙

- 사용자가 언어를 지정하면 따른다. 지정하지 않으면 컴포넌트와 관계 라벨은 짧은 영어로 쓴다.
- 이미지 생성 모델이 정확히 렌더링할 수 있도록 제목 40자, 컴포넌트 이름 20자, 관계 라벨 5단어 이내로 줄인다.
- 프롬프트에서 모든 표시 문구를 정확한 문자열로 명시하고, 그 밖의 텍스트를 추가하지 말라고 지시한다.

## 프롬프트 조립

입력에 맞춰 아래 항목을 구체적으로 채운 하나의 영어 프롬프트를 만든다. `<...>` 토큰이나 선택지 표기를 남기지 않는다.

```text
Create a clean 16:9 system architecture diagram for a technical presentation.

CONTENT
- Title, shown exactly: "..."
- One bullet message below the title, shown exactly: "..."
- Components: ...
- Boundaries, only where they clarify ownership or deployment: ...
- Directed relationships, including exact short labels: ...
- Key sequence badges, only where order matters: ...
- Failure or bottleneck emphasis, only when supported by the source: ...

COMPOSITION
Use the upper-left area for the title and the single bullet message. Place the architecture in the
middle and lower area with generous whitespace. Choose a left-to-right or top-to-bottom reading
direction that best matches the system. Keep every box, label, and arrow separate and legible.
Do not imitate a fixed example layout; arrange the supplied components for the clearest flow.

VISUAL STYLE
A flat matte charcoal background (#242424), no texture or gradient. Large off-white sans-serif
title, smaller light-gray bullet text. Components are unfilled square-corner rectangles with thin
off-white 1–2 px outlines and centered labels. Boundaries are unfilled white dashed rectangles with
small labels near their upper-left edges. Default arrows are thin solid off-white lines with small
triangular arrowheads. Use bright red (#F01818) only for a supported failure, retry, overload, or
bottleneck path. If ordered emphasis is needed, use small circular number badges: yellow (#FFC400)
for the first key step and red (#F01818) for a risky step. Place a small red X and a very short issue
label near an affected component only when a failure is part of the supplied content. Keep yellow
and red accents below 5% of the canvas. Minimal, precise, calm, presentation-ready.

TEXT
Render only the exact title, bullet, component names, boundary labels, relationship labels, step
numbers, and issue labels listed above. Preserve their spelling exactly.

DO NOT
No logos, product icons, pictograms, characters, photos, 3D effects, shadows, gradients, neon,
decorative patterns, legends, watermarks, extra UI, extra text, overlapping shapes, or crossing
arrows.
```

## 완료 전 확인

- 컴포넌트가 3~7개이며 실행·배포 단위로 추상화됐는가?
- 원본 이미지의 피사체, 문구, 고정 배치를 복제하지 않고 시각 스타일만 사용했는가?
- 관계와 장애 표현에 입력 근거가 있는가?
- 차콜·흰색·노랑·빨강 외 색을 추가하지 않았는가?
- 이미지 생성 가능 여부에 따라 직접 생성 또는 프롬프트 출력 중 하나만 수행했는가?
- PPTX를 요청했다면 편집 가능한 16:9 슬라이드로 만들고 렌더링 QA를 마쳤는가?
- 골든 이미지나 예시 이미지를 만들지 않았는가?
