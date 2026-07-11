---
name: akbun-draw-storytellingimage
description: >
  스토리텔링(발표, 블로그, 영상)에서 이야기 장면마다 쓸 삽화를 손그림 마커 스케치 스타일(크림색 종이 배경,
  진한 잉크 외곽선, 마커 낙서 채색)의 이미지 생성 프롬프트로 만든다. 그림을 직접 그리지 않고 GPT image,
  nano-banana 같은 이미지 생성 모델에 그대로 넣을 영어 프롬프트만 만든다.
---

# 스토리텔링 이미지 생성 프롬프트 만들기

## 이 skill이 하는 일

사용자가 남긴 이야기(발표 시나리오, 블로그 스토리, 설명하려는 개념)를 분석해서 **이야기 장면(scene)마다 하나씩 이미지 생성 프롬프트**를 만든다. 결과물은 그림이 아니라, GPT image나 nano-banana 같은 이미지 생성 모델에 그대로 붙여넣을 **영어 프롬프트**다. 프롬프트를 받은 이미지 생성 AI가 실제 그림을 그린다.

스토리텔링 이미지는 한 장짜리 웹툰이 아니다. 이야기를 말로 풀어갈 때 **각 대목을 받쳐주는 삽화**다. 그래서 장면 하나에 메시지 하나만 담고, 여러 장을 만들 때는 스타일과 등장인물이 이어지도록 유지하는 것이 핵심이다.

왜 영어인가: 이미지 생성 모델은 영어 프롬프트를 가장 정확히 해석하고, 그림 속 글자도 영어를 가장 정확히 렌더링한다. (SKILL 설명은 한국어, 산출물 프롬프트는 영어다.)

## 비주얼 스타일 (모든 프롬프트에 고정)

모든 프롬프트는 아래 스타일을 그대로 묘사한다. 화이트보드 애니메이션이나 그래픽 레코딩에서 볼 수 있는, 마커로 빠르게 그린 손그림 낙서 스타일이다.

- **배경**: 따뜻한 크림색/미색 종이 배경. 순백색이 아니라 살짝 아이보리 톤. 격자·질감·그림자 없음.
- **선**: 진한 네이비/검정 잉크의 손그림 외곽선. 굵고 자신감 있게, 살짝 흔들리고 겹쳐 그은 스케치 느낌.
- **채색**: 마커(사인펜)로 **낙서하듯 빗금으로 칠한** 채색. 면을 꽉 채우지 않고 스크리블(scribble) 획이 그대로 보이며, 색이 외곽선을 살짝 삐져나온다.
- **팔레트**: 밝은 원색 위주 — 파랑, 노랑, 주황, 초록, 빨강. 갈색은 나무·흙·머리카락 같은 보조색. 한 장면에 3~5색이면 충분하다.
- **인물(주인공)**: akbun 마스코트 고래를 마커 낙서 스타일로 그린다. 외형(콩 모양 통통한 몸, 흰 배, 밝은 회색 등, 작은 지느러미, 점 눈, 한 줄 곡선 입)은 `akbun-mascot-whale` skill의 캐릭터 스펙을 따르고, 과장된 표정과 몸짓으로 감정을 표현한다.
- **인물(군중)**: 여러 명이 필요한 장면에서는 채색 없는 단순한 흰 미니 고래 실루엣(이목구비 없음)으로 그려 주인공과 구분한다.
- **연출 요소**: 움직임 곡선(motion swoosh), 땀방울, 강조 화살표(빨강/주황), 짧은 라벨 같은 만화적 기호를 아껴서 쓴다.
- **비유 소품**: 산, 바위, 깃발, 씨앗, 사다리처럼 이야기의 비유를 그대로 그린 큼직한 소품이 잘 어울린다.
- **여백**: 대상 하나가 화면 가운데를 차지하고 주변은 넉넉히 비운다. 배경 디테일을 그리지 않는다.
- **그림 속 텍스트**: 기본은 없음. 꼭 필요하면 짧은 손글씨 라벨 1~2개만. 기본은 영어로 쓰고, 사용자가 한국어 라벨을 명시하면 짧게(1~3단어) 넣는다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 장면마다 하나씩, 각각 별도의 코드 펜스 블록(```text)에 담아 그대로 복사해 붙여넣을 수 있게 한다.
2. **한국어 장면 구성 설명** — 이야기를 어떻게 장면으로 나눴고 각 장면이 이야기의 어느 대목을 받치는지 장면당 1문장.

## 작업 순서

1. **이야기 파악.** 사용자가 남긴 이야기/개념/시나리오를 읽는다. 첨부 자료가 있으면 그 내용도 소재로 삼는다.
2. **장면 나누기.** 사용자가 장면 수나 장면 내용을 지정하면 그대로 따른다. 지정이 없으면 이야기의 전환점(도입 → 문제 → 절정/해결)을 기준으로 2~5장면을 제안한다. 한 장짜리 요청이면 이야기 전체를 대표하는 한 장면만 만든다.
3. **주인공 고정.** 주인공은 akbun 마스코트 고래다. CHARACTER 문장을 한 번 정하고 모든 장면 프롬프트에 **똑같은 문장으로** 복사해 넣는다. 이미지 모델은 장면 간 기억이 없어서, 문장이 다르면 인물이 달라진다.
4. **장면 묘사 작성.** 장면마다 (a) 인물의 행동과 표정, (b) 꼭 필요한 소품, (c) 연출 요소(움직임 곡선, 화살표, 라벨)를 정한다. 개념 설명이면 인물 대신 비유 소품 중심으로 구성해도 된다.
5. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채워 장면마다 영어 프롬프트를 완성한다.
6. **출력.** 장면별 영어 프롬프트 블록들 + 한국어 장면 구성 설명을 출력한다.

## 장면 구성 원칙

- **한 장면 = 한 메시지.** 이야기의 한 대목만 담는다. 두 사건을 한 장면에 넣지 않는다.
- **감정은 몸으로.** 표정은 단순하니 기쁨은 번쩍 든 팔, 곤란함은 땀방울과 웅크린 자세처럼 몸짓과 기호로 전달한다.
- **비유는 크게.** 개념을 설명할 때는 비유 소품(산, 씨앗, 저울 등)을 화면의 주인공으로 삼는다.
- **시리즈 일관성.** 장면이 여러 개면 배경 톤, 팔레트, 인물 정의 문장을 모든 프롬프트에서 동일하게 유지한다.
- **텍스트 최소화.** 그림만으로 전달되면 라벨을 생략한다. 이야기는 말/글이 하고 그림은 받쳐주기만 한다.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 장면마다 하나씩 완성한다. 사용하지 않는 줄(라벨, 군중)은 지운다. `CHARACTER` 문장은 시리즈 전체에서 글자 그대로 재사용한다.

```text
A hand-drawn marker sketch illustration on a warm cream paper background, in the style of a
whiteboard-animation doodle. Bold, confident dark navy ink outlines with a slightly wobbly
hand-drawn feel. Colored with loose marker scribble strokes that leave visible hatching and
slightly overshoot the outlines — not flat fills. Bright palette of <3-5 colors, e.g. blue,
yellow, orange, green>.

CHARACTER: the akbun whale mascot — a chubby bean-shaped whale with a white belly, a light gray
back, two tiny side fins, a small flat tail, black dot eyes and a simple curved-line smile,
colored in loose marker scribbles. (Reuse this exact sentence in every scene of the series.)

SCENE: <what happens in this moment: the character's action, posture and emotion, plus the one or
two props that matter, e.g. "the whale holds a tiny green sprout in a clay pot, leaning in close with a
proud smile, small motion swooshes around the sprout">.

<Optional CROWD: small simple white doodle whale figures with plain rounded bodies, no facial
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

입력 예시:

```text
"작심삼일을 이기는 법"이라는 발표를 하려고 해. 새해에 운동을 결심했다가 사흘 만에 포기하고,
목표를 아주 작게 줄인 뒤에야 습관이 된 이야기야. 3장면으로 만들어줘.
```

출력 개요 예시 (장면 나누기와 CHARACTER 문장 재사용을 보여준다):

```text
Scene 1 — 결심: the whale mascot stands proudly with its fins on its hips next to a huge to-do
list covered in red marker scribbles, a small red flag planted beside it.
Scene 2 — 포기: the same whale (identical CHARACTER sentence) slumps on the floor with sweat
drops, the giant to-do list toppling over it like a falling wall.
Scene 3 — 아주 작은 습관: the same whale does one tiny push-up on its fins with a big smile,
next to a small calendar where three days are checked with green marker.
```

각 장면을 위 템플릿에 넣어 3개의 독립된 영어 프롬프트로 출력한다.

## 완료 전 확인

- 사용자가 남긴 이야기를 근거로 장면을 나눴는가? (skill이 임의로 이야기를 지어내지 않았는가?)
- 장면마다 프롬프트가 하나씩, 각각 복사 가능한 코드 블록으로 출력됐는가?
- 크림색 배경, 진한 잉크 외곽선, 마커 스크리블 채색을 모든 프롬프트에 명시했는가?
- 같은 인물이 나오는 장면들에서 CHARACTER 문장을 글자 그대로 재사용했는가?
- 한 장면에 메시지가 하나인가?
- 그림 속 텍스트를 최소화했고, 라벨을 쓴 경우 짧은가?
- DO NOT에 사실적 렌더링·플랫 벡터·순백 배경 금지를 넣었는가?
