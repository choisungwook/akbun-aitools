---
name: akbun-draw-sketchbook-card
description: >
  개념·주제를 손글씨 제목·체크리스트와 액자 속 연필 일러스트가 있는 스파이럴 스케치북 카드 스타일로
  그리는 이미지 생성 프롬프트를 만든다.
---

# 연필 스케치북 카드 그림 프롬프트 생성

## 이 skill이 하는 일

하나의 개념을 한 장짜리 **연필 스케치북 카드**로 보여주는 그림의 **이미지 생성 프롬프트**를 만든다. 입력은 개념 이름과 설명, 체크리스트, 시리즈 번호 같은 카드 내용이거나, 그냥 주제 하나일 수도 있다. 결과물은 그림이 아니라, GPT image나 nano-banana 같은 이미지 생성 모델에 그대로 붙여넣을 **영어 프롬프트 한 덩어리**다.

카드의 레이아웃은 레퍼런스에 고정되어 있다. 스파이럴 링이 달린 세로형 스케치북 한 페이지에, 위쪽에는 손글씨로 쓴 번호·제목·부제·설명·체크리스트가 있고, 아래쪽에는 얇은 연필 테두리 액자 안에 정밀한 연필 일러스트가 있다. 일러스트 위에는 개념을 설명하는 주석(점선 화살표 등)을 굵은 연필 선으로 덧그린다. 카드 전체가 흑연 연필로만 그린 모노크롬이다.

`akbun-draw-component`(하이레벨 아키텍처), `akbun-draw-network-relationship`(네트워크 흐름)과 짝이 되는, "개념 카드 일러스트" 버전이다. 다이어그램이 아니라 **한 장면의 그림으로 개념을 각인시키고 싶을 때** 쓴다. 인스타그램 카루셀, 블로그 표지, 시리즈물 카드에 어울린다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 코드 블록 하나에 담아, 그대로 복사해 이미지 생성 모델에 붙여넣을 수 있게 한다.
2. **한국어 한 줄 설명** — 카드에 어떤 텍스트를 넣었고, 어떤 장면과 주석으로 개념을 표현했는지 1~2문장.

## 입력 다루기

사용자가 전달한 내용은 **분석하거나 그대로 사용한다**.

- **카드 내용이 이미 있으면 그대로 쓴다.** 번호, 제목, 부제, 설명, 체크리스트를 사용자가 적어줬으면 문구를 바꾸지 않고 그대로 카드에 넣는다. 요약하거나 다듬지 않는다.
- **주제만 있으면 skill이 카드를 채운다.** 제목(영어 대문자 한 단어~짧은 구), 부제(선택), 한두 줄 설명, 체크 항목 2~4개, 그리고 개념을 보여줄 장면과 주석을 skill이 정한다.
- **비어 있는 요소는 굳이 만들지 않는다.** 시리즈 번호가 없으면 번호 없이, 부제가 없으면 부제 없이 카드를 만든다.

## 카드 구성 요소

레퍼런스 카드는 아래 요소로 이루어진다. 괄호는 레퍼런스에서의 예다.

- **인덱스 번호** (선택): 왼쪽 위 큰 손글씨 숫자 (`07`)
- **제목**: 대문자 손글씨 영어 제목 (`BLOOM`)
- **부제** (선택): 제목 아래 괄호 안 작은 손글씨. 한국어 가능 (`(블루밍)`)
- **밑줄**: 제목 블록 아래 짧고 굵은 손그림 밑줄
- **설명**: 한두 줄 손글씨 설명 (`가운데부터 원을 그리며 물을 부어 부풀린다`)
- **체크리스트**: 손그림 체크마크로 시작하는 항목 2~4개 (`균일한 추출`, `가스 배출`, `부드러운 바디`)
- **일러스트**: 아래쪽 약 2/3 영역, 얇은 연필 테두리 액자 안의 정밀한 연필 그림 (드리퍼 위 손과 커피)
- **주석 오버레이** (선택이지만 강력 추천): 일러스트 위에 굵은 연필 선으로 덧그린 개념 표시 (중심에서 퍼지는 점선 나선 화살표)

## 장면과 주석 고르기 (이 skill의 핵심)

카드의 힘은 텍스트가 아니라 **장면 하나 + 주석 하나**가 개념을 즉시 이해시키는 데서 나온다.

- **장면은 피사체가 하나뿐인 단순한 장면**으로 고른다. 위 커피 브루잉 예시는 "드리퍼 위에서 물을 붓는 손" 하나로 블루밍 동작의 대상을 만들었다. 배경은 넓고, 주인공은 한 명(하나)이다.
- **주석은 개념의 동작·구조를 기하학적으로 보여주는 표시**다. 점선 타원(궤도), 방향 화살표(이동), 확대 원(줌), 프레임 안 프레임(구도) 같은 것들이다. 개념이 "움직임"이면 화살표가, "범위"면 점선 영역이, "비교"면 두 표시가 어울린다.
- **장면은 분위기를, 주석은 정의를 담당한다.** 체크리스트가 "시네마틱 무드"를 말하면 장면이 시네마틱해야 하고, 설명이 "원을 그리며 이동"이면 주석이 원과 방향을 보여줘야 한다.
- 장면 묘사는 한두 문장이면 충분하다. 소품을 나열하지 말고, 피사체·배경·구도(뒷모습, 로우앵글 등)만 말한다.
- 장면에 인물·캐릭터가 필요하면 akbun 마스코트 고래(`akbun-mascot-whale` skill의 캐릭터 스펙)를 연필 스타일로 그린다.

## 텍스트 언어 규칙

- **프롬프트 자체는 영어**로 쓴다. 이미지 모델이 지시를 가장 잘 따르는 언어다.
- **제목은 영어 대문자**가 기본이다. 손글씨 대문자 제목이 이 카드 스타일의 얼굴이다.
- **부제·설명·체크리스트는 사용자가 준 언어 그대로** 넣는다. 레퍼런스처럼 한국어도 된다. 다만 짧게 유지한다 — 긴 문장일수록 이미지 모델이 글자를 틀릴 확률이 높다.
- 그림에 들어갈 모든 텍스트는 프롬프트에 `reading exactly: "..."` 형태로 **정확히 철자까지 지정**한다.

## 작업 순서

1. **입력 파악.** 사용자가 준 내용에서 번호/제목/부제/설명/체크리스트를 찾는다. 있으면 그대로, 없으면 주제에서 만든다.
2. **장면 결정.** 개념을 대표할 단일 피사체 장면을 한두 문장으로 정한다.
3. **주석 결정.** 개념의 동작·구조를 보여줄 기하학적 표시(점선 화살표, 원, 프레임 등)를 정한다. 표현할 것이 없으면 생략한다.
4. **선택 요소 정리.** 번호·부제 중 근거 없는 것은 뺀다.
5. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채우고, 쓰지 않는 줄은 지운다.
6. **출력.** 영어 프롬프트 블록 + 한국어 한 줄 설명을 출력한다.

## 비주얼 스타일 (레퍼런스에 고정)

모든 프롬프트는 아래 스타일을 그대로 묘사한다.

- **매체**: 흑연 연필로만 그린 모노크롬. 색 없음. 손글씨와 일러스트 모두 연필.
- **종이**: 따뜻한 미색(off-white) 스케치북 종이, 은은한 종이 질감. 왼쪽 가장자리에 검은 스파이럴 링.
- **위쪽 텍스트 블록**: 페이지의 위 약 1/3. 큰 손글씨 번호·제목, 작은 손글씨 부제·설명, 체크마크 리스트.
- **아래쪽 일러스트**: 페이지의 아래 약 2/3. 얇은 손그림 연필 테두리 액자, 그 안에 섬세한 해칭과 풍부한 음영의 정밀 연필화.
- **주석**: 일러스트 위에 일반 선보다 굵은 연필 선으로 덧그린 점선/화살표. 스케치 위의 개념 다이어그램처럼 읽힌다.
- **비율**: 세로형 4:5 (1080×1350, 인스타그램 세로형).

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. `(delete if none)`이 붙은 줄은 해당 요소가 없으면 지운다.

```text
A single page of a spiral-bound sketchbook, photographed straight-on. Black spiral rings run
along the left edge. The paper is a warm off-white with a subtle grain. Everything on the page
is drawn in graphite pencil only — hand lettering and illustration alike — monochrome, no color,
like a designer's concept sketchbook.

TOP BLOCK (about the top third of the page, hand-lettered in pencil, top to bottom):
- A large handwritten index number, reading exactly: "<NUMBER>". (delete if none)
- A large hand-lettered title in capital letters, reading exactly: "<TITLE>".
- Below the title, a smaller handwritten subtitle in parentheses, reading exactly:
  "(<SUBTITLE>)". (delete if none)
- A short, thick hand-drawn underline below the title block.
- A short handwritten description over one or two lines, reading exactly: "<DESCRIPTION>".
- A vertical checklist; each item starts with a bold hand-drawn checkmark:
  - reading exactly: "<CHECK ITEM 1>"
  - reading exactly: "<CHECK ITEM 2>"
    ... (2–4 items)

BOTTOM (about the lower two thirds of the page): a thin hand-drawn pencil rectangle frames a detailed
graphite pencil illustration: <SCENE — one or two sentences: a single clear subject, the
background, and the composition, e.g. "a lone astronaut seen from behind, standing on a rocky
ridge overlooking a vast desolate landscape under a hazy sky">. Fine hatching, rich pencil
shading, strong sense of depth.

ANNOTATION OVERLAY: drawn on top of the illustration in bolder pencil strokes than the drawing
itself: <ANNOTATION — e.g. "a large dashed ellipse circling horizontally around the subject,
with an arrowhead showing the direction of movement">. It reads like a concept diagram sketched
over the illustration. (delete if none)

STYLE: monochrome graphite pencil on off-white sketchbook paper, hand-drawn and warm, clean
composition, very legible lettering. Portrait 4:5 (1080x1350) aspect ratio.

DO NOT: use any color except the pencil graphite and paper tone. No digital-looking fonts —
all text is handwritten. Do not misspell any text. Do not add extra text beyond what is listed
above. Do not let the annotation obscure the subject of the illustration.
```

## 예시 (gold reference)

이 예시는 이 스타일을 적용한 완성 프롬프트다. 새 프롬프트의 품질 기준으로 삼는다.

입력 예:

```text
커피 브루잉 시리즈 3번째. BLOOM (블루밍). 가운데부터 원을 그리며 소량의 물을 부어 커피를 부풀린다.
용도: 균일한 추출, 가스 배출, 부드러운 바디.
```

skill이 한 판단: 카드 텍스트는 사용자가 준 그대로 썼다. 장면은 "블루밍 동작의 손"이 필요해, 위에서 내려다본 손 하나가 드리퍼 위 커피 가루에 물을 붓는 장면을 골랐다. 주석은 개념 정의("가운데부터 원을 그리며 붓는다")를 그대로 보여주는, 중심에서 바깥으로 퍼지는 점선 나선 화살표다.

출력 프롬프트:

```text
A single page of a spiral-bound sketchbook, photographed straight-on. Black spiral rings run
along the left edge. The paper is a warm off-white with a subtle grain. Everything on the page
is drawn in graphite pencil only — hand lettering and illustration alike — monochrome, no color,
like a designer's concept sketchbook.

TOP BLOCK (about the top third of the page, hand-lettered in pencil, top to bottom):
- A large handwritten index number, reading exactly: "03".
- A large hand-lettered title in capital letters, reading exactly: "BLOOM".
- Below the title, a smaller handwritten subtitle in parentheses, in Korean, reading exactly:
  "(블루밍)".
- A short, thick hand-drawn underline below the title block.
- A short handwritten description over two lines, in Korean, reading exactly:
  "가운데부터 원을 그리며 소량의 물을 부어 부풀린다".
- A vertical checklist; each item starts with a bold hand-drawn checkmark:
  - reading exactly: "균일한 추출"
  - reading exactly: "가스 배출"
  - reading exactly: "부드러운 바디"

BOTTOM (about the lower two thirds of the page): a thin hand-drawn pencil rectangle frames a detailed
graphite pencil illustration: an overhead view of a single hand holding a kettle, pouring hot
water onto coffee grounds resting in a dripper on a wooden table, thin wisps of steam rising.
Fine hatching, rich pencil shading, strong sense of depth.

ANNOTATION OVERLAY: drawn on top of the illustration in bolder pencil strokes than the drawing
itself: a dashed spiral line starting at the center of the coffee grounds and winding outward,
with an arrowhead at the outer end showing the direction of the pour. It reads like a concept
diagram sketched over the illustration.

STYLE: monochrome graphite pencil on off-white sketchbook paper, hand-drawn and warm, clean
composition, very legible lettering. Portrait 4:5 (1080x1350) aspect ratio.

DO NOT: use any color except the pencil graphite and paper tone. No digital-looking fonts —
all text is handwritten. Do not misspell any text. Do not add extra text beyond what is listed
above. Do not let the annotation obscure the subject of the illustration.
```

한국어 한 줄 설명: 사용자가 준 카드 텍스트(03 / BLOOM / 블루밍 / 설명 / 체크 3개)를 그대로 넣고, 블루밍 동작의 대상으로 위에서 내려다본 손과 드리퍼 장면을 골라 중심에서 바깥으로 퍼지는 점선 나선 화살표로 "원을 그리며 붓는다"를 표현했습니다.

## 완료 전 확인

- 사용자가 준 카드 텍스트를 바꾸지 않고 그대로 넣었는가? (주제만 받았을 때만 skill이 채운다)
- 그림 속 모든 텍스트를 `reading exactly: "..."`로 철자까지 지정했는가?
- 장면의 피사체가 하나로 명확한가? 주석이 개념의 동작·구조를 보여주는가?
- 번호·부제 등 근거 없는 선택 요소를 지웠는가?
- 모노크롬 연필 스타일과 스파이럴 스케치북 레이아웃을 템플릿대로 유지했는가?
- 프롬프트를 그대로 복사해 이미지 생성 모델에 붙여넣을 수 있는 한 블록으로 출력했는가?
