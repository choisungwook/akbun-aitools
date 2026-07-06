---
name: akbun-cardnews
description: >
  사용자가 준 이미지·텍스트를 분석해 에디토리얼 타이포그래피 스타일 카드뉴스를 만든다.
  카드별 문구, 이미지 생성 AI agent용 영어 프롬프트, Figma/Canva로 가져갈 수 있는 SVG 파일을 함께 생성한다.
---

# 카드뉴스 생성 (문구 + 이미지 프롬프트 + SVG)

## 이 skill이 하는 일

사용자가 이미지나 텍스트(또는 둘 다)를 주면, 인스타그램 카루셀 같은 **한 세트의 카드뉴스**를 만든다. 결과물은 세 가지다.

1. **카드 구성안** — 카드별 문구(제목, 본문 또는 리스트, 강조 문구)를 표로 정리한다.
2. **이미지 생성 프롬프트** — 카드마다 GPT image, nano-banana 같은 이미지 생성 AI agent에 그대로 붙여넣을 영어 프롬프트를 만든다.
3. **SVG 파일** — 카드마다 텍스트가 편집 가능한 상태로 남는 SVG를 저장한다. Figma에 드래그하거나 Canva에 업로드해 바로 수정할 수 있다.

카드 스타일은 이 skill에 고정되어 있다: 따뜻한 크림색 정사각형 배경 위에 세리프 제목과 파스텔 형광펜 하이라이트가 있는 **에디토리얼 타이포그래피 카드**다. 사진이나 일러스트 없이 타이포그래피와 하이라이트만으로 구성한다.

## 입력 다루기

- **사용자가 카드 문구를 이미 줬으면 그대로 쓴다.** 요약하거나 다듬지 않는다. 카드 분할만 skill이 한다.
- **글 없이 이미지·자료·주제만 주면 skill이 문구를 만든다.** 이미지를 읽고 핵심 메시지를 뽑아 카드 문구 초안을 작성한 뒤, 그 문구로 이미지 프롬프트와 SVG 작업까지 진행한다. 초안을 만들었다는 사실을 결과에 명시한다.
- **사용자가 준 이미지가 "내용 원본"인지 "스타일 참고"인지 구분한다.** 애매하면 내용 원본으로 간주하고 문구를 추출한다.
- 카드에는 계정 핸들이나 워터마크 같은 하단 부가 텍스트를 넣지 않는다. 제목·본문·리스트로만 구성한다.

## 카드 세트 구성 규칙

- 첫 카드는 **후크 카드**다: 제목(+선택적 부제) 중심으로 시선을 잡는다.
- 내용 카드는 두 종류 레이아웃 중에서 고른다.
  - **텍스트 카드**: 제목 + 본문 문단 1~3개. 본문 중 핵심 구절 하나에 파스텔 하이라이트를 넣는다.
  - **리스트 카드**: 제목 + 번호 리스트 3~7개. 각 항목 전체에 파스텔 하이라이트 바를 번갈아 넣는다.
- 카드 수는 내용에 맞게 3~10장. 한 카드에 한 메시지만 담는다.
- 문구 길이 제한: 제목은 최대 2줄(줄당 한글 기준 약 14자), 본문 문단은 2~3줄, 리스트 항목은 한 줄.

## 레이아웃 스펙 (고정)

모든 카드는 아래 수치를 그대로 따른다. 캔버스는 1080×1080이다. 실제 렌더링 시 여백이 좁고 글씨가 커 보이지 않도록, 여백과 폰트 크기를 보수적으로 잡는다.

- **배경**: 따뜻한 크림색 `#F8F4EC`, 전체 채움. 테두리 없음.
- **좌우 여백**: 최소 150px(각 변). 텍스트 최대 폭 780px(`x=150`~`x=930`).
- **제목**: 가로 중앙 정렬. 첫 baseline `y=300`(한 줄), 두 줄 제목이면 첫 줄 `y=270`, 둘째 줄 `+60`(`y=330`). 색 `#1E1B3A`(잉크빛 다크 네이비).
- **리스트 블록**: 첫 항목 baseline은 제목 마지막 줄 baseline `+130`(한 줄 제목이면 `y=430`, 두 줄 제목이면 `y=460`). 항목 간격 76px. 항목들은 좌측 정렬하되 블록 전체(가장 긴 항목 기준)가 가로 중앙에 오도록 좌측 시작 `x`를 계산한다.
- **본문 블록**: 첫 줄 baseline은 제목 마지막 줄 baseline `+150`(한 줄 제목이면 `y=450`, 두 줄 제목이면 `y=480`). 줄 간격 44px, 문단 사이 +26px. 가로 중앙 정렬, 색 `#3B3A43`.
- **하이라이트 바**: 텍스트 뒤 `<rect>`. 높이 42px(리스트)/36px(본문), baseline 기준 위로 30px/26px, 좌우 패딩 10px. 모서리 둥글림 없음.
- **하단 여백**: 콘텐츠가 끝나는 지점부터 캔버스 하단까지 최소 260px을 비워 둔다. 핸들·워터마크 등 어떤 요소도 채우지 않는다. 콘텐츠를 세로 중앙으로 내리지 않는다 — 상단에 무게가 실린 구도가 이 스타일의 핵심이다.
- **후크 카드(제목+부제만 있는 카드)**: 리스트·본문 블록 없이 제목과 부제만 두므로 아래쪽 여백이 훨씬 커진다. 정상이다 — 억지로 요소를 채우지 않는다.

파스텔 하이라이트 팔레트는 아래 6색을 순서대로 순환한다.

```text
#E3D7F4 (라벤더) → #CBE3F5 (하늘) → #E8DDF6 (라일락) → #FADBC8 (피치) → #CFEBD4 (민트) → #FAEFC7 (버터)
```

본문 내 단일 강조 구절에는 피치 `#FADBC8`를 기본으로 쓴다.

## 폰트 규칙 (저작권 침해 없는 폰트만 사용)

핵심 기준은 **상업적 사용에 라이선스 문제가 없는가**다. 상용 유료 폰트나 라이선스가 불분명한 폰트는 쓰지 않는다. 아래는 SIL Open Font License 기반의 권장 예시이며, 같은 라이선스 조건을 만족하는 다른 폰트로 대체해도 된다.

- **제목(영문)**: Playfair Display Bold(예시) — 한 줄 52px, 두 줄 48px
- **제목(한글)**: Noto Serif KR Bold(예시) — 같은 크기
- **리스트 항목**: 제목과 같은 세리프 계열 SemiBold/Bold, 34px
- **본문**: Pretendard(예시, 대체: Noto Sans KR) Regular, 28px

SVG의 `font-family`에는 항상 대체 폰트까지 지정한다: `"Playfair Display", "Noto Serif KR", serif` / `Pretendard, "Noto Sans KR", sans-serif`.

## SVG 작성 규칙 (Figma/Canva 호환)

- 루트는 `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">`.
- 텍스트는 반드시 `<text>`/`<tspan>` 요소로 넣는다. path로 아웃라인화하지 않는다 — Figma에서 텍스트 편집이 가능해야 한다.
- SVG에는 자동 줄바꿈이 없으므로 줄바꿈은 skill이 직접 나눠 `<tspan x="..." dy="...">`로 처리한다.
- 하이라이트 `<rect>`는 해당 `<text>`보다 먼저(뒤 레이어로) 둔다. 글자 폭은 대략 `글자수 × 폰트크기 × 0.55`(한글은 `× 1.0`)로 추정해 rect 폭을 잡는다.
- 외부 리소스 금지: `<image>` 링크, 웹폰트 `@import`, CSS `<style>` 블록을 쓰지 않는다. 속성 기반 스타일만 쓴다.
- 파일은 카드마다 하나씩 `$HOME/Downloads/cardnewsC-<timestamp>/` 폴더에 `card-01.svg`, `card-02.svg` … 로 저장한다. `<timestamp>`는 작업 시작 시각 기준 `YYYYMMDD-HHMMSS` 형식이다.
- 사용자에게 안내 한 줄을 덧붙인다: Figma/Canva에서 지정 폰트가 설치되어 있지 않으면 대체 폰트로 표시되므로, 사용한 폰트(예: Playfair Display·Noto Serif KR·Pretendard)를 설치(또는 Canva 폰트 목록에서 선택)하라고 알린다.

## 이미지 생성 프롬프트 규칙

- 프롬프트는 **영어**로 쓰고, 카드 하나당 코드 블록 하나로 출력한다.
- 그림에 들어갈 모든 텍스트는 `reading exactly: "..."` 형태로 철자까지 지정한다. 한글 문구는 한글 그대로 넣는다.
- 스타일 문단은 고정이다: warm cream paper background, elegant serif headline in dark navy ink, pastel highlighter bars behind key lines, flat editorial typography poster, square 1:1, no photos or illustrations, generous top-weighted white space.
- 금지 문단도 넣는다: 오탈자 금지, 지정 외 텍스트 추가 금지, 사진·일러스트·그라데이션 금지.

프롬프트 골격은 아래 템플릿을 채워 쓴다. 카드 종류(후크/리스트/텍스트)에 맞는 CONTENT BLOCK 한 가지만 남기고 나머지는 지운다.

```text
A minimal editorial typography card, square 1:1, flat graphic design (no photo, no illustration).
Background: solid warm cream paper (#F8F4EC), subtle clean finish, generous margins on all sides.

Centered near the upper third, an elegant bold serif headline in dark navy ink (#1E1B3A),
reading exactly: "<TITLE>".

<CONTENT BLOCK — pick one:
for a hook/cover card: "Below the headline, a single small centered subtitle line in muted
gray serif," reading exactly: "<SUBTITLE>". The rest of the card below stays empty cream space.
for a list card: "Below the headline, a left-aligned numbered list; each line sits on its own
soft pastel highlighter bar (rotating lavender, light blue, lilac, peach, mint, butter yellow):"
followed by one line per item, each as — reading exactly: "<ITEM>".
for a text card: "Below the headline, short centered paragraphs of clean sans-serif body text
in dark gray," each as — reading exactly: "<PARAGRAPH>", plus "one key phrase sits on a soft
peach highlighter bar, reading exactly: "<PHRASE>"".>

STYLE: flat editorial poster typography, warm and calm, high legibility, generous margins on
every side, top-weighted composition with large empty space below the text block.

DO NOT: misspell any text. Do not add any text beyond what is listed. No photos, illustrations,
icons, gradients, textures, borders, or handles/watermarks.
```

## 작업 순서

1. **git 동기화.** 작업 시작 전에 `git pull origin main --rebase`를 실행하고, 충돌이 나면 해결한 뒤 진행한다.
2. **입력 파악.** 텍스트가 있으면 그대로 쓰고, 이미지·주제만 있으면 분석해 문구 초안을 만든다.
3. **카드 분할.** 후크 카드 + 내용 카드(텍스트/리스트)로 나누고 카드 구성안 표를 만든다.
4. **프롬프트 작성.** 카드마다 템플릿을 채워 영어 프롬프트를 만든다.
5. **SVG 생성.** `$HOME/Downloads/cardnewsC-<timestamp>/` 폴더를 만들고, 카드마다 레이아웃 스펙 수치대로 SVG 파일을 저장한다.
6. **출력.** 카드 구성안 → 카드별 프롬프트 → SVG 파일 경로 + 폰트 안내 순으로 정리해 보여준다.

## 예시 (후크 카드 + 리스트 카드, 2장)

카드가 여러 장이면 **카드마다 각각** 프롬프트와 SVG를 만든다. 아래는 첫 두 장(표지 후크 카드, 첫 내용 카드)의 전체 결과물이다.

입력 예:

```text
홈카페 입문 장비 5가지를 카드뉴스로.
제목: 홈카페 시작 장비
1. 핸드밀 그라인더 2. 드리퍼와 필터 3. 구스넥 주전자 4. 서버 5. 미니 저울
```

카드 구성안:

| 카드 | 종류 | 내용 |
|---|---|---|
| 1 | 후크 | 제목 "홈카페 시작 장비" / 부제 "시작 전 챙길 다섯 가지" |
| 2 | 리스트 | 제목 "무엇을 준비할까" / 항목 5개 |

### 카드 1 (후크)

이미지 생성 프롬프트:

```text
A minimal editorial typography card, square 1:1, flat graphic design (no photo, no illustration).
Background: solid warm cream paper (#F8F4EC), subtle clean finish, generous margins on all sides.

Centered near the upper third, an elegant bold serif headline in dark navy ink (#1E1B3A),
in Korean, reading exactly: "홈카페 시작 장비".

Below the headline, a single small centered subtitle line in muted gray serif, in Korean,
reading exactly: "시작 전 챙길 다섯 가지". The rest of the card below stays empty cream space.

STYLE: flat editorial poster typography, warm and calm, high legibility, generous margins on
every side, top-weighted composition with large empty space below the text block.

DO NOT: misspell any text. Do not add any text beyond what is listed. No photos, illustrations,
icons, gradients, textures, borders, or handles/watermarks.
```

SVG(`$HOME/Downloads/cardnewsC-20260706-153000/card-01.svg`):

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
  <rect width="1080" height="1080" fill="#F8F4EC"/>
  <text x="540" y="300" text-anchor="middle" font-family="'Noto Serif KR', 'Playfair Display', serif"
        font-weight="700" font-size="52" fill="#1E1B3A">홈카페 시작 장비</text>
  <text x="540" y="356" text-anchor="middle" font-family="'Noto Serif KR', serif"
        font-weight="400" font-size="28" fill="#7A7568">시작 전 챙길 다섯 가지</text>
</svg>
```

### 카드 2 (리스트)

이미지 생성 프롬프트:

```text
A minimal editorial typography card, square 1:1, flat graphic design (no photo, no illustration).
Background: solid warm cream paper (#F8F4EC), subtle clean finish, generous margins on all sides.

Centered near the upper third, an elegant bold serif headline in dark navy ink (#1E1B3A),
in Korean, reading exactly: "무엇을 준비할까".

Below the headline, a left-aligned numbered list in the same serif; each line sits on its own
soft pastel highlighter bar (lavender, light blue, lilac, peach, mint from top to bottom):
- reading exactly: "1. 핸드밀 그라인더"
- reading exactly: "2. 드리퍼와 필터"
- reading exactly: "3. 구스넥 주전자"
- reading exactly: "4. 서버"
- reading exactly: "5. 미니 저울"

STYLE: flat editorial poster typography, warm and calm, high legibility, generous margins on
every side, top-weighted composition with large empty space below the text block.

DO NOT: misspell any text. Do not add any text beyond what is listed. No photos, illustrations,
icons, gradients, textures, borders, or handles/watermarks.
```

SVG(`$HOME/Downloads/cardnewsC-20260706-153000/card-02.svg`):

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
  <rect width="1080" height="1080" fill="#F8F4EC"/>
  <text x="540" y="300" text-anchor="middle" font-family="'Noto Serif KR', 'Playfair Display', serif"
        font-weight="700" font-size="52" fill="#1E1B3A">무엇을 준비할까</text>
  <rect x="380" y="400" width="320" height="42" fill="#E3D7F4"/>
  <text x="390" y="430" font-family="'Noto Serif KR', serif" font-weight="600" font-size="34"
        fill="#1E1B3A">1. 핸드밀 그라인더</text>
  <rect x="380" y="476" width="280" height="42" fill="#CBE3F5"/>
  <text x="390" y="506" font-family="'Noto Serif KR', serif" font-weight="600" font-size="34"
        fill="#1E1B3A">2. 드리퍼와 필터</text>
  <rect x="380" y="552" width="280" height="42" fill="#E8DDF6"/>
  <text x="390" y="582" font-family="'Noto Serif KR', serif" font-weight="600" font-size="34"
        fill="#1E1B3A">3. 구스넥 주전자</text>
  <rect x="380" y="628" width="150" height="42" fill="#FADBC8"/>
  <text x="390" y="658" font-family="'Noto Serif KR', serif" font-weight="600" font-size="34"
        fill="#1E1B3A">4. 서버</text>
  <rect x="380" y="704" width="220" height="42" fill="#CFEBD4"/>
  <text x="390" y="734" font-family="'Noto Serif KR', serif" font-weight="600" font-size="34"
        fill="#1E1B3A">5. 미니 저울</text>
</svg>
```

나머지 카드(3장 이상)도 같은 방식으로 카드마다 프롬프트 한 블록 + SVG 한 파일을 만든다.

## 완료 전 확인

- 사용자가 준 문구를 바꾸지 않고 그대로 넣었는가? (문구가 없을 때만 skill이 초안을 만들고, 만들었다고 밝혔는가?)
- 레이아웃 수치(배경색, 제목 위치, 넉넉한 좌우/상하 여백, 상단 무게 구도)를 스펙 그대로 지켰는가? 여백이 좁거나 글씨가 커 보이지 않는가?
- 하단에 핸들·워터마크 등 부가 텍스트를 넣지 않았는가?
- 사용한 폰트가 저작권을 위반하지 않는가? (예: Noto Sans KR처럼 상업적 사용이 자유로운 라이선스인가)
- SVG의 텍스트가 `<text>` 요소로 편집 가능하게 남아 있고, 외부 리소스가 없는가?
- 카드가 여러 장이면 **카드마다 각각** 프롬프트와 SVG를 만들었는가? (표지 한 장만 만들고 끝내지 않았는가?)
- 프롬프트의 모든 텍스트를 `reading exactly: "..."`로 지정했는가?
- SVG 파일을 `$HOME/Downloads/cardnewsC-<timestamp>/`에 저장했는가?
- 세 가지 결과물(구성안, 카드별 프롬프트, 카드별 SVG 파일 경로)을 모두 출력했는가?
