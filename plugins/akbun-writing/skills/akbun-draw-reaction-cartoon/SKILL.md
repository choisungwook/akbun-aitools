---
name: akbun-draw-reaction-cartoon
description: >
  상황·주제·이미지를 "왼쪽 인물이 갸웃하며 오른쪽 모니터 속 대상의 말풍선을 바라보는" 한 컷 손그림
  반응 만화로 만든다. 산출물은 두 가지다: 이미지 생성 모델(GPT image, nano-banana 등)에 그대로 넣을
  영어 프롬프트와, Figma/Canva로 가져와 편집할 수 있는 SVG 파일. 말풍선 문구를 사용자가 주면 그대로
  쓰고, 없으면 내용을 분석해 skill이 만든다.
  Trigger on: "반응 만화", "한 컷 만화", "리액션 만화", "모니터 만화", "말풍선 만화 프롬프트",
  "reaction cartoon", "one-panel cartoon", "만화 SVG", "figma svg 만화", "canva svg 만화",
  or any request to turn a situation into a one-panel reaction cartoon prompt or SVG.
---

# 한 컷 반응 만화 프롬프트 + SVG 생성

## 이 skill이 하는 일

하나의 상황을 **한 컷 반응 만화**로 보여주는 결과물을 만든다. 장면은 고정이다: 왼쪽에서 인물이 턱을
괴고 갸웃(오렌지 물음표)하며, 오른쪽 책상 위 모니터 속 대상이 말풍선으로 한마디 하는 장면이다.
"화면 속 대상이 하는 말"과 "그걸 보는 사람의 갸웃"의 대비로 상황을 즉시 전달한다. AI의 이상한 답변,
예상 밖의 알림, 어이없는 결과 화면처럼 **화면이 사람에게 말을 거는 상황**에 어울린다.

산출물은 그림이 아니라 두 가지다.

1. **영어 이미지 생성 프롬프트** — GPT image나 nano-banana 같은 이미지 생성 모델에 그대로 붙여넣는다.
2. **SVG 파일** — 같은 장면을 벡터로 재구성한 파일. Figma나 Canva로 가져와 문구·색을 직접 편집한다.

`akbun-draw-webtoon`(3~4컷 스토리), `akbun-draw-sketchbook-card`(개념 카드)와 짝이 되는 "한 컷 상황
반응" 버전이다. 이 skill만 SVG를 함께 만든다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록에 담아 그대로 복사할 수 있게 한다.
2. **SVG 파일** — 작업 디렉터리에 `<주제-slug>-cartoon.svg`로 저장하고 경로를 알려준다.
3. **한국어 한 줄 설명** — 화면 속 대상과 말풍선 문구를 어떻게 정했는지 1~2문장.

## 입력 다루기

사용자가 주는 것은 상황 설명, 참고 이미지, 말풍선 문구의 조합이며 전부 선택이다.

- **말풍선 문구를 줬으면 그대로 쓴다.** 요약하거나 다듬지 않는다.
- **참고 이미지를 줬으면 내용을 분석한다.** 이미지에서 상황·대상·감정을 읽어 화면 속 대상과 말풍선
  문구 후보를 정한다. 참고 이미지는 픽셀 복제 대상이 아니라 내용 파악용이다. 레이아웃과 스타일은
  항상 아래 고정 레이아웃을 따른다.
- **글이 없으면 skill이 만든다.** 상황을 분석해 말풍선 문구(1~2줄, 짧게)를 만들고 그대로 진행한다.
  사용자에게 문구를 물어보며 멈추지 않는다.
- **화면 속 대상**은 상황의 화자다. AI/봇이면 로봇, 클라우드 서비스면 구름, 알림이면 종 캐릭터처럼
  단순한 의인화 캐릭터 하나로 정한다.

## 작업 순서

1. **상황 파악.** 사용자가 준 설명·이미지·문구에서 "누가(화면 속 대상) 무슨 말을 하고, 왜 갸웃한가"를
   정한다.
2. **말풍선 문구 확정.** 사용자가 준 문구는 그대로, 없으면 짧게 만든다. 말줄임표(`...`)로 끝나는
   심드렁한 톤이 이 스타일과 잘 어울린다.
3. **화면 속 대상 결정.** 단순한 의인화 캐릭터 하나. 오렌지 포인트를 줄 핵심부(얼굴, 화면 등)도 정한다.
4. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채운다.
5. **SVG 조립.** 아래 `SVG 템플릿`의 좌표를 유지한 채 말풍선 텍스트와 화면 속 대상만 바꿔 저장한다.
6. **출력.** 프롬프트 블록 + SVG 파일 경로 + 한국어 한 줄 설명을 출력한다.

## 비주얼 스타일 (레퍼런스에 고정)

모든 산출물은 아래 스타일을 그대로 따른다. 바꾸지 않는다.

- **매체**: 균일한 굵기의 진회색 잉크 라인으로 그린 손그림 만화. 면은 플랫한 회색 톤으로만 칠한다.
- **팔레트**: 배경 off-white `#F4F2ED`, 잉크 라인 `#3A3A3A`, 음영 회색 `#C9C9C9`/`#E3E3E3`,
  모니터 화면 배경 `#5A5A5A`.
- **포인트 색**: 따뜻한 오렌지 `#E8833A` 하나만. **물음표**와 **화면 속 대상의 핵심부**(얼굴 등)
  딱 두 곳에만 쓴다. 그 외 전부 모노크롬.
- **인물**: 상반신만. 짧은 검은 머리, 반팔 셔츠(소매는 회색), 한 손으로 턱을 괴고 눈썹을 찌푸린 채
  화면을 곁눈질하는 갸웃한 표정.
- **글씨**: 말풍선 문구는 손글씨 느낌. 한국어 그대로 가능하다. 길수록 이미지 모델이 글자를 틀리므로
  1~2줄로 짧게 유지한다.

## 레이아웃과 간격 (레퍼런스에 고정)

한 컷의 배치와 상하좌우 간격은 아래 수치에 고정한다. 캔버스는 가로형 7:5(예: 1680×1200)다.
좌표는 캔버스 폭·높이에 대한 비율이다.

- **여백**: 위 8%, 아래 8%, 왼쪽 9%, 오른쪽 8%. 모든 요소는 이 안쪽에 둔다.
- **인물 (왼쪽)**: 가로 9~33% 영역. 머리 꼭대기가 높이 20% 지점, 몸통은 책상 뒤로 내려간다.
- **물음표 생각 방울**: 중심 (37%, 24%), 지름 약 9%. 작은 꼬리 방울 2개가 인물 머리 쪽(왼쪽 아래)으로
  이어진다. 물음표는 오렌지.
- **말풍선 (위 오른쪽)**: 가로 49~67%, 세로 12~28%의 둥근 사각형. 꼬리는 아래로 뻗어 모니터 상단에
  닿는다.
- **모니터 (오른쪽)**: 가로 46~82%. 화면은 세로 28~66%, 받침 기둥과 바닥판은 66~77%에서 책상 위에
  선다. 화면은 진회색이고 그 안에 화면 속 대상이 있다.
- **화면 속 대상**: 화면 영역의 가운데~오른쪽에 상반신이 보이게 배치한다.
- **책상**: 윗면이 높이 76% 지점, 가로 8~92%를 가로지른다. 인물 몸통과 모니터가 모두 책상에 걸친다.
- **읽는 순서**: 인물(왼쪽) → 물음표 → 말풍선 → 화면 속 대상. 시선과 말풍선 꼬리가 이 흐름을 만든다.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다.

```text
A single-panel hand-drawn editorial cartoon, landscape 7:5 aspect ratio, drawn with uniform
dark-gray ink outlines (#3A3A3A) and flat gray shading on a warm off-white paper background
(#F4F2ED), like a friendly illustration in a tech book.

PALETTE: monochrome grays only, plus exactly ONE accent color — warm orange (#E8833A) — used
ONLY on the question mark and on <ORANGE FOCAL PART of the on-screen subject, e.g. "the robot's
screen-shaped face">. Nothing else has color.

LAYOUT (fixed positions, generous margins of about 8-9% on all sides):
- LEFT THIRD: a person shown from the waist up behind a desk, short dark hair, short-sleeve
  shirt with gray sleeves, resting their chin on one hand, eyebrows slightly furrowed, glancing
  sideways at the monitor with a puzzled, skeptical expression. Head top at about 20% of the
  image height.
- Between the person and the monitor, near the top: a round thought bubble containing a large
  orange question mark, with two small trailing bubbles leading down-left toward the person's
  head.
- RIGHT SIDE: a desktop computer monitor standing on the desk (screen spans roughly the 46-82%
  band horizontally, from about 28% to 66% of the height, with a neck and flat base below).
  The screen background is dark gray (#5A5A5A).
- INSIDE THE SCREEN: <ON-SCREEN SUBJECT — one simple personified character shown from the waist
  up, e.g. "a cute retro robot with a TV-shaped head">. <ORANGE FOCAL PART> is the only colored
  part of the subject.
- Above the monitor: a rounded rectangular speech bubble whose tail points down to the top of
  the monitor, containing handwritten text reading exactly: "<SPEECH LINE 1>" <and on a second
  line: "<SPEECH LINE 2>">. The text is hand-lettered in dark ink.
- A simple desk surface runs across the bottom at about 76% of the height; both the person and
  the monitor rest on it. Keep the area below the desk empty.

STYLE: clean uniform ink lines, flat fills, no hatching, no texture noise, warm and friendly,
very legible hand lettering. Landscape 7:5 aspect ratio.

DO NOT: use any color other than the grays and the single orange accent. Do not add text other
than the speech bubble text and the question mark. Do not misspell the text. No logos, no
watermarks, no panel borders, no background objects other than the desk.
```

## SVG 템플릿

SVG는 아래 뼈대의 **좌표와 스타일을 유지한 채** 두 곳만 바꾼다: `speech-text`의 문구와
`screen-subject` 그룹의 캐릭터. 캐릭터는 단순한 도형 조합으로 그리고, 오렌지는 물음표와 캐릭터
핵심부 두 곳만 유지한다.

Figma/Canva 호환 규칙:

- SVG 1.1 기본 요소만 쓴다: `rect`, `circle`, `ellipse`, `path`, `polygon`, `text`, `g`.
- `filter`, `mask`, `foreignObject`, 외부 이미지 참조, 임베디드 폰트는 쓰지 않는다.
- 텍스트는 `text` 요소로 남겨 가져온 뒤 바로 편집할 수 있게 한다.
- 폰트는 저작권 걱정 없는 SIL OFL 폰트만 지정한다: 한글 손글씨 `Gaegu`(개구체), 대체
  `Nanum Pen Script`, 라틴 대체 `Patrick Hand`. 셋 다 Google Fonts에서 무료다. Figma/Canva에서
  해당 폰트가 없으면 fallback으로 표시되며, 텍스트가 편집 가능하므로 원하는 폰트로 바꾸면 된다.
- Figma는 SVG를 드래그해 넣고, Canva는 업로드 → 디자인에 추가로 가져온다.

아래는 뼈대 SVG다.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1680 1200" width="1680" height="1200">
  <!-- palette: bg #F4F2ED / ink #3A3A3A / grays #C9C9C9 #E3E3E3 / screen #5A5A5A / accent #E8833A -->
  <rect id="bg" width="1680" height="1200" fill="#F4F2ED"/>

  <g id="desk" stroke="#3A3A3A" stroke-width="6">
    <rect x="134" y="912" width="1412" height="42" fill="#E3E3E3"/>
    <rect x="168" y="954" width="1344" height="56" fill="#C9C9C9"/>
  </g>

  <g id="person" stroke="#3A3A3A" stroke-width="6" fill="#F4F2ED">
    <path id="torso" d="M240 912 V620 Q240 520 335 505 L460 488 Q528 484 540 550 L562 912 Z"/>
    <path id="sleeve" d="M240 912 V680 Q240 610 300 598 L336 592 L344 740 L300 912 Z" fill="#C9C9C9"/>
    <path id="neck" d="M330 438 L330 500 L400 500 L390 438 Z"/>
    <circle id="head" cx="355" cy="345" r="100"/>
    <path id="hair" d="M258 330 Q250 232 355 228 Q462 232 452 322 Q420 250 355 262 Q290 252 258 330 Z" fill="#3A3A3A"/>
    <g id="face" fill="#3A3A3A" stroke="none">
      <circle cx="330" cy="352" r="9"/>
      <circle cx="408" cy="352" r="9"/>
      <path d="M310 320 L352 312" stroke="#3A3A3A" stroke-width="7" stroke-linecap="round"/>
      <path d="M388 314 L428 322" stroke="#3A3A3A" stroke-width="7" stroke-linecap="round"/>
      <path d="M352 408 Q370 400 386 410" fill="none" stroke="#3A3A3A" stroke-width="7" stroke-linecap="round"/>
    </g>
    <path id="forearm" d="M352 912 C344 740 352 620 396 540 L448 566 C420 640 416 750 424 912 Z"/>
    <ellipse id="hand" cx="400" cy="487" rx="38" ry="32"/>
  </g>

  <g id="thought-bubble" stroke="#3A3A3A" stroke-width="6" fill="#FFFFFF">
    <circle cx="540" cy="446" r="14"/>
    <circle cx="578" cy="392" r="22"/>
    <circle cx="622" cy="288" r="74"/>
    <text x="622" y="322" text-anchor="middle" fill="#E8833A" stroke="none"
          font-family="Gaegu, 'Nanum Pen Script', 'Patrick Hand', sans-serif"
          font-size="96" font-weight="700">?</text>
  </g>

  <g id="monitor" stroke="#3A3A3A" stroke-width="8">
    <rect x="774" y="336" width="606" height="470" rx="28" fill="#F4F2ED"/>
    <rect x="812" y="374" width="530" height="386" rx="12" fill="#5A5A5A" stroke-width="6"/>
    <rect x="1038" y="806" width="82" height="70" fill="#E3E3E3" stroke-width="6"/>
    <rect x="946" y="876" width="266" height="30" rx="12" fill="#E3E3E3" stroke-width="6"/>
  </g>

  <!-- screen-subject: 화면 속 대상. 아래는 예시 캐릭터이며 내용에 맞는 단순한 도형 캐릭터로 교체한다.
       오렌지(#E8833A)는 캐릭터 핵심부 한 곳에만 쓴다. -->
  <g id="screen-subject" stroke="#3A3A3A" stroke-width="6">
    <rect x="1030" y="430" width="190" height="160" rx="18" fill="#E3E3E3"/>
    <rect x="1058" y="456" width="134" height="108" rx="10" fill="#E8833A"/>
    <g fill="#3A3A3A" stroke="none">
      <circle cx="1098" cy="500" r="8"/>
      <circle cx="1152" cy="500" r="8"/>
    </g>
    <path d="M1100 534 Q1125 550 1150 534" fill="none" stroke-linecap="round"/>
    <rect x="1075" y="612" width="100" height="110" rx="16" fill="#E3E3E3"/>
  </g>

  <g id="speech-bubble" stroke="#3A3A3A" stroke-width="6" fill="#FFFFFF">
    <polygon points="988 300 1042 300 1000 372" stroke-linejoin="round"/>
    <rect x="822" y="132" width="360" height="176" rx="24"/>
    <text id="speech-text" x="1002" y="204" text-anchor="middle" fill="#3A3A3A" stroke="none"
          font-family="Gaegu, 'Nanum Pen Script', 'Patrick Hand', sans-serif" font-size="52">
      <tspan x="1002" dy="0">말풍선 1줄</tspan>
      <tspan x="1002" dy="60">말풍선 2줄...</tspan>
    </text>
  </g>
</svg>
```

## 예시 (gold reference)

이 예시는 위 스타일을 적용한 완성 산출물이다. 새 산출물의 품질 기준으로 삼는다.

입력 예:

```text
상황: 이번 달 클라우드 비용이 갑자기 튀었다. 콘솔을 열어보고 할 말을 잃은 개발자.
```

skill이 한 판단: 말풍선 문구가 없으므로 화면 속 화자를 "청구서를 든 구름 캐릭터"로 정하고, 문구를
"이번 달 청구 금액 / $3,247..."로 만들었다. 오렌지 포인트는 물음표와 구름이 든 청구서 두 곳이다.

출력 프롬프트:

```text
A single-panel hand-drawn editorial cartoon, landscape 7:5 aspect ratio, drawn with uniform
dark-gray ink outlines (#3A3A3A) and flat gray shading on a warm off-white paper background
(#F4F2ED), like a friendly illustration in a tech book.

PALETTE: monochrome grays only, plus exactly ONE accent color — warm orange (#E8833A) — used
ONLY on the question mark and on the invoice sheet held by the on-screen cloud character.
Nothing else has color.

LAYOUT (fixed positions, generous margins of about 8-9% on all sides):
- LEFT THIRD: a person shown from the waist up behind a desk, short dark hair, short-sleeve
  shirt with gray sleeves, resting their chin on one hand, eyebrows slightly furrowed, glancing
  sideways at the monitor with a puzzled, skeptical expression. Head top at about 20% of the
  image height.
- Between the person and the monitor, near the top: a round thought bubble containing a large
  orange question mark, with two small trailing bubbles leading down-left toward the person's
  head.
- RIGHT SIDE: a desktop computer monitor standing on the desk (screen spans roughly the 46-82%
  band horizontally, from about 28% to 66% of the height, with a neck and flat base below).
  The screen background is dark gray (#5A5A5A).
- INSIDE THE SCREEN: a chubby smiling cloud character with stubby arms, shown from the waist
  up, cheerfully holding up a small orange invoice sheet. The orange invoice is the only
  colored part of the subject.
- Above the monitor: a rounded rectangular speech bubble whose tail points down to the top of
  the monitor, containing handwritten text reading exactly: "이번 달 청구 금액" and on a second
  line: "$3,247...". The text is hand-lettered in dark ink.
- A simple desk surface runs across the bottom at about 76% of the height; both the person and
  the monitor rest on it. Keep the area below the desk empty.

STYLE: clean uniform ink lines, flat fills, no hatching, no texture noise, warm and friendly,
very legible hand lettering. Landscape 7:5 aspect ratio.

DO NOT: use any color other than the grays and the single orange accent. Do not add text other
than the speech bubble text and the question mark. Do not misspell the text. No logos, no
watermarks, no panel borders, no background objects other than the desk.
```

SVG는 템플릿에서 `speech-text`를 `이번 달 청구 금액` / `$3,247...` 두 줄로 바꾸고,
`screen-subject`를 구름 몸통(회색 타원 조합) + 오렌지 청구서(작은 사각형)로 교체해
`cloud-bill-cartoon.svg`로 저장한다.

한국어 한 줄 설명: 화면 속 화자를 청구서를 든 구름 캐릭터로 정하고, 말풍선 문구 "이번 달 청구 금액 /
$3,247..."를 만들어 개발자의 갸웃(오렌지 물음표)과 대비시켰습니다.

## 완료 전 확인

- 사용자가 준 말풍선 문구를 바꾸지 않고 그대로 넣었는가? (문구가 없을 때만 skill이 만든다)
- 프롬프트 속 말풍선 텍스트를 `reading exactly: "..."`로 철자까지 지정했는가?
- 오렌지 `#E8833A`를 물음표와 화면 속 대상 핵심부 두 곳에만 썼는가?
- 고정 레이아웃(인물 왼쪽 9~33%, 물음표 37%/24%, 말풍선 49~67%, 모니터 46~82%, 책상 76%)과
  상하좌우 여백(8~9%)을 지켰는가?
- SVG가 기본 요소만 쓰고 텍스트가 편집 가능한 `text`로 남아 있는가? 폰트가 SIL OFL(Gaegu 등)인가?
- 프롬프트 블록, SVG 파일 경로, 한국어 한 줄 설명을 모두 출력했는가?
