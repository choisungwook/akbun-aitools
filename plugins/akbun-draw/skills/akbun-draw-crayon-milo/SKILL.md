---
name: akbun-draw-crayon-milo
description: 개념·시스템 구조·흐름을 "아이가 크레용으로 그린 다이어그램" 스타일로 그리는 이미지 생성 프롬프트를 만든다. 흰 종이 위에 두세 겹 흔들린 크레용 외곽선 + 같은 색 낙서 채움으로 그린 사각형·원·타원 노드, 굵은 크레용 다발 연결선, 회색 점선으로 표시한 대기·비활성 요소, 검은 손글씨 라벨로 이뤄진다. 이 skill이 고정하는 건 그림체·색감(스타일)뿐이고 노드 수·배치·연결 방향(레이아웃)은 입력에 맞춰 매번 정한다. 산출물은 GPT image, nano-banana 같은 이미지 생성 모델에 그대로 넣을 영어 프롬프트다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-crayon-milo

## 이 skill이 하는 일

개념·시스템 구조·흐름을 **아이가 크레용으로 그린 듯한 다이어그램 스타일**의 영어 이미지 생성 프롬프트로 만든다. 그림을 직접 그리지 않는다.

- 고정하는 것: 종이, 색, 크레용 선과 채움, 연결선 모양, 점선 규칙, 손글씨 라벨(스타일).
- 고정하지 않는 것: 노드 수, 노드 위치, 연결 방향, 화면 비율(레이아웃). 입력 내용에 맞게 매번 새로 정한다.

## 스타일

### 종이

- 배경은 아주 옅은 회백색 종이 `#F6F6F4` 단색. 줄·격자·얼룩·테두리 장식 없음.
- 화면의 40% 이상을 빈 종이로 남긴다. 노드끼리 붙이지 않고 노드 지름(또는 긴 변)의 0.5배 이상 띄운다.

### 색

노드 하나에 색 하나를 준다. 아래 표에서 고르고, 한 그림에 노드 색은 5색까지 쓴다. 같은 역할의 노드가 여럿이면 같은 색을 반복하고 1색으로 센다.

| 이름 | 값 | 쓰임 예 |
|---|---|---|
| YELLOW | `#F2D43A` | 사용자·입력 쪽 |
| RED | `#E0474C` | 중심·분배·판단 요소 |
| GREEN | `#36A33C` | 활성·정상 상태 |
| BLUE | `#2478D4` | 저장소·대상 |
| ORANGE | `#F0801E` | 연결선·보조 노드 |
| PINK | `#E86FA8` | 보조 노드 |

| 고정 색 | 값 | 쓰임 |
|---|---|---|
| INK | `#232323` | 라벨 글자 |
| GRAY | `#8C8C8C` | 대기·비활성 표시 점선 |

- "쓰임 예"는 기본값이다. 입력에 다른 의미가 있으면 바꿔도 되지만, 한 그림 안에서 같은 의미는 같은 색이다.
- 형광색·파스텔·그라데이션은 쓰지 않는다. 크레용처럼 채도가 높은 원색 계열이다.

### 노드

- 모양은 사각형·원·타원 중에서 고른다. 한 그림에 두 가지 이상 섞는다. 모서리는 손으로 그린 듯 살짝 둥글고 변은 반듯하지 않다.
- **외곽선**: 그 노드 색의 크레용으로 2~3번 겹쳐 그린다. 겹친 선이 서로 조금씩 어긋나 이중선처럼 보이고, 시작점과 끝점이 살짝 삐져나온다.
- **채움**: 같은 색으로 빠르게 문지른 낙서(대각선·지그재그 획)로 면을 채운다. 외곽선보다 옅고, 획 사이로 흰 종이가 비친다. 면 전체를 고르게 칠하지 않는다.
- 노드 크기는 내용의 비중에 맞춘다. 가장 중요한 노드가 가장 크되, 가장 큰 노드의 긴 변이 가장 작은 노드 긴 변의 2배를 넘지 않는다.

### 연결선

| 관계 | 그리는 법 |
|---|---|
| 활성 연결(지금 흐르는 길) | 같은 색 크레용 직선 3~5가닥을 나란히 겹친 굵은 다발. 화살촉 없음. 색은 출발 노드 색 또는 ORANGE |
| 대기·비활성 연결 | GRAY 점선 1~2가닥 + 양 끝이나 한쪽 끝에 작은 화살촉 |

- 연결선은 노드 외곽선에 닿거나 살짝 겹친다. 곡선보다 직선을 쓴다.

### 대기·비활성 요소

- 대기 중·꺼진·예비 노드는 원래 색으로 그리고, 바깥에 노드와 같은 모양의 GRAY 굵은 점선 테두리를 한 겹 두른다(노드와 점선 사이 간격은 노드 높이의 0.1~0.2배).
- 비활성 표시는 이 점선 테두리 하나뿐이다. 색을 회색으로 바꾸거나 X 표시를 하지 않는다.

### 라벨

- INK 검은 마커 손글씨. 둥글고 또박또박한 아이 글씨지만 읽기 쉬워야 한다. 대소문자를 섞은 영어(sentence case 또는 Title Case).
- 라벨은 노드 안 가운데에 1~2줄, 한 줄에 영어 단어 1~2개. 노드 밖 설명 문장·제목·범례를 넣지 않는다.
- 한국어 라벨을 원하면 한글 손글씨로 쓰되, 이미지 모델이 한글을 틀리게 그릴 수 있으니 결과에서 확인하라고 안내한다.

## 작업 순서

1. **내용 파악.** 입력에서 노드(구성 요소)와 관계를 뽑는다. 노드는 3~7개로 줄인다. 8개 이상이면 묶거나 그림을 나눈다.
2. **상태 결정.** 각 노드·연결을 활성 또는 대기·비활성으로 나눈다. 대기가 없으면 점선을 쓰지 않는다.
3. **색·모양 배정.** 색 표에서 노드마다 색을 고르고(5색 이하), 모양을 섞어 배정한다.
4. **레이아웃 설계.** 흐름에 맞는 배치를 직접 정한다(가로 줄, 세로 줄, 방사형, 갈림길, 원형 등). 이 skill은 특정 배치를 기본값으로 두지 않는다. 비율도 내용에 맞춰 1:1, 4:3, 16:9 중 고른다.
5. **프롬프트 조립.** 아래 템플릿의 `<...>`만 채운다. 스타일 문구는 바꾸지 않는다.
6. **출력.** 결과물 형식대로 출력한다.

## 결과물 형식

1. 영어 이미지 생성 프롬프트 한 개(코드 펜스 하나).
2. 한국어 설명 1~2문장: 노드 구성, 고른 배치, 점선으로 표시한 요소.

## 프롬프트 템플릿

`<...>`만 채우는 영어 프롬프트 템플릿이다.

```text
A child's hand-drawn crayon diagram on plain off-white paper (#F6F6F4), aspect ratio <1:1 | 4:3 | 16:9>.
Lots of empty paper around the shapes. Flat, top-down, no shading, no shadows, no gradients, no 3D.

DRAWING STYLE: every shape is drawn with waxy crayon. Outlines are traced two or three times with
loose, slightly wobbly, overlapping strokes that don't line up perfectly, with stroke ends overshooting
the corners. Each shape is filled with quick scribbled crayon strokes of its own color, lighter than the
outline, with white paper showing through the scribbles. Saturated primary crayon colors only.

NODES (each node is one shape in one color, with a black handwritten label centered inside):
<list every node: shape (rectangle / circle / ellipse), color name and hex from the palette, label text,
and rough position in the frame, e.g. "a large red circle (#E0474C) labeled 'Router' in the center">

CONNECTIONS:
<list every link: active links are thick bundles of 3-5 parallel straight crayon strokes in <color>,
no arrowheads; standby links are gray (#8C8C8C) dashed crayon lines with small arrowheads>

STANDBY ELEMENTS: <nodes that are idle/standby keep their own color and get one extra thick gray
(#8C8C8C) dashed crayon outline around them, same shape, with a small gap | none>

LABELS: neat, rounded, child-like black marker handwriting (#232323), easy to read, 1-2 words per line,
only inside the shapes.

DO NOT: no title, no legend, no captions outside shapes, no frame or decorative border around the
diagram, no clouds, no background scenery, no watermark or signature, no logos, no computer icons,
no pastel or neon colors, no clean vector lines.
```

## 예시 (gold reference)

스타일이 소재·배치와 무관하게 재사용됨을 보이는 예시다. 이 배치를 기본값으로 쓰지 않는다.

입력 예다.

```text
CI 파이프라인을 그려줘. 코드 push → 빌드 → 테스트 → 배포. 테스트가 실패하면 알림이 가는데 지금은 꺼져 있어.
```

skill이 한 판단: 노드 5개(Push, Build, Test, Deploy, Alert). 왼쪽 위에서 오른쪽 아래로 내려가는 계단 배치, 16:9. Alert는 꺼져 있으니 회색 점선 테두리와 점선 연결.

출력 프롬프트다.

```text
A child's hand-drawn crayon diagram on plain off-white paper (#F6F6F4), aspect ratio 16:9.
Lots of empty paper around the shapes. Flat, top-down, no shading, no shadows, no gradients, no 3D.

DRAWING STYLE: every shape is drawn with waxy crayon. Outlines are traced two or three times with
loose, slightly wobbly, overlapping strokes that don't line up perfectly, with stroke ends overshooting
the corners. Each shape is filled with quick scribbled crayon strokes of its own color, lighter than the
outline, with white paper showing through the scribbles. Saturated primary crayon colors only.

NODES (each node is one shape in one color, with a black handwritten label centered inside):
a small yellow circle (#F2D43A) labeled 'Push' at the upper left; an orange rectangle (#F0801E)
labeled 'Build' a step down and to the right; a large red ellipse (#E0474C) labeled 'Test' another
step down and to the right; a green rectangle (#36A33C) labeled 'Deploy' at the lower right;
a pink circle (#E86FA8) labeled 'Alert' at the lower left, below 'Test'.

CONNECTIONS:
Push to Build: thick bundle of 4 parallel straight yellow crayon strokes, no arrowheads.
Build to Test: thick bundle of 4 parallel straight orange crayon strokes, no arrowheads.
Test to Deploy: thick bundle of 4 parallel straight red crayon strokes, no arrowheads.
Test to Alert: gray (#8C8C8C) dashed crayon line with a small arrowhead pointing at 'Alert'.

STANDBY ELEMENTS: the 'Alert' circle keeps its pink color and gets one extra thick gray (#8C8C8C)
dashed crayon circle around it, with a small gap.

LABELS: neat, rounded, child-like black marker handwriting (#232323), easy to read, 1-2 words per line,
only inside the shapes.

DO NOT: no title, no legend, no captions outside shapes, no frame or decorative border around the
diagram, no clouds, no background scenery, no watermark or signature, no logos, no computer icons,
no pastel or neon colors, no clean vector lines.
```

한국어 설명: CI 단계 4개를 계단으로 내려가게 놓고 굵은 크레용 다발로 이었으며, 꺼져 있는 Alert만 회색 점선 테두리와 점선 화살표로 표시했습니다.

## 완료 전 확인

- 노드가 3~7개이고 노드 색이 5색 이하인가(같은 역할 반복은 1색).
- 노드마다 겹친 크레용 외곽선 + 같은 색 낙서 채움이 프롬프트에 있는가.
- 활성 연결은 3~5가닥 다발, 대기 연결은 GRAY 점선 + 화살촉인가. 대기 노드에만 GRAY 점선 테두리를 둘렀는가.
- 라벨이 노드 안에만 있고 제목·범례·테두리 장식이 없는가.
- 배치를 입력에 맞춰 새로 정했는가(예시 배치를 그대로 쓰지 않았는가).
- 알려진 캐릭터·로고와 닮은 요소가 없는가.
