---
name: akbun-draw-cardnews-cream
description: >
  아무 개념·주제·글을 "크림 손글씨 설명형 카드뉴스 스타일"로 그리는 결과물을 만든다. 이 스타일은
  따뜻한 크림색 종이 배경 + 검정 원형 번호 배지 + 굵은 손글씨 제목 + 화살표(→)로 인과를 잇는 손글씨
  본문 + 말풍선·화살표·막대·상자만으로 그린 낙서 다이어그램 + 딱 하나의 로열 블루 대각선 빗금 포인트로
  이뤄진, 기술 개념을 한 장에 설명하는 카드뉴스의 그림체다. 이 skill이 고정하는 건 그림체·색감·
  레이아웃(스타일)이고, 무엇을 설명할지(주제·다이어그램 구성)는 입력에 맞춰 자유롭게 정한다. 산출물은
  두 가지다: 이미지 생성 모델(GPT image, nano-banana 등) AI agent에 그대로 넣을 영어 프롬프트와,
  Figma/Canva로 가져와 편집할 수 있는 편집 가능 텍스트 SVG 파일. Trigger on: "크림 카드뉴스",
  "손글씨 카드뉴스", "설명 카드뉴스 그려", "개념 카드뉴스", "번호 카드뉴스", "cream card news",
  "handwritten explainer card", "카드뉴스 SVG", or any request to explain a concept in this
  cream handwritten doodle explainer card-news style as a prompt or SVG.
---

# 크림 손글씨 설명형 카드뉴스 프롬프트 + SVG 생성

## 이 skill이 하는 일

아무 개념·주제를 **하나의 정해진 설명형 카드뉴스 스타일**로 그린 결과물을 만든다. 그 스타일은 참고
카드 한 장에서 뽑아낸 것이다: 따뜻한 크림색 종이 배경, 왼쪽 위 검정 원형 배지 안의 흰 번호, 배지
옆에 크게 쓴 굵은 손글씨 제목, 화살표(`→`)로 원인과 결과를 잇는 손글씨 본문 두어 줄, 그리고 카드
아래쪽 절반을 차지하는 아주 단순한 낙서 다이어그램(말풍선, 화살표, 막대, 상자). 카드 전체가 무채색
손그림이고, **핵심 도형 하나의 안쪽만 로열 블루 대각선 빗금**으로 채워 시선을 모은다. 기술 개념을
SNS 카드 한 장으로 설명하는 필기 노트 같은 느낌이다.

**이 skill이 고정하는 것은 "그림체·색감·레이아웃"뿐이다.** 무엇을 설명하는지(주제·다이어그램 구성)는
매번 입력에 맞게 자유롭게 정한다. 참고 카드가 어떤 주제였는지는 중요하지 않다. 그 카드에서 읽어낸
**종이색·손글씨·빗금·점선 처리 방식**을 다른 주제에 그대로 입힌다.

산출물은 그림이 아니라 두 가지다.

1. **영어 이미지 생성 프롬프트** — GPT image나 nano-banana 같은 이미지 생성 AI agent에 그대로 붙여넣는다.
2. **SVG 파일** — 같은 카드를 이 스타일의 벡터로 그린 파일. Figma나 Canva로 가져와 색·문구를 편집한다.

`akbun-draw-cartoon-b`, `akbun-draw-sketchbook-card`처럼 "정해진 비주얼 스타일로 카드 프롬프트와
SVG를 만드는" 계열이다. 이 skill은 특정 다이어그램이 아니라 **설명형 카드뉴스 스타일 자체**를 재사용한다.

## 스타일 정의 (고정 — 절대 바꾸지 않는다)

무엇을 설명하든 아래 그림체·색감·레이아웃은 그대로 유지한다.

- **매체**: 필기 노트 같은 손글씨·손그림. 균일한 검정 잉크 라인(`#1F1D1A`)으로 삐뚤빼뚤하게 그린다.
  질감·그라데이션·사진 음영 없음. 전부 플랫하다.
- **배경**: 따뜻한 크림색 종이 `#F5EFE0` 단색. 배경에 무늬·질감·잡다한 소품을 넣지 않는다.
- **번호 배지**: 왼쪽 위에 **검정 원형 배지**(`#1F1D1A`) 하나, 안에 흰색 굵은 숫자. 카드 시리즈의
  순번이다. 여러 장을 만들면 장마다 숫자만 올린다.
- **제목**: 배지 오른쪽에 **굵은 마커 손글씨** 한 줄. 검정. 카드에서 가장 큰 글씨다.
- **본문**: 제목 아래 2~3줄의 중간 굵기 손글씨. 한글 문장 안에 영어 기술 용어를 그대로 섞어 쓴다.
  인과·흐름은 줄 앞이나 문장 안의 화살표 `→`로 잇는다.
- **다이어그램**: 카드 아래쪽 절반의 낙서 다이어그램. 쓸 수 있는 도형은 말풍선, 화살표, 막대(bar),
  상자, 원 정도로 제한한다. 도형 개수는 5개 안팎으로 적게, 여백을 넉넉하게 둔다.
- **로열 블루 포인트 (핵심 규칙)**: 선명한 로열 블루 `#3B5FD9` **하나만** 쓴다. 카드가 말하려는
  **핵심 도형 하나의 안쪽을 대각선 빗금(hatching)으로 채우는 데** 쓰고, 그 도형 옆의 강조 반짝
  선에도 같은 파랑을 쓸 수 있다. 그 외 전부 무채색(검정 선 + 크림/흰 면)이다.
- **점선 규칙**: 없어진 것, 절약된 것, 아직 생기지 않은 것(잠재)은 **검정 점선 윤곽**으로만 그린다.
  실선(현재 있는 것)과 점선(없는/생길 것)의 대비가 이 스타일의 설명 장치다.
- **강조 반짝**: 핵심 지점 바깥쪽에 짧은 선 2~3개를 방사형으로 친다. 만화의 반짝임 표시다.
- **분위기**: 공부 노트를 카드로 옮긴 듯한 친근한 설명 톤. 단순하지만 개념이 또렷하게 읽힌다.

## 캐릭터 (선택)

이 스타일은 기본적으로 캐릭터 없이 도형과 글씨만으로 설명한다. 소재상 인물이 꼭 필요하면 사람 대신
`akbun-mascot-whale` skill의 고래 캐릭터를 같은 검정 손글씨 라인의 낙서풍으로 그린다.

## 레이아웃·간격 규칙 (참고 카드의 비율을 따른다)

캔버스는 **정사각형 카드**다. 기본 `1080×1080`. 요소를 억지로 고정 좌표에 두지 않되, 참고 카드의
**상하좌우 간격 비율**을 지킨다.

- **여백**: 사방 약 7%(≈ 76px)를 비운다. 글씨·도형이 가장자리에 붙지 않는다.
- **번호 배지 + 제목**: 위 약 9~17% 높이 구간. 배지는 왼쪽 여백에 붙여 지름 약 9%(≈ 96px)로 그리고,
  제목은 배지 오른쪽에서 시작해 배지와 세로 중심을 맞춘다.
- **본문 블록**: 약 24~38% 높이 구간. 왼쪽 여백에서 시작해 왼쪽 정렬로 2~3줄을 넉넉한 줄간격으로 쌓는다.
- **다이어그램 영역**: 약 45~90% 높이 구간. 좌→우로 읽히게 배치한다(원인·입력은 왼쪽, 결과·출력은
  오른쪽). 말풍선은 그것이 가리키는 도형의 위나 왼쪽에 둔다.
- **시선 흐름**: 배지·제목(위) → 본문(중간) → 다이어그램(아래) 순서로 읽히게 세 구역을 확실히 나눈다.

## 문구 패턴 (권장, 강제 아님)

참고 카드의 글 구성을 일반화한 패턴이다. 소재에 맞으면 쓰고, 안 맞으면 자유롭게 바꾼다.

- **제목**: 명사구 한 줄. 예: `느려지는 진짜 이유`, `트래픽 급증 대응`.
- **본문 1줄 — 상황/원인**: 조건이나 현상을 쓴다. 예: `CPU 사용률이 임계값을 넘으면`.
- **본문 2줄 — `→` + 결과**: 화살표로 시작해 결과를 쓴다. 예: `→ HPA가 replica를 자동으로 늘림`.
- 영어 기술 용어(`replica`, `cache`, `token` 등)는 번역하지 않고 손글씨 그대로 섞어 쓴다.

## 입력 다루기

사용자가 주는 것은 주제(개념·글·이미지·상황)와 카드에 넣을 문구이며 전부 선택이다.

- **문구를 줬으면 그대로 쓴다.** 요약하거나 다듬지 않는다.
- **이미지를 줬으면 주제 파악용으로만 본다.** 그 이미지의 구도·픽셀을 복제하지 않는다. 무엇을 설명할지
  정하는 참고 자료일 뿐, 그림체·색감·레이아웃은 위 스타일 정의를 따른다.
- **글이 없으면 skill이 만든다.** 주제를 분석해 제목·본문·다이어그램 구성을 만들고 그대로 진행한다.
  지어낸 문구임을 밝히되, 사용자에게 물어보며 멈추지 않는다.
- **여러 장을 요청하면** 장마다 같은 규칙을 적용하고 번호 배지의 숫자만 1씩 올린다.

## 작업 순서

1. **주제 파악.** 무엇을 설명할지 정한다. 이미지·글이 있으면 거기서 개념을 뽑고, 없으면 주제에서 정한다.
2. **핵심 도형·파랑 결정.** 카드가 말하려는 핵심 도형 하나를 정하고, 로열 블루 빗금을 거기에 준다.
3. **점선 대상 결정.** 없어지거나 절약되거나 아직 생기지 않은 요소가 있으면 점선 윤곽으로 배정한다.
4. **다이어그램 구성.** 말풍선·화살표·막대·상자 5개 안팎으로 좌→우 흐름을 설계한다.
5. **문구 확정.** 사용자가 준 문구는 그대로, 없으면 `문구 패턴`으로 제목·본문을 만든다.
6. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 `<...>`를 채운다. 스타일 문구는 건드리지 않는다.
7. **SVG 조립.** 아래 `SVG 규칙`과 스타일 키트를 따라 카드를 벡터로 그려 저장한다.
8. **출력.** 프롬프트 블록 + SVG 파일 경로 + 한국어 한 줄 설명을 출력한다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록에 담아 그대로 복사할 수 있게 한다.
2. **SVG 파일** — 작업 디렉터리에 `<주제-slug>-cardnews-cream.svg`로 저장하고 경로를 알려준다.
3. **한국어 한 줄 설명** — 무엇을 어떤 다이어그램으로 설명했고 파란 빗금을 어디에 줬는지 1~2문장.

## 프롬프트 템플릿

`<...>`(번호·문구·다이어그램)만 채우고, 그 외 스타일 문구는 그대로 둔다. 점선 요소가 없으면 그 줄은 지운다.

```text
A square explainer "card-news" illustration (1:1), drawn like a friendly handwritten study
note. The whole card sits on a flat warm cream paper background (#F5EFE0). Everything is drawn
with simple, slightly wobbly black ink lines (#1F1D1A), like casual handwriting and doodles.
Flat only: no texture, no gradients, no photographic shading.

HEADER: at the top-left, a solid black circle badge with the white bold number "<N>" inside.
To its right, one line of big bold Korean marker-style handwriting as the title.

BODY TEXT (medium handwriting, left-aligned, below the title, keep English tech words as-is,
render each line exactly):
- line 1: "<situation/cause line>"
- line 2: "<→ result line, starting with the arrow →>"

DIAGRAM (lower half of the card, a very simple doodle diagram read left to right, five shapes
or fewer, lots of empty space): <describe the diagram simply using only speech bubbles, arrows,
bars, boxes and circles, e.g. "a speech bubble saying 80% points at a horizontal gauge bar;
a hand-drawn arrow leads to two solid boxes and one dashed-outline box on the right">.

COLOR RULE: the whole card is monochrome black-on-cream EXCEPT for exactly ONE accent, royal
blue (#3B5FD9), used only as diagonal hatching strokes filling <THE SINGLE KEY SHAPE the card
is about, e.g. "the filled part of the gauge bar"> and for two or three small blue sparkle
dashes next to it. Nothing else has any color.

DASHED RULE: draw <the absent / saved / not-yet-existing element> with a black dashed outline
only, contrasting with the solid-line shapes. <remove this line if nothing is dashed>

STYLE: handwritten Korean study-note explainer card-news, cream paper, black doodle lines,
one royal-blue hatched accent, dashed outlines for absent things, small sparkle emphasis
dashes, generous margins, three clear zones top-to-bottom (badge+title, body text, diagram).

DO NOT: use any color other than black, white, cream and the single royal blue. No characters,
no photos, no texture, no busy background. Do not misspell, translate, or rearrange the Korean
text. No watermarks, no logos.
```

## SVG 규칙

Figma/Canva 호환을 위해 아래를 지킨다.

- SVG 1.1 기본 요소만 쓴다: `rect`, `circle`, `ellipse`, `path`, `polygon`, `line`, `text`, `g`.
- `filter`, `mask`, `pattern`, `clipPath`, `foreignObject`, 외부 이미지 참조, 임베디드 폰트는 쓰지
  않는다. **빗금은 `line` 요소를 도형 안쪽 크기에 맞춰 직접 그린다.**
- 텍스트는 `text` 요소로 남겨 가져온 뒤 바로 편집할 수 있게 한다.
- 폰트는 저작권 없는 폰트를 사용한다(SIL OFL): 손글씨는 `Gaegu`(개구체), 대체 `Nanum Pen Script`
  (나눔손글씨 펜). 둘 다 Google Fonts에서 무료다. `font-family`는 항상
  `'Gaegu', 'Nanum Pen Script', sans-serif`로 지정하고 제목·숫자는 `font-weight="700"`을 준다.
  Figma/Canva에서 해당 폰트가 없으면 fallback으로 표시되며, 텍스트가 편집 가능하므로 원하는 폰트로
  바꾸면 된다.

스타일 키트 (SVG에 그대로 반영):

- 배경: `<rect>` 하나로 캔버스 전체를 크림색 `#F5EFE0`으로 채운다.
- 선: 모든 아웃라인 `stroke="#1F1D1A"`, `stroke-width` 5~8, `stroke-linejoin="round"`,
  `stroke-linecap="round"`. 점선은 `stroke-dasharray="14 12"` 정도로 성기게 준다.
- 번호 배지: 검정 `circle` + 흰색 `text` 숫자(`text-anchor="middle"`).
- 파랑: `#3B5FD9`를 핵심 도형 안쪽 대각선 빗금 `line`들과 반짝 선에만 `stroke`로 쓴다.
- 글씨: 제목 검정 `#1F1D1A` 크게, 본문 같은 검정으로 중간 크기, 전부 `text-anchor="start"` 왼쪽 정렬.
- 도형은 단순한 기본 도형 조합으로 그린다. 겹치는 도형은 내부 선이 지저분하지 않게 정리한다.

## 예시 (gold reference)

이 예시는 위 스타일을 **참고 카드와 전혀 다른 주제**(Kubernetes HPA)에 입힌 완성 산출물이다. 스타일이
주제와 무관하게 재사용된다는 걸 보여준다.

입력 예:

```text
주제: HPA가 CPU 부하에 따라 pod을 자동으로 늘리는 걸 카드뉴스 한 장으로. 시리즈 2번 카드. 문구는 알아서.
```

skill이 한 판단: 핵심 도형을 "CPU 게이지의 채워진 부분"으로 잡아 파란 빗금을 거기에만 줬다. 아직
생기지 않은 세 번째 pod은 점선 윤곽으로 그리고 반짝 선으로 강조했다. 문구가 없어 제목·본문 2줄을
만들었다.

출력 프롬프트:

```text
A square explainer "card-news" illustration (1:1), drawn like a friendly handwritten study
note. The whole card sits on a flat warm cream paper background (#F5EFE0). Everything is drawn
with simple, slightly wobbly black ink lines (#1F1D1A), like casual handwriting and doodles.
Flat only: no texture, no gradients, no photographic shading.

HEADER: at the top-left, a solid black circle badge with the white bold number "2" inside.
To its right, one line of big bold Korean marker-style handwriting as the title: "트래픽 급증 대응".

BODY TEXT (medium handwriting, left-aligned, below the title, keep English tech words as-is,
render each line exactly):
- line 1: "CPU 사용률이 임계값을 넘으면"
- line 2: "→ HPA가 replica를 자동으로 늘림"

DIAGRAM (lower half of the card, a very simple doodle diagram read left to right, five shapes
or fewer, lots of empty space): a small speech bubble saying "80%" points down at a horizontal
CPU gauge bar; a hand-drawn arrow leads to the right where two solid-outline pod boxes stand,
and a third pod box drawn with a dashed outline is being added next to them.

COLOR RULE: the whole card is monochrome black-on-cream EXCEPT for exactly ONE accent, royal
blue (#3B5FD9), used only as diagonal hatching strokes filling the filled part of the CPU
gauge bar and for two or three small blue sparkle dashes next to the dashed pod box. Nothing
else has any color.

DASHED RULE: draw the not-yet-created third pod box with a black dashed outline only,
contrasting with the solid-line shapes.

STYLE: handwritten Korean study-note explainer card-news, cream paper, black doodle lines,
one royal-blue hatched accent, dashed outlines for absent things, small sparkle emphasis
dashes, generous margins, three clear zones top-to-bottom (badge+title, body text, diagram).

DO NOT: use any color other than black, white, cream and the single royal blue. No characters,
no photos, no texture, no busy background. Do not misspell, translate, or rearrange the Korean
text. No watermarks, no logos.
```

출력 SVG (`hpa-cardnews-cream.svg`로 저장):

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
  <!-- palette: bg #F5EFE0 / ink #1F1D1A / accent #3B5FD9 -->

  <!-- 크림색 종이 배경 -->
  <rect width="1080" height="1080" fill="#F5EFE0"/>

  <!-- 번호 배지: 검정 원 + 흰 숫자 -->
  <circle cx="128" cy="150" r="48" fill="#1F1D1A"/>
  <text x="128" y="176" text-anchor="middle" fill="#FFFFFF"
        font-family="'Gaegu', 'Nanum Pen Script', sans-serif" font-size="72" font-weight="700">2</text>

  <!-- 제목: 굵은 손글씨 한 줄 -->
  <text x="204" y="182" text-anchor="start" fill="#1F1D1A"
        font-family="'Gaegu', 'Nanum Pen Script', sans-serif" font-size="92" font-weight="700">트래픽 급증 대응</text>

  <!-- 본문: 2줄, → 로 인과 연결 -->
  <text x="84" y="322" text-anchor="start" fill="#1F1D1A"
        font-family="'Gaegu', 'Nanum Pen Script', sans-serif" font-size="58">CPU 사용률이 임계값을 넘으면</text>
  <text x="84" y="404" text-anchor="start" fill="#1F1D1A"
        font-family="'Gaegu', 'Nanum Pen Script', sans-serif" font-size="58">→ HPA가 replica를 자동으로 늘림</text>

  <g stroke="#1F1D1A" stroke-width="7" stroke-linejoin="round" stroke-linecap="round" fill="none">
    <!-- 말풍선: 게이지를 가리킴 -->
    <ellipse cx="230" cy="600" rx="96" ry="66"/>
    <path d="M250 662 L268 706 L296 668"/>

    <!-- CPU 게이지 막대 -->
    <rect x="120" y="740" width="380" height="76" rx="14"/>
    <!-- 채워진 정도 구분선 -->
    <line x1="386" y1="740" x2="386" y2="816"/>

    <!-- 손그림 화살표 -->
    <path d="M552 778 L648 778 M618 750 L652 778 L618 806"/>

    <!-- 기존 pod 상자 2개: 실선 -->
    <rect x="690" y="700" width="96" height="150" rx="10"/>
    <rect x="806" y="700" width="96" height="150" rx="10"/>

    <!-- 새로 생길 pod 상자: 점선 -->
    <rect x="922" y="700" width="96" height="150" rx="10" stroke-dasharray="14 12"/>
  </g>

  <!-- 파란 빗금: 게이지의 채워진 부분 (유일한 유채색) -->
  <g stroke="#3B5FD9" stroke-width="6" stroke-linecap="round">
    <line x1="140" y1="810" x2="192" y2="748"/>
    <line x1="176" y1="810" x2="228" y2="748"/>
    <line x1="212" y1="810" x2="264" y2="748"/>
    <line x1="248" y1="810" x2="300" y2="748"/>
    <line x1="284" y1="810" x2="336" y2="748"/>
    <line x1="320" y1="810" x2="372" y2="748"/>
  </g>

  <!-- 파란 반짝 강조: 점선 pod 옆 -->
  <g stroke="#3B5FD9" stroke-width="6" stroke-linecap="round">
    <line x1="1006" y1="668" x2="1022" y2="644"/>
    <line x1="1030" y1="694" x2="1052" y2="682"/>
    <line x1="972" y1="660" x2="976" y2="634"/>
  </g>

  <!-- 말풍선 글씨 -->
  <text x="230" y="622" text-anchor="middle" fill="#1F1D1A"
        font-family="'Gaegu', 'Nanum Pen Script', sans-serif" font-size="60" font-weight="700">80%</text>
</svg>
```

한국어 한 줄 설명: CPU 게이지의 채워진 부분에만 파란 빗금을 줘 원인을 강조했고, HPA가 새로 띄울
세 번째 pod은 점선 윤곽 + 반짝 선으로 그려 "아직 없는 것" 대비를 살린 설명 카드뉴스입니다.

## 완료 전 확인

- 참고 카드의 주제·문구·다이어그램 구성을 복제하지 않고, 소재에 맞는 새 구성에 **그림체·색감·레이아웃만**
  입혔는가?
- 로열 블루 `#3B5FD9`를 카드가 말하려는 **핵심 도형 하나의 빗금(+반짝 선)**에만 썼는가? 나머지는
  전부 무채색인가?
- 없어진/절약된/아직 없는 요소를 점선 윤곽으로 그렸는가? (해당 없으면 생략)
- 크림 배경, 검정 원형 번호 배지, 굵은 손글씨 제목, `→` 본문, 낙서 다이어그램의 세 구역 레이아웃을
  지켰는가?
- 다이어그램 도형이 5개 안팎으로 단순하고 여백이 넉넉한가?
- 문구는 사용자가 준 그대로 넣었는가? (없을 때만 skill이 만든다)
- SVG가 기본 요소만 쓰고(빗금도 `line` 직접 그리기) 텍스트가 편집 가능한 `text`로 남아 있는가?
  폰트가 저작권 없는 폰트(`'Gaegu', 'Nanum Pen Script'`, SIL OFL)인가?
- 프롬프트 블록, SVG 파일 경로, 한국어 한 줄 설명을 모두 출력했는가?
