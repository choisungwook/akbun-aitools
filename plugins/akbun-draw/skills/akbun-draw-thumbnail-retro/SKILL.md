---
name: akbun-draw-thumbnail-retro
disable-model-invocation: true
description: >
  IT 기술·여행 글이나 영상 대본을 읽고 유튜브(16:9)·티스토리(1:1) 썸네일을 레트로 필름 포스터
  스타일로 만드는 영어 이미지 생성 프롬프트를 작성한다. 70년대 필름 사진 한 장 위에 크림·버터색
  레트로 디스플레이 글자를 얹은 그림체를 고정하고, 핵심 키워드·비유 소재·구도는 글 내용으로 정한다.
  사진과 서체는 생성 모델이 새로 만들게 해 저작권을 피한다. Trigger on: "레트로 썸네일",
  "썸네일 프롬프트", "유튜브 썸네일 그려", "티스토리 썸네일", "retro thumbnail prompt".
---

# 레트로 필름 포스터 썸네일 프롬프트

글·영상 내용을 읽고 **썸네일의 구조를 정한 뒤 영어 이미지 생성 프롬프트**를 만든다. 이미지 생성은 사용자가 요청할 때만 한다. 고정하는 것은 그림체(필름 사진 + 큰 레트로 디스플레이 글자 + 작은 산세리프 글자)와 색 규칙이고, 무엇을 찍을지(비유 소재)와 어디에 둘지(구도)는 입력에 맞춰 고른다.

목표는 딱딱한 IT·여행 썸네일을 포스터처럼 보이게 하되, 목록에서 1초 안에 **무슨 글인지** 읽히게 하는 것이다. 예쁜데 주제를 모르면 실패다.

## 입력

- 블로그 글(markdown), 영상 대본·자막, 또는 둘 다. 둘 다 있으면 같은 구조 결정으로 두 비율을 만든다.
- 플랫폼을 말하지 않으면 유튜브 16:9와 티스토리 1:1을 둘 다 만든다. 티스토리 스킨이 가로 썸네일이면 16:9 하나로 둘 다 쓴다.
- 입력에 없는 사실(버전, 수치, 장소, 인물)을 썸네일 글자에 지어내지 않는다.

## 1단계: 구조 결정

프롬프트를 쓰기 전에 아래 6개를 정해 한국어 표로 출력한다.

1. **요지 한 문장.** 글이 독자에게 남기려는 결론. 예: "캐시가 동시에 만료되면 요청이 한꺼번에 DB로 몰린다."
2. **메인 글자(키워드).** 독자가 검색하거나 알아보는 이름 하나. 제품·기술·CVE 별칭·지명처럼 입력에 나온 고유명사를 우선한다. 라틴 문자 10자 이하(공백은 빼고 숫자·기호는 넣어 센다) 또는 한글 6음절 이하. 넘으면 더 짧은 이름을 고르고, 자르거나 줄여 새 약어를 만들지 않는다.
3. **비유 소재.** 요지의 **상태**를 보여 주는 1980년 이전의 손에 잡히는 물건 하나. 주제의 로고나 화면이 아니라 "무슨 일이 일어났는지"가 보이는 물건이다. 주제를 들으면 바로 떠오르는 상징(보안이면 자물쇠·금고·후드 쓴 해커, 클라우드면 구름)은 쓰지 않고, 요지의 원인이나 과정이 보이는 장면을 고른다. 검사: 메인 글자와 소재만 본 사람이 "무슨 일인지" 한마디로 짐작할 수 있는가. 여행은 그 장소를 대표하는 물건·풍경을 그 시절 휴가 스냅처럼 찍는다.
4. **구도.** 아래 구도 표에서 비율마다 하나. 같아도 되지만 16:9가 측면이면 1:1은 다른 구도를 고른다.
5. **서체.** 메인 글자에 쓸 레트로 디스플레이 글자 모양. 아래 서체 표는 예시이고 표에 없는 모양도 된다.
6. **색 쌍과 작은 글.** 색 쌍 표에서 하나, 작은 글은 0~2개(위 머리글, 아래 꼬리말), 서명 `by akbun`의 모서리.

아래 표는 "물건 + 그 물건의 상태"로 요지를 보여 주는 방식의 예시일 뿐 선택지가 아니다. 소재는 표에서 고르지 말고 글의 요지에서 직접 찾는다. 표에 있는 물건을 그대로 쓰면 글마다 같은 썸네일이 나온다. 표에서 가져갈 것은 형식(무엇이, 어떤 상태인지)뿐이다.

| 주제 | 예시 물건 | 예시 상태 |
|---|---|---|
| 보안 취약점·침입 | 자동판매기, 엘리베이터 버튼판, 호텔 프런트 열쇠함 | 엉뚱한 입력 하나로 기계가 통째로 열림, 열쇠가 전부 걸려 있지 않음 |
| 장애·메모리·과부하 | 압력솥, 넘치는 서류함, 퓨즈 상자 | 넘침, 김이 샘, 뚜껑이 들림 |
| 네트워크·요청 | 다이얼 전화기, 전화 교환대, 우체통 | 수화기가 내려진 채, 선이 엉킴, 편지가 쏟아짐 |
| 데이터·저장 | 카세트테이프, 서랍장, 필름 통 | 테이프가 풀림, 서랍이 모두 열림 |
| 배포·컨테이너 | 여행 가방, 나무 화물 상자, 기차표 | 짐이 꽉 참, 상자가 줄지어 쌓임 |
| 학습·입문 | 타자기, 교과서, 계산기 | 첫 장에 종이가 끼워짐 |
| 여행 | 장소의 탈것·건물 일부·음식·소품 | 그 장소에서만 보이는 순간 |

## 2단계: 스타일 규칙

### 사진

- 전체가 70년대 35mm 필름 사진 한 장이다. 따뜻하게 바랜 색, 들뜬 검정(lifted blacks), 부드러운 대비, 하이라이트의 약한 번짐.
- 주인공은 비유 소재 하나. 풍경이면 가장 큰 구조물(계단, 건물 벽 등)이 주인공이고, 그림자와 배경은 세지 않는다. 상태를 만드는 원인 요소(걸린 카드, 쏟아진 봉투)는 썸네일을 폭 200px로 줄여도 보이도록 외곽 상자 높이를 주인공 외곽 상자 높이의 15% 이상으로 키운다. 반복 구도는 물건 무리 전체를 감싼 상자를 주인공 상자로 센다. 주인공 외곽 상자의 높이가 캔버스 높이의 40~75%(경계 포함)다. 프레임 밖으로 잘리는 부분은 주인공 높이의 40% 이하다.
- 사람은 필요할 때만, 얼굴 없이 손·다리·뒷모습 일부로 둔다.
- 글자 뒤에 들어갈 자리는 하늘·벽·흐린 배경처럼 디테일이 적은 중간~어두운 톤이어야 한다. 밝은 글자가 그 위에서 읽힌다.

### 색 쌍

배경색과 주인공 색이 서로 대비되는 쌍을 하나 고른다. 나머지 색은 모두 탁하고 바래게 둔다. 색은 주제가 아니라 **비유 소재가 놓인 장소와 빛**으로 고른다. 주제의 뻔한 색(보안은 어둡고 빨갛게, 클라우드는 파랗게)을 따르면 딱딱한 썸네일로 돌아간다. 글자색은 표의 값을 쓴다.

| 색 쌍 | 배경 | 주인공 | 글자 | 장소와 빛 |
|---|---|---|---|---|
| sky-vermilion | 하늘 파랑 `#5B86B5` | 주홍 `#D9542B` | 버터 `#FCE38A` | 맑은 날 야외, 하늘이 배경 |
| sage-tomato | 세이지 청록 `#6E9A8B` | 토마토 `#E0572A` | 크림 `#FFF3D6` | 낮의 실내, 타일·벽이 배경 |
| dusk-neon | 저녁 보라 `#5C5A8A` | 네온 분홍 `#F06BA8` | 크림 `#FFF3D6` | 해 질 녘이나 밤의 야외 조명 |
| night-mustard | 짙은 갈색 `#2A1E17` | 머스터드 `#E3A92B` | 크림 `#FFF3D6` | 밤의 실내, 전구 하나 |
| slate-brick | 흐린 청회색 `#55708C` | 벽돌 빨강 `#B23A2E` | 버터 `#FCE38A` | 흐린 날 야외, 바닷가·거리 |

### 구도

| 구도 | 배치 | 고르는 경우 |
|---|---|---|
| 중앙 띠 | 메인 글자가 화면 가운데를 가로지르고 주인공은 뒤나 아래 | 키워드 하나가 강할 때 |
| 위 제목 | 글자가 모두 위 45% 안, 주인공이 아래에서 올라옴 | 주인공이 세로로 긴 물건일 때 |
| 반복 | 같은 물건 여러 개가 평면 위에 비스듬히 줄지어 놓인 부감, 메인 글자는 가운데의 빈 바닥 위 | 많음·규모·여러 개가 요지일 때 |
| 측면 (16:9 전용) | 메인 글자를 왼쪽에 쌓고 주인공은 오른쪽 | 주인공 디테일을 가리면 안 될 때 |

메인 글자가 주인공과 겹쳐도 되지만 겹친 면적은 메인 글자 잉크 면적의 25% 이하이고, 겹친 곳에서도 글자가 끊기지 않고 읽혀야 한다.

### 서체

서체의 제약은 저작권 하나다. 프롬프트에 기존 서체 이름·디자이너·파운드리를 쓰지 않고 글자 모양으로만 묘사하며, "original custom lettering, not any existing typeface"를 붙인다. 그 밖에는 메인 글자와 글의 분위기에 맞춰 자유롭게 정한다. 아래 표는 레트로 디스플레이 글자를 묘사하는 말의 예시다.

| 예시 | 글자 모양(프롬프트에 쓸 말) |
|---|---|
| condensed | tall narrow hand-cut letters, vertical strokes slightly wobble |
| blade | wide heavy sans with sharp wedge-shaped cuts carved into the strokes |
| bubble | ultra-bold rounded sans, tiny counters, plump and soft corners |
| swash-serif | bouncy serif with curled swash terminals, letters slightly vary in height |
| groovy | 70s psychedelic display letters, stroke weight flows softly, swollen rounded terminals, legs of R and G curl like waves |

### 글자 크기와 위치

세는 법: 모든 값은 캔버스 높이 또는 너비에 대한 비율이고, 범위는 양 끝을 포함하고, 측정값은 소수 첫째 자리에서 반올림해 비교한다. 글자 높이는 메인 글자에서 가장 큰 라틴 대문자의 높이 또는 한글 음절 높이다. 너비는 메인 글자 덩어리의 가장 왼쪽 잉크부터 가장 오른쪽 잉크까지다. 글자 사이 간격은 위 요소 잉크의 아래 끝부터 아래 요소 잉크의 위 끝까지를 캔버스 높이로 나눈 값이다.

| 요소 | 16:9 | 1:1 |
|---|---|---|
| 메인 글자 높이 | 18~28% | 12~22% |
| 메인 글자 너비 | 중앙 띠·위 제목·반복 70~85%, 측면 40~50% | 75~90% |
| 작은 글 높이 | 4~6% | 4~6% |
| 안전 여백(모든 글자) | 각 변에서 6% 이상. 이미지 모델이 글자를 가장자리로 붙이는 경향이 있어 프롬프트에는 10%로 쓴다 | 같음 |

- 너비 범위가 먼저다. 너비를 지키면 높이가 정해진다. 글자 수가 많아 높이가 범위 아래로 떨어지면 더 좁은 글자 모양으로 바꾸고, 글자 수가 적어 높이가 범위 위로 넘치면 높이를 상한에 맞추고 너비를 범위보다 좁게 둔다. 측면 구도는 메인 글자가 6자 이하이거나 두 줄일 때만 쓴다.
- 메인 글자는 한 줄. 두 단어이고 각 7자 이하일 때만 두 줄로 쌓고, 줄 간격은 글자 높이의 8% 이하로 좁힌다. 16:9 위 제목 구도는 위 45%에 두 줄이 들어가지 않으므로 한 줄만 쓴다.
- 머리글은 메인 글자 바로 위 간격 3~5%, 꼬리말은 바로 아래 간격 3% 이하. 정렬은 메인 글자의 가운데·왼쪽 끝·오른쪽 끝 중 주인공을 가리지 않는 쪽으로 고른다. 위 제목 구도에서는 글자 3개가 모두 위 45% 안에 든다. 작은 글은 깔끔한 기하학 산세리프다.
- 작은 글은 맥락을 더하고, 없어도 된다. 머리글은 분류 이름(라틴 대문자), 꼬리말은 한국어 한 줄 훅 12자 이하(공백 포함) 또는 본문에 나온 버전·사건 날짜. 문서 메타데이터(front matter)의 작성일은 쓰지 않는다. 메인 글자를 반복하지 않는다.
- 모든 글자는 한 색이다. 외곽선·그림자·광택·입체 효과를 쓰지 않는다. 필름 입자와 먼지가 글자 위에도 덮여 사진에 인쇄된 것처럼 보이게 한다.
- 유튜브 16:9는 오른쪽 아래(너비 22%, 높이 15%)에 영상 길이 표시가 덮이므로 글자와 주인공을 두지 않는다.
- 글자 요소는 메인 글자 포함 최대 3개다. 아래 서명은 세지 않는다.
- 모든 썸네일에 akbun이 만든 사진이라는 서명 `by akbun`을 작게 넣는다. 소문자 산세리프, 글자 높이 2.5~3.5%, 다른 글자와 같은 색. 자리는 왼쪽 위·오른쪽 위·왼쪽 아래 모서리 중 메인 글자와 주인공에서 먼 곳이고, 다른 글자처럼 각 변 6% 여백을 지킨다. 16:9는 오른쪽 아래(영상 길이 표시 자리)에 두지 않고, 1:1은 오른쪽 아래도 된다.

## 저작권

- **사진**은 생성 모델이 새로 만든다. 프롬프트에 사진가·영화·감독·미술 작품·유명인 이름, 유명한 사진·영화 장면 묘사를 쓰지 않는다. 물건에 실제 상표·로고·간판을 넣지 않고 "unbranded"로 쓴다. 실제 제품 모양이 뚜렷한 탈것·기기는 "generic 1970s ..."로 쓴다.
- **서체**는 위 서체 절대로 모양만 묘사한다.
- 이미지 안 글자에 한글이 있거나 사용자가 글자를 나중에 고치려면, 비율마다 무문자 프롬프트(아래 템플릿 절)도 함께 낸다. 생성된 한글이 깨지면 무문자 이미지를 쓰고 글자는 SIL OFL 서체로 따로 얹는다. 서체는 가로세로 비율을 바꾸지 않고 크기만 조절하며, 사진과 같은 필름 입자를 글자 위에도 입혀 붙인 티가 나지 않게 한다. 얹는 서체는 SIL OFL처럼 상업적 사용이 허락된 것이면 무엇이든 된다(예: 메인 글자 Bagel Fat One·Black Han Sans·Gasoek One, 작은 글 Pretendard·Noto Sans KR). 서체 파일은 Google Fonts나 서체 공식 저장소에서 받는다.

## 프롬프트 템플릿

`<...>`만 채우고 나머지 문장은 그대로 둔다. `<16:9 only: ...>`는 16:9에서 안내어를 지우고 문장만 남기며, 1:1에서는 통째로 지운다. 플랫폼마다 한 개씩 만든다. 16:9를 잘라 1:1로 쓰지 않는다. 비율마다 글자 크기와 구도가 다르다.

```text
A retro film-poster style thumbnail, <16:9 landscape | 1:1 square>. The whole image is a single
1970s 35mm film photograph with bold display lettering printed over it.

PHOTO: <hero object and its state, setting, camera angle, how much is cropped>. The background
is <background color name and hex>, the hero is <hero color name and hex>; every other color
is muted and faded. Warm faded film color, lifted blacks, soft contrast, slight halation on
highlights. <people only as faceless partial figures, or "No people.">

LAYOUT: <composition, positions of the text block and the hero>. The text sits over
<low-detail zone>, a mid-to-dark tone so the light lettering reads clearly. Keep at least 10% empty margin between all text and every edge.
<16:9 only: Keep the bottom-right corner, 22% of the width and 15% of the height, free of text
and of the hero.>

DISPLAY WORD: "<keyword>" in <letterform traits from the type table>, original custom lettering,
not any existing typeface. Letter height <n>% of the image height, spanning <n>% of the image
width, <one line | two tightly stacked lines>. Color <cream #FFF3D6 | butter yellow #FCE38A>.
SMALL TEXT: <"<kicker>" directly above the display word, centered | left-aligned> <and "<label>"
directly below, aligned to the right edge of the display word>, clean geometric sans-serif,
letter height 5% of the image height, same color as the display word.
SIGNATURE: "by akbun" as a tiny signature in the <top-left | top-right | bottom-left | 1:1 only:
bottom-right> corner, lowercase clean sans-serif, letter height 3% of the image height, same
color as the display word. Spell every word exactly as given. No other text.

FINISH: fine film grain, a few dust specks and hairline scratches over the entire image,
including the lettering, so the text looks printed into the photo. Flat lettering with no
outline, no drop shadow, no glow and no 3D effect.

DO NOT: no logos, brand names or trademarks on any object, no real signage, no watermarks,
no recognizable real people or celebrities, no recreation of film stills or famous photographs,
no extra text, no UI elements, no borders or frames.
```

작은 글이 없으면 `SMALL TEXT` 단락을 지우고 `SIGNATURE`는 그대로 둔다. 작은 글이 하나면 해당 자리만 남긴다.

무문자 프롬프트는 비율마다 하나씩 만든다. 첫 문장의 `with bold display lettering printed over it`을 `with empty space reserved for lettering`으로, `DISPLAY WORD`·`SMALL TEXT`·`SIGNATURE` 세 단락을 아래 한 단락으로 바꾸고(서명도 나중에 얹는다), `LAYOUT`의 `The text sits over ... reads clearly.`와 여백 문장은 지운다. 글자 자리는 `TEXT` 단락이 비워 둔다. `FINISH`의 lettering 언급은 지우고, `DO NOT`의 `no extra text`는 `no text`로 바꾼다.

```text
TEXT: No letters, numbers or symbols anywhere. Leave <low-detail zone> empty for lettering
that will be added later.
```

## 예시 (gold reference)

입력은 "Redis 키 만료가 한꺼번에 몰려 DB가 요청에 깔리는 cache stampede와 대응법" 글이고 플랫폼은 유튜브다.

| 항목 | 결정 |
|---|---|
| 요지 | 캐시가 동시에 만료되면 요청이 한꺼번에 DB로 몰린다 |
| 메인 글자 | `REDIS` |
| 비유 소재 | 번호표 발급기에서 번호표가 끝없이 쏟아져 바닥에 쌓임. 요청이 한 창구로 몰리는 상태 |
| 구도 | 위 제목. 발급기가 세로로 길어 아래에서 올라오게 둠 |
| 서체 | groovy 예시의 모양 |
| 색 쌍·작은 글 | sage-tomato, 머리글 `CACHE STAMPEDE`, 꼬리말 `만료가 몰릴 때`, 서명 오른쪽 위 |

위 결정으로 채운 완성 16:9 프롬프트다.

```text
A retro film-poster style thumbnail, 16:9 landscape. The whole image is a single
1970s 35mm film photograph with bold display lettering printed over it.

PHOTO: a tomato-red unbranded 1970s ticket dispenser on a short pole stands at the lower
center-left, seen slightly from below; a long ribbon of paper number tickets pours out of
its slot and piles up in loose curls on a tiled floor. The dispenser is cut off by the bottom
edge. The background is a plain sage-teal tiled wall (#6E9A8B), the hero is tomato red
(#E0572A); every other color is muted and faded. Warm faded film color, lifted blacks, soft
contrast, slight halation on highlights. No people.

LAYOUT: top title. The kicker, the display word and the label fill the upper 45% of the frame,
and the dispenser rises from the bottom with its top just below the label. The text sits over
the plain tiled wall, a mid-to-dark tone so the light lettering reads clearly. Keep at least
10% empty margin between all text and every edge. Keep the bottom-right corner, 22% of the
width and 15% of the height, free of text and of the hero.

DISPLAY WORD: "REDIS" in 70s psychedelic display letters, stroke weight flows softly, swollen
rounded terminals, legs of R and G curl like waves, original custom lettering, not any existing typeface. Letter height 24% of the image height,
spanning 72% of the image width, one line. Color cream #FFF3D6.
SMALL TEXT: "CACHE STAMPEDE" directly above the display word, centered, and "만료가 몰릴 때"
directly below, aligned to the right edge of the display word, clean geometric sans-serif,
letter height 5% of the image height, same color as the display word.
SIGNATURE: "by akbun" as a tiny signature in the top-right corner, lowercase clean sans-serif,
letter height 3% of the image height, same color as the display word. Spell every word exactly
as given. No other text.

FINISH: fine film grain, a few dust specks and hairline scratches over the entire image,
including the lettering, so the text looks printed into the photo. Flat lettering with no
outline, no drop shadow, no glow and no 3D effect.

DO NOT: no logos, brand names or trademarks on any object, no real signage, no watermarks,
no recognizable real people or celebrities, no recreation of film stills or famous photographs,
no extra text, no UI elements, no borders or frames.
```

꼬리말이 한글이므로 결과물에는 무문자 프롬프트(첫 문장·`LAYOUT`·`FINISH`·`DO NOT`을 위 규칙대로 바꾸고 `TEXT: ... Leave the plain tiled wall above the dispenser empty ...`)와 OFL 조판 지시(`REDIS` Bagel Fat One, `CACHE STAMPEDE`·`만료가 몰릴 때` Pretendard, `by akbun` Pretendard, 위치는 위 프롬프트와 같음)도 함께 낸다.

## 결과물

1. 1단계 구조 결정 표(한국어).
2. 플랫폼마다 완성 영어 프롬프트 한 개씩, 각각 `text` 코드 블록.
3. 이미지 안 글자에 한글이 있으면 비율마다 무문자 프롬프트 하나와 OFL 서체로 얹을 글자·위치를 함께 적는다.
4. 이미지를 생성하지 않았으면 `프롬프트 작성까지만 완료`로 보고한다. 생성했다면 결과를 두 단계로 확인한다. 이미지 모델은 글자 크기 수치를 정확히 따르지 않으므로 글자 높이·너비는 프롬프트의 목표값이고, 벗어나면 측정값만 보고한다. 반면 철자 오류, 각 변 6% 여백 침범, 유튜브 오른쪽 아래 영역 침범, 폭 200px에서 메인 글자나 원인 요소가 안 보이는 경우는 실패이므로 같은 프롬프트에 그 항목을 강조해 다시 생성한다.

## 완료 전 확인

- 메인 글자가 입력에 나온 이름이고 라틴 10자·한글 6음절 이하인가?
- 비유 소재가 주제의 로고가 아니라 요지의 상태를 보여 주는가? 글자와 소재만으로 무슨 일인지 짐작되는가?
- 비유 소재가 주제의 뻔한 상징(자물쇠·금고·구름 등)이 아니고, 색 쌍이 주제가 아니라 소재가 놓인 장소의 빛으로 골라졌는가?
- 글자 크기·너비·여백·유튜브 오른쪽 아래 비움이 표의 범위 안인가? 글자 요소가 3개 이하인가? `by akbun` 서명이 허용된 모서리에 있는가?
- 프롬프트에 서체 이름, 사진가·영화·유명인 이름, 상표가 없는가?
- 비율마다 따로 프롬프트를 만들었는가? 한글 글자가 있으면 무문자 프롬프트도 냈는가?
- 생성한 결과가 알려진 영화 장면·포스터·사진과 닮지 않았는가? 닮았으면 비유 소재나 구도를 바꿔 다시 만든다.
