---
name: akbun-draw-cartoon-b
description: >
  아무 소재(주제·글·이미지·상황)를 "이슈 카드뉴스 낙서 스타일"로 그리는 결과물을 만든다. 이 스타일은
  회색 그라데이션 배경 + 얇은 베이지 테두리 액자 + 어린아이 낙서 같은 검정 잉크 라인의 단순한 고래
  캐릭터 + 딱 하나의 올리브 그린 포인트 + 왼쪽 아래에 쌓은 굵은 고딕 헤드라인으로 이뤄진, 안전·경고성
  카드뉴스 한 장의 그림체다. 이 skill이 고정하는 건 그림체·색감·레이아웃(스타일)이고, 무엇을 그릴지
  (소재·구도)는 입력에 맞춰 자유롭게 정한다. 산출물은 두 가지다: 이미지 생성 모델(GPT image,
  nano-banana 등) AI agent에 그대로 넣을 영어 프롬프트와, Figma/Canva로 가져와 편집할 수 있는
  편집 가능 텍스트 SVG 파일. Trigger on: "카드뉴스 스타일로 그려", "이슈카드 그려", "경고 카드뉴스",
  "낙서 스타일 카드", "고래 캐릭터 카드", "issue card news", "safety card illustration",
  "카드뉴스 SVG", "figma 카드뉴스 svg", or any request to render a subject in this
  naive-doodle safety/issue card-news style as a prompt or SVG.
---

# 이슈 카드뉴스 낙서 스타일 프롬프트 + SVG 생성

## 이 skill이 하는 일

아무 소재를 **하나의 정해진 카드뉴스 그림 스타일**로 그린 결과물을 만든다. 그 스타일은 참고 카드
한 장에서 뽑아낸 것이다: 위에서 아래로 밝아졌다 어두워지는 회색 그라데이션 배경, 그 위를 감싸는
얇은 베이지 테두리 액자, 어린아이가 그린 듯한 단순한 검정 잉크 라인의 고래 캐릭터, 화면에서 가장
중요한 사물 **딱 하나에만** 칠한 올리브 그린 포인트, 그리고 왼쪽 아래에 굵은 고딕으로 쌓아 놓은
경고성 헤드라인. 뉴스·SNS에서 보는 안전 이슈 카드뉴스 같은 느낌이다.

**이 skill이 고정하는 것은 "그림체·색감·레이아웃"뿐이다.** 무엇을 그리는지(소재·구도)는 매번 입력에
맞게 자유롭게 정한다. 참고 카드가 "긴 우산을 든 상황"이었다고 해서 그 장면을 재현하는 게 아니다.
그 카드에서 읽어낸 **선·색·배치 처리 방식**을 다른 소재에 그대로 입힌다.

산출물은 그림이 아니라 두 가지다.

1. **영어 이미지 생성 프롬프트** — GPT image나 nano-banana 같은 이미지 생성 AI agent에 그대로 붙여넣는다.
2. **SVG 파일** — 같은 카드를 이 스타일의 벡터로 그린 파일. Figma나 Canva로 가져와 색·문구를 편집한다.

`akbun-draw-poster-monogray`, `akbun-draw-minimal-poster`처럼 "정해진 비주얼 스타일로 카드/포스터
프롬프트와 SVG를 만드는" 계열이다. 이 skill은 특정 장면이 아니라 **카드뉴스 스타일 자체**를 재사용한다.

## 캐릭터 (고정 — 고래)

이 카드뉴스는 사람을 그리지 않고 **akbun 마스코트 고래를 낙서풍으로 그린 캐릭터**만 쓴다. 기본
외형(콩 모양 몸통, 흰 배, 작은 지느러미, 점 눈, 곡선 입)은 `akbun-mascot-whale` skill의 캐릭터
스펙을 따르고, 이 skill에서는 어린아이 낙서 같은 잉크 라인으로 렌더링한다. 아래 정의 문장을
프롬프트에 **글자 그대로** 복사한다. 이미지 모델은 문장이 다르면 캐릭터가 달라지므로 표현을 바꾸지
않는다. 사용자가 다른 동작·소품을 지정해도 고래 캐릭터는 유지한다.

고래 캐릭터의 영어 CHARACTER 문장:

```text
a simple naive-doodle rendering of the akbun whale mascot standing upright on its small flat
tail, drawn with a childlike hand-drawn black ink outline: a chubby bean-shaped whale body,
white belly, two small stubby side fins, two black dot eyes and a small curved smile, no other
facial features
```

- **여러 캐릭터가 나오면 채움으로 대비한다.** 행동의 주체인 고래는 **속이 빈 흰색(검정 외곽선만)**
  으로, 그 상황에 당하거나 반응하는 상대 고래는 **꽉 찬 중간 회색 실루엣**으로 그린다. 참고 카드에서
  한 인물은 윤곽선만, 다른 인물은 회색 실루엣이었던 대비를 고래에 그대로 옮긴 것이다.
- **한 마리만 나오면** 흰색(검정 외곽선) 고래로 그린다.

## 스타일 정의 (고정 — 절대 바꾸지 않는다)

무엇을 그리든 아래 그림체·색감·레이아웃은 그대로 유지한다.

- **매체**: 어린아이 낙서 같은 단순한 손그림. 균일한 검정 잉크 아웃라인(`#1A1A1A`)으로 형태만
  그리고, 면은 플랫하게만 칠한다. 그라데이션·질감·해칭·사진 음영 없음(배경 그라데이션은 예외).
- **배경**: 세로 회색 그라데이션. 위 `#EDEDED`(밝은 회색) → 아래 `#8C8C8C`(중간 회색). 배경에
  잡다한 소품을 넣지 않는다.
- **테두리 액자**: 캔버스 안쪽으로 살짝 들여 그린 **얇은 따뜻한 베이지 테두리**(`#CBB994`, 두께 3~5).
  네 변을 감싸는 단순한 사각 액자다.
- **잉크 라인**: `#1A1A1A`, 둥근 모서리·둥근 끝(round join/cap). 손으로 삐뚤빼뚤 그린 듯 단순하다.
- **채움**: 흰색(`#FFFFFF`)과 중간 회색(`#8C8C8C`) 두 톤. 바닥·계단 같은 환경선은 검정 라인만 쓴다.
- **올리브 그린 포인트 (핵심 규칙)**: 머스터드빛 올리브 그린 `#A8B43C` **하나만** 쓴다. 카드가
  말하려는 **핵심 사물 하나**에만 칠한다(예: 위험한 물건, 문제의 대상). 그 외 전부 무채색이다.
- **헤드라인 글씨**: 굵은 고딕. 카드 아래쪽에 왼쪽 정렬로 2~3줄 쌓는다. 색은 진한 회색/검정.
- **분위기**: 안전·경고·목격담 톤의 이슈 카드뉴스. 단순하지만 메시지가 또렷하다.

## 레이아웃·간격 규칙 (참고 카드의 비율을 따른다)

캔버스는 **세로형 카드**다. 기본 `1080×1350`(4:5, 인스타그램 세로형). 요소를 억지로 고정 좌표에 두지
않되, 참고 카드의 **상하좌우 간격 비율**을 지킨다.

- **테두리 액자**: 사방 가장자리에서 약 2%(≈ 22px) 안쪽으로 들여 그린다.
- **그림 영역**: 위 약 3%부터 아래 약 62% 높이까지. 캐릭터와 핵심 사물을 여기 둔다.
- **바닥/지지선**: 캐릭터가 서 있는 계단·바닥·연석 같은 단순한 검정 라인을 화면 중하단(약 45~62% 높이)에
  둔다. 참고 카드처럼 캐릭터에 높이차를 주고 싶으면 계단형으로 그린다.
- **헤드라인 블록**: **왼쪽 아래**. 왼쪽 여백 약 7%(≈ 76px)에서 시작해 왼쪽 정렬로 쌓는다. 첫 줄은
  약 70% 높이, 마지막 줄은 약 93% 높이까지 3줄이 넉넉한 줄간격으로 내려온다.
- **여백**: 그림과 글씨가 테두리 액자에 붙지 않게 사방 여백을 남긴다. 그림은 위쪽, 글씨는 아래쪽으로
  확실히 구역을 나눈다.
- **시선 흐름**: 위(그림)에서 아래(헤드라인)로 읽히게 배치한다.

## 헤드라인 패턴 (권장, 강제 아님)

참고 카드의 헤드라인은 3줄 구성이었다. 소재에 맞으면 이 패턴을 쓰고, 안 맞으면 자유롭게 바꾼다.

- **1줄 — 경고 한마디**: 큰따옴표로 감싼 짧은 위험 표현. 예: `"부딪힐 뻔"`.
- **2줄 — 대상 + 상황**: 문제의 대상만 작은따옴표로 강조하고 상황을 잇는다. 예: `'전동킥보드' 이렇게 타고 쌩쌩,`.
- **3줄 — 목격담 마무리**: 빈도·경험으로 마무리. 예: `오늘만 3번 봤습니다`.

## 입력 다루기

사용자가 주는 것은 소재(주제·글·이미지·상황)와 카드에 넣을 문구이며 전부 선택이다.

- **문구를 줬으면 그대로 쓴다.** 요약하거나 다듬지 않는다.
- **이미지를 줬으면 소재 파악용으로만 본다.** 그 이미지의 구도·픽셀을 복제하지 않는다. 무엇을 그릴지
  정하는 참고 자료일 뿐, 그림체·색감·레이아웃은 위 스타일 정의를 따른다.
- **글이 없으면 skill이 만든다.** 소재를 분석해 그릴 상황과 3줄 헤드라인을 만들고 그대로 진행한다.
  지어낸 문구임을 밝히되, 사용자에게 물어보며 멈추지 않는다.

## 작업 순서

1. **소재 파악.** 무엇을 그릴지 정한다. 이미지·글이 있으면 거기서 상황을 뽑고, 없으면 주제에서 정한다.
2. **핵심 사물·올리브 결정.** 카드가 말하려는 핵심 사물 하나를 정하고, 올리브 그린을 거기에 준다.
3. **캐릭터 배정.** 행동 주체 고래는 흰색(검정 외곽선), 반응하는 상대 고래는 회색 실루엣. 정의 문장을
   그대로 복사한다.
4. **구도·간격 결정.** `레이아웃·간격 규칙`에 맞춰 그림 영역과 헤드라인 블록을 나눈다.
5. **헤드라인 확정.** 사용자가 준 문구는 그대로, 없으면 3줄 패턴으로 만든다.
6. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 `<...>`를 채운다. 스타일 문구는 건드리지 않는다.
7. **SVG 조립.** 아래 `SVG 규칙`과 스타일 키트를 따라 카드를 벡터로 그려 저장한다.
8. **출력.** 프롬프트 블록 + SVG 파일 경로 + 한국어 한 줄 설명을 출력한다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록에 담아 그대로 복사할 수 있게 한다.
2. **SVG 파일** — 작업 디렉터리에 `<주제-slug>-cartoon-card.svg`로 저장하고 경로를 알려준다.
3. **한국어 한 줄 설명** — 무엇을 어떤 구도로 그렸고 올리브를 어디에 줬는지 1~2문장.

## 프롬프트 템플릿

`<...>`(소재·상황·헤드라인)만 채우고, 그 외 스타일 문구는 그대로 둔다. 나오지 않는 캐릭터 줄은 지운다.

```text
A vertical issue "card-news" illustration (portrait 4:5, 1080x1350), in a naive childlike doodle
style. The whole card sits on a smooth vertical gray gradient background, light gray at the top
(#EDEDED) fading to medium gray at the bottom (#8C8C8C). A thin warm-beige rectangular border
frame (#CBB994) is inset a little from all four edges.

Everything is drawn with simple, slightly wobbly uniform black ink outlines (#1A1A1A) with
rounded corners — like a child's doodle. Flat fills only: white and medium gray. No gradients on
the figures, no texture, no hatching, no photographic shading.

CHARACTERS: a simple naive-doodle rendering of the akbun whale mascot standing upright on its
small flat tail, drawn with a childlike hand-drawn black ink outline: a chubby bean-shaped whale
body, white belly, two small stubby side fins, two black dot eyes and a small curved smile, no
other facial features.
CONTRAST: draw the acting whale as an OUTLINE-ONLY white figure (black outline, white fill), and
the reacting/second whale as a SOLID medium-gray silhouette. <remove this line if only one whale>

COLOR RULE: the whole card is grayscale (black lines, white and gray fills, gray gradient
background) EXCEPT for exactly ONE accent color, muted olive-green (#A8B43C), applied only to
<THE SINGLE KEY OBJECT the card is about, e.g. "the electric kick-scooter">. Nothing else has
any color.

SCENE: <describe the situation simply, with the whale characters and the one key object, and a
simple black-line ground/steps/curb they stand on, e.g. "a white outline whale rides an olive-
green electric kick-scooter fast along a sidewalk curb, almost hitting a gray silhouette whale
that leans back startled">. Illustration fills the upper ~60% of the card; keep it simple with
generous empty space.

TEXT IN IMAGE (bold Korean gothic, bottom-left, left-aligned, stacked, render each line exactly):
- line 1 (in double quotes): "<alarm phrase, e.g. 부딪힐 뻔>"
- line 2 (topic in single quotes): "<'대상' + 상황, e.g. '전동킥보드' 이렇게 타고 쌩쌩,>"
- line 3: "<witness closing, e.g. 오늘만 3번 봤습니다>"

STYLE: naive doodle safety issue card-news, bold gothic headline in the lower-left, one olive-
green accent, gray gradient background, thin beige border frame, lots of clean space.

DO NOT: use any color other than the grays and the single olive-green accent. No human
characters — only the whale characters. No gradients on the figures, no photographic shading, no
busy background. Do not misspell, translate, or rearrange the Korean text. No watermarks, no logos.
```

## SVG 규칙

Figma/Canva 호환을 위해 아래를 지킨다.

- SVG 1.1 기본 요소만 쓴다: `rect`, `circle`, `ellipse`, `path`, `polygon`, `line`, `text`, `g`,
  그리고 배경 그라데이션용 `linearGradient`.
- `filter`, `mask`, `foreignObject`, 외부 이미지 참조, 임베디드 폰트는 쓰지 않는다.
- 텍스트는 `text` 요소로 남겨 가져온 뒤 바로 편집할 수 있게 한다.
- 폰트는 저작권 없는 폰트를 사용한다(SIL OFL): 굵은 고딕 헤드라인은 `Gothic A1`(고딕 A1), 대체
  `Nanum Gothic`(나눔고딕). 둘 다 Google Fonts에서 무료다. `font-family`는 항상
  `'Gothic A1', 'Nanum Gothic', sans-serif`로 지정하고 `font-weight="800"`을 준다. Figma/Canva에서
  해당 폰트가 없으면 fallback으로 표시되며, 텍스트가 편집 가능하므로 원하는 폰트로 바꾸면 된다.

스타일 키트 (SVG에 그대로 반영):

- 배경: `linearGradient`(세로) 위 `#EDEDED` → 아래 `#8C8C8C`로 캔버스 전체를 채운다.
- 테두리: `<rect>` 하나를 `fill="none" stroke="#CBB994"`, 두께 4로 사방 22px 안쪽에 둔다.
- 선: 모든 아웃라인 `stroke="#1A1A1A"`, `stroke-width` 6~9, `stroke-linejoin="round"`,
  `stroke-linecap="round"`.
- 채움: 흰색 `#FFFFFF`(외곽선 고래·기본 면), 중간 회색 `#8C8C8C`(실루엣 고래). 그라데이션 없음.
- 올리브: `#A8B43C`를 핵심 사물 **한 곳**에만 `fill`로 쓴다.
- 헤드라인: 왼쪽 아래, `text-anchor="start"`, 진회색 `#2A2A2A`(경고 한마디는 검정 `#1A1A1A`도 가능),
  3줄을 넉넉한 줄간격으로 쌓는다.
- 캐릭터·사물은 단순한 도형 조합으로 그린다. 겹치는 도형은 내부 선이 지저분하지 않게 정리한다.

## 예시 (gold reference)

이 예시는 위 스타일을 **참고 카드와 전혀 다른 소재**(우산 없음)에 입힌 완성 산출물이다. 스타일이
소재와 무관하게 재사용된다는 걸 보여준다.

입력 예:

```text
소재: 인도에서 전동킥보드를 둘이 타거나 너무 빨리 몰아서 위험한 상황을 카드뉴스 한 장으로. 문구는 알아서.
```

skill이 한 판단: 핵심 사물을 "전동킥보드"로 잡아 올리브를 거기에만 줬다. 킥보드를 모는 고래는 흰색
외곽선, 부딪힐 뻔한 상대 고래는 회색 실루엣으로 대비했다. 문구가 없어 3줄 헤드라인을 만들었다.

출력 프롬프트:

```text
A vertical issue "card-news" illustration (portrait 4:5, 1080x1350), in a naive childlike doodle
style. The whole card sits on a smooth vertical gray gradient background, light gray at the top
(#EDEDED) fading to medium gray at the bottom (#8C8C8C). A thin warm-beige rectangular border
frame (#CBB994) is inset a little from all four edges.

Everything is drawn with simple, slightly wobbly uniform black ink outlines (#1A1A1A) with
rounded corners — like a child's doodle. Flat fills only: white and medium gray. No gradients on
the figures, no texture, no hatching, no photographic shading.

CHARACTERS: a simple naive-doodle rendering of the akbun whale mascot standing upright on its
small flat tail, drawn with a childlike hand-drawn black ink outline: a chubby bean-shaped whale
body, white belly, two small stubby side fins, two black dot eyes and a small curved smile, no
other facial features.
CONTRAST: draw the acting whale as an OUTLINE-ONLY white figure (black outline, white fill), and
the reacting/second whale as a SOLID medium-gray silhouette.

COLOR RULE: the whole card is grayscale (black lines, white and gray fills, gray gradient
background) EXCEPT for exactly ONE accent color, muted olive-green (#A8B43C), applied only to
the electric kick-scooter. Nothing else has any color.

SCENE: a white outline whale leans forward riding an olive-green electric kick-scooter fast along
a simple black-line sidewalk curb, and a gray silhouette whale on the right leans back startled
with a small surprise mark. Illustration fills the upper ~60% of the card; keep it simple with
generous empty space.

TEXT IN IMAGE (bold Korean gothic, bottom-left, left-aligned, stacked, render each line exactly):
- line 1 (in double quotes): "부딪힐 뻔"
- line 2 (topic in single quotes): "'전동킥보드' 이렇게 타고 쌩쌩,"
- line 3: "오늘만 3번 봤습니다"

STYLE: naive doodle safety issue card-news, bold gothic headline in the lower-left, one olive-
green accent, gray gradient background, thin beige border frame, lots of clean space.

DO NOT: use any color other than the grays and the single olive-green accent. No human
characters — only the whale characters. No gradients on the figures, no photographic shading, no
busy background. Do not misspell, translate, or rearrange the Korean text. No watermarks, no logos.
```

출력 SVG (`kickscooter-cartoon-card.svg`로 저장):

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1350" width="1080" height="1350">
  <!-- palette: bg grad #EDEDED->#8C8C8C / frame #CBB994 / ink #1A1A1A / gray #8C8C8C / accent #A8B43C -->
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#EDEDED"/>
      <stop offset="1" stop-color="#8C8C8C"/>
    </linearGradient>
  </defs>

  <!-- 배경 그라데이션 -->
  <rect width="1080" height="1350" fill="url(#bg)"/>
  <!-- 얇은 베이지 테두리 액자 -->
  <rect x="22" y="22" width="1036" height="1306" fill="none" stroke="#CBB994" stroke-width="4"/>

  <!-- 바닥/연석: 단순한 검정 라인 -->
  <path d="M120 640 L640 640 L640 700 L980 700"
        fill="none" stroke="#1A1A1A" stroke-width="8"
        stroke-linejoin="round" stroke-linecap="round"/>

  <g stroke="#1A1A1A" stroke-width="8" stroke-linejoin="round" stroke-linecap="round">
    <!-- 상대 고래: 회색 실루엣, 오른쪽에서 놀라 젖힘 -->
    <g>
      <ellipse cx="820" cy="560" rx="86" ry="112" fill="#8C8C8C"/>
      <line x1="820" y1="448" x2="820" y2="418" stroke-width="6"/>       <!-- 분수 -->
      <path d="M756 662 L730 700 M884 662 L910 700" stroke-width="6"/>   <!-- 꼬리 -->
      <circle cx="792" cy="536" r="7" fill="#1A1A1A" stroke="none"/>     <!-- 눈 -->
      <path d="M905 505 L935 495 M912 530 L944 528" stroke-width="5"/>   <!-- 놀람 표시 -->
    </g>

    <!-- 전동킥보드: 유일한 올리브 포인트 -->
    <g>
      <line x1="300" y1="632" x2="470" y2="632" stroke="#A8B43C" stroke-width="16"/> <!-- 발판 -->
      <line x1="300" y1="632" x2="270" y2="470" stroke="#A8B43C" stroke-width="14"/> <!-- 핸들 기둥 -->
      <line x1="238" y1="470" x2="302" y2="470" stroke="#A8B43C" stroke-width="14"/> <!-- 핸들바 -->
      <circle cx="300" cy="672" r="34" fill="#FFFFFF"/>                              <!-- 앞바퀴 -->
      <circle cx="470" cy="672" r="34" fill="#FFFFFF"/>                              <!-- 뒷바퀴 -->
    </g>

    <!-- 모는 고래: 흰색 외곽선, 앞으로 기울임 -->
    <g>
      <ellipse cx="392" cy="470" rx="92" ry="120" fill="#FFFFFF"/>
      <line x1="392" y1="350" x2="392" y2="318" stroke-width="6"/>       <!-- 분수 -->
      <path d="M300 470 L262 476 M300 500 L268 512" stroke-width="7"/>   <!-- 손잡이 잡은 앞지느러미 -->
      <path d="M330 582 L308 628 M454 582 L476 628" stroke-width="6"/>   <!-- 꼬리 -->
      <circle cx="356" cy="446" r="7" fill="#1A1A1A" stroke="none"/>     <!-- 눈 -->
    </g>
  </g>

  <!-- 헤드라인: 왼쪽 아래, 굵은 고딕, 3줄 -->
  <text x="80" y="982" text-anchor="start" fill="#1A1A1A"
        font-family="'Gothic A1', 'Nanum Gothic', sans-serif" font-size="72" font-weight="800">"부딪힐 뻔"</text>
  <text x="80" y="1086" text-anchor="start" fill="#2A2A2A"
        font-family="'Gothic A1', 'Nanum Gothic', sans-serif" font-size="60" font-weight="800">'전동킥보드' 이렇게 타고 쌩쌩,</text>
  <text x="80" y="1178" text-anchor="start" fill="#2A2A2A"
        font-family="'Gothic A1', 'Nanum Gothic', sans-serif" font-size="60" font-weight="800">오늘만 3번 봤습니다</text>
</svg>
```

한국어 한 줄 설명: 핵심 사물을 전동킥보드로 잡아 올리브를 거기에만 줬고, 모는 고래는 흰 외곽선·상대
고래는 회색 실루엣으로 대비해 카드뉴스로 그렸습니다. (참고 카드의 우산·계단 구도는 쓰지 않고
그림체·색감·레이아웃만 가져왔습니다.)

## 완료 전 확인

- 참고 카드의 구도(우산·계단·인물)를 복제하지 않고, 소재에 맞는 새 구도에 **그림체·색감·레이아웃만**
  입혔는가?
- 사람이 아니라 **고래 캐릭터**로 그렸고, 캐릭터 정의 문장을 프롬프트에 글자 그대로 복사했는가?
- 올리브 그린 `#A8B43C`를 카드가 말하려는 **핵심 사물 하나**에만 썼는가? 나머지는 전부 무채색인가?
- 회색 세로 그라데이션 배경, 얇은 베이지 테두리 액자, 낙서풍 검정 라인을 지켰는가?
- 그림은 위쪽, 굵은 고딕 헤드라인은 왼쪽 아래로 구역을 나눴고, 참고 카드의 상하좌우 간격 비율을 따랐는가?
- 헤드라인 문구는 사용자가 준 그대로 넣었는가? (없을 때만 skill이 만든다)
- SVG가 기본 요소만 쓰고 텍스트가 편집 가능한 `text`로 남아 있는가? 폰트가 저작권 없는 폰트
  (`'Gothic A1', 'Nanum Gothic'`, SIL OFL)인가?
- 프롬프트 블록, SVG 파일 경로, 한국어 한 줄 설명을 모두 출력했는가?
