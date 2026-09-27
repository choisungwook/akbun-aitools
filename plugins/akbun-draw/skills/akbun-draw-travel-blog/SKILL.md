---
name: akbun-draw-travel-blog
disable-model-invocation: true
description: >
  여행블로그의 썸네일·코스 약도·장면 삽화를 크림 배경과 크레용 질감의 플랫 일러스트로 만드는
  영어 이미지 생성 프롬프트를 작성한다. 사진삽입 주석의 썸네일·약도를 읽고 직접 찍을 현장 사진은
  건너뛴다. Trigger on: "여행블로그 사진", "여행 썸네일", "코스 약도 그려", "여행 지도 일러스트",
  "travel blog thumbnail", "illustrated course map". 그림 생성이 아니라 프롬프트 작성 요청에 사용한다.
---

# 여행블로그 이미지 프롬프트 생성

여행 글에 넣을 **일러스트의 영어 이미지 생성 프롬프트**를 만든다. 그림체와 색감은 고정하되 소재와 구도는 입력에 맞춘다. 이미지를 직접 생성하지 않는다.

| 종류 | 비율 | 쓰는 곳 | 그림 속 글자 |
|---|---|---|---|
| 썸네일 | 기본 1:1, 요청 시 16:9 | 글 맨 위·목록 화면 | 짧은 제목과 선택 부제, 또는 무문자 |
| 코스 약도 | 3:4 | 코스 미리보기 아래 | 번호만 |
| 장면 삽화 | 4:3 | 사용자가 삽화를 요청한 자리 | 없음 |

실제 가게·음식·풍경 사진을 생성하지 않는다. 실물의 모습을 확인하는 용도는 직접 찍은 사진으로 남긴다.

## 입력과 주석 계약

주석 형식은 `akbun-writing-travel-blog`와 함께 유지한다.

```markdown
<!-- 사진삽입: [종류] 사진에 무엇이 보여야 하는지 | 캡션: 사진 아래에 넣을 한 문장 -->
```

- 주석이 있는 글은 `[썸네일]`과 `[약도]`마다 프롬프트를 만든다. 글에 없는 약도를 자동 추가하지 않는다.
- `[현장]`은 기본적으로 건너뛰고 개수를 보고한다. 파일이 없다는 사실만으로 삽화를 만들지 않는다. 사용자가 그 자리를 삽화로 바꾸라고 요청했거나 주석에 `장면 삽화`로 명시한 경우에만 만든다. 별도 요청으로 전환하면 원문 주석을 고쳐 쓰지 않고 `장면 삽화`라고 표시한 대체 캡션을 함께 제안한다.
- 주석 없는 여행지·동선 설명은 썸네일 1개, 이동 코스가 있을 때만 약도 1개를 만든다.
- 알 수 없는 종류는 추측해서 만들지 않고 `확인 필요`로 보고한다.
- 장소 이름·순서·방향·길의 연결은 입력만 따른다. 방향이나 길 정보가 없으면 **위에서 아래로 흐르는 방문 순서도**를 만든다. 실제 지도처럼 도로망·해안선·방위·거리·도보 시간을 추가하지 않는다.
- 참고 이미지에서는 배치·여백·색·글자의 위계 같은 재사용 가능한 스타일만 추출한다. 피사체·장면·문구·고유 구도를 옮기지 않는다. 사진을 참고했어도 출력은 일러스트다.

## 스타일 규칙

색은 다음 값을 사용한다.

| 역할 | 색 |
|---|---|
| 종이 배경 | 크림 `#FBF6E9` |
| 확인된 길 | 회색 `#B9AEA6` |
| 동선 1·2·3 | 잎 초록 `#8CC63F`, 보라 `#8E6BB0`, 주황 `#F2A03D` |
| 녹지·나무 | 연두 `#DDE8B5`, 초록 `#7FB241`·`#3F6B2A` |
| 물 | 하늘색 `#A9CDE8` |
| 선·글자 | 먹색 `#2B2B2B` |
| 밝은 패널 | 크림 `#F7F1DC` |

썸네일 배경은 소재에 맞춰 하나를 고른다.

| 소재 | 배경색 |
|---|---|
| 숲·산 | 청록 `#5FA98C` |
| 바다·강 | 파랑 `#4F86A6` |
| 옛 동네 | 갈색 `#8A5A4B` |
| 카페·소품 | 자주 `#B5577F` |
| 시장·골목 | 올리브 `#5F7B3A` |

- 길과 동선은 가장자리가 거친 크레용·오일 파스텔 선이다.
- 소품과 인물은 외곽선 없는 플랫 색면이다. 사진 질감·그라데이션·입체 음영을 쓰지 않는다.
- 인물은 필요할 때만 1~3명, 얼굴 없는 작은 실루엣으로 둔다. 본문에 없던 인물이나 행동을 실제 경험처럼 묘사하지 않는다.
- 나무는 해당 소재가 있을 때 두 초록의 둥근 색면과 가는 먹색 줄기로 표현한다. 장소 아이콘도 입력에서 고르고 4개 이하로 제한한다.
- 세부 묘사·글자·소재가 없는 여백을 캔버스의 35% 이상 남긴다. 배경색 자체는 여백으로 센다.

## 썸네일: 작은 화면에서 읽히는 구성

짧은 제목과 대표 소재 하나가 먼저 보이게 한다. 사진 사례의 글자 위계와 시각적 집중만 일러스트에 적용한다.

| 요소 | 기준 |
|---|---|
| 안전 여백 | 상하좌우 최소 8% |
| 제목 | 장소명 중심 12자 안팎, 최대 2줄. 임의로 지명을 줄이지 않고 길면 의미 단위로 줄바꿈 |
| 부제 | 필요한 경우에만 특징 하나, 20자 이하. 제목과 같은 내용 반복 금지 |
| 위계 | 제목 글자 높이는 캔버스 높이의 8~12%, 부제는 제목의 40~50% |
| 주 소재 | 입력의 장소·활동을 상징하는 큰 소재 하나. 부수 아이콘 2개 이하 |
| 대비 | 단색 배경에는 흰색 또는 먹색 중 읽히는 색. 부족하면 크림 패널+먹색 글자 사용 |

구도는 아래 중 소재에 맞는 하나를 고른다. 같은 구도를 매번 강제하지 않는다.

- **분리형:** 제목은 위 30~35%, 주 소재는 아래 45~55%에 둔다. 실루엣 띠나 패널은 필요한 경우만 쓴다.
- **장면형:** 주 소재를 한쪽에 크게 두고 반대쪽 빈 공간에 제목을 둔다. 글자로 핵심 소재를 가리지 않는다.
- **무문자형:** 사용자가 원하거나 목록의 글 제목만으로 충분하면 글자를 생략한다. 한눈에 구분되는 주 소재와 여백을 남긴다.

16:9를 1:1로 중앙 크롭할 때 양끝 약 22%씩이 잘린다. 두 비율이 모두 필요하면 각각 구도를 짠 별도 프롬프트를 낸다. 같은 이미지를 크롭해 쓰겠다고 명시한 경우에만 제목과 핵심 소재를 중앙 너비 약 56% 안에 둔다.

제작 후에는 폭 200px 정도의 목록 크기로 줄여 제목과 소재가 구분되는지 확인하도록 안내한다. 프롬프트만 만든 상태에서 가독성이 검증됐다고 보고하지 않는다. 한글이 깨지면 `TEXT`를 무문자로 바꾸고 제목·부제·위치를 별도 편집 지시로 낸다.

## 코스 약도와 방문 순서도

- 상하좌우 6% 여백, 크림 배경, 흰 원과 먹색 숫자를 쓴다. 이름은 그림 밖 한국어 범례에 적는다.
- 지리 근거가 있을 때만 회색 길 위에 색 동선을 겹친다. 입력의 방향·연결을 보존하되 실제 축척은 보장하지 않는다.
- 방향이나 길 정보가 없으면 도로를 그리지 않는다. 번호를 위에서 아래로 놓고 방문 순서만 색 선으로 연결한다. 캡션과 설명에 `방문 순서도 · 실제 방향·거리와 다름`을 명시한다.
- 동선 색은 한 장에 3개 이하, 장소는 8개 이하. 넘으면 구간별로 나누고 전체 번호를 유지한다. 분할 후 같은 장소의 번호를 바꾸지 않는다.
- 인물·나무·물·건물은 입력에 있거나 명확한 비지리적 장식일 때만 넣는다. 장식으로 실제 지형·시설을 암시하지 않는다.

## 장면 삽화

가로 4:3 안에 소재 1~3개로 한 장면을 만든다. 크림 배경에 둥근 사각 틀과 먹색 가는 테두리를 쓸 수 있다. 실제 간판·로고·가게 이름은 그림에 넣지 않는다. 캡션은 그림 밖에 두고 `장면 삽화`임을 표시한다.

## 프롬프트 조립

1. 대상 주석과 대응 번호를 정하고 건너뛸 `[현장]`을 센다.
2. 썸네일의 소재·배경색·구도·문구를 정한다. 약도는 지리 근거 유무에 따라 도로 또는 순서 연결을 정한다.
3. 해당 템플릿의 빈칸을 채우고 불필요한 선택지를 지운다. 주석의 장소 순서·파일명·캡션과 대조한다.
4. 아래 공통 스타일 블록을 모든 프롬프트 끝에 그대로 붙인다.

공통 스타일 블록은 다음과 같다.

```text
STYLE: flat travel illustration on subtly grainy paper. Route lines have rough crayon and
oil-pastel edges. Objects are flat color shapes without outlines, gradients or 3D shading.
If people are specified, keep them tiny and faceless. If trees are specified, use round
two-tone green shapes (#7FB241, #3F6B2A) on thin dark trunks. Keep at least 35% of the canvas
free of objects, details and text.

DO NOT: no photorealism, no photo textures, no real shop signage, no logos, no brand marks,
no watermarks, no detailed faces, no drop shadows, no glossy effects.
```

썸네일 템플릿은 다음과 같다. `TEXT`는 제목형과 무문자형 중 하나만 남긴다.

```text
A travel blog thumbnail illustration, <aspect ratio>. Solid muted <background color and hex>
with subtle paper grain.

LAYOUT: <chosen composition, positions and sizes of the title area and main subject>.
MAIN SUBJECT: <one subject grounded in the input>. Keep all essential elements at least
8% away from every edge. <crop-safe instruction only if one image must serve both ratios>.

TEXT: <title placement>, bold rounded sans-serif, <white or dark #2B2B2B>, reading "<제목>".
Title letter height is 8–12% of the canvas height, at most two lines. <optional subtitle
reading "<부제>", 40–50% of the title letter height>. <cream panel if contrast needs it>.
No other text.

<공통 스타일 블록>
```

무문자형의 `TEXT` 대체 문구는 다음과 같다.

```text
TEXT: No text, letters or numbers anywhere. Keep the composition focused on the main subject.
```

약도 템플릿은 다음과 같다. 방향이 없으면 `SCHEMATIC`에 순서도임을 쓰고 `CONNECTIONS`에 도로·방위·거리를 넣지 않도록 명시한다.

```text
An illustrated <walking course map | visit-order diagram>, portrait 3:4, on cream paper
(#FBF6E9), with 6% margins on all sides.

SCHEMATIC: <what geographic relationships are known, or explicitly non-geographic order>.
CONNECTIONS: <only the known roads in gray #B9AEA6, or a top-to-bottom sequence without roads>.
ROUTES: <one to three crayon colors, each with a specified path and hex value>.
MARKERS: <each number and position>, white circles with thin dark (#2B2B2B) outlines.
Numbers only, no place names, compass labels, distances or travel times.
DECORATION: <input-grounded icons, or none>.

<공통 스타일 블록>
```

장면 삽화 템플릿은 다음과 같다.

```text
A flat travel illustration, landscape 4:3, on cream paper (#FBF6E9).
SCENE: <one input-grounded moment with one to three subjects>.
<optional rounded rectangular frame with a thin dark #2B2B2B border>.
No text anywhere in the image.

<공통 스타일 블록>
```

## 결과물

이미지마다 다음을 출력한다.

1. 대응 주석과 비율을 적은 한국어 한 줄 설명.
2. 공통 스타일까지 붙인 완성 영어 프롬프트를 `text` 코드 블록 하나에 작성.
3. 약도는 번호와 장소 이름의 한국어 범례 및 축척·방향의 한계. 삽화 전환은 대체 캡션.

마지막에 `[현장]` 전체 개수 중 건너뛴 개수와 명시적 요청으로 삽화로 전환한 개수를 구분해 알린다. 이미지 생성·축소 가독성 확인을 실행하지 않았다면 `프롬프트 작성까지만 완료`로 보고한다.

## 예시

다음은 가상 장소의 입력이다. 주석 없는 장소 설명에서는 이동이 있을 때만 약도를 만든다.

```text
물버들 수목원. 온실 → 씨앗 전시실 → 연못 순서로 걸었음. 정확한 방향·거리·길 모양은 모름.
온실은 유리 건물. 썸네일 제목은 물버들 수목원, 부제 없이. 사진 W01은 온실 전경.
<!-- 사진삽입: [썸네일] 유리 온실을 주 소재로 | 캡션: 물버들 수목원 산책 일러스트 -->
<!-- 사진삽입: [약도] 온실, 씨앗 전시실, 연못. 방향 미확인, 방문 순서만 표시 | 캡션: 방문 순서도 · 실제 방향·거리와 다름 -->
<!-- 사진삽입: [현장] 파일: W01 온실 전경 | 캡션: 수목원의 온실 -->
```

썸네일은 제목 상단·온실 하단의 분리형을 선택한다. 입력의 건물 종류만 표현하고 실제 외형을 보장하지 않는다. 약도는 다음처럼 도로 없는 방문 순서도로 만든다.

```text
An illustrated visit-order diagram, portrait 3:4, on cream paper (#FBF6E9), with 6% margins
on all sides.

SCHEMATIC: non-geographic visit order only; positions do not represent actual directions
or distances. Do not draw roads, shorelines, terrain, a compass or a scale.
CONNECTIONS: one vertical sequence from top to bottom, connecting 1, 2 and 3 in that order.
ROUTES: one leaf-green (#8CC63F) rough crayon connector from marker 1 through 2 to 3.
MARKERS: 1 at upper center, 2 at center, 3 at lower center. White circles with thin dark
(#2B2B2B) outlines. Numbers only; no place names, distances or travel times.
DECORATION: none.

STYLE: flat travel illustration on subtly grainy paper. Route lines have rough crayon and
oil-pastel edges. Objects are flat color shapes without outlines, gradients or 3D shading.
If people are specified, keep them tiny and faceless. If trees are specified, use round
two-tone green shapes (#7FB241, #3F6B2A) on thin dark trunks. Keep at least 35% of the canvas
free of objects, details and text.

DO NOT: no photorealism, no photo textures, no real shop signage, no logos, no brand marks,
no watermarks, no detailed faces, no drop shadows, no glossy effects.
```

범례는 1 온실, 2 씨앗 전시실, 3 연못이다. `[현장]` 1개는 건너뛰고 삽화 전환은 0개다. 방문 순서도는 실제 방향·거리와 다르며 프롬프트 작성까지만 완료한 예다.

## 완료 전 확인

- 주석별 생성 대상과 건너뛴 현장 개수가 맞는가? 사진 부재만으로 삽화를 만들지 않았는가?
- 모든 생성 대상이 일러스트인가? 금지문 `no photorealism` 등을 사진 생성 지시로 오인하지 않았는가?
- 제목이 실제 장소 이름을 보존하고 핵심 소재를 가리지 않는가? 비율별 크롭 조건을 처리했는가?
- 약도의 모든 장소·연결·순서가 입력에 있으며, 미확인 방향을 순서도로 명시했는가?
- 범례와 번호가 일치하고 한 장당 색 3개·장소 8개 이하인가?
- 공통 스타일 블록이 완성 프롬프트마다 있으며 참고 자료의 이름·문구·장면·고유 구도가 없는가?
- 프롬프트 작성과 실제 이미지 생성·가독성 검증을 구분해 보고했는가?
