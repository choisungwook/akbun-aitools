---
name: akbun-draw-filestructure
description: >
  파일·폴더 구조 목록을 다크 패널 + 캡션 박스 카드로 보여주는 이미지 생성 프롬프트와
  Figma/Canva에서 편집 가능한 SVG를 만든다.
---

# 파일·폴더 구조 카드 프롬프트/SVG 생성

## 이 skill이 하는 일

파일·폴더 구조(폴더 이름 목록)를 한 장짜리 **폴더 목록 카드**로 보여주는 결과물을 만든다. 카드는 구겨진 밝은 회색 종이 배경 위에, 폴더 행이 나열된 다크 네이비 패널과 그 아래 설명 캡션 박스가 놓인 고정 레이아웃이다. 인스타그램 카루셀, 블로그 본문 그림, 발표 자료에 어울린다.

결과물은 두 종류다.

1. GPT image나 nano-banana 같은 이미지 생성 모델에 그대로 붙여넣는 **영어 이미지 생성 프롬프트**
2. Figma나 Canva로 가져와 바로 편집할 수 있는 **SVG 파일**

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 코드 블록 하나에 담아, 그대로 복사해 이미지 생성 모델에 붙여넣을 수 있게 한다.
2. **SVG 파일** — 작업 디렉터리에 `<주제-slug>-filestructure.svg`로 저장한다. 텍스트는 `<text>` 요소로 남겨 Figma/Canva에서 수정할 수 있게 한다.
3. **한국어 한 줄 설명** — 어떤 폴더 목록과 캡션을 넣었는지 1~2문장.

## 입력 다루기

사용자가 전달한 내용은 **분석하거나 그대로 사용한다**.

- **폴더 목록과 캡션이 이미 있으면 그대로 쓴다.** 폴더 이름, 순서, 캡션 문구를 바꾸거나 다듬지 않는다.
- **글이나 주제만 있으면 skill이 내용을 분석해 만든다.** 내용에서 작업 단계·분류를 뽑아 폴더 이름 4~9개와 캡션 3~4줄을 skill이 정한다. 폴더 이름은 `0_이름`, `1_이름`처럼 숫자 접두사로 순서를 드러내는 것을 기본으로 하고, 순서가 없는 항목(보관함, 캐시 등)은 접두사 없이 마지막에 둔다.
- **폴더 이름은 짧게 유지한다.** 한 행에 2~8자 내외. 길면 이미지 모델이 글자를 틀린다.

## 레이아웃 규격 (고정)

레이아웃과 상하좌우 간격은 아래 규격에 고정한다. 좌표는 1080×1080 기준이고 괄호는 캔버스 대비 비율이다. 프롬프트와 SVG 모두 이 규격을 그대로 따른다.

- **캔버스**: 1:1 정사각형 (1080×1080 기준)
- **배경**: 밝은 회색 종이. 이미지 프롬프트에서는 은은하게 구겨진 종이 질감, SVG에서는 단색 `#E9E7E3`
- **다크 패널**: 색 `#232637`, 모서리 radius 10
  - 상단 여백 86 (8%)
  - 가로 중앙 정렬, 너비 632 (58.5%), 좌우 여백 각 254 (23.5%)
  - 내부 위/아래 패딩 50, 행 간격(중심 간) 63
  - 행이 n개일 때 패널 높이 = 100 + 63 × (n − 1)
- **폴더 행** (모든 행 동일):
  - 파란 폴더 아이콘: 패널 왼쪽에서 44 안쪽, 크기 약 43×33
  - 폴더 이름: 아이콘 오른쪽, 패널 왼쪽에서 110 안쪽, 흰색 볼드 34px
  - 셰브론 `>`: 연회색(`#B9BDCE`), 모든 행에서 같은 x 위치로 패널 오른쪽에서 56 안쪽에 오른쪽 정렬
- **캡션 박스**: 패널 아래 36 간격, 패널과 같은 x·너비
  - 흰 배경, 검정 2px 테두리
  - 높이 = 40 + 52 × 줄수
  - 텍스트: 가운데 정렬, `#222222`, 33px, 줄간격 52, 3~4줄

## 폰트 규칙

저작권 걱정 없는 오픈소스 폰트만 쓴다.

- SVG의 `font-family`는 `Pretendard, 'Noto Sans KR', sans-serif`로 지정한다. 둘 다 SIL OFL 라이선스라 상업적 사용이 자유롭다.
- 이미지 생성 프롬프트에는 "clean free open-source Korean sans-serif (like Pretendard or Noto Sans KR)"로 폰트 느낌을 지정한다.
- 손글씨체나 상용 폰트 이름(예: 산돌, Apple SD 산돌고딕 등)을 프롬프트에 넣지 않는다.

## 이미지 생성 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. 폴더 행과 캡션 줄은 실제 개수만큼 반복한다.

```text
A square 1:1 image. Background: a light warm-gray sheet of paper with a subtle crumpled
texture, softly lit.

Centered horizontally, starting about 8% from the top edge, a dark navy rounded-rectangle
panel (deep ink blue #232637, slightly rounded corners) about 58% of the image width, with
equal margins on the left and right sides.

Inside the panel, a vertical list of <N> folder rows with perfectly even spacing and
comfortable equal padding above the first row and below the last row. Each row shows, from
left to right:
- a small blue folder icon (macOS folder emoji style),
- a bold white folder name in a clean free open-source Korean sans-serif font (like
  Pretendard or Noto Sans KR),
- a thin light-gray chevron ">" aligned near the right edge of the panel, at the exact same
  x position in every row.

The folder names, top to bottom, reading exactly:
1. "<FOLDER 1>"
2. "<FOLDER 2>"
   ... (repeat for all rows)

Below the panel, separated by a small gap, a white rectangle with a thin black border, the
same width and horizontal position as the panel. Inside it, center-aligned dark-gray text
over <LINE COUNT> lines in the same sans-serif font, with generous line spacing, reading
exactly:
"<CAPTION LINE 1>"
"<CAPTION LINE 2>"
   ... (repeat for all lines)

STYLE: flat, clean UI-mockup look. Crisp legible text, high contrast between the white
labels and the dark panel. No gradients on text, no shadows except a very subtle paper
texture in the background.

DO NOT: misspell any text. Do not add extra icons, badges, or text beyond what is listed.
Do not change the row order or alignment. Do not round the caption box corners.
```

## SVG 생성 규칙

`assets/filestructure-template.svg`를 기준으로 좌표를 계산해 새 SVG를 만든다.

- viewBox는 `0 0 1080 1080`으로 고정한다.
- 행 i(0부터)의 세로 중심 `cy = 86 + 50 + 63 × i`. 아이콘은 `translate(298, cy − 17)`, 이름 baseline은 `cy + 12`, 셰브론은 `M830 (cy − 11) l11 11 l-11 11`.
- 캡션 박스 y = 패널 아래끝 + 36. 캡션 줄 k(1부터)의 baseline = 박스 y + 62 + 52 × (k − 1).
- 텍스트는 절대 path로 변환하지 않고 `<text>` 요소로 남긴다. Figma/Canva에서 더블클릭으로 수정하게 하기 위해서다.
- 배경 종이 질감은 SVG에 넣지 않는다. 필터가 Figma/Canva 임포트에서 깨지기 때문에 단색 배경만 쓴다.
- 저장 후 사용자에게 가져오기 방법을 한 줄로 안내한다: Figma는 캔버스에 드래그 앤 드롭, Canva는 업로드 → 디자인에 추가.

## 예시 (gold reference)

이 예시는 이 skill을 적용한 완성 결과다. 새 결과물의 품질 기준으로 삼는다.

입력 예:

```text
블로그 글쓰기 폴더 정리법을 소개하는 카드를 만들어줘.
폴더: 0_아이디어, 1_초안, 2_퇴고, 3_이미지, 4_발행, 보관함
```

skill이 한 판단: 폴더 목록을 사용자가 준 그대로 6행으로 넣었다. 캡션은 입력에 없어 폴더 흐름을 소개하는 4줄을 만들었다. 패널 높이 = 100 + 63 × 5 = 415, 캡션 박스 높이 = 40 + 52 × 4 = 248.

출력 프롬프트:

```text
A square 1:1 image. Background: a light warm-gray sheet of paper with a subtle crumpled
texture, softly lit.

Centered horizontally, starting about 8% from the top edge, a dark navy rounded-rectangle
panel (deep ink blue #232637, slightly rounded corners) about 58% of the image width, with
equal margins on the left and right sides.

Inside the panel, a vertical list of 6 folder rows with perfectly even spacing and
comfortable equal padding above the first row and below the last row. Each row shows, from
left to right:
- a small blue folder icon (macOS folder emoji style),
- a bold white folder name in a clean free open-source Korean sans-serif font (like
  Pretendard or Noto Sans KR),
- a thin light-gray chevron ">" aligned near the right edge of the panel, at the exact same
  x position in every row.

The folder names, top to bottom, reading exactly:
1. "0_아이디어"
2. "1_초안"
3. "2_퇴고"
4. "3_이미지"
5. "4_발행"
6. "보관함"

Below the panel, separated by a small gap, a white rectangle with a thin black border, the
same width and horizontal position as the panel. Inside it, center-aligned dark-gray text
over 4 lines in the same sans-serif font, with generous line spacing, reading exactly:
"블로그 글 하나가 발행될 때까지"
"이 순서대로 폴더를 거쳐가는데요!"
"각 폴더가 어떤 역할을 하는지"
"하나씩 소개해드릴게요!"

STYLE: flat, clean UI-mockup look. Crisp legible text, high contrast between the white
labels and the dark panel. No gradients on text, no shadows except a very subtle paper
texture in the background.

DO NOT: misspell any text. Do not add extra icons, badges, or text beyond what is listed.
Do not change the row order or alignment. Do not round the caption box corners.
```

SVG는 같은 내용으로 `assets/filestructure-template.svg`와 동일한 좌표 공식을 적용해 저장한다.

한국어 한 줄 설명: 블로그 글쓰기 폴더 6개(0_아이디어~보관함)를 순서대로 다크 패널에 넣고, 폴더 흐름을 소개하는 4줄 캡션을 아래 박스에 배치했습니다.

## 완료 전 확인

- 사용자가 준 폴더 이름·순서·캡션을 바꾸지 않고 그대로 넣었는가? (주제만 받았을 때만 skill이 만든다)
- 그림 속 모든 텍스트를 `reading exactly: "..."`로 철자까지 지정했는가?
- 패널·캡션 박스의 위치와 간격이 레이아웃 규격의 수치를 그대로 따르는가?
- 폰트를 Pretendard/Noto Sans KR 같은 오픈소스 폰트로만 지정했는가?
- SVG의 텍스트를 `<text>` 요소로 남겼는가? (path 변환 금지)
- 프롬프트 한 블록 + SVG 파일 + 한국어 설명을 모두 출력했는가?
