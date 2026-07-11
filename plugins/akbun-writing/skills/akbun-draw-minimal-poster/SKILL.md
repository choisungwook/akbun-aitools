---
name: akbun-draw-minimal-poster
description: >
  이미지나 주제, 문구를 받아 미니멀 포스터 카드(세리프 대문자 제목 + 흑백 플랫 일러스트 + 손글씨 캡션)
  스타일의 이미지 생성 프롬프트와 Figma/Canva에서 편집 가능한 SVG를 함께 만든다. 사용자가 포스터, 카드,
  표지, 명대사 이미지, SVG 내보내기를 언급하면 이 skill을 사용한다.
---

# 미니멀 포스터 카드 프롬프트 + SVG 생성

## 이 skill이 하는 일

사진·그림·주제·문구를 **한 장짜리 미니멀 포스터 카드**로 바꾼다. 카드는 얇은 검은 테두리 안에
상단 세리프 대문자 제목, 중앙 흑백 플랫 일러스트(포인트 색 1개), 하단 손글씨 캡션으로 구성된다.
영화 포스터를 한 컷으로 요약한 듯한, 조용하고 여백이 많은 스타일이다.

결과물은 두 가지 형태로 같은 카드를 만든다.

1. **이미지 생성 프롬프트** — GPT image, nano-banana 같은 이미지 생성 모델(AI agent)에 그대로 붙여넣는 영어 프롬프트.
2. **SVG 파일** — Figma나 Canva로 불러와 직접 수정할 수 있는 벡터 파일. 텍스트가 `<text>` 요소로 남아 있어 편집 가능하다.

`akbun-draw-sketchbook-card`(연필 개념 카드), `akbun-draw-storytellingimage`(장면별 삽화)와 짝이 되는
"명장면 포스터" 버전이다. 블로그 표지, 인용구 카드, 시리즈 썸네일에 어울린다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 코드 블록 하나.
2. **SVG 파일** — 작업 디렉터리에 `<slug>.svg`로 저장하고 경로를 알려준다.
3. **한국어 한 줄 설명** — 어떤 장면·제목·캡션으로 구성했는지 1~2문장.

## 입력 다루기

사용자가 준 것에 따라 부족한 부분만 skill이 채운다.

- **이미지 + 문구**: 이미지에서 장면(피사체, 배경, 구도)을 읽어내고, 문구는 그대로 제목/캡션에 넣는다. 문구를 다듬거나 번역하지 않는다.
- **이미지만**: 이미지 내용을 분석해 제목(영어 대문자 한 단어~짧은 구)과 캡션(장면의 정서를 담은 한 문장)을 skill이 만들고, 사용자에게 만든 문구를 함께 보여준다.
- **주제·문구만 (이미지 없음)**: 주제를 대표하는 단순한 장면을 skill이 정한다. 피사체 1~2개, 배경 1개를 넘지 않는다.
- 제목과 캡션 중 하나만 있으면 나머지 하나만 만든다.

## 카드 구성 요소

- **테두리**: 카드 가장자리를 두르는 얇은 검은 직사각형 프레임.
- **제목**: 상단 중앙, 세리프 대문자, 넓은 자간. (예: `D E E P   D I V E`)
- **일러스트**: 지평선으로 상하가 나뉜 배경 위의 플랫 벡터 장면. 주 피사체는 크게, 보조 요소는 작게.
- **캡션**: 하단 중앙, 손글씨 느낌의 한 문장. (예: `Down here, we only have each other.`)

## 스타일이 정체성이다

이 skill이 지키는 것은 **스타일**이지 특정 장면이 아니다. 어떤 입력이 와도 아래 두 가지는 항상 같다.

1. **레이아웃**: 테두리 프레임, 상단 세리프 대문자 제목, 지평선으로 나뉜 배경, 하단 손글씨 캡션과 그 사이 여백.
2. **그림 언어**: 균일한 검은 외곽선의 플랫 벡터, 그레이스케일 + 포인트 색 1개, 디테일 억제.

반대로 **장면 구성(피사체가 무엇인지, 몇 개인지, 어디에 서는지)은 입력에 맞게 자유**다. 인물 없이 사물
하나만 있어도 되고, 풍경만 있어도 된다. 장면을 스타일에 끼워 맞추지 말고, 스타일로 장면을 그린다.
장면에 인물·캐릭터가 필요하면 akbun 마스코트 고래(`akbun-mascot-whale` skill의 캐릭터 스펙)를 이
스타일의 플랫 벡터로 그린다.

## 레이아웃 스펙 (고정)

프롬프트와 SVG 모두 아래 수치를 그대로 따른다. 좌표는 인스타그램 세로형 1080×1350 기준이다.

- **비율**: 세로형 4:5, 1080×1350 (SVG viewBox `0 0 1080 1350`).
- **테두리**: 가장자리에서 6 안쪽, 굵기 3.5의 검은 프레임. 모든 요소 위에 얹는다.
- **제목**: 가로 중앙 정렬, 베이스라인 y=146 (높이의 약 11%). 자간을 글자 크기의 절반 이상으로 넓게.
- **지평선**: y=580 (높이의 43%). 위는 밝은 회색 하늘/배경, 아래는 중간 회색 바닥.
- **바닥**: 아래로 갈수록 조금 어두워진다. 짧은 흰색 대시 마크 6~9개를 흩뿌린다.
- **캡션**: 가로 중앙 정렬, 베이스라인 y=1262 (높이의 약 93%).
- **여백**: 제목 위, 캡션 아래, 좌우 모두 이 좌표에서 자연스럽게 생기는 여백을 유지한다. 어떤 요소도 테두리에 닿지 않는다.

## 권장 구도 (장면에 맞게 조절)

장면 구성은 자유지만, 막막할 때는 아래 구도가 이 스타일과 잘 어울린다.

- **주 피사체**는 중앙 또는 약간 옆으로 비켜 크게 세운다. 지평선 위로 머리가 올라가면 보기 좋다.
- **보조 피사체**는 반대쪽 중경에 주 피사체의 60% 이하 크기로 둔다. 없어도 된다.
- **큰 오브젝트**(탈것·건물 등)는 지평선에 걸쳐 피사체 뒤에 낮게 눕힌다. 없어도 된다.
- 피사체의 발 위치는 캡션과 겹치지 않게 y≈1150 위에서 끝낸다.

## 비주얼 스타일 (고정)

- **선**: 모든 형태에 균일한 굵기(3~3.5)의 검은 외곽선(`#1A1A1A`). 손그림 느낌의 단순한 플랫 벡터.
- **색**: 흑백 그레이스케일(흰색 `#EDEDEA`, 밝은 회색 `#E9E9E6`, 중간 회색 `#ABABA7`, 어두운 회색 `#4A4A46`, 검정 `#2E2E2C`)에 **포인트 색 딱 1개**.
- **포인트 색**: 기본은 주황 `#D96B2B`. 헬멧 바이저, 창문, 램프처럼 **작은 면적에만** 쓴다. 주제에 맞으면 다른 색 1개로 바꿔도 되지만 개수는 늘리지 않는다.
- **디테일 억제**: 피사체당 형태 10개 안팎. 얼굴·질감·그림자 묘사를 넣지 않는다. 바닥 그림자는 납작한 타원 하나면 충분하다.

## 폰트 규칙 (저작권 무료)

모두 SIL Open Font License 폰트만 쓴다. 상업적 사용에 제약이 없다.

- **제목**: `Cinzel` (대체: `Playfair Display`). 세리프 대문자 전용.
- **캡션(영문)**: `Patrick Hand`. 둥근 손글씨체.
- **캡션(한글)**: `Nanum Pen Script` (대체: `Gaegu`).
- SVG에는 `font-family="Cinzel, 'Playfair Display', Georgia, serif"`처럼 대체 폰트까지 함께 선언한다.

## 텍스트 언어 규칙

- **프롬프트는 영어**로 쓴다. 그림에 들어갈 텍스트는 `reading exactly: "..."` 형태로 철자까지 지정한다.
- **제목은 영어 대문자**가 기본이다. 사용자가 한글 제목을 원하면 그대로 쓰되 폰트를 한글 세리프(`Noto Serif KR`, OFL)로 바꾼다.
- **캡션은 사용자가 준 언어 그대로** 넣는다. 길면 이미지 모델이 글자를 틀리므로 한 문장을 넘기지 않는다.

## 작업 순서

1. **입력 파악.** 이미지가 있으면 피사체·배경·구도를 읽는다. 제목·캡션이 있으면 그대로, 없으면 만든다.
2. **장면 단순화.** 주 피사체 1개, 보조 피사체 0~1개, 큰 오브젝트 0~1개로 줄인다. 그 이상은 버린다.
3. **포인트 색 위치 결정.** 장면에서 시선이 모일 작은 면적 하나를 고른다.
4. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채우고, 쓰지 않는 줄은 지운다.
5. **SVG 작성.** 아래 `SVG 작성 규칙`을 따라 같은 장면을 그려 파일로 저장한다.
6. **출력.** 프롬프트 블록 + SVG 파일 경로 + 한국어 한 줄 설명을 출력한다.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. `(delete if none)`이 붙은 줄은 해당 요소가 없으면 지운다.

```text
A minimal flat vector poster card, portrait 4:5 aspect ratio (1080x1350, Instagram portrait),
framed by a thin black rectangular border just inside the card edge. Muted monochrome palette:
off-white, light gray, mid gray, near-black — plus exactly ONE accent color,
<ACCENT COLOR, e.g. "burnt orange">, used only on small areas.

TOP (inside the frame, upper 11% of the card): a movie-title-style heading in an elegant serif
typeface, all capital letters with very wide letter-spacing, centered, black,
reading exactly: "<TITLE>".

SCENE (middle of the card): a flat vector illustration with uniform bold black outlines and
simple geometric shapes, no facial details, no textures. A horizon line at 43% of the card
height separates a pale gray sky from a mid-gray ground that darkens slightly toward the
bottom; short white dashes are scattered on the ground.
- Main subject, large, standing slightly off-center: <MAIN SUBJECT — one sentence,
  e.g. "a diver in a bulky suit facing the viewer, helmet visor in the accent color">.
- Secondary subject, smaller, in the mid-ground on the other side: <SECONDARY SUBJECT>.
  (delete if none)
- Behind them, lying low across the horizon: <LARGE OBJECT, e.g. "a sleek dark submarine
  resting on the ground">. (delete if none)

BOTTOM (inside the frame, lower 7% of the card): a single handwritten-style caption line,
centered, dark gray, reading exactly: "<CAPTION>".

STYLE: quiet, spare, lots of negative space, storybook-flat, uniform outline weight,
clean composition, very legible lettering.

DO NOT: add any color beyond the grays and the single accent color. Do not add extra text,
logos, textures, gradients on the subjects, or facial features. Do not misspell any text.
Do not let any element touch the border frame.
```

## SVG 작성 규칙

SVG는 skill이 직접 그린다. 형태 배치와 수치는 아래 `레이아웃 스펙 (고정)`과 `비주얼 스타일 (고정)` 규칙을 기준으로 삼는다.

- `viewBox="0 0 1080 1350"`(인스타그램 세로형 4:5), 외부 이미지·스크립트 없는 순수 SVG 1.1로 작성한다. Figma와 Canva가 그대로 불러온다.
- 레이어 순서: 배경(하늘→바닥 그라디언트) → 대시 마크 → 큰 오브젝트 → 보조 피사체 → 주 피사체 → 제목 `<text>` → 캡션 `<text>` → 테두리 프레임.
- 제목·캡션은 `<text>`로 남긴다. Figma에서는 그대로 편집되고, 폰트가 없으면 대체 폰트로 표시되므로 사용자에게 Google Fonts에서 Cinzel/Patrick Hand(한글이면 Nanum Pen Script)를 설치하라고 안내한다.
- Canva는 SVG의 `<text>`를 지원하지 않는 경우가 있다. 사용자가 Canva용이라고 하면 텍스트를 지우고 도형만 있는 버전을 하나 더 저장한 뒤, 문구는 Canva에서 직접 얹으라고 안내한다.
- 피사체는 `rect`, `circle`, `ellipse`, `path` 같은 기본 도형 10개 안팎으로 그린다. 정밀함보다 실루엣이 읽히는 게 중요하다.
- 저장 후 가능하면 렌더링(headless 브라우저 스크린샷 등)으로 형태가 깨지지 않았는지 확인한다.

## 예시 (gold reference)

이 예시는 이 스타일을 적용한 완성 결과다. 새 작업의 품질 기준으로 삼는다.

입력 예:

```text
심해 탐사를 주제로 포스터 카드 하나 만들어줘. 제목은 DEEP DIVE.
```

skill이 한 판단: 캡션이 없어서 장면의 정서(깊은 곳의 고립과 동료애)를 담은 한 문장을 만들었다.
장면은 정면을 보는 다이버(주 피사체, 왼쪽), 등을 보이는 작은 다이버(보조, 오른쪽), 지평선에 걸친
잠수함(큰 오브젝트)으로 구성했고, 포인트 색은 두 다이버의 헬멧 바이저에만 썼다.

출력 프롬프트:

```text
A minimal flat vector poster card, portrait 4:5 aspect ratio (1080x1350, Instagram portrait),
framed by a thin black rectangular border just inside the card edge. Muted monochrome palette:
off-white, light gray, mid gray, near-black — plus exactly ONE accent color, burnt orange,
used only on small areas.

TOP (inside the frame, upper 11% of the card): a movie-title-style heading in an elegant serif
typeface, all capital letters with very wide letter-spacing, centered, black,
reading exactly: "DEEP DIVE".

SCENE (middle of the card): a flat vector illustration with uniform bold black outlines and
simple geometric shapes, no facial details, no textures. A horizon line at 43% of the card
height separates a pale gray sky from a mid-gray ground that darkens slightly toward the
bottom; short white dashes are scattered on the ground.
- Main subject, large, standing slightly left of center: a deep-sea diver in a bulky suit
  facing the viewer, helmet visor in the accent color, a small control panel on the chest.
- Secondary subject, smaller, mid-ground right: a second diver seen from behind, a thin
  sliver of the accent color on the edge of the helmet.
- Behind them, lying low across the horizon: a sleek dark submarine resting on the ground,
  a pale deck stripe with small dark windows.

BOTTOM (inside the frame, lower 7% of the card): a single handwritten-style caption line,
centered, dark gray, reading exactly: "Down here, we only have each other.".

STYLE: quiet, spare, lots of negative space, storybook-flat, uniform outline weight,
clean composition, very legible lettering.

DO NOT: add any color beyond the grays and the single accent color. Do not add extra text,
logos, textures, gradients on the subjects, or facial features. Do not misspell any text.
Do not let any element touch the border frame.
```

한국어 한 줄 설명: 제목 DEEP DIVE 아래에 정면 다이버·뒷모습 다이버·잠수함으로 심해 탐사 장면을 만들고,
헬멧 바이저에만 주황 포인트를 줘서 "Down here, we only have each other." 캡션으로 마무리했습니다.

## 완료 전 확인

- 사용자가 준 제목·캡션을 바꾸지 않고 그대로 넣었는가? (없을 때만 skill이 만든다)
- 그림 속 모든 텍스트를 `reading exactly: "..."`로 철자까지 지정했는가?
- 세로형 4:5(1080×1350)와 레이아웃 수치(제목 11%, 지평선 43%, 캡션 93%, 테두리)를 프롬프트와 SVG 양쪽에 지켰는가?
- 스타일(레이아웃·그림 언어)만 고정하고 장면 구성은 입력에 맞게 자유롭게 정했는가?
- 그레이스케일 + 포인트 색 1개 규칙을 지켰는가? 포인트 색이 작은 면적에만 있는가?
- 폰트가 전부 SIL OFL(Cinzel, Patrick Hand, Nanum Pen Script 등)인가?
- SVG를 파일로 저장하고 경로를 알려줬는가? 텍스트가 `<text>` 요소로 편집 가능한가?
- 프롬프트를 그대로 복사해 이미지 생성 모델에 붙여넣을 수 있는 한 블록으로 출력했는가?
