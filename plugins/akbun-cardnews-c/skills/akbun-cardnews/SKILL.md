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
- 계정 핸들(예: `@myaccount`)을 알려주면 카드 하단에 넣고, 없으면 하단 핸들 줄을 생략한다.

## 카드 세트 구성 규칙

- 첫 카드는 **후크 카드**다: 제목(+선택적 부제) 중심으로 시선을 잡는다.
- 내용 카드는 두 종류 레이아웃 중에서 고른다.
  - **텍스트 카드**: 제목 + 본문 문단 1~3개. 본문 중 핵심 구절 하나에 파스텔 하이라이트를 넣는다.
  - **리스트 카드**: 제목 + 번호 리스트 3~7개. 각 항목 전체에 파스텔 하이라이트 바를 번갈아 넣는다.
- 카드 수는 내용에 맞게 3~10장. 한 카드에 한 메시지만 담는다.
- 문구 길이 제한: 제목은 최대 2줄(줄당 한글 기준 약 14자), 본문 문단은 2~3줄, 리스트 항목은 한 줄.

## 레이아웃 스펙 (고정)

모든 카드는 아래 수치를 그대로 따른다. 캔버스는 1080×1080이다.

- **배경**: 따뜻한 크림색 `#F8F4EC`, 전체 채움. 테두리 없음.
- **좌우 여백**: 최소 100px. 텍스트 최대 폭 880px.
- **제목**: 가로 중앙 정렬. 첫 baseline은 위에서 약 31% 지점 — 한 줄 제목이면 `y=340`, 두 줄 제목이면 첫 줄 `y=320`, 둘째 줄 `+76`. 색 `#1E1B3A`(잉크빛 다크 네이비).
- **리스트 블록**: 제목 아래에서 시작, 첫 항목 baseline `y=420`, 항목 간격 64px. 항목들은 좌측 정렬하되 블록 전체가 가로 중앙에 오도록 배치(기본 좌측 시작 `x=340`, 가장 긴 항목에 맞춰 조정).
- **본문 블록**: 첫 줄 baseline `y=480`(두 줄 제목이면 `y=520`), 줄 간격 50px, 문단 사이 +30px. 가로 중앙 정렬, 색 `#3B3A43`.
- **하이라이트 바**: 텍스트 뒤 `<rect>`. 높이 48px(리스트)/42px(본문), baseline 기준 위로 36px/32px, 좌우 패딩 12px. 모서리 둥글림 없음.
- **하단 핸들**: 가로 중앙, baseline `y=1030`, 색 `#B7B1A6`.
- **하단 여백**: 본문/리스트가 끝난 뒤 남는 아래쪽 공간은 비워 둔다. 콘텐츠를 세로 중앙으로 내리지 않는다 — 상단에 무게가 실린 구도가 이 스타일의 핵심이다.

파스텔 하이라이트 팔레트는 아래 6색을 순서대로 순환한다.

```text
#E3D7F4 (라벤더) → #CBE3F5 (하늘) → #E8DDF6 (라일락) → #FADBC8 (피치) → #CFEBD4 (민트) → #FAEFC7 (버터)
```

본문 내 단일 강조 구절에는 피치 `#FADBC8`를 기본으로 쓴다.

## 폰트 규칙 (저작권 무료만 사용)

모두 SIL Open Font License라 상업적 사용이 자유롭다. 다른 폰트를 쓰지 않는다.

- **제목(영문)**: Playfair Display Bold — 한 줄 64px, 두 줄 60px
- **제목(한글)**: Noto Serif KR Bold — 같은 크기
- **리스트 항목**: 제목과 같은 세리프 계열 SemiBold/Bold, 42px
- **본문·핸들**: Pretendard(대체: Noto Sans KR) — 본문 Regular 34px, 핸들 24px

SVG의 `font-family`에는 항상 대체 폰트까지 지정한다: `"Playfair Display", "Noto Serif KR", serif` / `Pretendard, "Noto Sans KR", sans-serif`.

## SVG 작성 규칙 (Figma/Canva 호환)

- 루트는 `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">`.
- 텍스트는 반드시 `<text>`/`<tspan>` 요소로 넣는다. path로 아웃라인화하지 않는다 — Figma에서 텍스트 편집이 가능해야 한다.
- SVG에는 자동 줄바꿈이 없으므로 줄바꿈은 skill이 직접 나눠 `<tspan x="..." dy="...">`로 처리한다.
- 하이라이트 `<rect>`는 해당 `<text>`보다 먼저(뒤 레이어로) 둔다. 글자 폭은 대략 `글자수 × 폰트크기 × 0.55`(한글은 `× 1.0`)로 추정해 rect 폭을 잡는다.
- 외부 리소스 금지: `<image>` 링크, 웹폰트 `@import`, CSS `<style>` 블록을 쓰지 않는다. 속성 기반 스타일만 쓴다.
- 파일은 카드마다 하나씩 작업 디렉터리의 `cardnews-<주제slug>/` 폴더에 `card-01.svg`, `card-02.svg` … 로 저장한다.
- 사용자에게 안내 한 줄을 덧붙인다: Figma/Canva에서 지정 폰트가 설치되어 있지 않으면 대체 폰트로 표시되므로, Playfair Display·Noto Serif KR·Pretendard를 설치(또는 Canva 폰트 목록에서 선택)하라고 알린다.

## 이미지 생성 프롬프트 규칙

- 프롬프트는 **영어**로 쓰고, 카드 하나당 코드 블록 하나로 출력한다.
- 그림에 들어갈 모든 텍스트는 `reading exactly: "..."` 형태로 철자까지 지정한다. 한글 문구는 한글 그대로 넣는다.
- 스타일 문단은 고정이다: warm cream paper background, elegant serif headline in dark navy ink, pastel highlighter bars behind key lines, flat editorial typography poster, square 1:1, no photos or illustrations, generous top-weighted white space.
- 금지 문단도 넣는다: 오탈자 금지, 지정 외 텍스트 추가 금지, 사진·일러스트·그라데이션 금지.

프롬프트 골격은 아래 템플릿을 채워 쓴다.

```text
A minimal editorial typography card, square 1:1, flat graphic design (no photo, no illustration).
Background: solid warm cream paper (#F8F4EC), subtle clean finish, generous margins.

Centered near the upper third, an elegant bold serif headline in dark navy ink (#1E1B3A),
reading exactly: "<TITLE>".

<CONTENT BLOCK — for a list card: "Below the headline, a left-aligned numbered list; each line
sits on its own soft pastel highlighter bar (rotating lavender, light blue, lilac, peach, mint,
butter yellow):" followed by one line per item, each as — reading exactly: "<ITEM>".
For a text card: "Below the headline, short centered paragraphs of clean sans-serif body text
in dark gray," each as — reading exactly: "<PARAGRAPH>", plus "one key phrase sits on a soft
peach highlighter bar, reading exactly: "<PHRASE>"".>

At the bottom center, a small light-gray handle, reading exactly: "<HANDLE>". (delete if none)

STYLE: flat editorial poster typography, warm and calm, high legibility, top-weighted
composition with empty space below the text block.

DO NOT: misspell any text. Do not add any text beyond what is listed. No photos, illustrations,
icons, gradients, textures, or borders.
```

## 작업 순서

1. **git 동기화.** 작업 시작 전에 `git pull origin main --rebase`를 실행하고, 충돌이 나면 해결한 뒤 진행한다.
2. **입력 파악.** 텍스트가 있으면 그대로 쓰고, 이미지·주제만 있으면 분석해 문구 초안을 만든다.
3. **카드 분할.** 후크 카드 + 내용 카드(텍스트/리스트)로 나누고 카드 구성안 표를 만든다.
4. **프롬프트 작성.** 카드마다 템플릿을 채워 영어 프롬프트를 만든다.
5. **SVG 생성.** 카드마다 레이아웃 스펙 수치대로 SVG 파일을 저장한다.
6. **출력.** 카드 구성안 → 카드별 프롬프트 → SVG 파일 경로 + 폰트 안내 순으로 정리해 보여준다.

## 예시 (리스트 카드 한 장)

입력 예:

```text
홈카페 입문 장비 5가지를 카드뉴스로. 핸들은 @homecafe.log
제목: 홈카페 시작 장비
1. 핸드밀 그라인더 2. 드리퍼와 필터 3. 구스넥 주전자 4. 서버 5. 미니 저울
```

이 카드의 이미지 생성 프롬프트:

```text
A minimal editorial typography card, square 1:1, flat graphic design (no photo, no illustration).
Background: solid warm cream paper (#F8F4EC), subtle clean finish, generous margins.

Centered near the upper third, an elegant bold serif headline in dark navy ink (#1E1B3A),
in Korean, reading exactly: "홈카페 시작 장비".

Below the headline, a left-aligned numbered list in the same serif; each line sits on its own
soft pastel highlighter bar (lavender, light blue, lilac, peach, mint from top to bottom):
- reading exactly: "1. 핸드밀 그라인더"
- reading exactly: "2. 드리퍼와 필터"
- reading exactly: "3. 구스넥 주전자"
- reading exactly: "4. 서버"
- reading exactly: "5. 미니 저울"

At the bottom center, a small light-gray handle, reading exactly: "@homecafe.log".

STYLE: flat editorial poster typography, warm and calm, high legibility, top-weighted
composition with empty space below the text block.

DO NOT: misspell any text. Do not add any text beyond what is listed. No photos, illustrations,
icons, gradients, textures, or borders.
```

같은 카드의 SVG(`cardnews-homecafe/card-01.svg`):

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
  <rect width="1080" height="1080" fill="#F8F4EC"/>
  <text x="540" y="340" text-anchor="middle" font-family="'Noto Serif KR', 'Playfair Display', serif"
        font-weight="700" font-size="64" fill="#1E1B3A">홈카페 시작 장비</text>
  <rect x="328" y="384" width="428" height="48" fill="#E3D7F4"/>
  <text x="340" y="420" font-family="'Noto Serif KR', serif" font-weight="600" font-size="42"
        fill="#1E1B3A">1. 핸드밀 그라인더</text>
  <rect x="328" y="448" width="386" height="48" fill="#CBE3F5"/>
  <text x="340" y="484" font-family="'Noto Serif KR', serif" font-weight="600" font-size="42"
        fill="#1E1B3A">2. 드리퍼와 필터</text>
  <rect x="328" y="512" width="386" height="48" fill="#E8DDF6"/>
  <text x="340" y="548" font-family="'Noto Serif KR', serif" font-weight="600" font-size="42"
        fill="#1E1B3A">3. 구스넥 주전자</text>
  <rect x="328" y="576" width="176" height="48" fill="#FADBC8"/>
  <text x="340" y="612" font-family="'Noto Serif KR', serif" font-weight="600" font-size="42"
        fill="#1E1B3A">4. 서버</text>
  <rect x="328" y="640" width="302" height="48" fill="#CFEBD4"/>
  <text x="340" y="676" font-family="'Noto Serif KR', serif" font-weight="600" font-size="42"
        fill="#1E1B3A">5. 미니 저울</text>
  <text x="540" y="1030" text-anchor="middle" font-family="Pretendard, 'Noto Sans KR', sans-serif"
        font-size="24" fill="#B7B1A6">@homecafe.log</text>
</svg>
```

## 완료 전 확인

- 사용자가 준 문구를 바꾸지 않고 그대로 넣었는가? (문구가 없을 때만 skill이 초안을 만들고, 만들었다고 밝혔는가?)
- 레이아웃 수치(배경색, 제목 위치, 줄 간격, 하단 핸들 위치, 상단 무게 구도)를 스펙 그대로 지켰는가?
- 폰트를 Playfair Display / Noto Serif KR / Pretendard(Noto Sans KR) 밖에서 쓰지 않았는가?
- SVG의 텍스트가 `<text>` 요소로 편집 가능하게 남아 있고, 외부 리소스가 없는가?
- 프롬프트의 모든 텍스트를 `reading exactly: "..."`로 지정했는가?
- 세 가지 결과물(구성안, 프롬프트, SVG 파일 경로)을 모두 출력했는가?
