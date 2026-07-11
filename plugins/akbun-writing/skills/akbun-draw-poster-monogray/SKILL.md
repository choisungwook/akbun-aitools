---
name: akbun-draw-poster-monogray
description: >
  아무 소재(주제·글·이미지·코드)를 "손그림 진회색 잉크 라인 + 플랫 회색 + 오렌지 포인트 하나 +
  off-white 종이"의 테크북 삽화 스타일로 그리는 결과물을 만든다. 이 skill이 고정하는 건 그림체와
  색감(스타일)이고, 구도는 소재에 맞춰 자유롭게 잡는다. 산출물은 두 가지다: 이미지 생성 모델(GPT
  image, nano-banana 등)에 그대로 넣을 영어 프롬프트와, Figma/Canva로 가져와 편집할 수 있는 SVG 파일.
  Trigger on: "이 스타일로 그려", "모노 그레이 스타일", "회색 손그림 삽화", "오렌지 포인트 삽화",
  "테크북 삽화 프롬프트", "monogray poster", "flat gray illustration", "포스터 SVG",
  "figma svg 삽화", "canva svg 삽화", or any request to render a subject in this hand-drawn
  gray-with-orange illustration style as a prompt or SVG.
---

# 모노 그레이 삽화 스타일 프롬프트 + SVG 생성

## 이 skill이 하는 일

아무 소재를 **하나의 정해진 그림 스타일**로 그린 결과물을 만든다. 그 스타일은 참고 그림 한 장에서
뽑아낸 것이다: 균일한 진회색 잉크 라인, 플랫한 회색 면, off-white 종이, 그리고 **딱 하나의 따뜻한
오렌지 포인트**. 친근한 기술책 삽화 같은 느낌이다.

**이 skill이 고정하는 것은 "그림체와 색감"뿐이다.** 무엇을 그리는지(소재·구도)는 매번 입력에 맞게
자유롭게 정한다. 참고 그림이 "사람이 모니터를 보는 장면"이었다고 해서 그 장면을 재현하는 게 아니다.
그 그림에서 읽어낸 **선·면·색 처리 방식**을 인물이든, 사물이든, 작은 장면이든 새 소재에 입힌다.
장면에 인물·캐릭터가 필요하면 akbun 마스코트 고래(`akbun-mascot-whale` skill의 캐릭터 스펙)를 이
그림체로 그린다.

산출물은 그림이 아니라 두 가지다.

1. **영어 이미지 생성 프롬프트** — GPT image나 nano-banana 같은 이미지 생성 모델에 그대로 붙여넣는다.
2. **SVG 파일** — 같은 소재를 이 스타일의 벡터로 그린 파일. Figma나 Canva로 가져와 색·문구를 편집한다.

`akbun-generateimage-code`, `akbun-draw-sketchbook-card`처럼 "정해진 비주얼 스타일로 그림 프롬프트를
만드는" 계열이며, 이 skill은 특정 구도가 아니라 **스타일 자체**를 재사용한다는 점이 다르다. SVG도
함께 만든다.

## 스타일 정의 (고정 — 절대 바꾸지 않는다)

무엇을 그리든 아래 그림체·색감은 그대로 유지한다.

- **매체**: 균일한 중간 굵기의 진회색 잉크 아웃라인으로 그린 손그림 삽화. 면은 플랫한 회색 톤으로만
  칠한다. 그라데이션·질감·해칭·사진 음영 없음.
- **종이/배경**: 따뜻한 off-white `#F4F2ED`. 여백을 넉넉히 둔다.
- **잉크 라인**: `#3A3A3A`, 둥근 모서리·둥근 끝(round join/cap). 손으로 그린 듯 부드럽고 균일하다.
- **회색 면**: 밝은 회색 `#E3E3E3`, 중간 회색 `#C9C9C9` 두 톤. 모니터/화면류 어두운 면은 `#5A5A5A`.
- **오렌지 포인트 (핵심 규칙)**: 따뜻한 오렌지 `#E8833A` **하나만** 쓴다. 화면에서 **가장 중요한
  한 요소**에만 칠한다(예: 핵심 사물, 감정을 나타내는 기호, 강조할 부분). 그 외 전부 무채색 회색이다.
- **글씨**: 그림 안에 글자가 들어가면 손글씨 느낌으로 쓴다. 한국어 가능. 길수록 이미지 모델이 글자를
  틀리므로 짧게 유지한다.
- **분위기**: 친근하고 차분하며 대비가 또렷하고 여백이 많은, 기술책 삽화 톤.

## 구도 (소재에 맞춰 자유)

구도는 고정하지 않는다. 소재에 가장 잘 맞는 배치를 고르되, 아래 원칙만 지킨다.

- **초점 하나.** 화면에 시선이 모이는 요소 하나를 정하고, 오렌지 포인트를 거기에 준다.
- **여백을 넉넉히.** 요소를 꽉 채우지 않는다.
- **단순한 형태.** 둥글고 깔끔한 도형 위주로, 디테일을 덜어낸 아이콘·삽화 수준으로 그린다.
- **비율**: 특별한 요청이 없으면 가로형(예: 7:5). 소재에 맞으면 정사각·세로도 된다.

## 입력 다루기

사용자가 주는 것은 소재(주제·글·이미지·코드)와 그림에 넣을 문구이며 전부 선택이다.

- **문구를 줬으면 그대로 쓴다.** 요약하거나 다듬지 않는다.
- **이미지를 줬으면 소재 파악용으로만 본다.** 그 이미지의 구도·픽셀을 복제하지 않는다. 무엇을 그릴지
  정하는 참고 자료일 뿐, 그림체·색감은 위 스타일 정의를 따른다.
- **글이 없으면 skill이 만든다.** 소재를 분석해 그릴 대상과(필요하면) 짧은 문구를 정하고 그대로
  진행한다. 사용자에게 물어보며 멈추지 않는다.

## 작업 순서

1. **소재 파악.** 무엇을 그릴지 정한다. 이미지·글이 있으면 거기서 대상을 뽑고, 없으면 주제에서 정한다.
2. **초점·오렌지 결정.** 화면의 초점 요소 하나를 정하고, 오렌지 포인트를 어디에 줄지 정한다.
3. **구도 결정.** 소재에 맞는 단순한 배치를 한두 문장으로 정한다.
4. **문구 확정.** 사용자가 준 문구는 그대로, 없으면 짧게 만들거나 생략한다.
5. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 `<...>`를 채운다. 스타일 문구는 건드리지 않는다.
6. **SVG 조립.** 아래 `SVG 규칙`과 스타일 키트를 따라 소재를 벡터로 그려 저장한다.
7. **출력.** 프롬프트 블록 + SVG 파일 경로 + 한국어 한 줄 설명을 출력한다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록에 담아 그대로 복사할 수 있게 한다.
2. **SVG 파일** — 작업 디렉터리에 `<주제-slug>-monogray.svg`로 저장하고 경로를 알려준다.
3. **한국어 한 줄 설명** — 무엇을 어떤 구도로 그렸고 오렌지를 어디에 줬는지 1~2문장.

## 프롬프트 템플릿

`<...>`(소재·초점·문구)만 채우고, 그 외 스타일 문구는 그대로 둔다.

```text
A hand-drawn editorial illustration in a friendly tech-book style, on a warm off-white paper
background (#F4F2ED). Everything is drawn with uniform medium-thickness dark-gray ink outlines
(#3A3A3A) with rounded corners, and filled with flat gray tones only (#E3E3E3 light, #C9C9C9
mid, #5A5A5A for dark screens) — no gradients, no texture, no hatching, no photographic shading.

COLOR RULE: the whole image is monochrome grayscale EXCEPT for exactly ONE accent color, warm
orange (#E8833A), applied only to <THE SINGLE FOCAL ELEMENT, e.g. "the light bulb" / "the
warning symbol">. Nothing else has any color.

SUBJECT: <describe the subject/scene freely and simply, with one clear focal point, e.g. "a
single stylized light bulb floating above an open book">. Keep shapes simple and rounded, like a
clean icon-illustration, with generous empty space around it.

<TEXT (optional): a short hand-lettered caption in dark gray, reading exactly: "<CAPTION>".>

STYLE: flat hand-drawn ink illustration, monochrome gray with a single warm-orange accent, warm
off-white paper, friendly and legible, plenty of whitespace. <ASPECT, e.g. "Landscape 7:5">.

DO NOT: use any color other than the grays and the single orange accent. No gradients, no
photographic shading, no digital gloss, no busy background. No watermarks, no logos.
```

## SVG 규칙

Figma/Canva 호환을 위해 아래를 지킨다.

- SVG 1.1 기본 요소만 쓴다: `rect`, `circle`, `ellipse`, `path`, `polygon`, `line`, `text`, `g`.
- `filter`, `mask`, `foreignObject`, 외부 이미지 참조, 임베디드 폰트는 쓰지 않는다.
- 텍스트는 `text` 요소로 남겨 가져온 뒤 바로 편집할 수 있게 한다.
- 폰트는 저작권 없는 폰트를 사용한다(예: SIL OFL): 한글 손글씨 `Gaegu`(개구체), 대체
  `Nanum Pen Script`, 라틴 대체 `Patrick Hand`. 셋 다 Google Fonts에서 무료다. Figma/Canva에서
  해당 폰트가 없으면 fallback으로 표시되며, 텍스트가 편집 가능하므로 원하는 폰트로 바꾸면 된다.

스타일 키트 (SVG에 그대로 반영):

- 배경: `<rect>` 전체를 `#F4F2ED`로 채운다.
- 선: 모든 아웃라인 `stroke="#3A3A3A"`, `stroke-width` 6~9, `stroke-linejoin="round"`,
  `stroke-linecap="round"`.
- 면: `#E3E3E3`/`#C9C9C9`(밝은/중간 회색), 어두운 화면류는 `#5A5A5A`. 그라데이션 없음.
- 오렌지: `#E8833A`를 초점 요소 **한 곳**에만 `fill`로 쓴다.
- 소재는 단순한 도형 조합으로 그린다. 겹치는 도형은 같은 그룹에서 내부 선이 지저분하게 겹치지 않도록
  가능한 한 하나의 `path` 실루엣으로 정리한다.

## 예시 (gold reference)

이 예시는 위 스타일을 **참고 그림과 전혀 다른 구도**(사람·모니터 없음)에 입힌 완성 산출물이다.
스타일이 소재와 무관하게 재사용된다는 걸 보여준다.

입력 예:

```text
소재: 서버가 자꾸 다운되는 상황을 한 장으로. 문구는 알아서.
```

skill이 한 판단: 초점을 "먹구름에서 내리치는 번개"로 잡고, 오렌지는 번개 하나에만 줬다. 문구가
없으므로 "서버가 또 죽었다..."를 만들어 손글씨 캡션으로 아래에 넣었다.

출력 프롬프트:

```text
A hand-drawn editorial illustration in a friendly tech-book style, on a warm off-white paper
background (#F4F2ED). Everything is drawn with uniform medium-thickness dark-gray ink outlines
(#3A3A3A) with rounded corners, and filled with flat gray tones only (#E3E3E3 light, #C9C9C9
mid, #5A5A5A for dark screens) — no gradients, no texture, no hatching, no photographic shading.

COLOR RULE: the whole image is monochrome grayscale EXCEPT for exactly ONE accent color, warm
orange (#E8833A), applied only to the lightning bolt. Nothing else has any color.

SUBJECT: a single chunky gray storm cloud in the center, with one jagged lightning bolt striking
straight down from its underside. Simple rounded shapes, like a clean icon-illustration, with
lots of empty off-white space around it.

TEXT: a short hand-lettered caption in dark gray below the cloud, reading exactly:
"서버가 또 죽었다...".

STYLE: flat hand-drawn ink illustration, monochrome gray with a single warm-orange accent, warm
off-white paper, friendly and legible, plenty of whitespace. Landscape 7:5.

DO NOT: use any color other than the grays and the single orange accent. No gradients, no
photographic shading, no digital gloss, no busy background. No watermarks, no logos.
```

출력 SVG (`server-down-monogray.svg`로 저장):

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1680 1200" width="1680" height="1200">
  <!-- palette: bg #F4F2ED / ink #3A3A3A / grays #C9C9C9 #E3E3E3 / accent #E8833A -->
  <rect width="1680" height="1200" fill="#F4F2ED"/>

  <g stroke="#3A3A3A" stroke-width="9" stroke-linejoin="round" stroke-linecap="round">
    <!-- storm cloud (flat gray), single silhouette path -->
    <path d="M560 620
             C470 620 440 520 520 486
             C500 396 620 356 690 416
             C726 344 862 344 900 420
             C986 372 1104 420 1092 508
             C1170 512 1188 612 1104 632
             Z" fill="#E3E3E3"/>

    <!-- lightning bolt = the ONLY orange element -->
    <polygon points="840,628 742,792 826,792 764,940 946,742 852,742 918,628"
             fill="#E8833A"/>
  </g>

  <text x="840" y="1064" text-anchor="middle" fill="#3A3A3A"
        font-family="Gaegu, 'Nanum Pen Script', 'Patrick Hand', sans-serif"
        font-size="76" font-weight="700">서버가 또 죽었다...</text>
</svg>
```

한국어 한 줄 설명: 초점을 먹구름에서 내리치는 번개로 잡고 오렌지를 번개 하나에만 줬으며, 문구가 없어
"서버가 또 죽었다..."를 손글씨 캡션으로 넣었습니다. (참고 그림의 사람·모니터 구도는 쓰지 않고
그림체·색감만 가져왔습니다.)

## 완료 전 확인

- 참고 그림의 구도를 복제하지 않고, 소재에 맞는 새 구도에 **그림체·색감만** 입혔는가?
- 오렌지 `#E8833A`를 화면에서 가장 중요한 **한 요소**에만 썼는가? 나머지는 전부 회색인가?
- 잉크 라인(`#3A3A3A`, 둥근 join/cap), 플랫 회색 면, off-white 종이, 넉넉한 여백을 지켰는가?
- 그림 속 문구는 사용자가 준 그대로 넣었는가? (없을 때만 skill이 만든다) 짧고 손글씨인가?
- SVG가 기본 요소만 쓰고 텍스트가 편집 가능한 `text`로 남아 있는가? 폰트가 저작권 없는 폰트(예: SIL OFL)인가?
- 프롬프트 블록, SVG 파일 경로, 한국어 한 줄 설명을 모두 출력했는가?
