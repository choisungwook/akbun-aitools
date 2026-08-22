---
name: akbun-draw-storytellingimage
description: >
  발표·블로그·영상의 이야기를 장면마다 하나씩 삽화 이미지 생성 프롬프트로 만든다. 스타일은 크림색 종이
  배경 + 진한 잉크 외곽선 + 마커 낙서 채색의 손그림 마커 스케치로 고정하고, 무엇을 그릴지(장면·소재)는
  이야기에 맞춰 정한다. 산출물은 그림이 아니라 GPT image, nano-banana 같은 이미지 생성 모델에 그대로
  넣을 영어 프롬프트다. Trigger on: "스토리텔링 이미지", "발표 삽화", "장면별 그림", "마커 스케치",
  "storytelling illustration", or any request to illustrate a story scene by scene.
---

# 스토리텔링 이미지 생성 프롬프트 만들기

## 이 skill이 하는 일

이야기(발표 시나리오, 블로그 스토리, 설명하려는 개념)를 장면으로 나누고 **장면마다 영어 이미지 생성
프롬프트 하나씩**을 만든다. 한 장짜리 웹툰이 아니라, 말로 이야기를 풀 때 각 대목을 받쳐주는 삽화다.
그래서 장면 하나에 메시지 하나만 담고, 여러 장이면 스타일과 등장인물을 이어지게 유지한다.

프롬프트를 영어로 쓰는 이유는 이미지 생성 모델이 영어를 가장 정확히 해석하고 그림 속 글자도 영어를
가장 정확히 렌더링하기 때문이다. 설명은 한국어, 프롬프트는 영어다.

## 비주얼 스타일

화이트보드 애니메이션·그래픽 레코딩에서 볼 수 있는, 마커로 빠르게 그린 손그림 낙서 스타일이다. 모든
프롬프트가 아래를 그대로 묘사한다.

- **배경**: 따뜻한 크림색 종이. 순백색이 아니라 아이보리 톤. 격자·질감·그림자 없음.
- **선**: 진한 네이비/검정 잉크의 손그림 외곽선. 굵고 살짝 흔들리는 스케치 느낌.
- **채색**: 마커로 낙서하듯 그은 빗금 채색. 면을 꽉 채우지 않고 획이 보이며 외곽선을 살짝 삐져나온다.
- **팔레트**: 밝은 원색(파랑, 노랑, 주황, 초록, 빨강) 중 한 장면에 3~5색. 갈색은 나무·흙·머리카락 보조색.
- **주인공**: 이야기에 맞는 캐릭터를 하나 정해 마커 낙서로 그리고, 표정·몸짓을 과장한다.
- **군중**: 채색 없는 단순한 흰 미니 실루엣(이목구비 없음)으로 주인공과 구분한다.
- **연출**: 움직임 곡선, 땀방울, 강조 화살표(빨강/주황), 짧은 라벨 같은 만화 기호를 아껴 쓴다.
- **소품**: 산, 바위, 깃발, 씨앗, 사다리처럼 이야기의 비유를 그대로 그린 큼직한 소품이 어울린다.
- **여백**: 대상 하나가 가운데를 차지하고 주변은 넉넉히 비운다. 배경 디테일을 그리지 않는다.
- **그림 속 텍스트**: 기본은 없음. 필요하면 짧은 영어 라벨 1~2개만. 사용자가 한국어 라벨을 요청하면 1~3단어.

## 작업 순서

1. **이야기 파악.** 사용자가 남긴 이야기·개념·시나리오와 첨부 자료를 읽는다.
2. **장면 나누기.** 사용자가 장면 수·내용을 지정하면 그대로 따른다. 지정이 없으면 전환점(도입 -> 문제 ->
   해결)을 기준으로 2~5장면을 제안한다. 한 장 요청이면 이야기 전체를 대표하는 한 장면만 만든다.
3. **주인공 고정.** CHARACTER 문장을 한 번 정하고 모든 장면에 **글자 그대로** 복사한다. 이미지 모델은
   장면 간 기억이 없어서 문장이 다르면 인물이 달라진다.
4. **장면 묘사.** 장면마다 인물의 행동·표정, 꼭 필요한 소품, 연출 요소를 정한다. 개념 설명이면 인물
   대신 비유 소품을 주인공으로 삼아도 된다.
5. **프롬프트 조립·출력.** 아래 템플릿을 채워 장면별 영어 프롬프트 블록과 한국어 장면 구성 설명을
   출력한다.

## 장면 구성 원칙

- **한 장면 = 한 메시지.** 두 사건을 한 장면에 넣지 않는다.
- **감정은 몸으로.** 기쁨은 번쩍 든 팔, 곤란함은 땀방울과 웅크린 자세처럼 몸짓과 기호로 전달한다.
- **비유는 크게.** 개념을 설명할 때는 비유 소품(산, 씨앗, 저울)을 화면의 주인공으로 삼는다.
- **시리즈 일관성.** 배경 톤, 팔레트, CHARACTER 문장을 모든 프롬프트에서 동일하게 유지한다.
- **텍스트 최소화.** 이야기는 말·글이 하고 그림은 받쳐주기만 한다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 장면마다 하나씩, 각각 별도의 코드 펜스 블록에 담아 그대로 복사할 수 있게 한다.
2. **한국어 장면 구성 설명** — 이야기를 어떻게 나눴고 각 장면이 어느 대목을 받치는지 장면당 1문장.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`만 채우고 스타일 문구는 그대로 둔다. 사용하지 않는 줄(라벨, 군중)은 지우고,
`CHARACTER` 문장은 시리즈 전체에서 글자 그대로 재사용한다.

```text
A hand-drawn marker sketch illustration on a warm cream paper background, in the style of a
whiteboard-animation doodle. Bold, confident dark navy ink outlines with a slightly wobbly
hand-drawn feel. Colored with loose marker scribble strokes that leave visible hatching and
slightly overshoot the outlines — not flat fills. Bright palette of <3-5 colors, e.g. blue,
yellow, orange, green>.

CHARACTER: <one sentence defining the main character — body shape, colors, face, clothing,
e.g. "a round chibi character with a big head, black dot eyes and a simple curved-line smile">,
colored in loose marker scribbles. (Reuse this exact sentence in every scene of the series.)

SCENE: <the character's action, posture and emotion, plus the one or two props that matter,
e.g. "the character holds a tiny green sprout in a clay pot, leaning in close with a proud
smile, small motion swooshes around the sprout">.

<Optional CROWD: small simple white doodle figures with plain rounded bodies, no facial
features, no color, doing <action> in the background.>

<Optional LABEL: one short handwritten label reading exactly: "<...>", with a small <red|orange>
arrow pointing at <target>.>

STYLE: minimalist doodle, one clear focal subject centered, generous empty cream space around it,
no background details, no grid, no shadows, playful and energetic linework. <Horizontal 3:2 |
square 1:1 | vertical 2:3> aspect ratio.

DO NOT: no photorealism, no flat vector fills, no gradients, no pure white background, no extra
text beyond the label, no watermarks, no panel borders.
```

## 예시

아래는 "작심삼일을 이기는 법" 발표를 3장면으로 요청받았을 때의 장면 구성 예시다. 각 장면을 위
템플릿에 넣어 3개의 독립된 영어 프롬프트로 출력한다.

```text
Scene 1 — 결심: the main character stands proudly with hands on hips next to a huge to-do
list covered in red marker scribbles, a small red flag planted beside it.
Scene 2 — 포기: the same character (identical CHARACTER sentence) slumps on the floor with sweat
drops, the giant to-do list toppling over it like a falling wall.
Scene 3 — 아주 작은 습관: the same character does one tiny push-up with a big smile,
next to a small calendar where three days are checked with green marker.
```

## 완료 전 확인

- 사용자가 남긴 이야기를 근거로 장면을 나눴는가? (이야기를 지어내지 않았는가?)
- 장면마다 프롬프트가 하나씩, 복사 가능한 코드 블록으로 나왔는가?
- 크림색 배경, 진한 잉크 외곽선, 마커 스크리블 채색을 모든 프롬프트에 명시했는가?
- 같은 인물이 나오는 장면에서 CHARACTER 문장을 글자 그대로 재사용했는가?
- 한 장면에 메시지가 하나인가?
- 그림 속 텍스트를 최소화했고, 라벨은 짧은가?
- DO NOT에 사실적 렌더링·플랫 벡터·순백 배경 금지를 넣었는가?
