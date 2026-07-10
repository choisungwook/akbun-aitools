---
name: akbun-draw-whale-poster
description: >
  주제나 글, 자료를 받아 흑백 손그림 고래 캐릭터가 안내하는 치트시트 포스터 한 장을 그리는
  이미지 생성 프롬프트와 Figma/Canva에서 편집 가능한 SVG를 함께 만든다. 사용자가 포스터,
  치트시트, 인포그래픽, 개념 정리 한 장, 고래 캐릭터를 언급하면 이 skill을 사용한다.
---

# 고래 치트시트 포스터 프롬프트 + SVG 생성

## 이 skill이 하는 일

하나의 주제(개념, 프로세스, 기술, 습관 등)를 **흑백 손그림 치트시트 포스터 한 장**으로 그린다.
결과물은 언제나 **포스터 1장, 프롬프트 1개, SVG 1개**다. 통통한 고래 마스코트가 포스터 곳곳에서
생각하고, 가리키고, 일하며 내용을 안내한다. 화이트보드 만화 같은 따뜻한 손그림 스타일이다.

이 skill이 지키는 것은 **스타일**이지 특정 레이아웃 틀이 아니다. 정해진 칸 개수나 고정된 구역 배치를
강요하지 않는다. 주제가 무엇이든 아래 스타일 규칙(비율, 색, 선·형태, 타이포그래피, 여백, 캐릭터)을
적용해서, 그 주제에 자연스러운 구성으로 포스터를 짠다.

결과물은 두 가지 형태로 같은 포스터를 만든다.

1. **이미지 생성 프롬프트** — GPT image, nano-banana 같은 이미지 생성 모델(AI agent)에 그대로 붙여넣는 영어 프롬프트.
2. **SVG 파일** — Figma나 Canva로 불러와 직접 수정할 수 있는 벡터 파일. 텍스트가 `<text>` 요소로 남아 있어 편집 가능하다.

`akbun-draw-sketchbook-card`(연필 개념 카드), `akbun-draw-minimal-poster`(미니멀 포스터)와 짝이 되는
"밀도 있는 한 장 정리" 버전이다. 개념 요약, 프로세스 설명, 발표 자료 표지, 블로그 대표 이미지에 어울린다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 포스터 한 장을 통째로 묘사하는 코드 블록 하나. 구역별로 프롬프트를 쪼개지 않는다.
2. **SVG 파일** — 작업 디렉터리에 `<slug>.svg`로 저장하고 경로를 알려준다. 파일도 한 개다.
3. **한국어 한 줄 설명** — 어떤 제목·구성으로 채웠는지 1~2문장.

## 입력 다루기

사용자가 준 것에 따라 부족한 부분만 skill이 채운다.

- **글(문구·카피)까지 준 경우**: 준 문구를 그대로 넣는다. 다듬거나 번역하지 않는다.
- **주제·자료만 준 경우**: 자료를 분석해 포스터에 들어갈 문구 전부를 skill이 직접 쓰고, 이미지 작업 전에
  작성한 카피를 사용자에게 함께 보여준다. 카피 확인을 기다리지 않고 바로 이미지 작업을 진행한다.
- 일부만 준 경우 빈 곳만 채운다.

포스터에 필요한 문구는 보통 다음과 같다. 주제에 맞게 개수를 늘리거나 줄인다.

- 큰 제목(2~4단어) + 부제(짧은 한두 문장)
- 2~5개의 구역 각각의 리본 제목 + 그 안에 들어갈 짧은 항목/캡션
- (선택) 좋고 나쁨을 대비하는 비교 한 쌍

## 캐릭터 규칙 (고정)

기본 마스코트는 **통통한 고래**다. 캐릭터가 1마리인 자리는 항상 고래다.

- 몸: 콩 모양의 둥근 몸통, 흰 배, 등은 밝은 회색. 작은 옆지느러미 2개, 납작한 꼬리지느러미.
- 얼굴: 까만 점 눈 2개, 작은 곡선 입. 뺨에 연회색 동그라미 패치를 넣어도 된다.
- 표정·포즈로 역할을 표현한다: 생각(지느러미를 턱에), 신남(물줄기 분수), 진지(안경), 지침(땀방울),
  작업(노트북·돋보기·렌치 같은 소품).
- 마스코트는 포스터에 여러 번(최소 4곳 이상) 등장해 시선을 이끈다.

한 자리에 캐릭터가 **2마리** 함께 등장하면(손님-주인, 전달, 협업 등) 두 번째 캐릭터는 **토끼**다.

- 토끼: 둥근 흰 몸통, 긴 귀 2개(귀 안쪽은 연회색), 까만 점 눈, 작은 입. 고래보다 약간 작게 그린다.
- 고래와 토끼 외의 동물은 쓰지 않는다. 한 자리에 고래를 2마리 겹쳐 그리지 않는다 — 두 번째는 항상 토끼다.
- 서로 다른 자리에 각각 1마리씩 있으면 둘 다 고래로 그린다.

## 스타일 스펙 (고정)

프롬프트와 SVG 모두 아래를 그대로 따른다. 이 값들이 어떤 주제에도 적용되는 재사용 스타일이다.

### 캔버스와 프레임

- **비율**: 거의 정사각형, 가로 1200 × 세로 1160 (SVG viewBox `0 0 1200 1160`). 흰 바탕.
- **외곽 프레임**: 가장자리에서 10 안쪽, 모서리 반지름 24, 굵기 7의 검은 둥근 사각형. 모든 요소는 이 안에 담긴다.

### 레이아웃 원리 (틀이 아니라 원리)

정해진 밴드나 칸 수는 없다. 아래 원리로 주제에 맞게 구성을 짠다.

- **제목 구역을 크게.** 포스터 위쪽에 큰 손글씨 제목과 부제가 들어가는 넉넉한 구역을 둔다. 그 옆이나 아래에
  주제를 상징하는 고래 마스코트(소품을 든)를 크게 배치한다.
- **몇 개의 구역으로 나눈다.** 나머지 공간을 내용에 맞춰 2~5개 구역으로 나눈다. 구역 크기는 균일할 필요가 없다 —
  중요한 것은 크게, 부수적인 것은 작게. 구역을 나누는 선은 **자를 대지 않은 굵은 검은 손그림 선**(가로·세로·부분선)이다.
- **각 구역엔 리본 제목 하나.** 구역마다 좌우 끝이 찢긴 라벨 테이프 모양의 리본 제목을 얹고, 그 아래 항목을 배치한다.
- **여백은 균일하게.** 구역 사이 간격(거터)과 프레임 안쪽 여백을 고르게 준다. 어떤 요소도 프레임이나
  구역 경계선에 닿지 않는다(최소 12 띄운다). 빽빽해 보여도 숨 쉴 여백이 있어야 한다.
- 순서 있는 항목엔 원문자 번호(①②③)와 그 사이 작은 화살표(→)를 쓴다.

### 색 (고정)

- **팔레트**: 흰색 `#FFFFFF` 바탕에 회색 3단계만 쓴다 — 연회색 `#F0F0F0`(구역 배경·뺨), 중간 회색
  `#D9D9D9`(고래 등·소품), 진회색 `#2B2B2B`(강조 배경·아이콘). 외곽선은 `#1A1A1A`. 그 외 색을 넣지 않는다.
- 배경 패턴·그라디언트·질감은 넣지 않는다.

### 선·형태 (고정)

- 모든 형태에 두껍고 둥근(끝이 둥근) 검은 외곽선(`#1A1A1A`, 굵기 3~5). 자를 대지 않은 손그림 느낌.
- 단순한 기하 도형으로 그린다. 얼굴 디테일·그림자·질감을 억제한다.

### 소품은 크게 (고정)

- 도구·물건 같은 소품은 옆 캐릭터 키의 60~100% 크기로 그린다. 기본 도형 3~6개로 단순하게 만들되,
  실루엣만으로 무엇인지 읽혀야 한다. 자리가 좁으면 캐릭터를 줄이고 소품을 키운다.
  소품이 캐릭터보다 눈에 띄지 않으면 잘못 그린 것이다.

### 장식

- 반짝이(✦), 짧은 움직임 선, 땀방울, 물줄기 분수를 아껴 쓴다.

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
- 항목 하나의 문구는 1~4단어로 짧게 유지한다. 문장은 부제와 설명 구역에만 허용한다.

## 작업 순서

1. **입력 파악.** 자료를 읽고 채워야 할 문구가 무엇인지 확인한다.
2. **카피 작성.** 큰 제목·부제와 각 구역의 리본 제목·항목을 쓴다. 순서 있는 내용은 시간·발전 순으로 배열한다.
3. **구성 설계.** 제목 구역을 위에 크게 두고, 나머지를 내용 중요도에 맞춰 2~5개 구역으로 나눈다.
   각 구역의 고래 포즈·소품을 하나씩 정한다. 같은 포즈를 연달아 쓰지 않고, 소품은 캐릭터만큼 크게 잡는다.
   캐릭터 2마리가 함께 나오는 자리는 고래+토끼로 구성한다.
4. **프롬프트 조립.** 아래 `프롬프트 템플릿`을 채워 **포스터 한 장을 통째로 묘사하는 프롬프트 하나**를 만든다.
5. **SVG 작성.** 아래 `SVG 작성 규칙`을 따라 같은 포스터를 그려 파일 하나로 저장한다.
6. **출력.** 작성한 카피 요약 + 프롬프트 블록 + SVG 파일 경로 + 한국어 한 줄 설명을 출력한다.

## 프롬프트 템플릿

아래 영어 템플릿에서 `<...>`를 채우고, 구역 목록은 주제에 맞게 늘리거나 줄인다. 구역별로 프롬프트를 나누지 말고
한 덩어리로 유지한다.

```text
ONE single hand-drawn black-and-white cheatsheet poster, nearly square (1200x1160),
white background, framed by a thick rounded black border. It is one unified drawing —
not a set of separate images, not a rigid grid of equal bands.

STYLE: whiteboard-comic, warm and playful. Everything has thick rounded hand-drawn black
outlines and simple geometric shapes. Grayscale ONLY — white, light gray, mid gray,
near-black; no other color, no gradients, no textures. Playful hand-lettered text.
Section titles sit on torn ribbon-tape labels; ordered items use circled numbers and
small arrows. Props and tools are drawn LARGE — each prop roughly as tall as the
character beside it, recognizable by silhouette alone. Generous even margins; nothing
touches the frame.

CHARACTERS: cute kawaii whale mascots (chubby body, white belly, light gray back, tiny
fins, dot eyes, small smile) appear throughout, thinking, pointing and working to guide
the content. When two characters share one spot (a hand-off, a comparison of people), the
second one is a small rabbit (round white body, two long ears, dot eyes). Only whales
and rabbits appear.

LAYOUT: a large title zone across the top holds a big hand-lettered title reading exactly:
"<TITLE>" with a short underline and a smaller subtitle reading exactly: "<SUBTITLE>",
with a whale mascot holding <a big prop related to the topic> beside it. Below and around
it, thick hand-drawn lines divide the rest of the poster into a few sections of DIFFERENT
sizes (not equal bands), arranged to fit the content. Each section has a ribbon label:

- Section "<RIBBON TITLE 1>": <what it shows — items/steps, each a whale with a big prop>.
- Section "<RIBBON TITLE 2>": <...>.
- Section "<RIBBON TITLE 3>": <...>.
(add or remove sections to fit the topic; optionally one section is a good-vs-bad
comparison with a whale succeeding on one side and a whale struggling on the other.)

DO NOT: use any color, add gradients or textures, force everything into equal horizontal
bands, use any animal other than the whale and the rabbit, draw props tiny or ambiguous,
misspell any text, or let elements touch the frame or the dividing lines.
```

## SVG 작성 규칙

SVG는 skill이 직접 그린다. 형태 배치와 수치는 `assets/example-poster.svg`를 열어 기준으로 삼는다.
단, 예시의 구성을 그대로 베끼지 말고 스타일만 따른다.

- `viewBox="0 0 1200 1160"`, 외부 이미지·스크립트 없는 순수 SVG 1.1로 작성한다. Figma와 Canva가 그대로 불러온다.
- 레이어 순서: 흰 배경 → 구역 구분선 → 구역 배경(연회색) → 고래·소품 일러스트 → 리본·상자 →
  텍스트 `<text>` → 외곽 프레임.
- 모든 텍스트는 `<text>`로 남긴다. Figma에서는 그대로 편집되고, 폰트가 없으면 대체 폰트로 표시되므로
  사용자에게 Google Fonts에서 Patrick Hand(한글이면 Gaegu)를 설치하라고 안내한다.
- Canva는 SVG의 `<text>`를 지원하지 않는 경우가 있다. 사용자가 Canva용이라고 하면 텍스트를 지우고
  도형만 있는 버전을 하나 더 저장한 뒤, 문구는 Canva에서 직접 얹으라고 안내한다.
- 고래 한 마리는 `ellipse`(몸) + `path`(꼬리·지느러미) + `circle`(눈) + `path`(입) 정도의 기본 도형
  5~8개로 그린다. 토끼는 `ellipse`(몸) + `ellipse`(귀 2개와 귀 안쪽) + `circle`(눈) + `path`(입)로
  그린다. 정밀함보다 실루엣과 표정이 읽히는 게 중요하다.
- 소품은 캐릭터 키의 60~100% 크기로 크게 그린다. 렌더링해서 봤을 때 소품이 무엇인지 바로 구별되지
  않으면 도형을 줄이지 말고 크기를 키운다.
- 저장 후 가능하면 렌더링(headless 브라우저 스크린샷 등)으로 형태가 깨지지 않았는지 확인한다.

## 예시 (gold reference)

이 예시는 이 스타일을 적용한 완성 결과다. 새 작업의 품질 기준으로 삼되, **구성은 베끼지 말고 스타일만** 따른다.

입력 예:

```text
딥 워크(깊은 몰입) 습관을 한 장 치트시트 포스터로 만들어줘.
```

skill이 한 판단: 문구가 없어서 카피 전부를 만들었다. 제목 옆에 헤드폰 낀 고래를 크게 두고, 아래를
크기가 다른 세 구역으로 나눴다 — 왼쪽 위엔 몰입 3단계(원문자+화살표), 왼쪽 아래엔 실전 두 사례
(그중 하나는 고래가 토끼에게 폴더를 넘기는 2인 자리), 오른쪽엔 얕은 몰입 vs 깊은 몰입 비교.
등폭 밴드로 나누지 않고 내용 중요도에 맞춰 크기를 달리했다.

출력 프롬프트:

```text
ONE single hand-drawn black-and-white cheatsheet poster, nearly square (1200x1160),
white background, framed by a thick rounded black border. It is one unified drawing —
not a set of separate images, not a rigid grid of equal bands.

STYLE: whiteboard-comic, warm and playful. Everything has thick rounded hand-drawn black
outlines and simple geometric shapes. Grayscale ONLY — white, light gray, mid gray,
near-black; no other color, no gradients, no textures. Playful hand-lettered text.
Section titles sit on torn ribbon-tape labels; ordered items use circled numbers and
small arrows. Props and tools are drawn LARGE — each prop roughly as tall as the
character beside it, recognizable by silhouette alone. Generous even margins; nothing
touches the frame.

CHARACTERS: cute kawaii whale mascots (chubby body, white belly, light gray back, tiny
fins, dot eyes, small smile) appear throughout, thinking, pointing and working to guide
the content. When two characters share one spot, the second one is a small rabbit (round
white body, two long ears, dot eyes). Only whales and rabbits appear.

LAYOUT: a large title zone across the top holds a big hand-lettered title reading exactly:
"Deep Work" with a short underline and a smaller subtitle reading exactly: "One hard
thing. No pings, no tabs — just you.", with a whale wearing big headphones sitting at a
large laptop beside it, plus a round hand-drawn seal reading exactly: "STAY DEEP" on the
far right. Below, thick hand-drawn lines divide the rest into sections of different sizes:

- A tall left section labeled "THE FOCUS LOOP": three cells with circled numbers 1-2-3 and
  arrows between them — 1 "Pick One" (a whale pointing at a big bullseye target), 2
  "Silence" (a whale pressing a big face-down phone with a struck bell), 3 "Deep Dive"
  (a whale beside a big hourglass).
- A shorter left-bottom section labeled "IN PRACTICE": "90-min Sprint" (a whale with a big
  hourglass) and "Hand-off" (a whale passing a big folder to a rabbit).
- A narrow right column split top and bottom into a comparison: top "Shallow" (a droopy
  whale buried under many tiny notification squares, a big X mark); bottom "Deep" (a happy
  whale hugging one big task block with a check mark and sparkles).

DO NOT: use any color, add gradients or textures, force everything into equal horizontal
bands, use any animal other than the whale and the rabbit, draw props tiny or ambiguous,
misspell any text, or let elements touch the frame or the dividing lines.
```

출력 SVG: `assets/example-poster.svg` — 같은 내용을 스타일 스펙 그대로 그린 파일이다.

한국어 한 줄 설명: 딥 워크를 주제로 헤드폰 낀 고래·STAY DEEP 씰이 있는 제목 구역 아래에 몰입 3단계,
실전 사례(고래→토끼 폴더 전달), 얕은 몰입 vs 깊은 몰입 비교를 크기가 다른 세 구역으로 배치했습니다.

## 완료 전 확인

- 결과물이 포스터 한 장인가? (프롬프트 1개, SVG 파일 1개)
- BAND 같은 등폭 고정 틀에 억지로 맞추지 않고, 내용에 맞는 크기의 구역으로 자유롭게 짰는가?
- 사용자가 준 문구를 바꾸지 않고 그대로 넣었는가? (없을 때만 skill이 만들고, 만든 카피를 보여줬는가?)
- 그림 속 모든 텍스트를 `reading exactly: "..."`로 철자까지 지정했는가?
- 캔버스·프레임·팔레트·선 규칙 등 고정 스타일 스펙을 프롬프트와 SVG 양쪽에 지켰는가?
- 캐릭터가 고래(2마리 자리는 고래+토끼)뿐인가? 여러 번 등장하고 포즈가 겹치지 않는가?
- 소품이 캐릭터 키의 60% 이상으로 커서 실루엣만으로 무엇인지 구별되는가?
- 흰색 + 회색 3단계 흑백 규칙을 지켰는가? 색·그라디언트·질감이 없는가?
- 폰트가 전부 SIL OFL(Patrick Hand, Comic Neue, Gaegu 등)인가?
- SVG를 파일로 저장하고 경로를 알려줬는가? 텍스트가 `<text>` 요소로 편집 가능한가?
- 프롬프트를 그대로 복사해 이미지 생성 모델에 붙여넣을 수 있는 한 블록으로 출력했는가?
