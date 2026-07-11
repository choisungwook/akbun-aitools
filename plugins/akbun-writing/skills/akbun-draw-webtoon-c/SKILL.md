---
name: akbun-draw-webtoon-c
description: >
  사용자가 남긴 글·이미지로 가로형 1컷 에세이툰 페이지를 만든다. 스타일은 고정이다 — 따뜻한
  오프화이트 배경, 페이지 상단의 굵은 손글씨 한글 내레이션, 그 아래 테두리 없는 한 장면.
  주인공은 플랫 채색된 akbun 고래 마스코트, 배경 인물은 채색 없는 선화 실루엣, 속마음은 부드러운
  회색 말풍선에 담는다. 결과물은 페이지별 영어 이미지 생성 프롬프트와 Figma/Canva에서 편집할 수
  있는 한글 텍스트 SVG다.
  Trigger on: "에세이툰", "가로형 웹툰", "1컷 웹툰", "내레이션 웹툰", "감성 회사툰",
  "essay-toon", "one-cut webtoon", or any request to turn a story/feeling into
  narration-driven single-scene webtoon pages.
---

# 가로형 1컷 에세이툰 페이지 만들기 (이미지 프롬프트 + SVG)

## 이 skill이 하는 일

사용자가 남긴 글(이야기, 상황, 감정)과 이미지를 분석해서 **가로형 1컷 에세이툰 페이지**를 만든다. 내레이션 문장이 이야기를 끌고 가고, 그림은 그 문장의 감정을 한 장면으로 보여주는 형식이다. 결과물은 두 가지다.

1. **페이지별 영어 이미지 생성 프롬프트** — GPT image, nano-banana 같은 이미지 생성 모델(agent)에 그대로 붙여넣는다. 내레이션·속마음 같은 한글 텍스트도 그림에 포함하도록 지시한다.
2. **페이지별 SVG 파일** — 같은 한글 텍스트를 편집 가능한 `text`로 담은 SVG. Figma/Canva로 가져와 문구를 다듬거나, 그림 속 글자가 틀렸을 때 그림 위에 얹는 텍스트 레이어로 쓴다.

사용자가 글을 주지 않으면 첨부 이미지와 대화 맥락을 분석해 내레이션 초안(한국어)을 먼저 만들고, 지어낸 이야기임을 밝힌 뒤 진행한다.

다른 웹툰 skill과의 구분: `akbun-draw-webtoon-a`는 가로로 나란한 3~4컷 흑백 스틱피겨 컷만화, `akbun-draw-webtoon-b`는 세로형(4:5) 파스텔 수채 치비 페이지다. 이 skill은 **가로형(16:10) 1컷 + 상단 내레이션 + 플랫 채색**이 고정이다.

## 캐릭터 (고정)

사람을 그리지 않는다. 아래 캐릭터 정의의 영어 문장을 해당 캐릭터가 나오는 모든 프롬프트에 **글자 그대로** 복사한다. 이미지 모델은 페이지 간 기억이 없어서, 문장이 다르면 캐릭터가 달라진다.

### 주인공 캐릭터

이야기의 화자("나")는 **akbun 마스코트 고래**다. 기본 외형(콩 모양 통통한 몸, 흰 배, 밝은 회색 등, 작은 옆지느러미 2개, 납작한 꼬리, 까만 점 눈, 작은 곡선 입)은 `akbun-mascot-whale` skill의 캐릭터 스펙을 따르고, 이 skill에서는 따뜻한 톤의 플랫 채색으로 렌더링한다 — 크림빛 배, 웜그레이 등, 가늘고 깔끔한 진갈색 외곽선, 연한 볼 패치. 형태·비율·점 눈·곡선 입은 바꾸지 않는다.

주인공의 영어 CHARACTER 문장:

```text
the akbun whale mascot: a chubby bean-shaped whale with a warm light-gray back and
cream-white belly, two tiny side fins, a small flat tail, two black dot eyes, a small
curved mouth, soft warm cheek patches, drawn with thin clean dark-brown outlines and
flat warm coloring, no shading, no texture
```

### 배경 인물 (채색 없는 선화)

주인공이 아닌 인물(동료, 지나가는 무리, 대화 상대의 뒷모습 등)은 개성을 주지 않고 **채색 없는 선화 실루엣**으로 그린다. 배경 인물도 사람이 아니라 둥근 동물 실루엣이다. 외곽선만 있고 속은 배경색 그대로 비워 두어, 채색된 주인공이 한눈에 구분되게 한다.

배경 인물의 영어 문장:

```text
background figures drawn as simple uncolored line-art animal silhouettes: rounded
bodies and heads in thin dark-brown outlines only, no fill color, no facial features
```

## 비주얼 스타일 (모든 프롬프트에 고정)

모든 이미지 프롬프트는 아래 스타일을 그대로 묘사한다. 담담한 내레이션과 귀여운 그림의 대비로 감정을 전달하는 한국 에세이툰 스타일이다.

- **캔버스**: 가로형 16:10 (1200×750 기준). 컷 테두리·괘선 없음. 페이지 전체가 하나의 장면이다.
- **배경**: 따뜻한 오프화이트(`#F7F4EE`) 단색. 벽·바닥·풍경을 그리지 않고, 장면에 꼭 필요한 소품만 남긴다.
- **선**: 가늘고 깔끔한 진갈색(웜 블랙) 외곽선. 흔들림 없이 부드러운 곡선 위주.
- **채색**: 플랫 단색 채우기. 그라데이션·질감·그림자 없음. 주인공과 소품만 칠하고 배경 인물은 칠하지 않는다.
- **팔레트**: 크림, 웜그레이, 연갈색에 웜 오렌지 포인트 하나. 한 페이지에 3~4색이면 충분하다.
- **소품**: 노트북, 책상, 의자, 서류처럼 장면을 설명하는 것만 1~3개, 차분한 회색 계열로 그린다.
- **속마음 말풍선**: 꼬리 없는 부드러운 회색 타원 덩어리(`#DEDAD3`) 안에 짧은 한글 손글씨. 페이지당 최대 1개.
- **소리·웅성거림**: 배경 인물 근처에 작게 띄우는 한글 손글씨(효과음, 수군거림, 지나가는 말). 말풍선 없이 글자만 띄운다.
- **감정 연출**: 점 눈과 입 모양, 자세, 땀방울·움직임 곡선 같은 만화 기호를 아껴 쓴다. 과장된 액션 없음.
- **분위기**: 담담하고 잔잔한 에세이 무드. 내레이션은 차분한데 그림 속 주인공의 속마음이 새어 나오는 대비가 핵심이다.

## 페이지 레이아웃 규칙

요소 위치를 고정 좌표로 정하지 않는다. 내레이션 길이와 장면 구성에 맞춰 자연스럽게 배치하되 아래 원칙을 지킨다.

- **상단 내레이션**: 페이지 맨 위 왼쪽 정렬, 1~2줄. 페이지에서 가장 크고 굵은 텍스트다. 내레이션이 페이지의 주인공이고 그림은 그 아래를 받친다.
- **그림 영역**: 내레이션 아래 남은 공간의 가운데(또는 살짝 오른쪽)에 장면 하나를 둔다. 그림 크기는 캔버스 높이의 절반 정도로 억제해 여백을 넉넉히 남긴다.
- **속마음 말풍선**: 주인공 머리 옆 빈 공간에 둔다. 내레이션과 겹치지 않게 한다.
- **여백**: 사방에 넉넉한 오프화이트 여백. 그림·글씨가 캔버스 가장자리에 붙지 않게 한다.
- **시선 흐름**: 내레이션(위) → 장면(아래) → 속마음(장면 옆) 순서로 읽히게 배치한다.

## 내레이션 문체 규칙

- 한 페이지에 내레이션 1~2문장. 길면 페이지를 나눈다.
- 문체는 담담한 서술체로 통일한다 — "~합니다/~있습니다"의 차분한 존댓말, 또는 "~함/~모름" 같은 짧은 개조식. 한 작품 안에서는 하나만 쓴다.
- 내레이션은 상황·사실을 말하고, 감정은 그림과 속마음 말풍선이 맡는다. 내레이션에 감탄사·이모티콘을 넣지 않는다.
- 속마음은 10자 안팎의 혼잣말로, 내레이션과 온도차가 나게 쓴다.

## 폰트 규칙

SVG의 모든 텍스트는 저작권 걱정 없는 무료 폰트만 쓴다.

- 내레이션(굵은 손글씨): **Jua** (주아, SIL OFL)
- 속마음·웅성거림(가는 손글씨): **Gaegu** (개구, SIL OFL)

두 폰트 모두 Google Fonts에서 무료로 내려받을 수 있다. Figma/Canva에서 텍스트가 올바르게 보이려면 사용자가 폰트를 설치해야 하므로, SVG를 건넬 때 이 안내를 한 줄 덧붙인다. `font-family`는 내레이션 `'Jua', 'Gaegu', cursive`, 그 외 텍스트 `'Gaegu', 'Jua', cursive`로 지정한다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **한국어 페이지 시나리오** — 페이지별 내레이션·장면·속마음. 사용자가 글을 안 줬으면 여기서 만든 이야기를 먼저 보여준다.
2. **페이지별 영어 이미지 생성 프롬프트** — 페이지마다 하나씩, 각각 코드 펜스 블록(```text)으로.
3. **페이지별 SVG 파일** — 작업 디렉터리에 `essaytoon-page-1.svg`처럼 저장하고 경로를 알려준다.

## 작업 순서

1. **입력 파악.** 사용자가 남긴 글과 이미지를 읽는다. 이미지가 있으면 상황·감정을 분석한다.
2. **이야기 확보.** 글이 있으면 그대로 쓴다. 없으면 맥락을 근거로 내레이션 초안을 한국어로 만들고, 지어낸 이야기임을 밝힌다.
3. **페이지 나누기.** 내레이션을 페이지당 1~2문장으로 자른다. 감정이 바뀌는 지점이 페이지 경계다.
4. **장면 구성.** 페이지마다 내레이션을 받치는 장면 하나를 정한다 — 주인공의 자세·표정·소품, 필요하면 배경 인물과 속마음 말풍선.
5. **페이지별 프롬프트 작성.** 아래 `이미지 프롬프트 템플릿`을 채운다. 그림에 넣을 한글 텍스트를 한 줄씩 정확히 나열한다.
6. **SVG 작성.** 아래 `SVG 템플릿`을 바탕으로 같은 텍스트를 같은 배치로 담아 저장한다. 좌표는 페이지 구성에 맞춰 조정한다.
7. **출력.** 페이지 시나리오 + 프롬프트 블록들 + SVG 파일 경로(폰트 설치 안내 포함)를 출력한다.

## 페이지 구성 원칙

- **한 페이지 = 한 문장 = 한 감정.** 내레이션 하나에 장면 하나만 담는다.
- **내레이션이 말하고, 그림이 느낀다.** 상황 설명은 내레이션에, 감정은 표정·자세·속마음에 둔다. 같은 내용을 둘 다에 쓰지 않는다.
- **주인공 중심.** 채색된 캐릭터는 주인공 하나가 기본이다. 다른 인물이 필요하면 채색 없는 선화 실루엣으로만 그린다.
- **속마음은 아껴 쓴다.** 모든 페이지에 넣지 않는다. 내레이션과 온도차가 필요한 페이지에만 1개.
- **마지막 페이지는 여운.** 가장 조용한 장면(뒷모습, 멈춘 자세, 빈 책상)으로 끝낸다.

## 이미지 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 페이지마다 채운다. 캐릭터 문장은 `캐릭터 (고정)` 섹션에서 글자 그대로 복사하고, 나오지 않는 캐릭터 줄과 쓰지 않는 텍스트 줄은 지운다.

```text
A wide 16:10 (1200x750) single-scene Korean essay-webtoon page. Flat minimal digital
illustration on a solid warm off-white background (#F7F4EE). Thin clean dark-brown
outlines, flat warm coloring only — cream, warm gray, light brown with one warm orange
accent. No gradients, no shading, no texture, no panel borders, no background walls or
scenery.

LAYOUT: bold handwritten Korean narration text at the top left of the page, one or two
lines, the largest text on the page. Below it, one borderless scene centered in the
remaining space, occupying about half of the canvas height, with generous empty
off-white margins on all sides.

MAIN CHARACTER: <paste the fixed whale sentence verbatim>.
BACKGROUND FIGURES: <paste the fixed silhouette sentence verbatim, only when extras appear>.

SCENE: <who does what, posture and emotion, plus the one to three gray-toned props that
matter, e.g. "the whale mascot slumps over a small gray desk, fins resting on a laptop
keyboard, eyes drooping, one small sweat drop near its cheek">.

TEXT IN IMAGE (handwritten Korean, render each line exactly as written):
- top narration, top left, bold and large: "<...>"
- inner-thought bubble near the main character, a soft gray rounded blob without a
  tail, smaller handwriting: "<...>"
- small floating murmur text near the background figures: "<...>"

STYLE: calm slice-of-life essay mood, emotion shown through posture and tiny comic
marks (a sweat drop, small motion curves) used sparingly.

DO NOT: no human characters, no photorealism, no gradients or shadows, no panel
borders, no saturated colors, no background scenery, no watermarks. Do not color the
background figures. Do not misspell, translate, or rearrange the Korean text, and do
not add any text beyond the lines listed above.
```

## SVG 템플릿

1페이지용 뼈대다. 캔버스는 항상 1200×750이고, 아래 좌표는 배치 예시다 — 내레이션 길이와 장면 구성에 맞춰 조정한다. 쓰지 않는 텍스트 요소는 지운다. 생성된 그림 파일이 이미 있으면 자리표시 `<rect>`/`<text>`를 `<image x="..." y="..." width="..." height="..." href="page-1.png"/>`로 교체한다.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="750" viewBox="0 0 1200 750">
  <!-- 배경: 따뜻한 오프화이트 -->
  <rect width="1200" height="750" fill="#F7F4EE"/>

  <!-- 상단 내레이션: 왼쪽 정렬, 페이지에서 가장 크고 굵게. 두 줄이면 tspan으로 나눈다 -->
  <text x="60" y="90" font-family="'Jua', 'Gaegu', cursive" font-size="52" fill="#2B2724">
    <tspan x="60" dy="0">내레이션 첫 줄…</tspan>
    <tspan x="60" dy="64">내레이션 둘째 줄…</tspan>
  </text>

  <!-- 그림 자리표시: 그림이 생기면 <image>로 교체 -->
  <rect x="380" y="280" width="440" height="380" fill="#EFEBE3"/>
  <text x="600" y="480" text-anchor="middle" font-family="'Gaegu', 'Jua', cursive"
        font-size="32" fill="#9A948A">장면 그림</text>

  <!-- 속마음 말풍선: 주인공 머리 옆 빈 공간. 꼬리 없는 회색 타원 -->
  <ellipse cx="960" cy="330" rx="150" ry="80" fill="#DEDAD3"/>
  <text x="960" y="330" text-anchor="middle" dominant-baseline="middle"
        font-family="'Gaegu', 'Jua', cursive" font-size="34" fill="#2B2724">속마음 한 마디…</text>

  <!-- 웅성거림: 배경 인물 근처에 작게. 없으면 지운다 -->
  <text x="300" y="620" text-anchor="middle" font-family="'Gaegu', 'Jua', cursive"
        font-size="28" fill="#2B2724">웅성웅성</text>
</svg>
```

## 예시

입력 예시:

```text
새벽에 서버 알림을 받고 혼자 장애를 수습한 날 이야기를 에세이툰으로 만들어줘.
알림 소리에 깨서 노트북을 열었고, 원인을 찾는 데 한참 걸렸고, 아침이 되어서야 끝났어.
```

출력 개요 예시 (페이지 구성을 보여준다):

```text
페이지 1
  내레이션: "새벽 세 시, 알림 소리에 눈이 떠졌습니다."
  장면: 이불 밖으로 몸을 반쯤 내민 주인공이 빛나는 휴대폰 화면을 바라봄 (놀란 점 눈)
  속마음: "설마…"

페이지 2
  내레이션: "원인을 찾는 시간은 언제나 생각보다 깁니다."
  장면: 어두운 책상에서 노트북을 들여다보는 주인공, 옆에 식은 컵 하나 (땀방울)

페이지 3
  내레이션: "끝났을 땐 이미 아침이었습니다."
  장면: 닫힌 노트북 옆에 엎드린 주인공의 뒷모습, 창밖 방향으로 작은 해 소품
  속마음: "…출근해야지."
```

각 페이지를 이미지 프롬프트 템플릿에 넣어 페이지별 프롬프트를 만들고, 페이지마다 SVG 파일을 저장한다.

## 완료 전 확인

- 사용자가 준 글·이미지를 근거로 이야기를 구성했는가? 글이 없어서 지어냈다면 그 사실을 밝혔는가?
- 페이지마다 내레이션이 1~2문장이고, 문체(존댓말 서술체 또는 개조식)가 작품 전체에서 하나로 통일됐는가?
- 주인공은 akbun 고래 마스코트 문장을, 배경 인물은 선화 실루엣 문장을 글자 그대로 복사했는가?
- 캔버스가 1200×750 가로형이고, 컷 테두리 없이 상단 내레이션 + 단일 장면 구성인가?
- 플랫 채색·오프화이트 배경·배경 인물 무채색을 프롬프트에 명시했고, DO NOT에 그라데이션·배경 풍경·텍스트 변형 금지를 넣었는가?
- 속마음 말풍선이 페이지당 최대 1개이고, 내레이션과 온도차가 있는가?
- SVG가 같은 한글 텍스트를 담고, 내레이션은 Jua, 그 외는 Gaegu를 쓰는가? 폰트 설치 안내를 덧붙였는가?
- SVG 파일을 저장하고 경로를 알려줬는가?
