---
name: akbun-draw-whale-infographic
description: >
  주제나 글, 자료를 받아 흑백 손그림 고래 캐릭터가 안내하는 한 장짜리 치트시트 인포그래픽
  (4단 밴드 포스터) 스타일의 이미지 생성 프롬프트와 Figma/Canva에서 편집 가능한 SVG를 함께 만든다.
  사용자가 인포그래픽, 치트시트, 요약 포스터, 개념 정리 한 장, 고래 캐릭터를 언급하면 이 skill을 사용한다.
---

# 고래 치트시트 인포그래픽 프롬프트 + SVG 생성

## 이 skill이 하는 일

하나의 주제(개념, 프로세스, 기술, 습관 등)를 **한 장짜리 흑백 손그림 치트시트 인포그래픽**으로 바꾼다.
둥근 모서리의 검은 외곽 프레임 안이 4개의 가로 밴드로 나뉘고, 각 밴드에 제목·단계·구성 요소·비교가
배치된다. 통통한 고래 마스코트가 곳곳에서 생각하고, 가리키고, 일하며 내용을 안내한다. 화이트보드
만화 같은 따뜻한 손그림 스타일이다.

결과물은 두 가지 형태로 같은 인포그래픽을 만든다.

1. **이미지 생성 프롬프트** — GPT image, nano-banana 같은 이미지 생성 모델(AI agent)에 그대로 붙여넣는 영어 프롬프트.
2. **SVG 파일** — Figma나 Canva로 불러와 직접 수정할 수 있는 벡터 파일. 텍스트가 `<text>` 요소로 남아 있어 편집 가능하다.

`akbun-draw-sketchbook-card`(연필 개념 카드), `akbun-draw-minimal-poster`(미니멀 포스터)와 짝이 되는
"밀도 높은 한 장 정리" 버전이다. 개념 요약, 프로세스 설명, 발표 자료 표지, 블로그 대표 이미지에 어울린다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 코드 블록 하나.
2. **SVG 파일** — 작업 디렉터리에 `<slug>.svg`로 저장하고 경로를 알려준다.
3. **한국어 한 줄 설명** — 어떤 제목·단계·구성으로 채웠는지 1~2문장.

## 입력 다루기

사용자가 준 것에 따라 부족한 부분만 skill이 채운다.

- **글(문구·카피)까지 준 경우**: 준 문구를 그대로 해당 칸에 넣는다. 다듬거나 번역하지 않는다.
- **주제·자료만 준 경우**: 자료를 분석해 아래 카피 슬롯 전부를 skill이 직접 쓰고, 이미지 작업 전에
  작성한 카피를 사용자에게 함께 보여준다. 카피 확인을 기다리지 않고 바로 이미지 작업을 진행한다.
- 일부만 준 경우 빈 슬롯만 채운다.

채워야 하는 카피 슬롯은 다음과 같다.

- 제목(2~4단어) + 부제(2~3줄의 짧은 문장)
- 4단 스택 항목(단계·레벨 목록, 맨 위가 강조 대상)
- 5개 스텝 이름(프로세스 순서)
- 6개 구성 요소 이름
- 우측 비교 패널: 패널 제목 + 나쁜 쪽/좋은 쪽 라벨
- 하단 좌: 실전 사례 3개 (이름 + 짧은 부연)
- 하단 중: 조심할 것 4개 (제목 + 항목 4줄)
- 하단 우: 대비 패널 제목 + A/B 라벨

내용이 슬롯 수와 안 맞으면 칸 수를 한두 개 줄이는 것은 허용하지만(예: 스텝 4개), 밴드 4개 구조와
간격 비율은 절대 바꾸지 않는다.

## 캐릭터 규칙 (고정)

마스코트는 **통통한 고래**다. 다른 동물로 바꾸지 않는다.

- 몸: 콩 모양의 둥근 몸통, 흰 배, 등은 밝은 회색. 작은 옆지느러미 2개, 납작한 꼬리지느러미.
- 얼굴: 까만 점 눈 2개, 작은 곡선 입. 뺨에 연회색 동그라미 패치를 넣어도 된다.
- 표정·포즈로 역할을 표현한다: 생각(지느러미를 턱에), 신남(물줄기 분수), 진지(안경), 지침(땀방울),
  작업(노트북·돋보기·렌치 같은 소품).
- 마스코트는 최소 6곳 이상 등장한다. 헤더에 2마리(생각하는 고래 + 사다리 고래), 스텝마다,
  구성 요소마다, 비교 패널마다 작게 등장한다.

## 스타일이 정체성이다

이 skill이 지키는 것은 **스타일**이지 특정 주제가 아니다. 어떤 입력이 와도 아래 두 가지는 항상 같다.

1. **레이아웃**: 둥근 검은 외곽 프레임, 4개의 가로 밴드와 그 경계선, 리본형 섹션 제목, 밴드 안의
   칸 나누기(세로 실선·점선)와 상하좌우 간격.
2. **그림 언어**: 두껍고 둥근 검은 외곽선의 손그림, 흰 바탕 + 회색 2~3단계만 쓰는 흑백,
   카와이 고래 마스코트, 원문자 번호, 반짝이·움직임 선.

반대로 **각 칸에 무엇이 들어가는지(주제, 문구, 소품)는 입력에 맞게 자유**다. 주제를 스타일에 끼워
맞추지 말고, 스타일로 주제를 그린다.

## 레이아웃 스펙 (고정)

프롬프트와 SVG 모두 아래 수치를 그대로 따른다. 좌표는 거의 정사각형인 1200×1160 기준이다.

- **비율**: 가로 1200 × 세로 1160 (SVG viewBox `0 0 1200 1160`). 흰 바탕.
- **외곽 프레임**: 가장자리에서 10 안쪽, 모서리 반지름 24, 굵기 7의 검은 둥근 사각형.
- **밴드 경계선**: y=385, y=660, y=920에 프레임 좌우를 잇는 굵기 5의 가로 실선 3개.
- **밴드 1 (헤더, y 10~385, 높이의 약 32%)**
  - 좌측(x 45~430): 제목 2줄(손글씨 대형, 첫 줄 베이스라인 y≈100, 둘째 줄 y≈165), 그 아래 짧은
    밑줄(y≈195), 부제 2~3줄(y≈240부터 줄 간격 35).
  - 중앙(x 250~520): 생각하는 고래(y 260~385)와 그 위 구름 모양 생각 풍선(y 80~270). 풍선 안에는
    주제를 상징하는 아이콘 하나. 풍선 꼬리는 작은 원 2~3개.
  - 우측(x 585~1100): 세로로 쌓인 둥근 사각형 4개 스택(각 높이≈62, 간격≈14, y≈60부터). 각 칸 왼쪽에
    원문자 번호(위에서부터 ④③②①), 맨 위 칸만 진회색 배경 + 흰 글자로 강조. 스택 오른쪽에 사다리를
    오르며 맨 위 칸을 가리키는 고래와 반짝이 2~3개.
- **밴드 2 (5 스텝, y 385~660, 높이의 약 24%)**
  - 리본형 제목 상자: 가로 중앙, y≈398~432.
  - 5개 등폭 칸(각 폭 236): x=246, 482, 718, 954에 y 440~660 세로 실선 4개.
  - 각 칸: 상단에 원문자 번호 + 스텝 이름(y≈470), 아래에 그 스텝을 수행하는 고래 일러스트(y 500~640).
  - 칸 사이 경계선 중앙(y≈560)에 작은 화살표 →.
- **밴드 3 (구성 요소 + 비교, y 660~920, 높이의 약 22%)**
  - 좌측 영역(x 10~860): 리본형 제목(영역 가로 중앙, y≈672~704). 6개 등폭 칸(각 폭≈141),
    칸 사이는 y 720~910의 세로 **점선** 5개. 각 칸: 요소를 든 고래 아이콘(y 740~850) + 요소 이름
    캡션(y≈880, 필요하면 2줄).
  - 우측 인셋 패널(x 870~1180, y 672~910): 굵기 5의 독립된 사각 프레임. 상단에 테두리 있는 제목 상자,
    내부는 세로선으로 2분할. 왼쪽 칸은 나쁜 예(라벨 + 고래 + 하단 ✗), 오른쪽 칸은 좋은 예(라벨 + 고래 + 하단 ✓).
- **밴드 4 (하단 3분할, y 920~1150, 높이의 약 21%)**
  - 세로 실선 2개: x=490, x=745 (y 920~1150).
  - 좌측 섹션(x 10~490): 리본형 제목(y≈932~962). 3개 사례 칸(점선 구분), 각 칸에 사례 이름
    1~2줄(y≈985) + 일하는 고래 일러스트(y 1010~1140).
  - 중앙 섹션(x 490~745): 리본형 제목. 아이콘 + 짧은 문구 4행(y≈1000, 1045, 1090, 1135).
  - 우측 섹션(x 745~1190): 리본형 제목. 점선으로 2분할, 각 칸에 A/B 라벨(y≈985) + 대비되는 고래
    일러스트(좋은 쪽은 트로피·반짝이, 나쁜 쪽은 엉킨 선·쌓인 상자 등).
- **여백**: 어떤 요소도 외곽 프레임이나 밴드 경계선에 닿지 않는다. 텍스트와 그림은 경계에서 최소 12 띄운다.

## 비주얼 스타일 (고정)

- **선**: 모든 형태에 두껍고 둥근(끝이 둥근) 검은 외곽선(`#1A1A1A`, 굵기 3~5). 자를 대지 않은 손그림 느낌.
- **색**: 흰색 `#FFFFFF` 바탕에 회색 3단계만 쓴다 — 연회색 `#F0F0F0`(칸 배경·뺨), 중간 회색
  `#D9D9D9`(고래 등·소품), 진회색 `#2B2B2B`(강조 칸 배경·아이콘). 그 외 색을 넣지 않는다.
- **리본형 제목**: 좌우 끝이 지그재그로 찢긴 라벨 테이프 모양의 가로 상자. 안에 대문자 손글씨 제목.
- **원문자 번호**: ①②③ 스타일. 원 안에 숫자.
- **장식**: 반짝이(✦), 짧은 움직임 선, 땀방울, 물줄기 분수를 아껴 쓴다. 배경 패턴·그라디언트·질감은 넣지 않는다.

## 폰트 규칙 (저작권 무료)

모두 SIL Open Font License 폰트만 쓴다. 상업적 사용에 제약이 없다.

- **제목·리본 제목(영문)**: `Patrick Hand` (대체: `Comic Neue`). 둥근 손글씨체.
- **본문·캡션(영문)**: `Patrick Hand`.
- **한글이 들어가면**: `Gaegu` (대체: `Nanum Pen Script`).
- SVG에는 `font-family="Patrick Hand, 'Comic Neue', 'Gaegu', cursive"`처럼 대체 폰트까지 함께 선언한다.

## 텍스트 언어 규칙

- **프롬프트는 영어**로 쓴다. 그림에 들어갈 텍스트는 `reading exactly: "..."` 형태로 철자까지 지정한다.
- 그림 속 텍스트 언어는 사용자가 준 언어를 따른다. 사용자가 한국어 자료만 줬고 별도 요청이 없으면
  그림 속 텍스트는 짧은 영어로 쓴다(이미지 모델의 한글 오타를 피한다). 한글을 원하면 SVG 쪽을 권한다.
- 칸 하나의 문구는 1~4단어로 짧게 유지한다. 문장은 부제와 하단 중앙 섹션에만 허용한다.

## 작업 순서

1. **입력 파악.** 자료를 읽고 카피 슬롯 중 비어 있는 것을 확인한다.
2. **카피 작성.** 빈 슬롯을 채운다. 스택은 아래→위로 갈수록 발전하는 순서, 스텝은 시간 순서로 배열한다.
3. **고래 포즈 설계.** 칸마다 내용에 맞는 포즈·소품을 하나씩 정한다. 같은 포즈를 연달아 쓰지 않는다.
4. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채우고, 쓰지 않는 줄은 지운다.
5. **SVG 작성.** 아래 `SVG 작성 규칙`을 따라 같은 인포그래픽을 그려 파일로 저장한다.
6. **출력.** 작성한 카피 요약 + 프롬프트 블록 + SVG 파일 경로 + 한국어 한 줄 설명을 출력한다.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다.

```text
A hand-drawn black-and-white cheatsheet infographic poster, nearly square (1200x1160),
white background, framed by a thick rounded black border. Cute kawaii whale mascots
(chubby body, white belly, light gray back, tiny fins, dot eyes, small smile) appear
throughout, guiding the content. Whiteboard-comic style: thick rounded black outlines,
grayscale only (white, light gray, mid gray, near-black), playful hand-lettered text,
circled numbers, small sparkles. No color.

The poster is divided into 4 horizontal bands by full-width black lines.

BAND 1 — HEADER (top 32%):
- Left: a large hand-lettered two-line title reading exactly: "<TITLE>", with a short
  underline, and below it a smaller subtitle reading exactly: "<SUBTITLE LINES>".
- Center: a whale thinking, fin on chin, with a cloud-shaped thought bubble above it
  containing <BUBBLE ICON, e.g. "a simple gear icon">.
- Right: a vertical stack of 4 rounded rectangles, numbered 4 to 1 from top to bottom
  with circled numbers, listing exactly: "<STACK ITEM 4>", "<STACK ITEM 3>",
  "<STACK ITEM 2>", "<STACK ITEM 1>". The TOP box is dark with white text. A happy
  whale climbs a ladder on the far right, pointing at the top box, with sparkles.

BAND 2 — 5 STEPS (next 24%):
- A ribbon-style label box centered at the top reading exactly: "<BAND 2 RIBBON TITLE>".
- Below, 5 equal columns separated by vertical lines, with small arrows between them.
  Each column has a circled number and a step name at the top, and a whale acting out
  the step below:
  1 "<STEP 1>" — <whale pose>; 2 "<STEP 2>" — <whale pose>; 3 "<STEP 3>" — <whale pose>;
  4 "<STEP 4>" — <whale pose>; 5 "<STEP 5>" — <whale pose>.

BAND 3 — PARTS + COMPARISON (next 22%):
- Left three quarters: a ribbon label reading exactly: "<BAND 3 RIBBON TITLE>", then
  6 columns separated by dashed vertical lines, each with a small whale holding or using
  the item and a caption below: "<PART 1>" ... "<PART 6>".
- Right quarter: an inset framed panel titled exactly: "<COMPARISON PANEL TITLE>",
  split into two columns: left labeled "<BAD LABEL>" with <bad whale pose> and a big X mark;
  right labeled "<GOOD LABEL>" with <good whale pose> and a big check mark.

BAND 4 — BOTTOM (last 21%), three sections separated by vertical lines:
- Left: ribbon label reading exactly: "<BAND 4 LEFT TITLE>", with 3 mini-columns, each a
  named example and a working whale: "<EXAMPLE 1>", "<EXAMPLE 2>", "<EXAMPLE 3>".
- Middle: ribbon label reading exactly: "<BAND 4 MIDDLE TITLE>", with 4 rows of a tiny
  icon plus a short phrase: "<COST 1>", "<COST 2>", "<COST 3>", "<COST 4>".
- Right: ribbon label reading exactly: "<BAND 4 RIGHT TITLE>", split in two: left
  "<A LABEL>" with a whale succeeding (trophy, sparkles); right "<B LABEL>" with a whale
  struggling (<struggle prop, e.g. "toppling boxes">).

STYLE: warm, playful, dense but organized, uniform thick rounded outlines, very legible
hand lettering, generous even margins — nothing touches the border or the band lines.

DO NOT: use any color, add gradients or textures, change the whale into another animal,
misspell any text, or let elements overlap the frame and band lines.
```

## SVG 작성 규칙

SVG는 skill이 직접 그린다. 형태 배치와 수치는 `assets/example-infographic.svg`를 열어 기준으로 삼는다.

- `viewBox="0 0 1200 1160"`, 외부 이미지·스크립트 없는 순수 SVG 1.1로 작성한다. Figma와 Canva가 그대로 불러온다.
- 레이어 순서: 흰 배경 → 밴드 경계선·칸 구분선 → 칸 배경(연회색) → 고래·소품 일러스트 → 리본·상자 →
  텍스트 `<text>` → 외곽 프레임.
- 모든 텍스트는 `<text>`로 남긴다. Figma에서는 그대로 편집되고, 폰트가 없으면 대체 폰트로 표시되므로
  사용자에게 Google Fonts에서 Patrick Hand(한글이면 Gaegu)를 설치하라고 안내한다.
- Canva는 SVG의 `<text>`를 지원하지 않는 경우가 있다. 사용자가 Canva용이라고 하면 텍스트를 지우고
  도형만 있는 버전을 하나 더 저장한 뒤, 문구는 Canva에서 직접 얹으라고 안내한다.
- 고래 한 마리는 `ellipse`(몸) + `path`(꼬리·지느러미) + `circle`(눈) + `path`(입) 정도의 기본 도형
  5~8개로 그린다. 정밀함보다 실루엣과 표정이 읽히는 게 중요하다.
- 저장 후 가능하면 렌더링(headless 브라우저 스크린샷 등)으로 형태가 깨지지 않았는지 확인한다.

## 예시 (gold reference)

이 예시는 이 스타일을 적용한 완성 결과다. 새 작업의 품질 기준으로 삼는다.

입력 예:

```text
핸드드립 커피 내리는 법을 한 장 치트시트로 만들어줘.
```

skill이 한 판단: 문구가 없어서 카피 전부를 만들었다. 스택은 커피 추출 방식의 발전 단계
(인스턴트 → 드립머신 → 프렌치프레스 → 푸어오버), 스텝은 한 잔을 내리는 시간 순서, 구성 요소는
도구 6가지, 비교는 원두 신선도로 정했다.

출력 프롬프트:

```text
A hand-drawn black-and-white cheatsheet infographic poster, nearly square (1200x1160),
white background, framed by a thick rounded black border. Cute kawaii whale mascots
(chubby body, white belly, light gray back, tiny fins, dot eyes, small smile) appear
throughout, guiding the content. Whiteboard-comic style: thick rounded black outlines,
grayscale only (white, light gray, mid gray, near-black), playful hand-lettered text,
circled numbers, small sparkles. No color.

The poster is divided into 4 horizontal bands by full-width black lines.

BAND 1 — HEADER (top 32%):
- Left: a large hand-lettered two-line title reading exactly: "Pour Over Coffee", with a
  short underline, and below it a smaller subtitle reading exactly: "The slow brew.
  You don't rush it. The water does the work.".
- Center: a whale thinking, fin on chin, with a cloud-shaped thought bubble above it
  containing a steaming coffee cup icon.
- Right: a vertical stack of 4 rounded rectangles, numbered 4 to 1 from top to bottom
  with circled numbers, listing exactly: "Pour Over", "French Press", "Drip Machine",
  "Instant". The TOP box is dark with white text. A happy whale climbs a ladder on the
  far right, pointing at the top box, with sparkles.

BAND 2 — 5 STEPS (next 24%):
- A ribbon-style label box centered at the top reading exactly: "ONE CUP = 5 MOVES".
- Below, 5 equal columns separated by vertical lines, with small arrows between them.
  Each column has a circled number and a step name at the top, and a whale acting out
  the step below:
  1 "Grind" — a whale turning a hand grinder; 2 "Bloom" — a whale watching wet grounds
  puff up; 3 "Pour" — a whale pouring from a gooseneck kettle in circles; 4 "Drawdown" —
  a whale waiting as water drips through a filter; 5 "Taste" — a whale sipping happily
  with sparkles.

BAND 3 — PARTS + COMPARISON (next 22%):
- Left three quarters: a ribbon label reading exactly: "6 TOOLS THAT MAKE IT", then
  6 columns separated by dashed vertical lines, each with a small whale holding or using
  the item and a caption below: "Beans", "Grinder", "Kettle", "Filter", "Scale", "Timer".
- Right quarter: an inset framed panel titled exactly: "FRESH ≠ STALE", split into two
  columns: left labeled "Months old?" with a droopy whale next to a dusty bag and a big
  X mark; right labeled "Fresh roast!" with a delighted whale hugging a shiny bag and a
  big check mark.

BAND 4 — BOTTOM (last 21%), three sections separated by vertical lines:
- Left: ribbon label reading exactly: "BREWS IN PRACTICE", with 3 mini-columns, each a
  named example and a working whale: "Morning V60" (a whale brewing beside a sunrise),
  "Camp Brew" (a whale pouring over a tiny campfire), "Cafe >300 cups/day" (a whale
  barista behind a counter with a queue).
- Middle: ribbon label reading exactly: "4 SILENT MISTAKES", with 4 rows of a tiny icon
  plus a short phrase: "Water too hot", "Grind too fine", "Uneven pour", "Dirty filter".
- Right: ribbon label reading exactly: "SAME BEANS, DIFFERENT CUP", split in two: left
  "Barista A takes care" with a whale holding a trophy cup, sparkles; right "Barista B
  rushes" with a frazzled whale beside an overflowing dripper.

STYLE: warm, playful, dense but organized, uniform thick rounded outlines, very legible
hand lettering, generous even margins — nothing touches the border or the band lines.

DO NOT: use any color, add gradients or textures, change the whale into another animal,
misspell any text, or let elements overlap the frame and band lines.
```

출력 SVG: `assets/example-infographic.svg` — 같은 내용을 레이아웃 스펙 좌표 그대로 그린 파일이다.

한국어 한 줄 설명: 푸어오버 커피를 주제로 추출 방식 4단 스택, 한 잔 내리는 5 스텝, 도구 6가지,
원두 신선도 비교, 실전 사례·실수·결과 대비까지 고래 마스코트가 안내하는 치트시트로 정리했습니다.

## 완료 전 확인

- 사용자가 준 문구를 바꾸지 않고 그대로 넣었는가? (없을 때만 skill이 만들고, 만든 카피를 보여줬는가?)
- 그림 속 모든 텍스트를 `reading exactly: "..."`로 철자까지 지정했는가?
- 4개 밴드 구조와 레이아웃 수치(밴드 경계 y=385/660/920, 프레임, 칸 좌표)를 프롬프트와 SVG 양쪽에 지켰는가?
- 마스코트가 전부 고래인가? 6곳 이상 등장하고 포즈가 겹치지 않는가?
- 흰색 + 회색 3단계 흑백 규칙을 지켰는가? 색·그라디언트·질감이 없는가?
- 폰트가 전부 SIL OFL(Patrick Hand, Comic Neue, Gaegu 등)인가?
- SVG를 파일로 저장하고 경로를 알려줬는가? 텍스트가 `<text>` 요소로 편집 가능한가?
- 프롬프트를 그대로 복사해 이미지 생성 모델에 붙여넣을 수 있는 한 블록으로 출력했는가?
