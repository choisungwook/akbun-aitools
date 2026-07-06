---
name: akbun-draw-webtoon-b
description: >
  사용자가 준 이미지·글로 파스텔 수채 치비 스타일 웹툰 페이지를 만든다. 컷별 이미지 생성 프롬프트(글자 없는 그림)와
  Figma/Canva로 가져갈 수 있는 한글 텍스트 오버레이 SVG를 함께 만들고, 글이 없으면 내용을 분석해 이야기를 먼저 만든다.
---

# 파스텔 웹툰 페이지 만들기 (이미지 프롬프트 + SVG)

## 이 skill이 하는 일

사용자가 남긴 이미지와 글(이야기, 상황, 일기)을 분석해서 **파스텔 수채 치비 스타일 웹툰 페이지**를 만든다. 결과물은 두 가지다.

1. **컷별 영어 이미지 생성 프롬프트** — GPT image, nano-banana 같은 이미지 생성 모델(agent)에 그대로 붙여넣는다. 그림에는 **글자를 넣지 않는다**.
2. **페이지 레이아웃 SVG** — 내레이션·대사·연출 텍스트를 담은 SVG 파일. Figma나 Canva로 가져와 생성된 그림과 합치고 텍스트를 자유롭게 수정할 수 있다.

글자를 그림과 분리하는 이유: 이미지 생성 모델은 한글을 자주 틀리게 렌더링한다. 그림은 모델이 그리고, 한글 텍스트는 SVG 레이어가 담당하면 글자가 항상 정확하고 나중에 Figma/Canva에서 편집할 수 있다.

사용자가 글을 주지 않으면 skill이 먼저 첨부 이미지나 대화 맥락을 분석해 내레이션·대사 초안(한국어)을 만들고, 그 초안으로 컷 구성과 프롬프트 작업을 진행한다.

akbun-draw-webtoon-a(xkcd풍 흑백 스틱피겨)와 다른 skill이다. 이 skill은 파스텔 채색 치비 그림체와 SVG 텍스트 오버레이가 고정이다.

## 비주얼 스타일 (모든 프롬프트에 고정)

모든 이미지 프롬프트는 아래 스타일을 그대로 묘사한다. 한국 감성 일상툰에서 볼 수 있는 부드러운 파스텔 손그림 스타일이다.

- **배경**: 순백색. 장면에 꼭 필요한 소품·벽·바닥만 옅은 회색 선과 연한 파스텔로 최소한만 그린다.
- **선**: 따뜻한 진회색(먹색)의 가늘고 살짝 흔들리는 연필/잉크 손그림 외곽선.
- **채색**: 수채처럼 투명하고 부드러운 파스텔 톤. 면을 꽉 채우지 않고 흰 여백이 배어나온다.
- **팔레트**: 더스티 로즈 핑크, 크림 옐로, 뮤트 그레이블루, 연갈색. 한 컷에 3~4색이면 충분하다.
- **인물**: 치비(2~3등신) 캐릭터. 크고 반짝이는 눈, 발그레한 볼터치, 단순한 코·입. 머리카락에 흰 하이라이트 줄기를 넣는다.
- **감정 연출**: 놀람 느낌표, 땀방울, 움직임 곡선 같은 만화 기호를 아껴서 쓴다. 이 기호들은 그림에 포함해도 된다(글자가 아니므로).
- **분위기**: 잔잔하고 따뜻한 일상·감성 무드. 과장된 액션보다 표정과 몸짓 중심.
- **글자 금지**: 그림 안에 어떤 언어의 텍스트도 넣지 않는다. 제목·대사·효과음은 전부 SVG가 담당한다.

## 페이지 레이아웃 규칙 (고정)

페이지는 두 종류다. 여백과 위치 수치는 아래를 그대로 따른다.

### 2컷 페이지 — 캔버스 1200×900 (4:3 가로)

- **상단 내레이션**: 페이지 맨 위, 가운데 정렬. 세로 중심 y=52(높이의 약 6%), 글자 크기 44.
- **패널 영역**: y=100부터 y=700까지(높이의 약 11%~78%). 영역의 위와 아래에 전폭 가로 괘선(두께 2, 진회색)을 긋는다. 좌우는 캔버스 끝까지 쓰고 세로 테두리는 긋지 않는다.
- **컷 분할선**: 두 컷 사이 세로선 하나. 위끝 x=612, 아래끝 x=580처럼 살짝 기울여 손그림 느낌을 낸다.
- **컷 안쪽 여백**: 인물·소품이 괘선과 분할선에서 24px 이상 떨어지게 그린다.
- **하단 내레이션**: 패널 아래, 가운데 정렬. 세로 중심 y=775, 글자 크기 52. 페이지의 핵심 문장을 둔다.
- **보조 내레이션**: 하단 내레이션 아래 오른쪽으로 치우쳐 배치. 세로 중심 y=845, 글자 크기 34, 괄호로 감싼 혼잣말 톤.
- **컷 안 대사**: 말풍선 대신 인물 머리 근처 빈 공간에 손글씨 텍스트로 띄운다. 글자 크기 30~36.

### 1컷 페이지 — 캔버스 1080×1080 (정사각)

- **상단 내레이션**: 가운데 정렬, 세로 중심 y=110, 글자 크기 48.
- **그림 영역**: 캔버스 중앙, 폭·높이의 약 60%를 차지. 테두리·괘선 없이 흰 여백에 그대로 놓는다.
- **대사·효과음**: 인물 옆 빈 공간에 손글씨 텍스트. 효과음은 글자 크기 28로 작게.
- **하단 내레이션(옵션)**: 필요하면 y=990, 가운데 정렬, 글자 크기 44.

인물 머리를 보여주는 대화 컷은 1컷 페이지에서 테두리 없이 인물 상반신 + 손그림 말풍선(SVG의 타원+꼬리)으로 구성해도 된다.

## 폰트 규칙

SVG의 모든 텍스트는 저작권 걱정 없는 무료 폰트만 쓴다.

- 기본: **Nanum Pen Script** (나눔손글씨 펜, SIL OFL)
- 대체: **Gaegu** (개구, SIL OFL)

두 폰트 모두 Google Fonts에서 무료로 내려받을 수 있다. Figma/Canva에서 텍스트가 올바르게 보이려면 사용자가 폰트를 설치해야 하므로, SVG를 건넬 때 이 안내를 한 줄 덧붙인다. `font-family`는 항상 `'Nanum Pen Script', 'Gaegu', cursive`로 지정한다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **한국어 컷 시나리오** — 페이지·컷 구성, 각 컷의 내레이션/대사. 사용자가 글을 안 줬으면 여기서 만든 이야기를 먼저 보여준다.
2. **컷별 영어 이미지 생성 프롬프트** — 컷마다 하나씩, 각각 코드 펜스 블록(```text)으로.
3. **페이지별 SVG 파일** — 작업 디렉터리에 `webtoon-page-1.svg`처럼 저장하고 경로를 알려준다.

## 작업 순서

1. **입력 파악.** 사용자가 남긴 이미지와 글을 읽는다. 이미지가 있으면 인물·상황·감정을 분석한다.
2. **이야기 확보.** 글이 있으면 그대로 쓴다. 없으면 첨부 이미지와 맥락을 근거로 내레이션·대사 초안을 한국어로 만든다. 지어낸 이야기임을 밝히고 컷 시나리오에 포함한다.
3. **페이지·컷 구성.** 이야기를 페이지 단위로 나눈다. 나란히 이어지는 두 장면은 2컷 페이지, 감정을 크게 보여줄 장면은 1컷 페이지로 잡는다.
4. **캐릭터 고정.** 등장인물의 외모(머리 색·모양, 옷, 특징)를 한 번 정의하고, 모든 컷 프롬프트에 **똑같은 문장으로** 복사해 넣는다. 이미지 모델은 컷 간 기억이 없다.
5. **컷별 프롬프트 작성.** 아래 `이미지 프롬프트 템플릿`을 채운다. 글자 금지를 매 프롬프트에 명시한다.
6. **SVG 작성.** 아래 `SVG 템플릿`을 페이지 레이아웃 규칙의 수치대로 채워 저장한다. 생성된 그림 파일이 이미 있으면 `<image>`로 넣고, 없으면 연회색 자리표시 사각형에 컷 번호를 적는다.
7. **출력.** 컷 시나리오 + 프롬프트 블록들 + SVG 파일 경로(폰트 설치 안내 포함)를 출력한다.

## 컷 구성 원칙

- **한 컷 = 한 감정.** 컷 하나에 행동과 감정 하나만 담는다.
- **내레이션이 이야기를 끌고, 그림은 감정을 보여준다.** 상황 설명은 상단 내레이션, 여운·반전은 하단 내레이션에 둔다.
- **대사는 짧게.** 컷당 한두 마디, 15자 이내. 길어지면 내레이션으로 옮긴다.
- **2컷 페이지는 대비.** 왼쪽 컷과 오른쪽 컷이 시점 전환(두 인물, 전후 순간)으로 대비되게 구성한다.
- **인물 수 최소화.** 컷당 1~2명이 가장 잘 그려진다.

## 이미지 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 컷마다 채운다. `CHARACTER` 문장은 모든 컷에서 글자 그대로 재사용한다.

```text
A single webtoon panel illustration in a soft pastel Korean chibi style. Thin, slightly wobbly
warm dark-gray pencil ink outlines on a pure white background. Transparent watercolor-like pastel
coloring that leaves white space showing through — dusty rose pink, cream yellow, muted gray-blue,
light brown palette.

CHARACTER: <recurring character definition, e.g. "a chibi young woman with long wavy dusty-pink
hair with white highlight streaks, big sparkling brown eyes, blushing cheeks, wearing a cream
yellow off-shoulder sweater and jeans">. (Reuse this exact sentence in every panel.)

SCENE: <what happens in this panel: action, posture, emotion, and the one or two props that
matter, e.g. "she crouches down holding out a small treat to a tiny gray kitten, leaning in with
a nervous but delighted smile, small sweat drop near her cheek">.

COMPOSITION: <full body | upper body | bust shot>, the subject centered with generous white
margins on all sides, minimal background — only <the one prop/surface that matters, in pale
gray lines and light pastel>.

STYLE: gentle slice-of-life mood, comic emotion marks allowed (surprise marks, sweat drops,
motion curves) but used sparingly. <4:5 vertical | 1:1 square> aspect ratio.

DO NOT: no text, no letters, no speech bubbles, no panel borders, no photorealism, no heavy
shading, no saturated colors, no gray or colored background fills, no watermarks.
```

## SVG 템플릿

2컷 페이지용 템플릿이다. 페이지 레이아웃 규칙의 수치를 그대로 쓰고, 텍스트만 컷 시나리오 내용으로 바꾼다. 1컷 페이지는 캔버스를 1080×1080으로 바꾸고 괘선·분할선을 지운다. 생성된 그림이 있으면 자리표시 `<rect>`/`<text>`를 `<image x="..." y="..." width="..." height="..." href="panel-1.png"/>`로 교체한다.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">
  <!-- 배경 -->
  <rect width="1200" height="900" fill="#ffffff"/>

  <!-- 상단 내레이션 -->
  <text x="600" y="52" text-anchor="middle" dominant-baseline="middle"
        font-family="'Nanum Pen Script', 'Gaegu', cursive" font-size="44" fill="#3a3a3a">상단 내레이션…</text>

  <!-- 패널 괘선 (위/아래 전폭 가로선) -->
  <line x1="0" y1="100" x2="1200" y2="100" stroke="#3a3a3a" stroke-width="2"/>
  <line x1="0" y1="700" x2="1200" y2="700" stroke="#3a3a3a" stroke-width="2"/>

  <!-- 컷 분할선 (살짝 기울임) -->
  <line x1="612" y1="100" x2="580" y2="700" stroke="#3a3a3a" stroke-width="2"/>

  <!-- 컷 1 자리표시: 그림이 생기면 <image>로 교체 -->
  <rect x="24" y="124" width="540" height="552" fill="#f4f4f4"/>
  <text x="294" y="400" text-anchor="middle" font-family="'Nanum Pen Script', 'Gaegu', cursive"
        font-size="36" fill="#9a9a9a">컷 1 그림</text>

  <!-- 컷 2 자리표시 -->
  <rect x="636" y="124" width="540" height="552" fill="#f4f4f4"/>
  <text x="906" y="400" text-anchor="middle" font-family="'Nanum Pen Script', 'Gaegu', cursive"
        font-size="36" fill="#9a9a9a">컷 2 그림</text>

  <!-- 컷 안 대사 (인물 머리 근처 빈 공간에 배치) -->
  <text x="820" y="170" text-anchor="middle" font-family="'Nanum Pen Script', 'Gaegu', cursive"
        font-size="34" fill="#3a3a3a">대사 한 마디 -</text>

  <!-- 하단 내레이션 -->
  <text x="600" y="775" text-anchor="middle" dominant-baseline="middle"
        font-family="'Nanum Pen Script', 'Gaegu', cursive" font-size="52" fill="#3a3a3a">하단 내레이션…</text>

  <!-- 보조 내레이션 (오른쪽 치우침, 괄호 혼잣말) -->
  <text x="950" y="845" text-anchor="middle" dominant-baseline="middle"
        font-family="'Nanum Pen Script', 'Gaegu', cursive" font-size="34" fill="#3a3a3a">(보조 내레이션…)</text>
</svg>
```

## 예시

입력 예시:

```text
유기묘를 처음 입양한 날 이야기를 웹툰으로 만들어줘. 보호소에서 데려올 때는 서로 어색했는데,
집에 오자마자 고양이가 내 무릎에서 잠들었어.
```

출력 개요 예시 (페이지 구성과 텍스트 배치를 보여준다):

```text
페이지 1 — 2컷 페이지 (1200×900)
  상단 내레이션: "보호소에서 처음 만난 날…"
  컷 1: 이동장 안에서 몸을 웅크리고 경계하는 회색 아기 고양이 (놀람 표시)
  컷 2: 같은 순간, 어색하게 손을 내밀며 땀 흘리는 주인공
  하단 내레이션: "우리는 서로가 낯설었다…"
  보조 내레이션: "(눈도 안 마주쳐줌…)"

페이지 2 — 1컷 페이지 (1080×1080)
  상단 내레이션: "그런데 집에 도착한 지 십 분 만에…"
  그림: 주인공 무릎 위에서 동그랗게 말려 잠든 고양이, 주인공은 감동해서 굳어 있음
  대사: "움직일 수가 없어…"
```

각 컷을 이미지 프롬프트 템플릿에 넣어 컷별 프롬프트를 만들고, 페이지마다 SVG 파일을 저장한다.

## 완료 전 확인

- 사용자가 준 이미지·글을 근거로 이야기를 구성했는가? 글이 없어서 지어냈다면 그 사실을 밝혔는가?
- 이미지 프롬프트의 DO NOT에 텍스트·말풍선·패널 테두리 금지를 넣었는가?
- CHARACTER 문장을 모든 컷 프롬프트에서 글자 그대로 재사용했는가?
- SVG가 페이지 레이아웃 규칙의 캔버스 크기·좌표·글자 크기를 그대로 따르는가?
- SVG의 모든 텍스트가 `'Nanum Pen Script', 'Gaegu', cursive`를 쓰는가? 폰트 설치 안내를 덧붙였는가?
- 컷당 감정이 하나이고, 대사가 15자 이내인가?
- SVG 파일을 저장하고 경로를 알려줬는가?
