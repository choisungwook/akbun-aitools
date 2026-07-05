---
name: akbun-draw-webtoon
description: >
  사용자가 남긴 내용(주제, 상황, 이야기)을 분석해 3컷 또는 4컷 웹툰의 이미지 생성 프롬프트를 만든다.
  스타일은 xkcd풍 흑백 스틱피겨 컷만화로 고정한다 — 깨끗한 흰 배경, 손으로 그린 가는 검정 잉크 선,
  동그란 머리의 스틱피겨, 얇은 검정 테두리의 컷 패널이 가로로 나란히 배치되고, 패널 위에 손글씨 제목이
  붙는다. 이 skill은 그림을 직접 그리지 않고 GPT image, nano-banana 같은 이미지 생성 모델(agent)에
  그대로 넣을 영어 프롬프트만 만든다.
  Trigger on: "웹툰 그려줘", "웹툰 프롬프트", "3컷 만화", "4컷 만화", "컷만화", "만화로 그려줘",
  "스틱피겨 만화", "webtoon prompt", "comic strip prompt", "draw a 3-panel comic",
  or any request to turn a topic/story into an image-generation prompt for a short panel comic.
---

# 웹툰(3~4컷) 이미지 생성 프롬프트 만들기

## 이 skill이 하는 일

사용자가 남긴 내용(주제, 상황 설명, 짧은 이야기)을 분석해서 **3컷 또는 4컷 웹툰의 이미지 생성 프롬프트**를 만든다. 결과물은 그림이 아니라, GPT image나 nano-banana 같은 이미지 생성 모델에 그대로 붙여넣을 **영어 프롬프트 한 덩어리**다. 프롬프트를 받은 이미지 생성 AI agent가 실제 그림을 그린다.

컷의 내용은 skill이 정하지 않는다. **사용자가 남긴 내용을 분석해서** 컷을 나누고 장면을 구성한다. 사용자가 이야기 흐름을 직접 컷 단위로 지정하면 그대로 따르고, 주제만 던지면 skill이 기승전결(또는 기-승-결)로 나눠 제안한다.

왜 영어인가: 이미지 생성 모델은 영어 글자를 가장 정확히 렌더링한다. 그래서 프롬프트 자체와 그림 속 모든 텍스트(제목/패널 라벨/말풍선)를 영어로 쓴다. (SKILL 설명은 한국어, 산출물 프롬프트는 영어다.)

## 비주얼 스타일 (레퍼런스에 고정)

모든 프롬프트는 아래 스타일을 그대로 묘사한다. xkcd풍 흑백 스틱피겨 컷만화 레퍼런스("Evolution of Programming")의 분위기를 따른다.

- **전체 구성**: 큰 손글씨 제목이 맨 위에 있고, 그 아래 컷 패널이 **가로로 나란히** 배치된다.
- **패널**: 각 컷은 얇은 검정 직선 테두리의 세로형 직사각형. 패널 사이에 흰 여백을 둔다.
- **패널 라벨**: 각 컷 위쪽 안에 짧은 라벨(연도, 단계 이름 등)을 손글씨로 쓸 수 있다. 없어도 된다.
- **배경**: 깨끗한 순백색. 격자·질감·그림자 없음.
- **선**: 손으로 그린 가는 검정 잉크 선. 살짝 흔들리는 손그림 느낌이지만 깔끔하다.
- **색**: **완전 흑백**. 채색·회색 음영·해칭 없음. 선과 흰 배경만 사용한다.
- **인물**: 스틱피겨. 동그란 빈 원 머리(눈코입 없음), 가는 선 몸통과 팔다리. 표정 대신 자세와 소품으로 감정을 전달한다.
- **소품**: 책상, 의자, 모니터, 마이크처럼 장면에 꼭 필요한 것만 최소한의 선으로 그린다.
- **텍스트**: 제목·라벨·말풍선 모두 친근한 손글씨체 영어. 말풍선은 꼭 필요할 때만 짧게.
- **유머 구조**: 컷이 진행되며 상황이 고조되거나 반전되는 진행형 유머. 마지막 컷이 펀치라인이다.
- **비율**: 3컷이면 가로형(약 3:2), 4컷이면 더 넓은 가로형(약 2:1). 사용자가 세로 스크롤형을 요구하면 세로 배치로 바꾼다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록(```text)에 담아, 그대로 복사해 붙여넣을 수 있게 한다.
2. **한국어 컷 구성 설명** — 사용자의 내용을 어떻게 3~4컷으로 나눴고 어느 컷이 펀치라인인지 2~3문장.

## 작업 순서

1. **내용 파악.** 사용자가 남긴 주제/상황/이야기를 읽는다. 첨부 이미지가 있으면 그 내용도 소재로 삼는다.
2. **컷 수 결정.** 사용자가 3컷 또는 4컷을 지정하면 그대로 따른다. 지정이 없으면 내용의 단계 수로 판단한다 — 진행 단계가 3개면 3컷, 기승전결이 뚜렷하면 4컷.
3. **컷 시나리오 작성.** 각 컷마다 (a) 패널 라벨(옵션), (b) 장면 묘사(인물 자세·소품·행동), (c) 말풍선 텍스트(옵션, 영어, 짧게)를 정한다. 마지막 컷이 펀치라인이 되도록 배치한다.
4. **제목 결정.** 전체를 관통하는 짧은 영어 제목을 정한다(예: "Evolution of Programming").
5. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채워 영어 프롬프트를 완성한다.
6. **출력.** 영어 프롬프트 블록 + 한국어 컷 구성 설명을 출력한다.

## 컷 시나리오 원칙

- **한 컷 = 한 장면 = 한 메시지.** 컷 하나에 행동 하나만 담는다. 여러 사건을 한 컷에 넣지 않는다.
- **반복 속의 변화.** 레퍼런스처럼 같은 구도(같은 인물, 같은 책상)를 컷마다 반복하고 **한 가지 요소만 바꾸면** 진행이 한눈에 읽힌다. 가능하면 이 패턴을 쓴다.
- **펀치라인은 마지막 컷.** 가장 과장되거나 반전인 장면을 마지막에 둔다.
- **말풍선은 최소화.** 그림만으로 전달되면 말풍선을 생략한다. 쓴다면 컷당 한 개, 10단어 이내.
- **인물 수 최소화.** 스틱피겨는 1~2명이 가장 잘 그려진다. 3명 이상은 꼭 필요할 때만.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. 4컷이면 PANEL 4를 추가하고 비율을 2:1로 바꾼다. 사용하지 않는 줄(라벨, 말풍선)은 지운다.

```text
A <3-panel|4-panel> black-and-white stick figure comic strip in the style of xkcd, drawn with thin
hand-drawn black ink lines on a clean white background. No color, no shading, no gray fills — pure
line art only. All text is in English, in a friendly handwritten font.

TITLE: large handwritten title at the top, above the panels, reading exactly: "<TITLE>".

LAYOUT: <3|4> tall rectangular panels side by side, each with a thin black border, with white
space between panels. Each panel has a short handwritten label at the top inside: <list one label
per panel, matching the panel count, e.g. "label 1", "label 2", "label 3" for 3 panels, or add a
4th for 4 panels>. (Delete the label sentence entirely if no labels.)

PANEL 1 (<label>): <scene: who is doing what, with which minimal props, e.g. "a stick figure with
a round empty head sits on a simple office chair at a desk, typing on a keyboard in front of a
monitor">. <Optional: speech bubble reading exactly: "...">.

PANEL 2 (<label>): <scene — keep the same character, same desk and framing as panel 1, change only
what moves the story forward>. <Optional speech bubble>.

PANEL 3 (<label>): <scene — the punchline: the most exaggerated or twisted moment>. <Optional
speech bubble>.

CHARACTERS: stick figures with round empty heads (no facial features), thin line bodies and limbs.
Express emotion through posture and props only. Keep the same character design across all panels.

STYLE: minimalist, clean, generous white space, slightly wobbly hand-drawn lines, legible
handwritten English text. <3:2 horizontal|2:1 wide horizontal> aspect ratio.

DO NOT: no color, no shading, no gradients, no photorealism, no facial features on the stick
figures, no watermarks, no extra panels, no Korean or other non-English text in the image. Do not
misspell the title, labels, or speech bubbles.
```

## 예시 (gold reference)

이 예시는 레퍼런스 이미지("Evolution of Programming" 3컷)를 위 템플릿으로 역산한 완성 프롬프트다. 새 프롬프트의 품질 기준으로 삼는다.

입력 예: "프로그래밍이 어떻게 변해왔는지 3컷으로 — 옛날엔 키보드로 치고, 요즘은 AI한테 말로 시키고, 미래엔 생각만 하면 된다."

skill이 한 구성(자동): 같은 인물·책상·의자 구도를 3컷 모두 반복하고 입력 장치만 키보드 → 마이크 → 뇌 케이블로 바꿔 진행을 표현했다. 연도 라벨(2019/2026/2040)로 시간 흐름을 보여주고, 마지막 컷(머리에 케이블을 꽂고 컴퓨터에 직접 연결)이 펀치라인이다.

출력 프롬프트:

```text
A 3-panel black-and-white stick figure comic strip in the style of xkcd, drawn with thin
hand-drawn black ink lines on a clean white background. No color, no shading, no gray fills — pure
line art only. All text is in English, in a friendly handwritten font.

TITLE: large handwritten title at the top, above the panels, reading exactly: "Evolution of
Programming".

LAYOUT: 3 tall rectangular panels side by side, each with a thin black border, with white space
between panels. Each panel has a short handwritten label at the top inside: "2019", "2026", "2040".

PANEL 1 (2019): a stick figure with a round empty head sits on a simple office swivel chair at a
desk, typing on a keyboard in front of a monitor.

PANEL 2 (2026): the same stick figure at the same desk, now leaning toward a large microphone on
the desk and speaking into it (small motion lines near the mouth area), with the monitor pushed to
the side. No keyboard.

PANEL 3 (2040): the same stick figure at the same desk, sitting still with a single cable plugged
directly from its round head into the computer on the desk. No keyboard, no microphone.

CHARACTERS: one stick figure with a round empty head (no facial features), thin line body and
limbs, identical design in all three panels. Express the change only through the input device.

STYLE: minimalist, clean, generous white space, slightly wobbly hand-drawn lines, legible
handwritten English text. 3:2 horizontal aspect ratio.

DO NOT: no color, no shading, no gradients, no photorealism, no facial features on the stick
figure, no watermarks, no extra panels, no Korean or other non-English text in the image. Do not
misspell the title or the year labels.
```

한국어 컷 구성 설명: 같은 인물과 책상을 3컷 내내 고정하고 입력 장치만 키보드 → 마이크 → 뇌 케이블로 바꿔 "프로그래밍의 진화"를 표현했습니다. 연도 라벨로 시간 흐름을 보여주고, 머리에 케이블을 꽂는 마지막 컷이 펀치라인입니다.

## 완료 전 확인

- 사용자가 남긴 내용을 근거로 컷을 나눴는가? (skill이 임의로 소재를 지어내지 않았는가?)
- 컷 수가 3 또는 4인가? (사용자 지정이 있으면 그대로 따랐는가?)
- 그림 속 모든 텍스트(제목/라벨/말풍선)가 영어인가?
- 흑백 선화, 흰 배경, 눈코입 없는 스틱피겨 스타일을 프롬프트에 명시했는가?
- 컷마다 장면이 하나씩이고, 마지막 컷이 펀치라인인가?
- 같은 인물·구도를 컷마다 유지하도록 지시했는가?
- DO NOT에 채색·음영·비영어 텍스트 금지를 넣었는가?
- 프롬프트를 그대로 복사해 이미지 모델에 붙여넣을 수 있는 한 블록으로 출력했는가?
