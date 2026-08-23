---
name: akbun-draw-learning-mono
disable-model-invocation: true
description: >
  논문·책·문서·코드·개념 설명을 학습 이해를 돕는 흑백 미니멀 16:9 설명 이미지로 만든다. 흰 배경 +
  검정·진회색 제목/본문 + 중간 회색 보조 설명 + 이해에 꼭 필요한 곳에만 쓰는 최소 강조색으로 구성하며,
  Figure 중심·수식 중심·과정 설명·비교 등 내용에 맞는 레이아웃을 매번 다르게 고른다. 주제가 여러 개면
  주제마다 이미지를 따로 만들고, 연관관계가 있는 것만 한 장에 묶는다. 이미지 생성 기능이 있으면 직접
  생성하고, 없으면 완성형 영어 프롬프트를 출력한다. 그림 속 글자는 짧은 영어, 발표 대본은 한국어로
  채팅에 함께 낸다. Trigger on: "이 논문 그림으로 설명해줘", "학습용 이미지 만들어줘", "개념 시각화",
  "이 Figure 쉽게 다시 그려줘", "공부용 그림", "강의자료 그림", "learning diagram", "explain this
  paper visually", or any request to turn study material into minimal black-and-white explanatory images.
---

# 학습용 흑백 미니멀 설명 이미지

논문·책·문서·코드·개념을 **공부하는 사람이 한눈에 이해하도록** 흑백 미니멀 16:9 이미지로 만든다.
목적은 예쁜 그림이 아니라 이해다. 그래서 장식은 전부 걷어내고, 화면에 남는 요소는 전부 이해에 기여해야 한다.

참고 자료를 받았더라도 그 배치를 그대로 베끼지 않는다. 자료에서 **무엇을 이해해야 하는지**를 뽑아
아래 시각 언어로 다시 그린다.

## 출력 모드

- **이미지 생성 가능**: 아래 규칙으로 영어 프롬프트를 조립해 이미지를 직접 생성하고, 이미지와 한국어
  발표 대본을 채팅에 함께 낸다. 프롬프트 원문은 굳이 보여주지 않는다.
- **이미지 생성 불가**: 생성을 시도하지 않는다. 완성된 영어 프롬프트를 이미지 한 장당 `text` 코드 블록
  하나에 담고, 같은 이미지의 한국어 발표 대본을 그 아래에 붙인다.

SVG, PPTX, 골든 이미지, 중간 분석, 초안 프롬프트는 요청받지 않으면 만들지 않는다.

## 주제 나누기

한 장에 다 넣으려다 복잡해지는 것이 이 종류 이미지가 실패하는 가장 흔한 이유다. 그래서 **분량이 아니라
주제**로 나눈다.

- 자료에서 독립적으로 이해할 수 있는 주제를 먼저 나열한다. 주제 하나당 이미지 하나가 기본이다.
- **연관관계가 있을 때만 한 장에 묶는다.** 연관관계란 앞 단계의 출력이 뒷 단계의 입력이 되거나(과정),
  같은 축 위에서 맞대어 봐야 의미가 생기는(비교) 관계다. 단순히 같은 장(chapter)에 있다는 이유로 묶지 않는다.
- 한 장 안의 핵심 설명은 3~5개로 유지한다. 큰 Figure나 수식 하나가 핵심인 장은 억지로 개수를 채우지 않는다.
- 여러 장을 만들면 제목 위치, 여백, 글자 크기, 페이지 번호를 전부 동일하게 유지한다. 장마다 바뀌어도
  되는 것은 다이어그램 레이아웃뿐이다.

## 레이아웃 고르기

페이지마다 같은 틀을 반복하지 않는다. 내용의 성격이 레이아웃을 결정한다.

- **Figure 중심**: 다이어그램 하나를 크게 두고 짧은 라벨과 한두 줄 설명만 곁들인다. Figure를 작게 만들지 않는다.
- **수식 중심**: 수식을 화면 중앙에 크게 두고, 각 기호가 무엇인지 가리키는 짧은 주석을 배치한다.
- **과정 설명**: 단계를 흐름으로 잇는다. 방향은 내용에 맞게 정한다. 좌→우, 위→아래를 기계적으로 고르지 않고,
  **화살표가 가장 적게 꺾이고 겹치지 않는 방향**을 고른다. 순환이면 원형 배치도 좋다.
- **비교**: 두 대상을 같은 축(같은 높이, 같은 크기, 같은 항목 순서)에 놓아야 차이가 보인다. 축이 어긋나면 비교가 아니다.

레이아웃과 무관하게 지키는 것:

- 선과 라벨은 서로 겹치지 않는다. 화살표 교차가 생기면 배치를 바꾼다.
- 제목, 본문, Figure 사이에 넉넉한 간격을 둔다.
- 본문이 텅 비어 보이지 않게 하되 긴 문단을 그대로 넣지 않는다. 긴 설명은 발표 대본으로 뺀다.

## 시각 스타일

- **캔버스**: 16:9, 흰 배경 `#FFFFFF`. 질감, 그라데이션, 배경 이미지 없음.
- **여백**: 바깥 안전 여백 5~7%. 상단 텍스트 영역과 아래 그림 영역 사이를 크게 띄운다.
- **제목**: 좌상단, 큰 검정 `#111111` 산세리프 한 줄. 밑줄이나 장식 없음.
- **본문**: 진회색 `#333333`, 짧은 문장이나 불릿.
- **보조 설명**: 중간 회색 `#767676`. 라벨, 주석, 캡션에 쓴다.
- **도형**: 채움 없는 직각 또는 살짝 둥근 사각형, 1~2px 진회색 선. 이름은 중앙 정렬.
- **묶음 경계**: 회색 파선 사각형. 이름은 선의 좌상단 가까이 작게.
- **연결선**: 얇은 진회색 실선과 작은 삼각형 화살촉. 라벨은 선 위에 2~4단어로.
- **강조색**: 원본 Figure나 차트를 이해하는 데 꼭 필요한 곳에만 쓴다. 색이 정보를 나르지 않으면 회색으로 둔다.
  기본 강조는 빨강 `#D93025` 하나이며, 원본이 색으로 계열을 구분하고 있을 때만 파랑 `#1A73E8`을 두 번째로 더한다.
  강조색 면적은 화면의 5% 미만.
- **출처**: 슬라이드 하단에 작은 중간 회색 글씨로 원본 페이지·Figure 번호·출처를 표시한다. 여러 장이면
  우하단에 `n / N` 페이지 번호를 같은 위치에 둔다.
- **금지**: 그라데이션, 장식용 아이콘, 화려한 도형, 배경 이미지, 로고, 제품 아이콘, 사진, 캐릭터, 워터마크,
  네온, 그림자, 범례.

참고할 PPT를 사용자가 주면 색·여백·글꼴·분위기는 비슷하게 맞추되 배치는 복사하지 않는다.

## 3D는 언제 쓰나

기본은 2D다. 3D는 **2D로는 설명이 안 되는 구조**일 때만 쓴다. 텐서의 차원, 메모리 블록의 적층, 겹쳐 쌓인
레이어처럼 "깊이 축 자체가 설명 대상"인 경우다.

쓸 때도 스타일은 유지한다. 흑백 아이소메트릭 선화로 그리고, 면은 비우거나 옅은 회색으로만 채운다.
그림자, 질감, 원근 왜곡, 반사는 쓰지 않는다.

## 텍스트 규칙

이미지 생성 모델은 한글을 자주 깨뜨린다. 그래서 **그림 안은 영어, 설명은 한국어**로 나눈다.

- 그림 속 제목·컴포넌트 이름·라벨·주석은 짧은 영어로 쓴다. 사용자가 언어를 지정하면 그것을 따른다.
- 제목 40자, 이름 20자, 라벨 4단어 이내로 줄인다. 짧을수록 정확히 렌더링된다.
- 프롬프트에는 표시할 문구를 정확한 문자열로 명시하고, 그 밖의 텍스트를 넣지 말라고 지시한다.
- 발표 대본은 한국어로 쓴다. 이미지에 넣지 않은 자세한 설명, 배경, 주의점이 여기 들어간다.

## 프롬프트 조립

이미지 한 장마다 아래 항목을 구체적으로 채운 영어 프롬프트를 하나 만든다. `<...>` 토큰이나 선택지 표기를 남기지 않는다.

```text
Create a clean 16:9 educational explainer figure for study material, on a pure white background.

CONTENT
- Title, shown exactly: "..."
- Supporting lines below the title, shown exactly: ...
- Layout type: <figure-centered | formula-centered | process | comparison>
- Elements and their exact labels: ...
- Directed relationships with exact short labels: ...
- Emphasis that is required to understand the original figure, if any: ...
- Source note at the bottom, shown exactly: "..."

COMPOSITION
Title at the upper left, supporting lines directly under it, then a generous gap before the main
figure, which occupies the largest area of the canvas. Choose the reading direction and arrangement
that keeps arrows short and non-crossing rather than defaulting to left-to-right. Keep every box,
label, and arrow separate and legible. Balance the figure against the text so the figure never
becomes small.

VISUAL STYLE
Flat pure white background. Black (#111111) sans-serif title, dark gray (#333333) body text, medium
gray (#767676) annotations and the bottom source note. Shapes are unfilled rectangles with thin
1-2 px dark gray outlines and centered labels. Grouping boundaries are gray dashed rectangles with
small labels near their upper-left edges. Arrows are thin dark gray solid lines with small
triangular arrowheads. Use accent color only where color is required to understand the original
figure: red (#D93025) as the single accent, adding blue (#1A73E8) only when the source distinguishes
two series by color. Keep accent color under 5% of the canvas. Minimal, precise, calm, textbook-clear.

TEXT
Render only the exact title, supporting lines, element names, relationship labels, annotations, and
source note listed above. Preserve their spelling exactly.

DO NOT
No gradients, decorative icons, ornamental shapes, background imagery, logos, product icons, photos,
characters, shadows, neon, watermarks, legends, extra UI, extra text, overlapping shapes, or
crossing arrows.
```

깊이 축 자체가 설명 대상일 때만 `VISUAL STYLE`에 다음 한 줄을 더한다.

```text
Draw the stacked structure as a flat black-and-white isometric line drawing with unfilled or
light-gray faces, no shading, no texture, no perspective distortion.
```

## 결과물 형식

이미지 한 장마다 다음 두 가지를 짝지어 낸다.

1. **이미지**(생성 가능할 때) 또는 **영어 프롬프트 코드 블록**(생성 불가할 때)
2. **한국어 발표 대본** — 이 장에서 무엇을 이해해야 하는지 3~6문장. 이미지에 넣지 않은 세부 설명을 담는다.

여러 장이면 장마다 이 짝을 반복하고, 맨 앞에 어떤 주제로 몇 장을 나눴는지 한 줄로 밝힌다.

## 완료 전 확인

- 주제 단위로 나눴는가? 한 장에 묶은 것들은 실제로 연관관계(과정 또는 비교)가 있는가?
- 레이아웃을 내용에 맞게 골랐는가? 여러 장이 같은 틀을 반복하고 있지 않은가?
- 화살표와 라벨이 겹치지 않고, 화살표가 교차하지 않는가?
- 흰 배경·검정/진회색·중간 회색을 지켰고, 강조색은 이해에 필요한 곳에만 5% 미만으로 썼는가?
- Figure가 충분히 크고, 설명문과 균형이 맞는가?
- 그림 속 글자는 짧은 영어이고, 긴 설명은 한국어 대본으로 뺐는가?
- 하단에 출처를 표시했고, 여러 장이면 페이지 번호 위치가 모든 장에서 같은가?
- 3D를 썼다면 깊이 축이 실제 설명 대상이었는가?
- 이미지 생성 가능 여부에 따라 직접 생성 또는 프롬프트 출력 중 하나만 했는가?
