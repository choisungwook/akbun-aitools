---
name: akbun-draw-quiet-pencil
description: >
  아무 순간·이야기·소재를 "조용한 연필 스케치 장면 스타일"로 그리는 이미지 생성 프롬프트를 만든다.
  이 스타일은 따뜻한 크림색 종이 배경 + 상단 3분의 2의 빈 여백 + 하단 지면선 위에 작게 그린 회색
  연필 소재 1~3개 + 뒷모습 인물 + 채도 낮은 틸(청록) 소품 딱 하나로 이뤄진, 일상의 정적인 한 장면을
  담는 그림체다. 스타일 정의는 같은 디렉터리의 design.md에 있고, 이 skill이 고정하는 건
  그림체·색감·구도 언어(스타일)이며 무엇을 그릴지(소재·장면)는 입력에 맞춰 자유롭게 정한다.
  산출물은 이미지 생성 모델(GPT image, nano-banana 등)에 그대로 넣을 영어 프롬프트다. Trigger on:
  "조용한 연필 그림", "연필 스케치 장면", "여백 많은 그림", "잔잔한 일상 그림", "quiet pencil
  sketch", "cream pencil scene", or any request to draw a moment in this quiet cream
  pencil-sketch style.
---

# 조용한 연필 스케치 장면 프롬프트 생성

## 이 skill이 하는 일

아무 순간·이야기·소재를 **하나의 정해진 조용한 연필 스케치 스타일**로 그린 이미지 생성 프롬프트를
만든다. 넓게 비운 크림색 종이, 하단 지면선 위의 작은 회색 연필 소재들, 뒷모습 인물, 그리고 시선이
마지막에 닿는 틸색 소품 하나 — 일상의 정적인 한 장면을 담는 그림체다.

**스타일 정의는 이 skill이 아니라 [design.md](./design.md)에 있다.** 프롬프트를 만들기 전에 반드시
design.md를 읽고, 거기 적힌 캔버스·색·선·구도·인물·포인트 색 규칙을 그대로 따른다. 이 문서는 작업
절차와 프롬프트 조립만 다룬다.

**이 skill이 고정하는 것은 "그림체·색감·구도 언어"뿐이다.** 무엇을 그리는지(소재·장면)는 매번
입력에 맞게 자유롭게 정한다.

산출물은 그림이 아니라 **영어 이미지 생성 프롬프트**다. GPT image나 nano-banana 같은 이미지 생성
모델에 그대로 붙여넣는다.

## 입력 다루기

사용자가 주는 것은 그리고 싶은 순간·이야기·소재이며, 형식은 자유다(문장, 글, 이미지).

- **장면이 구체적이면 그대로 쓴다.** 소재를 마음대로 바꾸지 않는다.
- **이미지를 줬으면 주제 파악용으로만 본다.** 그 이미지의 구도·픽셀을 복제하지 않는다. 그림체·색감은
  design.md를 따른다.
- **글·개념만 있으면 skill이 장면을 만든다.** 이야기에서 가장 정적인 한 순간을 골라 소재 1~3개짜리
  장면으로 구성하고, 지어낸 장면임을 밝히되 사용자에게 물어보며 멈추지 않는다.
- **여러 장을 요청하면** 장마다 같은 규칙을 적용한다.

## 작업 순서

1. **design.md를 읽는다.** 스타일 규칙 전체를 확인한다.
2. **장면 결정.** 입력에서 정적인 한 순간을 고르고 소재 1~3개로 압축한다.
3. **틸 포인트 결정.** 장면의 의미가 모이는 작은 소품 하나를 골라 틸색을 배정한다.
4. **배치 설계.** 소재가 하나면 한쪽에 치우쳐 두고 나머지를 비운다. 소재가 여럿이면 좌우로 나눠
   사이를 넓게 비우고, 장면에 자연스러우면 소재 사이의 관계를 배치로 암시해도 좋다(선택 요소).
5. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 `<...>`를 채운다. 스타일 문구는 건드리지 않는다.
6. **출력.** 프롬프트 블록 + 한국어 한 줄 설명을 출력한다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록에 담아 그대로 복사할 수 있게 한다.
2. **한국어 한 줄 설명** — 어떤 순간을 어떤 소재로 구성했고 틸 포인트를 어디에 줬는지 1~2문장.

## 프롬프트 템플릿

`<...>`(장면·소재·틸 포인트)만 채우고, 그 외 스타일 문구는 그대로 둔다. 스타일 값의 근거는 전부
design.md다.

```text
A quiet hand-drawn pencil sketch illustration on a flat warm cream paper background (#F4ECDC),
landscape 4:3. The upper two thirds of the canvas are completely empty cream space — no sky,
no clouds, no background details. All subjects stand small on a single thin gray ground line
near the bottom of the frame, with only a faint soft shadow under each subject.

Everything is drawn with soft gray graphite pencil lines (#4A4A4A to #9A9A9A), slightly wobbly
and sketchy, shaded only with light pencil hatching. The whole scene is grayscale — no ink
black, no gradients, no photographic shading.

SCENE (one to three subjects only, placed small along the ground line with generous empty
cream space around them, each subject about a quarter to a third of the canvas height):
<describe the moment: what stands where along the ground line — a single subject sits
off-center with the rest of the frame empty; multiple subjects are spread far apart left and
right with a wide empty gap between them. People are seen from behind or in profile,
faceless, in calm everyday postures. A passing or leaving subject may be partially cropped
by the frame edge.>

COLOR RULE: the entire drawing is grayscale pencil on cream EXCEPT for exactly ONE small
hand-sized object — <the single teal object, e.g. "the scarf on the bench">, filled flat with
muted teal (#2E7D8C). Nothing else has any color.

STYLE: minimal quiet slice-of-life pencil sketch, generous negative space, restrained detail,
still and contemplative mood, like a wordless page from a gentle picture essay.

DO NOT: no text, no speech bubbles, no logos, no second accent color, no background or ground
details, no front-facing faces, no cartoon emotion marks, no dramatic action, no more than
three subjects, no texture or watermarks.
```

## 예시 (gold reference)

이 예시는 위 스타일을 새로운 장면에 입힌 완성 산출물이다. 스타일이 소재와 무관하게 재사용된다는 걸
보여준다.

입력 예:

```text
낮잠에서 막 깬 고양이의 한가로운 오후를 그려줘.
```

skill이 한 판단: 정적인 순간을 "낮잠에서 깬 고양이가 굴러가다 멈춘 털실 뭉치를 바라보는 오후"로
잡았다. 오른쪽에 옆모습으로 앉은 고양이를 두고 왼쪽에 작은 털실 뭉치 하나만 떨어뜨려 나머지를 넓게
비웠으며, 틸 포인트는 털실 뭉치에 줬다.

출력 프롬프트:

```text
A quiet hand-drawn pencil sketch illustration on a flat warm cream paper background (#F4ECDC),
landscape 4:3. The upper two thirds of the canvas are completely empty cream space — no sky,
no clouds, no background details. All subjects stand small on a single thin gray ground line
near the bottom of the frame, with only a faint soft shadow under each subject.

Everything is drawn with soft gray graphite pencil lines (#4A4A4A to #9A9A9A), slightly wobbly
and sketchy, shaded only with light pencil hatching. The whole scene is grayscale — no ink
black, no gradients, no photographic shading.

SCENE (one to three subjects only, placed small along the ground line with generous empty
cream space around them, each subject about a quarter to a third of the canvas height): on
the right, a plump cat sits in profile on the ground line, just woken from a nap, eyes
half-closed, drawn with soft pencil hatching; on the left, far from the cat, a small ball of
yarn rests where it stopped rolling, a faint wavy pencil trail behind it; the wide empty
cream space between them holds the lazy stillness of the afternoon.

COLOR RULE: the entire drawing is grayscale pencil on cream EXCEPT for exactly ONE small
hand-sized object — the ball of yarn, filled flat with muted teal (#2E7D8C). Nothing else
has any color.

STYLE: minimal quiet slice-of-life pencil sketch, generous negative space, restrained detail,
still and contemplative mood, like a wordless page from a gentle picture essay.

DO NOT: no text, no speech bubbles, no logos, no second accent color, no background or ground
details, no front-facing faces, no cartoon emotion marks, no dramatic action, no more than
three subjects, no texture or watermarks.
```

한국어 한 줄 설명: 낮잠에서 깬 고양이의 한가로운 오후를 옆모습 고양이와 멈춘 털실 뭉치 두 소재로
구성했고, 틸 포인트는 털실 뭉치에 줬습니다.

## 완료 전 확인

- design.md를 읽고 캔버스·색·선·구도·인물·포인트 규칙을 프롬프트에 반영했는가?
- 참고 자료의 장면·구도를 복제하지 않고, 입력에 맞는 새 장면에 **그림체·색감·구도 언어만** 입혔는가?
- 소재가 1~3개이고 하단 지면선 위에 작게 배치됐는가? 소재 주변과 상단 여백을 넉넉히 비웠는가?
- 틸 `#2E7D8C`를 작은 소품 **딱 하나**에만 줬는가? 나머지는 전부 회색 연필 그레이스케일인가?
- 인물이 뒷모습/옆모습이고 정면 얼굴·감정 기호가 없는가?
- 그림 속 텍스트를 넣지 않았는가?
- 프롬프트 블록과 한국어 한 줄 설명을 모두 출력했는가?
