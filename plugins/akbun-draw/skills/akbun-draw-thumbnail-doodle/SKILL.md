---
name: akbun-draw-thumbnail-doodle
disable-model-invocation: true
description: >
  블로그·유튜브 썸네일을 흰 종이 펜 낙서(doodle) 그림체 한 장으로 그리는 영어 이미지 생성 프롬프트를
  만든다. 기본 산출물은 16:9(1920x1080)와 4:3(1440x1080) 프롬프트이고, 사용자가 생성 모델(codex 등)로
  만들라고 할 때만 이미지를 생성해 ~/Downloads에 저장한다. 그림체·색은 akbun-draw-motion-doodle을
  따르고 구도·캐릭터·소재는 글 내용으로 정한다. Trigger on: "낙서 썸네일", "doodle 썸네일",
  "블로그 썸네일 프롬프트", "유튜브 썸네일 낙서".
---

# 낙서 썸네일 프롬프트

글 제목과 내용을 읽고 **썸네일 한 장의 구조를 정한 뒤 영어 이미지 생성 프롬프트**를 만든다. 고정하는 것은 그림체(흰 종이 위 검정 마커 낙서 + 주황 강조색 하나 + 손글씨 제목)이고, 무엇을 그릴지(캐릭터·소재)와 어디에 둘지(구도)는 입력에 맞춰 고른다.

목표는 목록에서 1초 안에 **무슨 글인지** 읽히는 것이다. 귀여운데 주제를 모르면 실패다.

## 두 가지 동작

| 동작 | 언제 | 결과 |
|---|---|---|
| 프롬프트 모드(기본) | 항상. 사용자가 생성 모델을 말하지 않았을 때 | 구조 결정 표 + 비율마다 영어 프롬프트. 저장 위치 없음 |
| 생성 모드 | 사용자가 "codex로 생성해", "이미지로 만들어"처럼 생성 모델로 호출하라고 했을 때만 | 프롬프트로 이미지를 만들어 `$HOME/Downloads`에 저장 |

- "그려줘"만으로는 생성 모드가 아니다. 생성 모델이나 이미지 파일을 요청한 말이 있을 때만 생성한다.
- 사용자가 모델을 지정하면 그 모델로만 생성한다. 모델을 지정하지 않았거나 codex를 말했을 때만 codex CLI(`command -v codex`로 확인)로 생성한다. 지정한 모델을 이 환경에서 호출할 수단이 없으면 다른 모델로 바꾸지 않고, 프롬프트 모드 결과와 그 이유 한 줄을 준다.

## 입력

- 제목(필수), 내용(글 핵심 한두 줄 또는 md 파일 경로). md 경로를 주면 파일을 읽고 요지를 뽑는다.
- 비율을 말하지 않으면 16:9(1920x1080)와 4:3(1440x1080) 두 장을 만든다. 사용자가 비율을 지정하면 그것만 만든다.
- 입력에 없는 사실(버전, 수치, 제품명)을 그림 속 글자에 지어내지 않는다.

## 1단계: 구조 결정

프롬프트를 쓰기 전에 아래 5개를 정해 한국어 표로 출력한다.

1. **요지 한 문장.** 글이 독자에게 남기려는 결론.
2. **제목 글자.** 사용자가 준 제목을 그대로 쓴다. 글자 수는 공백을 포함해 센다. 14자를 넘으면 두 줄로 나누고, 첫 줄은 14자 이하가 되는 마지막 단어 경계까지 채운다. 두 줄로도 줄마다 14자를 넘으면 제목에서 검색어가 되는 부분만 제목 글자로 쓰고, 고른 부분을 표에 적는다. 단어를 새로 만들거나 약어로 줄이지 않는다.
3. **캐릭터·소재.** 요지의 **상태**를 보여 주는 장면. 주제 대상(서버, 파일, 요청 등)을 도형 캐릭터로 만들고 무슨 일이 일어나는지를 표정과 소품으로 보인다. 캐릭터마다 [akbun-draw-motion-doodle](../akbun-draw-motion-doodle/SKILL.md)의 캐릭터 설계 규칙 표에서 머리·몸통, ACCENT 위치, 성격 소품 칸을 하나씩 골라 표에 적는다. 캐릭터가 둘이면 세 열 중 두 열 이상을 다르게 고른다. 사용자가 기존 캐릭터(예: [akbun-mascot-whale](../akbun-mascot-whale/SKILL.md))를 지정하면 그 스펙을 따른다. 검사: 제목과 그림만 본 사람이 "무슨 일인지" 한마디로 짐작할 수 있는가.
4. **구도.** 아래 구도 표에서 비율마다 하나. 좌우 구도는 제목이 줄마다 7자 이하일 때만 고른다. 4:3은 16:9와 같아도 되지만 16:9가 좌우 구도면 4:3은 위아래 구도를 우선 검토한다.
5. **강조 단어.** 제목에서 주황으로 칠할 단어 하나, 또는 없음.

### 구도

| 구도 | 배치 | 고르는 경우 |
|---|---|---|
| 좌우 | 제목을 왼쪽 절반에 쌓고 캐릭터 묶음은 오른쪽 | 제목이 줄마다 7자 이하이고 캐릭터 하나가 상태를 다 보여 줄 때 |
| 위아래 | 제목이 위 35% 안, 캐릭터 묶음이 아래 | 장면이 가로로 넓을 때 |
| 크기 대비 | 큰 대상(작은 쪽 키의 2배 이상)과 작은 캐릭터, 제목은 남은 빈 곳 | 양·힘·부담의 차이가 요지일 때 |
| 대화 | 두 캐릭터 좌우, 한쪽 머리 옆에 말풍선 하나(대사 공백 포함 8자 이하), 제목은 위 | 질문·오해·비교가 요지일 때 |

## 2단계: 스타일 규칙

그림체·선·색·음영·표정의 원본은 [akbun-draw-motion-doodle](../akbun-draw-motion-doodle/SKILL.md)의 `## 스타일`이다. 아래 템플릿은 그 규칙을 이미지 모델이 따를 영어 문장으로 옮긴 것이므로 템플릿 문장을 고치지 않는다.

- 색은 PAPER `#FEFEFE`, INK `#000000`, SHADE `#E0E0E0`, ARROW `#B0B0B0`, ACCENT `#E89850`, ACCENT_SHADE `#E05018`만 쓴다. ACCENT는 1단계에서 고른 ACCENT 위치 칸과 강조 단어에만 쓴다. 두 번째 대상을 색으로 구분해야 할 때만 ACCENT2 `#7CD0FC`를 하나 더한다.
- 화면 면적의 85% 이상은 흰 종이다. 배경 풍경·바닥선·테두리·액자를 그리지 않는다.
- 제목은 손글씨 느낌의 둥근 마커 글씨이고, 글자마다 기울기와 높이가 조금씩 다르다. 기존 서체 이름을 프롬프트에 쓰지 않는다.
- 실제 제품 로고·상표·아이콘 모양을 그리지 않는다. 주제가 특정 제품이어도 도형 캐릭터로만 표현한다.

### 글자 크기와 위치

세는 법: 값은 캔버스 높이에 대한 비율이고 범위는 양 끝을 포함한다. 글자 높이는 한글 음절 또는 라틴 대문자의 높이다.

| 요소 | 16:9 | 4:3 |
|---|---|---|
| 제목 글자 높이 | 11~16% | 9~13% |
| 제목 묶음 너비(캔버스 너비 대비) | 좌우 구도 35~48%, 그 밖 60~80% | 65~85% |
| 안전 여백(모든 글자·캐릭터) | 각 변에서 6% 이상. 모델이 가장자리로 붙이는 경향이 있어 프롬프트에는 8%로 쓴다 | 같음 |

- 유튜브용 16:9는 오른쪽 아래(너비 22%, 높이 15%)에 영상 길이 표시가 덮이므로 글자와 캐릭터 얼굴을 두지 않는다.
- 그림 속 글자는 제목, 말풍선 대사 하나(대화 구도만)까지다. 부제·서명·날짜는 넣지 않는다.

## 프롬프트 템플릿

`<...>`만 채우고 나머지 문장은 그대로 둔다. `<16:9 only: ...>`는 16:9에서 안내어를 지우고 문장만 남기며, 4:3에서는 통째로 지운다. 비율마다 한 개씩 만든다. 16:9를 잘라 4:3으로 쓰지 않는다.

```text
A blog thumbnail in a hand-drawn doodle style, <16:9 landscape, 1920x1080 | 4:3 landscape, 1440x1080>.
Plain flat white paper background (#FEFEFE), no texture, no background scenery, no ground line,
no border or frame. At least 85% of the image is empty white paper.

DRAWING STYLE: thick black marker lines (#000000), drawn in one confident stroke, slightly wobbly,
round line caps; no perfectly straight lines or exact right angles. Shapes are a few simple forms
(circles, rounded boxes, drops, sticks) with no fine details like fingers, hair or clothing folds.
Flat fills only: white bodies, one crescent of flat light gray (#E0E0E0) shade on one side of
round shapes. A single accent color, orange (#E89850) with darker orange shade (#E05018), used only
on <where the accent goes>. <optional: one second object in flat sky blue #7CD0FC.> No gradients,
no 3D, no glow, no photographic texture.

SCENE: <characters and props, what state they show, expressions made only with dot eyes and a
single-line mouth, limbs as single thick lines touching what they hold>. Small flat gray (#B0B0B0)
oval shadows under standing characters.

LAYOUT: <composition and where the title and the character group sit>. Keep at least 8% empty
margin between every element and every edge, and at least 5% of the image height between the title
and the drawing. <16:9 only: Keep the bottom-right corner, 22% of the width and 15% of the height, free of
text and of character faces.>

TITLE: "<title line 1>"<, second line "<title line 2>">, hand-lettered with a round black marker,
each letter slightly varied in tilt and height, original handwriting, not any existing typeface.
Letter height <n>% of the image height. <The word "<accent word>" is in orange #E89850; the rest
is black. | All letters are black.> No outline, no shadow, no box behind the letters.
<dialogue only: One white speech bubble with a hand-drawn rounded outline near <character>'s head,
containing "<line>".> Spell every word exactly as given. No other text.

DO NOT: no logos, brand names or product icons, no extra text, no watermark, no UI elements,
no realistic rendering, <no colors other than orange and gray | no colors other than orange, sky blue
and gray>.
```

강조 단어, 하늘색 대상(`<optional: ...>`), 말풍선이 없으면 해당 `<...>` 문장을 통째로 지운다. `DO NOT`의 마지막 갈래는 하늘색을 썼는지에 따라 하나만 남긴다.

## 생성 모드

사용자가 생성을 요청했을 때만 한다. 비율마다 아래 순서로 돌린다.

1. 저장 이름을 정한다. `$HOME/Downloads/thumbnail-<slug>-<ratio>.png`이고 `<ratio>`는 `16x9` 또는 `4x3`이다. `<slug>`는 제목 글자의 라틴 단어를 소문자·하이픈으로 잇고, 라틴 단어가 없으면 `YYYYMMDD-HHMM`이다. 같은 이름이 있으면 끝에 `-2`, `-3`을 붙이고 덮어쓰지 않는다.
2. 작업 폴더 `WORK`를 임시 폴더(세션 scratchpad 아래 새 폴더 등)로 만들고 완성 프롬프트를 `$WORK/prompt-<ratio>.txt`로 저장한 뒤 codex를 부른다. 한 장에 30~60초 걸리고, 두 비율은 동시에 돌려도 된다.

프롬프트 파일을 codex 이미지 생성 도구에 넘기고 결과 PNG를 작업 폴더에 받는 명령이다. `<ratio>`를 채워 쓴다.

```bash
codex exec --skip-git-repo-check -s workspace-write -C "$WORK" -o "$WORK/last-<ratio>.txt" \
  "Use your image generation tool to create exactly one image from the prompt in prompt-<ratio>.txt. Save the final PNG in the current directory as out-<ratio>.png. Reply only with the saved file path." < /dev/null
```

`< /dev/null`을 빼면 codex가 stdin 입력을 기다리며 멈춘다(백그라운드·병렬 실행에서 실측).

3. 결과 크기를 목표 크기로 맞춘다. 모델은 정확한 픽셀을 지키지 않는다(실측: 16:9 요청에 1672x941). 비율이 0.5% 이상 다르면 가운데를 기준으로 목표 비율만큼 먼저 자르고(`sips -c <h> <w>`), 그다음 목표 크기로 늘이거나 줄인다(`sips -z <높이> <너비>`). `sips -z`는 높이가 먼저다.
4. 맞춘 파일을 1번의 이름으로 `$HOME/Downloads`에 복사하고 `sips -g pixelWidth -g pixelHeight`로 크기를 확인한다.
5. 결과를 한 번 보고 아래 실패 항목이 있으면 그 항목을 프롬프트 맨 앞에 한 문장으로 강조해 한 번 다시 만든다. 다시 만들어도 실패면 그 상태로 저장하고 무엇이 틀렸는지 보고한다.
   - 제목 철자가 틀리거나 한글이 깨짐
   - 글자·캐릭터가 각 변 6% 여백을 침범함
   - 16:9 오른쪽 아래 영역에 글자나 얼굴이 있음
   - 주황 외의 강조색이 더 있거나 배경에 풍경·질감이 있음

## 예시 (gold reference)

입력은 제목 "파드가 OOMKilled 되는 이유", 내용 "컨테이너가 memory limit을 넘으면 커널이 프로세스를 죽인다"이고 비율 지정은 없다.

| 항목 | 결정 |
|---|---|
| 요지 | 메모리 limit을 넘는 순간 컨테이너는 강제로 죽는다 |
| 제목 글자 | 공백 포함 19자라 두 줄: `파드가 OOMKilled` / `되는 이유` |
| 캐릭터·소재 | 파드 캐릭터가 자기 몸보다 큰 짐 더미를 껴안고 버팀. 위에 눈금 막대가 끝까지 차 있음. 표에서 고른 칸: 사람이 아닌 대상의 도형(둥근 상자) / 뚜껑 / 머리 위 땀방울 하나 |
| 구도 | 첫 줄이 13자라 좌우 구도를 쓸 수 없음. 16:9·4:3 모두 위아래 |
| 강조 단어 | `OOMKilled` |

위 결정으로 채운 완성 16:9 프롬프트다.

```text
A blog thumbnail in a hand-drawn doodle style, 16:9 landscape, 1920x1080.
Plain flat white paper background (#FEFEFE), no texture, no background scenery, no ground line,
no border or frame. At least 85% of the image is empty white paper.

DRAWING STYLE: thick black marker lines (#000000), drawn in one confident stroke, slightly wobbly,
round line caps; no perfectly straight lines or exact right angles. Shapes are a few simple forms
(circles, rounded boxes, drops, sticks) with no fine details like fingers, hair or clothing folds.
Flat fills only: white bodies, one crescent of flat light gray (#E0E0E0) shade on one side of
round shapes. A single accent color, orange (#E89850) with darker orange shade (#E05018), used only
on the character's lid and the word OOMKilled. No gradients, no 3D, no glow, no
photographic texture.

SCENE: a rounded-box character with two dot eyes and a wavy single-line mouth hugs a wobbly pile of
white boxes taller than itself; one sweat drop floats above its head. Above it, a horizontal gauge
bar drawn as a rounded outline is filled to the very end with flat gray, its last tick bent outward.
Its two stick arms wrap around the pile and touch it. A small flat gray (#B0B0B0) oval shadow lies
under the character.

LAYOUT: top and bottom. The two title lines sit within the upper 35% of the frame, centered; the
character, the pile and the gauge stand below it, centered. Keep at least 8% empty margin between
every element and every edge, and at least 5% of the image height between the title and the
drawing. Keep the bottom-right corner, 22% of the width and 15% of the height, free of text and of
character faces.

TITLE: "파드가 OOMKilled", second line "되는 이유", hand-lettered with a round black marker,
each letter slightly varied in tilt and height, original handwriting, not any existing typeface.
Letter height 13% of the image height. The word "OOMKilled" is in orange #E89850; the rest
is black. No outline, no shadow, no box behind the letters. Spell every word exactly as given.
No other text.

DO NOT: no logos, brand names or product icons, no extra text, no watermark, no UI elements,
no realistic rendering, no colors other than orange and gray.
```

4:3은 같은 결정에서 첫 줄을 `4:3 landscape, 1440x1080`으로, 글자 높이를 11%로 바꾸고 오른쪽 아래 문장을 지운다.

## 결과물

1. 1단계 구조 결정 표(한국어).
2. 비율마다 완성 영어 프롬프트 한 개씩, 각각 `text` 코드 블록.
3. 프롬프트 모드면 `프롬프트 작성까지만 완료`로 끝낸다. 생성 모드면 저장한 파일 경로와 실측 크기, 다시 만든 항목이 있으면 그 이유를 보고한다.

## 완료 전 확인

- 제목 글자가 사용자 제목 그대로이거나 표에 적은 고른 부분이고, 줄마다 14자 이하인가? 좌우 구도면 줄마다 7자 이하인가?
- 그림이 주제의 로고가 아니라 요지의 상태를 보여 주는가? 제목과 그림만으로 무슨 일인지 짐작되는가?
- 템플릿의 스타일 문장을 고치지 않았는가? 강조색이 주황 하나(필요 시 하늘색 하나 추가)인가?
- 비율마다 따로 프롬프트를 만들었고, 16:9에 오른쪽 아래 비움 문장이 있는가?
- 프롬프트에 서체 이름·상표·로고가 없는가?
- 캐릭터·장면이 이미 알려진 캐릭터·마스코트와 닮아 보이지 않는가? 닮았으면 캐릭터 설계 규칙 표에서 두 칸 이상 바꿔 다시 만든다.
- 생성 모드는 사용자가 생성을 요청했을 때만 돌렸고, 파일이 `$HOME/Downloads`에 목표 크기로 있는가?
