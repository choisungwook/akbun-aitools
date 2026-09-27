---
name: akbun-draw-travel-blog
disable-model-invocation: true
description: >
  여행블로그 글에 넣을 썸네일·코스 약도·장면 삽화를 "크레용 질감 플랫 여행 일러스트 스타일"로 그리는
  이미지 생성 프롬프트를 만든다. 이 스타일은 크림색 종이 배경 + 크레용으로 그은 듯한 회색 길 + 구간마다
  다른 색의 동선(초록·보라·주황) + 얼굴 없는 작은 플랫 인물과 소품 아이콘 + 채도 낮은 단색 표지 배경으로
  이뤄진다. 이 skill이 고정하는 건 그림체·색감·레이아웃이고, 무엇을 그릴지는 입력에 맞춰 정한다. 입력은
  `사진삽입` 주석이 있는 여행 글 초안이거나 여행지·동선 설명이다. 산출물은 이미지 생성 모델(GPT image,
  nano-banana 등)에 그대로 넣을 영어 프롬프트다. Trigger on: "여행블로그 사진", "여행 썸네일",
  "코스 약도 그려", "여행 지도 일러스트", "travel blog thumbnail", "illustrated course map".
---

# 여행블로그 이미지 프롬프트 생성

## 이 skill이 하는 일

여행블로그 글에 들어갈 이미지를 **하나의 정해진 일러스트 스타일**로 그리는 영어 프롬프트를 만든다. 그림을 직접 그리지 않는다.

만드는 이미지는 세 종류다.

| 종류 | 비율 | 쓰는 곳 | 그림 속 글자 |
|---|---|---|---|
| 썸네일 | 블로그 대표 이미지 1:1, 영상 썸네일 16:9 | 글 맨 위, 목록 화면 | 제목과 부제 |
| 코스 약도 | 세로 3:4 | 구간 미리보기 아래, 구간 제목 아래 | 번호만 |
| 장면 삽화 | 가로 4:3 | 사진이 없는 자리의 분위기 그림 | 없음 |

**생성 이미지는 실제 사진을 대신하지 않는다.** 실제 가게 외관, 간판, 음식, 메뉴판, 풍경의 인증 사진은 글쓴이가 직접 찍은 사진을 쓴다. 생성 모델은 그 장소의 실제 모습을 모르고, 사진처럼 보이는 가짜는 독자를 속인다. 그래서 세 종류 모두 그림임이 드러나는 플랫 일러스트로만 만든다.

## 입력 다루기

- **`사진삽입` 주석이 있는 글 초안**(`akbun-writing-travel-blog` 산출물)을 받으면 주석을 종류별로 모은다. `[썸네일]`과 `[약도]`는 프롬프트를 만든다. `[현장]`은 직접 찍은 사진 자리이므로 건너뛰고, 건너뛴 개수를 보고한다.
- 사용자가 `[현장]` 자리에 넣을 사진이 없다고 밝힌 경우에만 그 자리를 장면 삽화로 만든다.
- **여행지·동선 설명만** 받으면 썸네일 1장과 코스 약도 1장을 기본으로 만든다.
- 약도는 입력에 있는 길과 장소의 순서·방향만 쓴다. 입력에 없는 길, 역, 건물을 채워 넣지 않는다. 방향 정보가 없으면 동선을 위에서 아래로 흐르는 한 줄로 단순화하고, 실제 지리와 다를 수 있음을 밝힌다.
- 참고 이미지를 받으면 주제 파악용으로만 본다. 구도와 픽셀을 복제하지 않는다.

## 스타일 규칙

색은 다음 값을 쓴다.

| 역할 | 색 |
|---|---|
| 종이 배경 | 크림 `#FBF6E9` |
| 길 | 따뜻한 회색 `#B9AEA6` |
| 동선 1·2·3 | 잎 초록 `#8CC63F`, 보라 `#8E6BB0`, 주황 `#F2A03D` |
| 녹지 | 연두 `#DDE8B5`, 나무 `#7FB241`과 `#3F6B2A` |
| 물 | 하늘색 `#A9CDE8` |
| 선·글자 | 먹색 `#2B2B2B` |
| 실루엣 띠·패널 | 밝은 크림 `#F7F1DC` |

썸네일 배경은 여행지 성격에 따라 하나를 고른다.

| 여행지 성격 | 배경색 |
|---|---|
| 숲·산·계곡 | 청록 `#5FA98C` |
| 바다·강·항구 | 바다 파랑 `#4F86A6` |
| 옛 동네·역사 | 벽돌 갈색 `#8A5A4B` |
| 카페·취향·소품 | 자주 `#B5577F` |
| 시장·골목·이국적인 거리 | 올리브 `#5F7B3A` |

그림 언어는 다음과 같다.

- **선.** 길과 동선은 크레용이나 오일 파스텔로 그은 듯 가장자리가 거칠고 알갱이가 보인다. 자로 그은 직선이 아니라 손으로 그은 선이다.
- **면.** 소품과 인물은 외곽선 없는 플랫 색면이다. 그라데이션, 입체 음영, 사진 질감을 쓰지 않는다.
- **인물.** 작고 얼굴이 없다. 걷거나 앉아 있는 일상 자세다. 한 장에 1~3명.
- **소품 아이콘.** 음식 그릇, 찻잔, 책, 꽃, 쇼핑백처럼 그 자리에서 하는 일을 나타내는 것. 한 장에 4개 이하.
- **나무.** 두 가지 초록의 둥근 덩어리에 가는 먹색 줄기. 2~3그루씩 모아 둔다.
- **여백.** 캔버스의 35% 이상을 비운다.

## 레이아웃

### 썸네일

| 요소 | 위치와 크기 |
|---|---|
| 배경 | 단색 배경색을 전면에. 옅은 종이 알갱이 |
| 제목 블록 | 왼쪽 위. 좌우 여백 8%, 위 여백 10%. 부제는 가는 흰 글씨 한 줄, 그 아래 제목은 굵고 둥근 흰 고딕 |
| 실루엣 띠 | 캔버스 높이 45~60% 구간에 가로 전체. 여행지의 지형·지붕선을 밝은 크림 단색 실루엣으로 |
| 아래 패널 | 실루엣 띠와 이어진 밝은 크림 패널. 아래 40%. 모서리 둥글게, 좌우 여백 6% |
| 전경 소재 | 아래 패널에 걸친 플랫 일러스트 소재 하나. 캔버스 너비의 35% 이하. 왼쪽 아래 또는 오른쪽 아래 |

- 제목은 12자 이하, 부제는 20자 이하로 줄인다. 글 제목이 길면 여행지 이름만 제목으로 쓴다.
- 이미지 모델이 한글을 깨뜨리면 글자 없는 버전을 쓴다. 프롬프트의 `TEXT` 단락을 `No text. Keep the upper-left title area empty.`로 바꾸고 제목은 편집 도구에서 얹는다.

### 코스 약도

| 요소 | 위치와 크기 |
|---|---|
| 배경 | 크림 종이. 녹지는 연두 색면, 물은 하늘색 크레용 띠 |
| 길 | 회색 크레용 선. 큰길은 굵게, 골목은 가늘게 |
| 동선 | 구간마다 색 하나. 길 위에 덧그린 굵은 크레용 선. 3개 이하 |
| 장소 표시 | 먹색 가는 테두리의 작은 흰 원. 옆에 번호 |
| 장식 | 한쪽 가장자리에 잎 덩어리. 소품 아이콘과 인물은 빈 곳에 |
| 여백 | 상하좌우 6% |

- 그림에는 **번호만** 넣는다. 장소 이름은 넣지 않는다. 이름은 프롬프트와 함께 내는 한국어 범례에 적고, 글에서 약도 아래에 붙인다.
- 장소 표시는 한 장에 8개 이하. 넘으면 구간별로 약도를 나눈다.

### 장면 삽화

| 요소 | 위치와 크기 |
|---|---|
| 틀 | 모서리가 둥근 사각 틀. 먹색 가는 테두리 |
| 장면 | 틀 안에 플랫 일러스트 한 장면. 소재 1~3개 |
| 인물 | 뒷모습이나 옆모습. 얼굴 없음 |

- 캡션은 그림에 넣지 않는다. 글의 `사진삽입` 주석에 있는 캡션을 그대로 쓴다.
- 실제 가게 이름, 간판 글씨, 로고를 그리지 않는다.

## 작업 순서

1. **그릴 목록을 정한다.** 입력에서 썸네일·약도·장면 삽화 대상을 고른다.
2. **썸네일.** 배경색 하나, 실루엣으로 쓸 지형·지붕선, 전경 소재 하나, 제목과 부제를 정한다.
3. **약도.** 구간에 동선 색을 배정하고 장소에 번호를 매긴다. 범례를 만든다.
4. **프롬프트 조립.** 아래 템플릿의 `<...>`만 채운다. 스타일 문구는 고치지 않는다.
5. **출력.** 이미지마다 프롬프트 블록과 한국어 한 줄 설명을 낸다. 약도는 범례를 함께 낸다.

## 프롬프트 템플릿

모든 프롬프트는 공통 스타일 블록으로 끝난다. 공통 스타일 블록은 다음과 같다.

```text
STYLE: flat travel-guide illustration with crayon and oil-pastel texture. Roads and route lines
look hand-drawn with grainy, rough crayon edges. Objects and people are flat color shapes with
no outlines, no gradients, no 3D shading. People are tiny and faceless in calm everyday poses.
Trees are round two-tone green blobs (#7FB241, #3F6B2A) on thin dark trunks, grouped in twos
and threes. Warm, quiet, friendly mood. At least 35% of the canvas is empty space.

DO NOT: no photorealism, no photo textures, no real shop names, no signboard lettering, no
logos, no brand marks, no watermarks, no faces, no drop shadows, no glossy effects.
```

썸네일 템플릿은 다음과 같다.

```text
A travel blog thumbnail illustration, <1:1 square | 16:9 landscape>. Full-bleed solid muted
background in <background color name and hex> with subtle paper grain.

LAYOUT: a cream (#F7F1DC) flat silhouette band of <landform or roofline of the destination>
runs across the full width between 45% and 60% of the canvas height and merges into a cream
rounded panel filling the lower 40%, with 6% side margins. One flat illustrated foreground
object — <single object> — sits at the <lower-left | lower-right>, overlapping the panel,
no wider than 35% of the canvas.

TEXT: upper-left, 8% side margin and 10% top margin. A thin white subtitle line reading
"<부제>" and below it a heavy rounded white sans-serif title reading "<제목>". No other text.

<공통 스타일 블록>
```

코스 약도 템플릿은 다음과 같다.

```text
An illustrated walking course map, portrait 3:4, on a flat cream paper background (#FBF6E9)
with 6% margins on all sides.

ROADS: warm gray (#B9AEA6) crayon lines, thick for main roads and thin for alleys:
<road layout in plain words, e.g. "one main road running top to bottom with three alleys
branching to the left">. <green areas in pale green (#DDE8B5) / water as a light blue
(#A9CDE8) crayon band, only if present in the input>.

ROUTES: <1 to 3> bold crayon route lines drawn over the roads — <route 1 path> in leaf green
(#8CC63F), <route 2 path> in violet (#8E6BB0), <route 3 path> in orange (#F2A03D).

MARKERS: small white circles with a thin dark (#2B2B2B) outline, each with a small dark
number beside it: <number and position of each marker>. Numbers only, no place names.

DECORATION: a cluster of leafy foliage along the <edge> edge, <up to 4 small flat icons and
what they are>, and <1 to 3> tiny faceless people walking.

<공통 스타일 블록>
```

장면 삽화 템플릿은 다음과 같다.

```text
A flat travel illustration, landscape 4:3, inside a rounded-corner rectangular frame with a
thin dark (#2B2B2B) outline on a cream paper background (#FBF6E9).

SCENE: <one moment with 1 to 3 subjects; people seen from behind or in profile>.

No text anywhere in the image.

<공통 스타일 블록>
```

## 결과물 형식

이미지마다 다음을 낸다.

1. **영어 이미지 생성 프롬프트.** 공통 스타일 블록까지 붙여 넣은 완성본을 코드 펜스 하나에 담는다.
2. **한국어 한 줄 설명.** 어느 `사진삽입` 자리에 넣는 이미지인지, 배경색과 소재를 왜 골랐는지.
3. **범례.** 약도일 때만. 번호와 장소 이름의 한국어 목록.

마지막에 건너뛴 `[현장]` 주석 개수를 한 줄로 알린다.

## 예시 (gold reference)

입력 예는 다음과 같다. 여행지는 설명을 위해 만든 가상의 장소다.

```text
솔내항 언덕마을 여행 글. 버스 종점에서 등대길 계단을 올라 등대, 등대 옆 다방, 내려와서 어시장.
<!-- 사진삽입: [썸네일] 등대와 항구 | 캡션: 없음 -->
<!-- 사진삽입: [약도] 버스 종점에서 등대, 다방, 어시장까지 | 캡션: 없음 -->
<!-- 사진삽입: [현장] 파일: IMG_0420 등대와 그 아래 항구 | 캡션: 등대 앞에 서면 항구가 내려다보인다. -->
```

skill이 한 판단: 항구 마을이라 썸네일 배경은 바다 파랑으로 골랐다. 실루엣은 언덕 위 등대와 지붕선, 전경 소재는 찻잔 하나다. 제목은 여행지 이름으로 줄였다. 약도는 방향 정보가 없어 위에서 아래로 흐르는 한 줄로 단순화했고, 오르는 길과 내려오는 길에 동선 색을 하나씩 줬다. `[현장]` 1개는 건너뛰었다.

썸네일 출력 프롬프트는 다음과 같다.

```text
A travel blog thumbnail illustration, 1:1 square. Full-bleed solid muted background in sea
blue (#4F86A6) with subtle paper grain.

LAYOUT: a cream (#F7F1DC) flat silhouette band of a hillside village roofline with a small
lighthouse on the hilltop runs across the full width between 45% and 60% of the canvas height
and merges into a cream rounded panel filling the lower 40%, with 6% side margins. One flat
illustrated foreground object — a steaming teacup on a saucer — sits at the lower-right,
overlapping the panel, no wider than 35% of the canvas.

TEXT: upper-left, 8% side margin and 10% top margin. A thin white subtitle line reading
"계단 끝에 바다가 열리는" and below it a heavy rounded white sans-serif title reading
"솔내항 언덕마을". No other text.

STYLE: flat travel-guide illustration with crayon and oil-pastel texture. Roads and route lines
look hand-drawn with grainy, rough crayon edges. Objects and people are flat color shapes with
no outlines, no gradients, no 3D shading. People are tiny and faceless in calm everyday poses.
Trees are round two-tone green blobs (#7FB241, #3F6B2A) on thin dark trunks, grouped in twos
and threes. Warm, quiet, friendly mood. At least 35% of the canvas is empty space.

DO NOT: no photorealism, no photo textures, no real shop names, no signboard lettering, no
logos, no brand marks, no watermarks, no faces, no drop shadows, no glossy effects.
```

코스 약도 출력 프롬프트는 다음과 같다.

```text
An illustrated walking course map, portrait 3:4, on a flat cream paper background (#FBF6E9)
with 6% margins on all sides.

ROADS: warm gray (#B9AEA6) crayon lines, thick for main roads and thin for alleys: one thick
road along the bottom edge, and one thin winding alley climbing from the bottom-left up to
the top-right. Water as a light blue (#A9CDE8) crayon band along the right edge.

ROUTES: 2 bold crayon route lines drawn over the roads — the climb from the bottom-left to
the top-right in leaf green (#8CC63F), and the way back down along the right side to the
bottom road in orange (#F2A03D).

MARKERS: small white circles with a thin dark (#2B2B2B) outline, each with a small dark
number beside it: 1 at the bottom-left start, 2 at the top-right end of the green route,
3 just beside marker 2, 4 on the bottom road at the end of the orange route. Numbers only,
no place names.

DECORATION: a cluster of leafy foliage along the top-left edge, a small flat lighthouse icon
near marker 2, a teacup icon near marker 3, a fish icon near marker 4, and 2 tiny faceless
people walking up the alley.

STYLE: flat travel-guide illustration with crayon and oil-pastel texture. Roads and route lines
look hand-drawn with grainy, rough crayon edges. Objects and people are flat color shapes with
no outlines, no gradients, no 3D shading. People are tiny and faceless in calm everyday poses.
Trees are round two-tone green blobs (#7FB241, #3F6B2A) on thin dark trunks, grouped in twos
and threes. Warm, quiet, friendly mood. At least 35% of the canvas is empty space.

DO NOT: no photorealism, no photo textures, no real shop names, no signboard lettering, no
logos, no brand marks, no watermarks, no faces, no drop shadows, no glossy effects.
```

범례는 다음과 같다.

```text
1 버스 종점
2 등대
3 다방
4 어시장
```

한국어 한 줄 설명: 썸네일은 항구 마을이라 바다 파랑 배경에 등대 지붕선 실루엣과 찻잔을 뒀고, 약도는 방향 정보가 없어 오르는 길(초록)과 내려오는 길(주황) 두 동선으로 단순화했습니다. `[현장]` 주석 1개는 직접 찍은 사진 자리라 건너뛰었습니다.

## 완료 전 확인

- `[현장]` 주석을 건너뛰었고 그 개수를 알렸는가?
- 사진처럼 보이게 하는 문구(photo, realistic, DSLR)가 프롬프트에 없는가?
- 실제 가게 이름·간판·로고를 그리라고 쓰지 않았는가?
- 썸네일 배경색이 하나이고 전경 소재가 하나인가?
- 약도에 번호만 있고 장소 이름은 범례로 뺐는가? 동선 색이 3개 이하, 장소 표시가 8개 이하인가?
- 약도에 입력에 없는 길·장소를 넣지 않았는가? 단순화했다면 그 사실을 밝혔는가?
- 공통 스타일 블록을 고치지 않고 그대로 붙였는가?
- 프롬프트와 설명 어디에도 참고한 자료의 이름이나 장면이 없는가?
