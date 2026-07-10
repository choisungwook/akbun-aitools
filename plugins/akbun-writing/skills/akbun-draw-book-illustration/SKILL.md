---
name: akbun-draw-book-illustration
description: >
  소재·글씨를 monogray 삽화 스타일(진회색 잉크 손그림 + 플랫 회색 + 오렌지 포인트 하나)로 그리되,
  구도를 자유롭게 두지 않고 참고 이미지에서 뽑은 고정 레이아웃 5종(아이콘 스트립·확대·대화·흐름·
  포스터 카드)과 상하좌우 간격에 맞춰 배치하는 이미지 생성 프롬프트와, Figma/Canva로 가져와 편집할
  수 있는 SVG 파일을 함께 만든다. 글씨가 없으면 내용을 분석해 skill이 문구를 만든다.
  Trigger on: "책 삽화 레이아웃", "고정 레이아웃 삽화", "아이콘 스트립 삽화", "확대 삽화",
  "대화 삽화", "흐름도 삽화", "삽화 레이아웃 SVG", "book figure layout", "icon strip illustration",
  or any request to lay an idea out in one of these fixed book-figure layouts as a prompt plus SVG.
  구도를 자유롭게 두고 스타일만 입히려면 akbun-draw-poster-monogray를 쓴다.
---

# 책 삽화 레이아웃 이미지 프롬프트 + SVG 생성

## 이 skill이 하는 일

개념, 장면, 짧은 글을 받아 **기술책 삽화**를 만들 수 있게 두 가지 산출물을 만든다.

1. GPT image나 nano-banana 같은 이미지 생성 모델(또는 이미지 생성 agent)에 그대로 붙여넣을
   **영어 이미지 생성 프롬프트**
2. Figma나 Canva로 가져와 직접 편집할 수 있는 **SVG 파일**

이 skill은 그림을 직접 렌더링하지 않는다. 프롬프트는 이미지 모델이 그리고, SVG는 사용자가
디자인 툴에서 다듬는다.

**`akbun-draw-poster-monogray`와의 관계.** 그림체·색감(진회색 잉크 + 플랫 회색 + 오렌지 포인트
하나 + off-white 종이)은 monogray와 **같은 팔레트를 공유**한다. 다른 점은 딱 하나다.
monogray는 구도를 소재에 맞춰 자유롭게 두지만, **이 skill은 참고 이미지에서 뽑은 고정 레이아웃
5종과 상하좌우 간격에 맞춰 배치한다.** "스타일만 필요하고 구도는 자유"면 monogray를, "정해진
책 삽화 레이아웃과 간격에 맞춰야" 하면 이 skill을 쓴다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록(```text)에 담아 그대로 복사할 수 있게 한다.
2. **SVG 파일** — 작업 디렉터리에 `<주제-slug>.svg`로 저장하고 경로를 알려준다.
   SVG 작성 규칙은 `references/svg-rules.md`를 따른다.
3. **한국어 한 줄 설명** — 어떤 레이아웃을 골랐고, 어떤 문구를 넣었고, 오렌지 포인트를 어디에
   줬는지 1~2문장.

## 입력 다루기

- **그림 소재**: 텍스트 설명, 개념 이름, 참고 이미지 등 무엇이든 받는다. 참고 이미지는 픽셀
  단위로 복제할 대상이 아니라 소재·구도를 읽는 참고다.
- **글씨(옵션)**: 사용자가 그림에 넣을 문구를 줬으면 **바꾸지 않고 그대로** 넣는다. 요약하거나
  다듬지 않는다.
- **글씨가 없으면 skill이 만든다.** 소재를 분석해 레이아웃에 맞는 짧은 문구(라벨, 제목, 캡션,
  말풍선)를 만든 뒤 그림 작업을 진행한다. 만든 문구는 한국어 한 줄 설명에서 알려준다.
- 문구는 짧게 유지한다. 라벨은 2~6자, 캡션·말풍선은 15자 안팎이 안전하다. 길수록 이미지
  모델이 글자를 틀릴 확률이 높다.

## 레이아웃 고르기

레이아웃은 아래 5종으로 고정한다. 각 레이아웃의 구성과 상하좌우 간격 수치는
`references/layout-patterns.md`에 있다. **간격 수치는 임의로 바꾸지 않는다.**

| 레이아웃 | 쓰임 |
|---|---|
| `flow-stack` | 단계·구조 설명. 세로 블록 스택 + 그룹 음영 + 오렌지 화살표 흐름 |
| `zoom-detail` | 대상의 내부·세부 강조. 주 피사체 + 확대 원 + 오렌지 링 |
| `poster-card` | 인용·장면 각인. 액자 프레임 + 상단 제목 + 중앙 장면 + 하단 캡션 |
| `dialog-scene` | 상호작용·의문 표현. 좌측 인물(생각 풍선) + 우측 상대(말풍선) |
| `icon-strip` | 수치·팩트 나열. 가로 아이콘 3~4개 + 아래 라벨 |

선택 기준: 내용이 "순서·구조"면 `flow-stack`, "안을 들여다보기"면 `zoom-detail`,
"한 문장을 각인"이면 `poster-card`, "묻고 답하기·오해"면 `dialog-scene`,
"숫자 비교·나열"이면 `icon-strip`. 사용자가 레이아웃을 지정하면 그것을 따른다.

## 비주얼 스타일 (고정 — monogray와 동일 팔레트)

모든 산출물(프롬프트와 SVG)은 아래 스타일을 그대로 따른다. 바꾸지 않는다. 색은
`akbun-draw-poster-monogray`와 **같은 팔레트**를 쓴다(플러그인 내 두 skill의 그림체가 하나로
보이게 하기 위함).

- **배경**: 따뜻한 off-white 종이(`#F4F2ED`). 종이 질감이 은은하다.
- **선**: 진회색(`#3A3A3A`) 잉크 아웃라인. 굵고 둥근 손그림 선이며 살짝 흔들린다(완벽한
  직선·정원이 아니다). 선 끝은 둥글다(round join/cap).
- **면**: 플랫한 회색 두 톤 — 밝은 회색(`#E3E3E3`), 중간 회색(`#C9C9C9`). 모니터·화면처럼
  어두운 면은 `#5A5A5A`. 그룹 배경은 사선 해칭(스크린톤) 느낌의 회색 라운드 사각형.
- **포인트 컬러**: 따뜻한 오렌지(`#E8833A`) **한 색만**. 화살표, 강조 블록, 물음표, 링 같은
  "가장 말하고 싶은 요소" 1~3곳에만 쓴다. 그 외 색은 쓰지 않는다.
- **텍스트**: 한국어 손글씨 느낌. 영어 제목은 세리프 대문자에 자간을 넓게.
- **여백**: 사방 캔버스의 약 10%. 요소를 가장자리에 붙이지 않는다.

## 폰트 규칙 (저작권 무료)

- SVG의 텍스트는 **SIL OFL 라이선스의 무료 폰트만** 지정한다.
  기본은 `Gaegu`(한글 손글씨), 대안은 `Nanum Pen Script`, 라틴 대체는 `Patrick Hand`
  (monogray와 동일 스택). 영어 세리프 제목이 필요하면 `Nanum Myeongjo`를 쓴다. 모두 Google
  Fonts에서 무료로 쓸 수 있다.
- 유료·상용 폰트나 라이선스 불명 폰트 이름을 지정하지 않는다.
- Figma는 Google Fonts를 내장 지원하므로 그대로 열린다. Canva는 폰트가 없으면 대체되므로,
  필요 시 OFL 폰트 파일을 Canva에 업로드하라고 안내한다.

## 작업 순서

1. **소재와 글씨 파악.** 사용자가 준 소재를 읽는다. 글씨가 있으면 그대로 쓰고, 없으면 소재를
   분석해 문구를 만든다.
2. **레이아웃 결정.** 위 선택 기준으로 5종 중 하나를 고른다.
3. **오렌지 포인트 결정.** 가장 말하고 싶은 요소 1~3곳을 정한다. 흐름이면 화살표, 강조
   블록이면 블록 글자, 의문이면 물음표 식이다.
4. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채우고, `references/layout-patterns.md`의
   해당 레이아웃 설명과 간격을 LAYOUT 절에 옮긴다.
5. **SVG 작성.** `references/svg-rules.md`의 규칙대로 같은 내용을 SVG로 그려 저장한다.
   `assets/example-icon-strip.svg`가 품질 기준이다.
6. **출력.** 영어 프롬프트 블록 + SVG 파일 경로 + 한국어 한 줄 설명을 출력한다.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. `(delete if none)`이 붙은 줄은 해당 요소가 없으면
지운다. LAYOUT 절에는 고른 레이아웃의 구성·간격을 그대로 옮긴다.

```text
A hand-drawn editorial illustration in a friendly Korean tech-book style, on a warm
off-white paper background (#F4F2ED). Everything is drawn with uniform dark-gray ink
outlines (#3A3A3A) with rounded corners and rounded stroke ends, slightly wobbly and
hand-drawn, filled with flat gray tones only (#E3E3E3 light, #C9C9C9 mid, #5A5A5A for
dark screens) — no gradients, no photographic shading.

LAYOUT (<layout-name>): <layout description copied from the layout pattern, including
the spacing rules — outer margins about 10% of the canvas on all sides, element gaps
as specified for this layout>.

SCENE: <one or two sentences describing the subjects — keep each subject simple,
one clear silhouette per element>.

TEXT (hand-lettered, Korean handwriting style unless noted):
- <position, e.g. "label under the first icon">, reading exactly: "<TEXT 1>"
- <position>, reading exactly: "<TEXT 2>" (delete if none)

ACCENT: exactly ONE accent color, warm orange (#E8833A), appears ONLY on <the 1-3 accent
elements, e.g. "the flow arrows and the question mark">. Everything else stays gray.

STYLE: flat hand-drawn ink illustration, monochrome gray with a single warm-orange accent,
bold rounded outlines, generous margins, clean and friendly composition like a printed
book figure. Aspect ratio <W:H>.

DO NOT: use any color other than the grays, paper off-white, and the single orange accent.
No digital-looking fonts — all text is hand-lettered. Do not misspell any text. Do not add
extra text, logos, or watermarks beyond what is listed above.
```

## SVG 생성 규칙 (요약)

상세 규칙은 `references/svg-rules.md`에 있다. 핵심만 요약하면:

- 레이아웃별 지정 viewBox를 쓰고, 사방 10% 여백을 지킨다.
- 텍스트는 아웃라인으로 변환하지 않고 `<text>` 요소로 남겨 Figma/Canva에서 편집 가능하게 한다.
- 손그림 느낌은 둥근 선끝(`stroke-linecap="round"`), 라운드 모서리, 요소별 ±1도 회전으로 낸다.
- 색은 monogray와 동일 팔레트(잉크 `#3A3A3A`/회색 `#E3E3E3`·`#C9C9C9`/어두운 면 `#5A5A5A`/오렌지 `#E8833A`)와 배경 `#F4F2ED`만 쓴다.
- 외부 이미지·외부 리소스 참조 없이 순수 벡터로만 그린다.

## 예시 (gold reference)

이 예시는 이 skill의 품질 기준이다. SVG 완성본은 `assets/example-icon-strip.svg`에 있다.

입력 예:

```text
홈랩 서버를 구축했다. 미니PC 1대, 메모리 64GB, 디스크 2TB인데 한 달 전기요금이 1만원밖에 안 나온다.
이걸 그림으로 만들어줘.
```

skill이 한 판단: 수치 나열이므로 `icon-strip` 레이아웃. 글씨가 없으므로 소재에서 라벨 4개
(`미니PC 1대`, `메모리 64GB`, `디스크 2TB`, `월 전기 1만원`)를 만들었다. 이야기의 반전이
"전기요금이 싸다"이므로 오렌지 포인트는 마지막 지폐 다발과 반짝임에만 줬다.

출력 프롬프트:

```text
A hand-drawn editorial illustration in a friendly Korean tech-book style, on a warm
off-white paper background (#F4F2ED). Everything is drawn with uniform dark-gray ink
outlines (#3A3A3A) with rounded corners and rounded stroke ends, slightly wobbly and
hand-drawn, filled with flat gray tones only (#E3E3E3 light, #C9C9C9 mid, #5A5A5A for
dark screens) — no gradients, no photographic shading.

LAYOUT (icon-strip): a single horizontal row of four simple ink icons, evenly spaced,
centered vertically slightly above the middle of the canvas. Outer margins are about
10% of the canvas on all sides. Each icon has a short hand-lettered label centered
below it, with a gap of about a quarter of the icon height between icon and label.

SCENE: from left to right — a small desktop mini PC with a monitor, a RAM memory stick
with small chips, a database-style disk cylinder, and a short stack of banknotes with
three small sparkle strokes above it.

TEXT (hand-lettered, Korean handwriting style):
- label under the first icon, reading exactly: "미니PC 1대"
- label under the second icon, reading exactly: "메모리 64GB"
- label under the third icon, reading exactly: "디스크 2TB"
- label under the fourth icon, reading exactly: "월 전기 1만원"

ACCENT: exactly ONE accent color, warm orange (#E8833A), appears ONLY on the bands of the
banknote stack and the three sparkle strokes above it. Everything else stays gray.

STYLE: flat hand-drawn ink illustration, monochrome gray with a single warm-orange accent,
bold rounded outlines, generous margins, clean and friendly composition like a printed
book figure. Aspect ratio 8:3.

DO NOT: use any color other than the grays, paper off-white, and the single orange accent.
No digital-looking fonts — all text is hand-lettered. Do not misspell any text. Do not add
extra text, logos, or watermarks beyond what is listed above.
```

한국어 한 줄 설명: 수치 나열이라 `icon-strip` 레이아웃을 골라 라벨 4개를 만들었고, 이야기의
반전인 "월 전기 1만원"의 지폐 다발과 반짝임에만 오렌지 포인트를 줬습니다. SVG는
`homelab-server-specs.svg`로 저장했습니다.

## 완료 전 확인

- 사용자가 준 글씨를 바꾸지 않고 그대로 넣었는가? (글씨가 없을 때만 skill이 만든다)
- 그림 속 모든 텍스트를 `reading exactly: "..."`로 철자까지 지정했는가?
- 레이아웃 5종 중 하나를 골랐고, `references/layout-patterns.md`의 간격 수치를 그대로 썼는가?
- 오렌지 포인트가 1~3곳에만 있는가? 팔레트 밖의 색을 쓰지 않았는가?
- SVG의 텍스트가 편집 가능한 `<text>` 요소인가? 폰트가 OFL 무료 폰트(Gaegu 등)인가?
- 프롬프트 블록, SVG 파일 경로, 한국어 한 줄 설명 세 가지를 모두 출력했는가?
