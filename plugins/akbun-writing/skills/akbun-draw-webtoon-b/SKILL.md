---
name: akbun-draw-webtoon-b
description: >
  사용자가 준 이미지·글로 파스텔 수채 치비 동물 캐릭터 웹툰 페이지를 만든다. 페이지별 이미지 생성 프롬프트와
  Figma/Canva에서 편집할 수 있는 한글 텍스트 SVG를 함께 만들고, 글이 없으면 내용을 분석해 이야기를 먼저 만든다.
---

# 파스텔 동물 캐릭터 웹툰 페이지 만들기 (이미지 프롬프트 + SVG)

## 이 skill이 하는 일

사용자가 남긴 이미지와 글(이야기, 상황, 일기)을 분석해서 **파스텔 수채 치비 동물 캐릭터 웹툰 페이지**를 만든다. 결과물은 두 가지다.

1. **페이지별 영어 이미지 생성 프롬프트** — 이미지 생성 모델(agent)에 그대로 붙여넣는다. 내레이션·대사 같은 한글 텍스트도 그림에 포함하도록 지시한다.
2. **페이지 레이아웃 SVG** — 같은 내레이션·대사를 편집 가능한 텍스트로 담은 SVG 파일. Figma나 Canva로 가져와 문구를 다듬거나, 그림 속 글자가 틀렸을 때 그림 위에 얹어 교체하는 텍스트 레이어로 쓴다.

사용자가 글을 주지 않으면 skill이 먼저 첨부 이미지나 대화 맥락을 분석해 내레이션·대사 초안(한국어)을 만들고, 그 초안으로 페이지 구성과 프롬프트 작업을 진행한다.

akbun-draw-webtoon-a(xkcd풍 흑백 스틱피겨)와 다른 skill이다. 이 skill은 파스텔 채색 치비 동물 캐릭터 그림체와 SVG 텍스트 오버레이가 고정이다.

## 캐릭터 (고정)

이 웹툰은 사람을 그리지 않고 의인화된 동물 캐릭터만 쓴다. 아래 세 캐릭터 정의를 그대로 쓰고, 각 영어 문장은 해당 캐릭터가 나오는 모든 프롬프트에 **글자 그대로** 복사한다. 이미지 모델은 컷 간 기억이 없어서, 문장이 다르면 캐릭터가 달라진다. 사용자가 다른 동물·외모를 지정하면 그대로 따르되, 동물 캐릭터는 유지한다.

### 주인공 캐릭터

이야기의 화자("나")를 그리는 캐릭터. 수컷 치비 수달 — 부드러운 연갈색 털, 크림색 주둥이와 배, 작고 동그란 귀, 크고 반짝이는 진갈색 눈, 발그레한 볼터치, 머리털에 흰 하이라이트 줄기, 뮤트 그레이블루 후드티.

주인공의 영어 CHARACTER 문장:

```text
a chibi male otter character with soft light-brown fur, a cream muzzle and belly, small round
ears, big sparkling dark-brown eyes, blushing cheeks, white highlight streaks on his head fur,
wearing a muted gray-blue hoodie
```

### 상대 캐릭터

2인 대화 장면에서 주인공의 대화 상대를 그리는 캐릭터. 치비 토끼 — 더스티 로즈 핑크 털, 길게 늘어진 귀, 크고 반짝이는 회색 눈, 발그레한 볼터치, 크림 옐로 가디건.

상대 캐릭터의 영어 CHARACTER 문장:

```text
a chibi rabbit character with dusty-pink fur, long droopy ears, big sparkling gray eyes,
blushing cheeks, wearing a cream yellow cardigan
```

### 군중 캐릭터 (얼굴 없음)

세 명 이상이 나오는 장면에서 주인공·상대를 제외한 무리를 그리는 캐릭터. 개별 인물로 그리지 않고 이목구비 없는 연회색 동물 실루엣으로 뭉뚱그려 하나의 무리처럼 그린다. 주인공·상대와 확실히 구분되게 채색하지 않는다.

군중 캐릭터의 영어 문장:

```text
a loose crowd of simple faceless animal figures with plain light-gray rounded bodies and heads,
no facial features, sketched softly together as one background group
```

## 비주얼 스타일 (모든 프롬프트에 고정)

모든 이미지 프롬프트는 아래 스타일을 그대로 묘사한다. 한국 감성 일상툰에서 볼 수 있는 부드러운 파스텔 손그림 스타일이다.

- **배경**: 순백색. 장면에 꼭 필요한 소품·벽·바닥만 옅은 회색 선과 연한 파스텔로 최소한만 그린다.
- **선**: 따뜻한 진회색(먹색)의 가늘고 살짝 흔들리는 연필/잉크 손그림 외곽선.
- **채색**: 수채처럼 투명하고 부드러운 파스텔 톤. 면을 꽉 채우지 않고 흰 여백이 배어나온다.
- **팔레트**: 더스티 로즈 핑크, 크림 옐로, 뮤트 그레이블루, 연갈색. 한 컷에 3~4색이면 충분하다.
- **인물**: `캐릭터 (고정)` 섹션의 동물 캐릭터만 쓴다.
- **감정 연출**: 놀람 느낌표, 땀방울, 움직임 곡선 같은 만화 기호를 아껴서 쓴다.
- **분위기**: 잔잔하고 따뜻한 일상·감성 무드. 과장된 액션보다 표정과 몸짓 중심.
- **글자**: 내레이션·대사·효과음을 짧은 한글 손글씨로 그림에 넣는다. 문장은 짧게 유지하고, 같은 텍스트를 SVG에도 담아 Figma/Canva에서 수정할 수 있게 한다.

## 페이지 레이아웃 규칙

캔버스는 **항상 1080×1350 세로형(4:5)**이고 배경은 순백색이다. 요소 위치를 고정 좌표로 정하지 않는다. 캐릭터 수, 대사 길이, 사물 위치, 글씨 위치에 맞춰 자연스럽게 배치하되 아래 원칙을 지킨다.

- **상단 내레이션**: 페이지 맨 위 가운데. 상황을 여는 문장을 둔다.
- **하단 내레이션**: 페이지 맨 아래 가운데, 상단보다 크게. 핵심·여운 문장을 둔다. 보조 내레이션이 필요하면 괄호로 감싸 더 작게, 오른쪽으로 치우쳐 그 아래 둔다.
- **컷 구성**: 페이지 내용에 맞춰 고른다.
  - 나란히 대비되는 두 장면 — 위·아래 전폭 가로 괘선과 살짝 기울인 세로 분할선으로 나눈 2컷.
  - 감정을 크게 보여줄 한 장면 — 테두리·괘선 없이 흰 여백 위에 그대로 놓는 1컷.
  - 대화 장면 — 테두리 없이 캐릭터 상반신(또는 머리)과 손그림 말풍선으로 구성.
- **대사**: 말하는 캐릭터 머리 근처 빈 공간에 손글씨로 띄우거나 말풍선에 넣는다. 효과음·혼잣말은 더 작게 캐릭터 옆에 둔다.
- **여백**: 사방에 넉넉한 흰 여백을 남긴다. 그림과 글씨가 캔버스 가장자리나 괘선에 붙지 않게 한다.
- **시선 흐름**: 위에서 아래로, 2컷이면 왼쪽에서 오른쪽으로 읽히게 배치한다.

## 폰트 규칙

SVG의 모든 텍스트는 저작권 걱정 없는 무료 폰트만 쓴다.

- 기본: **Nanum Pen Script** (나눔손글씨 펜, SIL OFL)
- 대체: **Gaegu** (개구, SIL OFL)

두 폰트 모두 Google Fonts에서 무료로 내려받을 수 있다. Figma/Canva에서 텍스트가 올바르게 보이려면 사용자가 폰트를 설치해야 하므로, SVG를 건넬 때 이 안내를 한 줄 덧붙인다. `font-family`는 항상 `'Nanum Pen Script', 'Gaegu', cursive`로 지정한다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **한국어 페이지 시나리오** — 페이지·컷 구성, 각 페이지의 내레이션/대사. 사용자가 글을 안 줬으면 여기서 만든 이야기를 먼저 보여준다.
2. **페이지별 영어 이미지 생성 프롬프트** — 페이지마다 하나씩, 각각 코드 펜스 블록(```text)으로.
3. **페이지별 SVG 파일** — 작업 디렉터리에 `webtoon-page-1.svg`처럼 저장하고 경로를 알려준다.

## 작업 순서

1. **입력 파악.** 사용자가 남긴 이미지와 글을 읽는다. 이미지가 있으면 인물·상황·감정을 분석한다.
2. **이야기 확보.** 글이 있으면 그대로 쓴다. 없으면 첨부 이미지와 맥락을 근거로 내레이션·대사 초안을 한국어로 만든다. 지어낸 이야기임을 밝히고 페이지 시나리오에 포함한다.
3. **페이지·컷 구성.** 이야기를 페이지 단위로 나누고, 페이지마다 컷 구성(2컷/1컷/대화)을 고른다.
4. **캐릭터 배정.** 화자는 주인공 캐릭터, 2인 대화 상대는 상대 캐릭터, 그 외 무리는 군중 캐릭터로 그린다. 정의 문장을 프롬프트에 글자 그대로 복사한다.
5. **페이지별 프롬프트 작성.** 아래 `이미지 프롬프트 템플릿`을 채운다. 그림에 넣을 한글 텍스트를 한 줄씩 정확히 나열한다.
6. **SVG 작성.** 아래 `SVG 템플릿`을 바탕으로 페이지의 텍스트를 같은 배치로 담아 저장한다. 좌표는 페이지 구성(캐릭터·사물·글씨 위치)에 맞춰 조정한다. 생성된 그림 파일이 이미 있으면 `<image>`로 넣고, 없으면 연회색 자리표시 사각형을 둔다.
7. **출력.** 페이지 시나리오 + 프롬프트 블록들 + SVG 파일 경로(폰트 설치 안내 포함)를 출력한다.

## 컷 구성 원칙

- **한 컷 = 한 감정.** 컷 하나에 행동과 감정 하나만 담는다.
- **내레이션이 이야기를 끌고, 그림은 감정을 보여준다.** 상황 설명은 상단 내레이션, 여운·반전은 하단 내레이션에 둔다.
- **대사는 짧게.** 컷당 한두 마디, 15자 이내. 길어지면 내레이션으로 옮긴다.
- **2컷 페이지는 대비.** 왼쪽 컷과 오른쪽 컷이 시점 전환(두 인물, 전후 순간)으로 대비되게 구성한다.
- **캐릭터 수 최소화.** 컷당 주인공·상대 1~2명이 기본. 무리가 필요하면 군중 캐릭터로 뭉뚱그린다.

## 이미지 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 페이지마다 채운다. 캐릭터 문장은 `캐릭터 (고정)` 섹션에서 글자 그대로 복사하고, 나오지 않는 캐릭터 줄과 쓰지 않는 텍스트 줄은 지운다.

```text
A vertical 4:5 (1080x1350) webtoon page illustration in a soft pastel Korean chibi style. Thin, slightly
wobbly warm dark-gray pencil ink outlines on a pure white background. Transparent
watercolor-like pastel coloring that leaves white space showing through — dusty rose pink,
cream yellow, muted gray-blue, light brown palette.

LAYOUT: <choose one and describe —
"two panels side by side, separated by full-width thin horizontal rules above and below the
panel row and a slightly slanted thin vertical divider between the panels" |
"one borderless scene centered on white space" |
"two character busts facing each other with hand-drawn speech bubbles, no borders">.
Generous white margins on all sides; nothing touches the canvas edges.

MAIN CHARACTER: <paste the fixed sentence verbatim>.
SECOND CHARACTER: <paste the fixed sentence verbatim, only for two-person dialogue>.
CROWD: <paste the fixed sentence verbatim, only when three or more figures appear>.

SCENE <1|2>: <who does what, posture and emotion, plus the one or two props that matter, e.g.
"the main character wrestles with sticky cookie dough on a small wooden table, flour dust on
his head fur, a nervous but determined expression, small sweat drop near his cheek">.

TEXT IN IMAGE (short handwritten Korean, render each line exactly as written):
- top narration, centered: "<...>"
- dialogue near <which character>: "<...>"
- bottom narration, centered, larger: "<...>"
- sub narration below it, smaller, in parentheses, shifted right: "(<...>)"

STYLE: gentle slice-of-life mood, comic emotion marks (surprise marks, sweat drops, motion
curves) used sparingly, minimal background props in pale gray lines and light pastel.

DO NOT: no human characters, no photorealism, no heavy shading, no saturated colors, no gray
or colored background fills, no watermarks. Do not misspell, translate, or rearrange the
Korean text, and do not add any text beyond the lines listed above.
```

## SVG 템플릿

2컷 페이지용 뼈대다. 캔버스는 항상 1080×1350이고, 아래 좌표는 배치 예시다 — 페이지의 캐릭터·사물·글씨 위치에 맞춰 조정한다. 1컷·대화 페이지는 괘선·분할선을 지우고 텍스트만 배치한다. 생성된 그림이 있으면 자리표시 `<rect>`/`<text>`를 `<image x="..." y="..." width="..." height="..." href="page-1.png"/>`로 교체한다.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">
  <!-- 배경 -->
  <rect width="1080" height="1350" fill="#ffffff"/>

  <!-- 상단 내레이션: 페이지 맨 위 가운데 -->
  <text x="540" y="70" text-anchor="middle" dominant-baseline="middle"
        font-family="'Nanum Pen Script', 'Gaegu', cursive" font-size="44" fill="#3a3a3a">상단 내레이션…</text>

  <!-- 패널 괘선(2컷 페이지만): 위·아래 전폭 가로선 -->
  <line x1="0" y1="130" x2="1080" y2="130" stroke="#3a3a3a" stroke-width="2"/>
  <line x1="0" y1="1060" x2="1080" y2="1060" stroke="#3a3a3a" stroke-width="2"/>

  <!-- 컷 분할선(2컷 페이지만): 살짝 기울임 -->
  <line x1="552" y1="130" x2="522" y2="1060" stroke="#3a3a3a" stroke-width="2"/>

  <!-- 그림 자리표시: 그림이 생기면 <image>로 교체 -->
  <rect x="30" y="160" width="470" height="870" fill="#f4f4f4"/>
  <text x="265" y="600" text-anchor="middle" font-family="'Nanum Pen Script', 'Gaegu', cursive"
        font-size="36" fill="#9a9a9a">컷 1 그림</text>
  <rect x="580" y="160" width="470" height="870" fill="#f4f4f4"/>
  <text x="815" y="600" text-anchor="middle" font-family="'Nanum Pen Script', 'Gaegu', cursive"
        font-size="36" fill="#9a9a9a">컷 2 그림</text>

  <!-- 대사: 말하는 캐릭터 머리 근처 빈 공간으로 옮겨 배치 -->
  <text x="760" y="210" text-anchor="middle" font-family="'Nanum Pen Script', 'Gaegu', cursive"
        font-size="34" fill="#3a3a3a">대사 한 마디 -</text>

  <!-- 하단 내레이션: 페이지 맨 아래 가운데, 상단보다 크게 -->
  <text x="540" y="1150" text-anchor="middle" dominant-baseline="middle"
        font-family="'Nanum Pen Script', 'Gaegu', cursive" font-size="52" fill="#3a3a3a">하단 내레이션…</text>

  <!-- 보조 내레이션: 괄호 혼잣말, 오른쪽 치우침 -->
  <text x="840" y="1230" text-anchor="middle" dominant-baseline="middle"
        font-family="'Nanum Pen Script', 'Gaegu', cursive" font-size="34" fill="#3a3a3a">(보조 내레이션…)</text>
</svg>
```

## 예시

입력 예시:

```text
처음으로 홈베이킹에 도전한 날 이야기를 웹툰으로 만들어줘. 반죽은 엉망이 되고 첫 판은
태워 먹었는데, 두 번째 판은 그럴싸한 쿠키가 나왔어. 친구가 놀러 와서 같이 먹었어.
```

출력 개요 예시 (페이지 구성과 캐릭터 배정을 보여준다):

```text
페이지 1 — 2컷 페이지 (주인공)
  상단 내레이션: "첫 홈베이킹에 도전한 날…"
  컷 1: 작은 나무 탁자에서 끈적한 반죽과 씨름하는 주인공, 머리털에 밀가루 (땀방울)
  컷 2: 연기가 새어 나오는 오븐 앞에서 놀라 뒤로 넘어지는 주인공 (놀람 표시)
  하단 내레이션: "첫 판은 숯이 되었다…"
  보조 내레이션: "(연기 감지기까지 울림…)"

페이지 2 — 대화 페이지 (주인공 + 상대 캐릭터)
  상단 내레이션: "그때 놀러 온 친구…"
  그림: 마주 본 두 캐릭터의 상반신과 말풍선
  상대 대사: "이 냄새 뭐야?"
  주인공 대사: "묻지 마…"

페이지 3 — 1컷 페이지 (주인공)
  상단 내레이션: "그런데 두 번째 판은…"
  그림: 그럴싸한 쿠키가 담긴 접시를 두 손으로 들고 눈을 반짝이며 감격한 주인공
  대사: "이게 되네…?"
```

각 페이지를 이미지 프롬프트 템플릿에 넣어 페이지별 프롬프트를 만들고, 페이지마다 SVG 파일을 저장한다.

## 완료 전 확인

- 사용자가 준 이미지·글을 근거로 이야기를 구성했는가? 글이 없어서 지어냈다면 그 사실을 밝혔는가?
- 화자는 주인공 캐릭터, 2인 대화는 상대 캐릭터, 셋 이상 무리는 얼굴 없는 군중 캐릭터로 배정했는가?
- 캐릭터 정의 문장을 모든 프롬프트에서 글자 그대로 재사용했는가?
- 캔버스가 1080×1350 세로형인가? 좌표를 억지로 고정하지 않고 내용에 맞춰 배치했는가?
- 그림에 넣을 한글 텍스트를 프롬프트에 한 줄씩 정확히 나열했고, DO NOT에 텍스트 변형·추가 금지를 넣었는가?
- SVG가 같은 텍스트를 담고, 모든 텍스트가 `'Nanum Pen Script', 'Gaegu', cursive`를 쓰는가? 폰트 설치 안내를 덧붙였는가?
- 컷당 감정이 하나이고, 대사가 15자 이내인가?
- SVG 파일을 저장하고 경로를 알려줬는가?
