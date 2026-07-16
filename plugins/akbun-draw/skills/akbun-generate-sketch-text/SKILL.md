---
name: akbun-generate-sketch-text
description: >
  문구(텍스트)를 받아 "린넨 원단 위 자수(스티치) 텍스트 + 노란 형광펜 강조" 스타일의 이미지 생성
  프롬프트를 만든다. GPT image나 nano-banana 같은 이미지 생성 모델(또는 이미지 생성 agent)에 그대로
  넣을 영어 프롬프트를 만든다. 이 skill은 그림을 직접 그리지 않고, 다른 agent나 이미지 모델이 그릴
  프롬프트만 생성한다. 어떤 줄을 형광펜으로 강조할지는 skill이 자동으로 판단한다.
  Trigger on: "자수 텍스트 프롬프트", "스티치 텍스트", "원단 텍스트 이미지", "다짐 이미지 프롬프트",
  "명언 이미지 프롬프트", "sketch text prompt", "stitched text prompt", "embroidered text image",
  or any request to turn a short quote/motto into a stitched-text-on-fabric image prompt.
---

# 자수 텍스트 이미지 프롬프트 생성

## 이 skill이 하는 일

짧은 문구(다짐, 명언, 제목, 메시지)를 받아, 레퍼런스 이미지와 같은 **린넨 원단 위 자수 텍스트** 스타일의
**이미지 생성 프롬프트**를 만든다. 결과물은 그림이 아니라, GPT image 또는 nano-banana 같은 이미지 생성
모델에 그대로 붙여넣을 **영어 프롬프트 한 덩어리**다.

왜 영어인가: 이미지 생성 모델은 영어 글자를 가장 정확히 렌더링한다. 그래서 프롬프트 자체와 그림 속
모든 텍스트를 영어로 쓴다. 사용자가 한국어 문구를 주면 그림에 넣을 영어 문구로 옮기고, 옮긴 결과를
사용자에게 함께 보여준다. (SKILL 설명은 한국어, 산출물 프롬프트는 영어다.)

이 skill은 그림을 직접 그리지 않는다. 프롬프트만 만들어서 사용자에게 보여주면, 사용자나 이미지 생성
agent가 그 프롬프트로 그림을 그린다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록(```text)에 담아, 그대로 복사해 붙여넣을 수 있게 한다.
2. **한국어 한 줄 설명** — 어떤 줄을 강조했고 왜 그것을 골랐는지 1~2문장. 한국어 문구를 영어로 옮겼다면 그 결과도 함께 적는다.

## 작업 순서

1. **문구와 맥락 파악.** 사용자가 준 문구를 읽는다. 한국어면 그림에 넣을 자연스러운 영어 문구로 옮긴다.
   문구가 없고 주제만 있으면(예: "운동 다짐") 주제에 맞는 짧은 영어 문구를 1개 제안해서 쓴다.
2. **줄 나누기.** 문구를 2줄(최대 3줄)로 나눈다. 레퍼런스처럼 **호칭/도입 줄 + 핵심 메시지 줄** 구조가
   가장 좋다(예: "Dear Self," + "I will win, I promise!"). 원문이 한 줄이면 그대로 한 줄로 둬도 된다.
3. **강조 줄 자동 선정.** 노란 형광펜으로 강조할 줄을 skill이 고른다. 기준은 아래 `강조 줄 고르기`를 따른다.
4. **글자 수 확인.** 이미지 모델은 긴 문장을 글자 깨짐 없이 그리지 못한다. 줄당 **5단어 안팎, 최대 8단어**로
   줄인다. 넘치면 의미를 유지한 채 짧게 다듬는다.
5. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채워 영어 프롬프트를 완성한다.
6. **출력.** 영어 프롬프트 블록 + 한국어 한 줄 설명을 출력한다.

## 강조 줄 고르기 (skill이 자동 판단)

노란 형광펜 강조는 **한 줄에만** 넣는다. 두 줄 이상 강조하면 그림이 시끄러워지고 강조 효과가 사라진다.

- 다짐/약속/행동이 담긴 줄을 강조한다. 호칭이나 도입 줄("Dear Self,")은 강조하지 않는다.
- 문구가 한 줄뿐이면 그 줄을 강조한다.
- 세 줄이면 가장 핵심 메시지 한 줄만 강조한다.

## 비주얼 스타일 (레퍼런스에 고정)

모든 프롬프트는 아래 스타일을 그대로 묘사한다. 이 스타일은 바꾸지 않는다.

- **배경**: 자연스러운 베이지/오트밀색 린넨(캔버스) 원단. 직조 짜임(weave) 질감이 은은하게 보인다.
  주름이나 소품 없이 원단만 평평하게 채운다.
- **텍스트 질감**: 모든 글자는 검정 실로 **자수(새틴/지그재그 스티치)** 놓은 것처럼 그린다. 글자
  가장자리가 실밥처럼 살짝 거칠고 오돌토돌하다. 인쇄된 매끈한 글자가 아니다.
- **글꼴 느낌**: 굵고 둥근 산세리프. 친근하고 단단한 인상.
- **크기 위계**: 첫 줄(도입/호칭)은 크게, 강조 줄은 그보다 작지만 굵게.
- **형광펜 강조**: 강조 줄 뒤에 **노란 형광펜을 한 번 쓱 그은 듯한 밴드**를 깐다. 밴드 가장자리는
  손으로 칠한 듯 불규칙하고, 텍스트보다 약간 넓다. 형광펜은 텍스트 뒤(배경)이고 글자는 그 위에 또렷하다.
- **전체 톤**: 따뜻하고 아늑하며 미니멀. 여백이 넉넉하고 다른 장식 요소는 없다.
- **비율**: 가로형(약 2.4:1 배너형). 텍스트 블록은 가운데보다 약간 왼쪽에 둔다.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. 사용하지 않는 줄(세 번째 줄 등)은 지운다.

```text
A wide horizontal photo-style image of text embroidered on natural linen fabric,
like a cozy motivational banner.

BACKGROUND: a flat piece of natural beige/oatmeal linen canvas filling the entire frame,
with a subtle visible weave texture. No wrinkles, no props, no other objects.

TEXT: all lettering looks stitched in black thread (dense satin/zigzag embroidery),
with slightly rough, fuzzy thread edges — not printed. Bold, rounded sans-serif letterforms.
Line 1 (large): "<LINE 1>"
Line 2 (smaller, bold): "<LINE 2>"
<Line 3 (smaller, bold): "<LINE 3>">
Render every word EXACTLY as written, with correct spelling.

HIGHLIGHT: behind line <N> only, a single swipe of yellow highlighter — a hand-painted
yellow band with rough, uneven edges, slightly wider than the text. The band sits behind
the stitched letters; the black text stays crisp on top. No highlight on the other lines.

LAYOUT: the text block sits slightly left of center with generous empty fabric around it.
Left-aligned lines, line 1 above line 2.

STYLE: warm, cozy, minimal, high contrast between black stitching and light fabric.
Wide banner aspect ratio (about 2.4:1).

DO NOT: add any text other than the lines above. Do not misspell the words.
No logos, icons, needles, threads, hoops, hands, or watermarks. No frame or border.
```

## 예시 (gold reference)

이 예시는 레퍼런스 이미지를 그대로 재현하는 완성 프롬프트다. 새 프롬프트의 품질 기준으로 삼는다.

입력 예:

```text
문구: 나 자신에게 — 반드시 이길 거라고 약속해
```

skill이 정한 것(자동): 영어 문구 "Dear Self," + "I will win, I promise!" 두 줄로 나누고,
약속이 담긴 두 번째 줄에만 노란 형광펜 강조를 넣었다.

출력 프롬프트:

```text
A wide horizontal photo-style image of text embroidered on natural linen fabric,
like a cozy motivational banner.

BACKGROUND: a flat piece of natural beige/oatmeal linen canvas filling the entire frame,
with a subtle visible weave texture. No wrinkles, no props, no other objects.

TEXT: all lettering looks stitched in black thread (dense satin/zigzag embroidery),
with slightly rough, fuzzy thread edges — not printed. Bold, rounded sans-serif letterforms.
Line 1 (large): "Dear Self,"
Line 2 (smaller, bold): "I will win, I promise!"
Render every word EXACTLY as written, with correct spelling.

HIGHLIGHT: behind line 2 only, a single swipe of yellow highlighter — a hand-painted
yellow band with rough, uneven edges, slightly wider than the text. The band sits behind
the stitched letters; the black text stays crisp on top. No highlight on line 1.

LAYOUT: the text block sits slightly left of center with generous empty fabric around it.
Left-aligned lines, line 1 above line 2.

STYLE: warm, cozy, minimal, high contrast between black stitching and light fabric.
Wide banner aspect ratio (about 2.4:1).

DO NOT: add any text other than the lines above. Do not misspell the words.
No logos, icons, needles, threads, hoops, hands, or watermarks. No frame or border.
```

한국어 한 줄 설명: 문구를 "Dear Self," / "I will win, I promise!" 두 줄로 옮기고, 다짐이 담긴 두 번째
줄에만 노란 형광펜 강조를 넣었습니다.

## 완료 전 확인

- 그림 속 모든 텍스트가 영어인가? 한국어 문구를 옮겼다면 사용자에게 옮긴 결과를 보여줬는가?
- 각 줄이 8단어 이하로 짧은가?
- 형광펜 강조는 정확히 한 줄에만 있는가? 호칭/도입 줄을 강조하지 않았는가?
- 자수(스티치) 질감, 린넨 배경, 노란 형광펜 밴드를 모두 묘사했는가?
- DO NOT 절에 다른 텍스트/로고/워터마크 금지를 넣었는가?
- 프롬프트를 그대로 복사해 이미지 모델에 붙여넣을 수 있는 한 블록으로 출력했는가?
