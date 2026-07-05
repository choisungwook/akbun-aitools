---
name: akbun-draw-file-tree
description: >
  파일/폴더 레이아웃(디렉터리 트리)을 오렌지 커넥터 카드 스타일 다이어그램으로 만드는 skill로,
  이미지 생성 AI agent용 영어 프롬프트와 Figma/Canva로 가져올 수 있는 SVG를 함께 출력한다.
---

# 파일/폴더 레이아웃 다이어그램 프롬프트 + SVG 생성

## 이 skill이 하는 일

디렉터리 트리(파일/폴더 구조)를 받아, 문서 figure로 쓸 수 있는 **파일/폴더 레이아웃 다이어그램**을 두 가지 형태로 만든다.

1. **영어 이미지 생성 프롬프트** — GPT image, nano-banana 같은 이미지 생성 AI agent에 그대로 붙여넣는 한 블록.
2. **SVG 파일** — Figma나 Canva에 import해서 편집할 수 있는 벡터 파일.

이 skill은 그림을 직접 렌더링하는 대신 프롬프트를 만들고, SVG는 직접 작성해 파일로 저장한다. 프롬프트와 그림 속 모든 텍스트(파일명/폴더명)는 영어로 쓴다. 이미지 생성 모델이 영어 글자를 가장 정확히 렌더링하기 때문이다.

## 입력 처리

- 사용자가 트리 구조(텍스트 트리, 파일 목록, 코드 블록)를 주면 그대로 사용한다.
- **사용자가 내용을 주지 않으면** 현재 작업 디렉터리·repo·대화에 남긴 자료를 분석해 트리를 직접 구성한 뒤, 구성한 트리를 짧게 보여주고 바로 이미지 작업을 진행한다. 따로 묻지 않는다.
- 트리는 **전체 15행 이내**로 다듬는다. 그림의 메시지에 기여하지 않는 파일(lock 파일, 캐시, 빌드 산출물 등)은 뺀다. 폴더 안 파일이 너무 많으면 대표 파일 2~3개만 남긴다.

## 레이아웃 규칙 (고정)

모든 산출물(프롬프트와 SVG 둘 다)은 아래 레이아웃을 그대로 따른다. 상하좌우 간격이 이 스타일의 핵심이므로 임의로 바꾸지 않는다.

- **카드**: 아주 옅은 웜화이트(`#FBFBFA`) 배경, 얇은 연회색(`#DDDDDD`) 외곽선, 둥근 모서리(반지름 14px). **네 변 모두 동일한 패딩 32px.**
- **행 높이**: 모든 행이 **동일하게 56px.** 행 사이 간격을 임의로 늘리거나 줄이지 않는다.
- **들여쓰기**: depth가 1 깊어질 때마다 아이콘 시작 x가 **정확히 44px씩** 오른쪽으로 이동한다.
- **아이콘–라벨 간격**: 아이콘(26px 크기) 오른쪽 끝에서 텍스트까지 **12px** 고정.
- **메인 스파인**: 카드 왼쪽에 **굵기 3px의 실선 오렌지(`#E8720C`) 세로선**이 최상위 행들을 잇는다. 첫 행, 모든 최상위 폴더 행, 마지막 최상위 행에는 스파인 위에 **채워진 오렌지 원(반지름 6px)** 을 찍는다.
- **자식 커넥터**: 폴더의 자식들은 부모 폴더 아이콘 아래에서 내려오는 **옅은 오렌지(`#F0A868`) 점선 세로선**에 매달린다. 각 자식은 짧은 점선 가로 스텁으로 연결한다. 자식 중 폴더 행에는 접점에 채워진 오렌지 원을 찍고, 파일 행은 스텁만 연결한다.
- **아이콘**: 플랫 미니멀 스타일. 폴더는 **오렌지 단색 폴더 아이콘**, 일반 텍스트/코드 파일은 **회색 아웃라인 문서 아이콘**, JSON 파일은 둥근 사각형 안 `{ }` 아이콘, 셸 스크립트는 둥근 사각형 안 `>_` 아이콘, 설정 파일은 기어(톱니) 아이콘.
- **텍스트**: 깔끔한 산세리프, 진한 회색(`#2B2B2B`), 크기 19px로 전부 동일. 폴더명만 살짝 굵게(weight 600), 파일명은 보통(weight 500). 폴더명은 `name/`처럼 끝에 슬래시를 붙인다.
- **폰트는 저작권 없는(오픈 라이선스) 폰트만 쓴다.** SIL OFL인 Inter, Noto Sans를 우선 지정하고 sans-serif로 폴백한다.
- **캔버스 크기**: 너비는 560px 기본(가장 긴 라벨이 넘치면 라벨 끝 + 32px까지 확장), 높이는 `32 + 행수 × 56 + 32`로 계산한다.

## 작업 순서

1. **트리 확정.** 입력을 정규화해 각 행의 (이름, depth, 폴더/파일, 아이콘 종류)를 정한다. 이름이 한국어면 영어로 바꾼다.
2. **이미지 프롬프트 조립.** 아래 `이미지 프롬프트 템플릿`의 ROWS를 채워 완성한다.
3. **SVG 작성.** 아래 `SVG 작성 규칙`대로 좌표를 계산해 SVG를 직접 작성하고, 작업 디렉터리에 `file-tree-<주제>.svg`로 저장한다.
4. **출력.** 영어 프롬프트 블록 + SVG 파일 경로 + 한국어 1~2문장 설명을 출력한다.

## 이미지 프롬프트 템플릿

아래 영어 템플릿의 `<...>`와 ROWS를 채워 완성한다. STRUCTURE의 행 순서가 곧 그림의 위→아래 순서다.

```text
A clean vertical file-and-folder tree diagram on a soft warm-white card with rounded corners
and a thin light-gray border, with identical generous padding on all four sides. Flat minimal
vector style, like a modern developer documentation figure.

STRUCTURE (one item per row, top to bottom; every row has exactly the same height, and each
depth level is indented by exactly the same step):
- "<name>" — <file / folder>, depth <n>, <icon: document / folder / json braces / gear / terminal>
  ... (one line per row)

CONNECTORS: a solid orange (#E8720C) vertical spine on the left links the top-level rows, with
a small filled orange circle on the spine at the first row and at every top-level folder row.
Children hang from a thin dotted light-orange vertical line dropping below their parent folder;
each child connects with a short dotted horizontal stub, and every child folder junction gets a
small filled orange dot.

ICONS: flat minimal icons to the left of each name — solid orange folder icons for directories,
thin gray outline document icons for text and code files, a rounded-square "{ }" icon for JSON
files, a small gear icon for settings files, a rounded-square ">_" icon for shell scripts.

TEXT: all file and folder names in English, in a clean open-license sans-serif font (Inter or
Noto Sans style), near-black, all the same size; folder names slightly bolder and ending with
a trailing slash.

SPACING: identical vertical spacing between all rows; identical indent step per depth; identical
gap between every icon and its label; the tree is left-aligned inside the card.

DO NOT: no title, no watermark, no shadows, no 3D, no extra decorations, no misspelled names,
no overlapping rows or connectors. 3:5 vertical aspect ratio.
```

## SVG 작성 규칙

Figma와 Canva에 문제없이 import되도록 아래를 지킨다.

- 루트는 `<svg xmlns="http://www.w3.org/2000/svg" width="..." height="..." viewBox="0 0 W H">` 하나. 외부 참조 없음.
- `rect`, `circle`, `line`, `path`, `text`만 사용한다. `<style>`, CSS class, filter, mask, clipPath, 외부 이미지·폰트 링크를 쓰지 않는다. 모든 스타일은 인라인 속성으로 넣는다.
- 점선은 `stroke-dasharray="2 5"`로 표현한다.
- 폰트는 `font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif"`로 지정한다(모두 오픈 라이선스). Canva가 폰트를 치환할 수 있으므로, 사용자가 글자 모양 고정을 원하면 Inkscape 등으로 text를 path로 변환하라고 안내한다.

좌표 계산 공식이다.

```text
PAD = 32, ROW = 56, INDENT = 44, ICON = 26, GAP = 12
height        = PAD*2 + 행수*ROW
행 i의 중심 y  = PAD + ROW/2 + i*ROW
depth d 아이콘 시작 x = 80 + d*INDENT
라벨 x        = 아이콘 시작 x + ICON + GAP
메인 스파인 x  = 56 (실선, 굵기 3)
부모 폴더의 자식 세로선 x = 부모 아이콘 시작 x + 12 (점선, 굵기 2)
```

## 예시 (gold reference)

입력 예다.

```text
package.json
src/
  index.js
  routes/
    users.js
public/
  index.html
docs/
  api.md
```

이 입력으로 만든 완성 SVG다. 새 SVG의 좌표·간격·색 기준으로 삼는다.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="560" height="568" viewBox="0 0 560 568">
  <rect x="1" y="1" width="558" height="566" rx="14" fill="#FBFBFA" stroke="#DDDDDD" stroke-width="2"/>

  <!-- main spine (top-level rows) -->
  <line x1="56" y1="60" x2="56" y2="452" stroke="#E8720C" stroke-width="3"/>
  <line x1="56" y1="60" x2="76" y2="60" stroke="#E8720C" stroke-width="3"/>
  <line x1="56" y1="116" x2="76" y2="116" stroke="#E8720C" stroke-width="3"/>
  <line x1="56" y1="340" x2="76" y2="340" stroke="#E8720C" stroke-width="3"/>
  <line x1="56" y1="452" x2="76" y2="452" stroke="#E8720C" stroke-width="3"/>
  <circle cx="56" cy="60" r="6" fill="#E8720C"/>
  <circle cx="56" cy="116" r="6" fill="#E8720C"/>
  <circle cx="56" cy="340" r="6" fill="#E8720C"/>
  <circle cx="56" cy="452" r="6" fill="#E8720C"/>

  <!-- children of src/ -->
  <line x1="92" y1="132" x2="92" y2="228" stroke="#F0A868" stroke-width="2" stroke-dasharray="2 5"/>
  <line x1="92" y1="172" x2="120" y2="172" stroke="#F0A868" stroke-width="2" stroke-dasharray="2 5"/>
  <line x1="92" y1="228" x2="120" y2="228" stroke="#F0A868" stroke-width="2" stroke-dasharray="2 5"/>
  <circle cx="92" cy="228" r="6" fill="#E8720C"/>

  <!-- children of routes/ -->
  <line x1="136" y1="244" x2="136" y2="284" stroke="#F0A868" stroke-width="2" stroke-dasharray="2 5"/>
  <line x1="136" y1="284" x2="164" y2="284" stroke="#F0A868" stroke-width="2" stroke-dasharray="2 5"/>

  <!-- children of public/ -->
  <line x1="92" y1="356" x2="92" y2="396" stroke="#F0A868" stroke-width="2" stroke-dasharray="2 5"/>
  <line x1="92" y1="396" x2="120" y2="396" stroke="#F0A868" stroke-width="2" stroke-dasharray="2 5"/>

  <!-- children of docs/ -->
  <line x1="92" y1="468" x2="92" y2="508" stroke="#F0A868" stroke-width="2" stroke-dasharray="2 5"/>
  <line x1="92" y1="508" x2="120" y2="508" stroke="#F0A868" stroke-width="2" stroke-dasharray="2 5"/>

  <!-- row 0: package.json (json icon) -->
  <rect x="80" y="49" width="24" height="22" rx="5" fill="#FFFFFF" stroke="#A8ADB3" stroke-width="2"/>
  <text x="92" y="65" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="12" font-weight="600" fill="#A8ADB3" text-anchor="middle">{ }</text>
  <text x="118" y="66" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="19" font-weight="500" fill="#2B2B2B">package.json</text>

  <!-- row 1: src/ (folder) -->
  <path d="M80 107 q0 -2 2 -2 h8 l3 3 h13 q2 0 2 2 v15 q0 2 -2 2 h-24 q-2 0 -2 -2 z" fill="#E8720C"/>
  <text x="118" y="122" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="19" font-weight="600" fill="#2B2B2B">src/</text>

  <!-- row 2: index.js (document icon) -->
  <rect x="124" y="160" width="20" height="24" rx="3" fill="#FFFFFF" stroke="#A8ADB3" stroke-width="2"/>
  <line x1="128" y1="168" x2="140" y2="168" stroke="#A8ADB3" stroke-width="1.5"/>
  <line x1="128" y1="173" x2="140" y2="173" stroke="#A8ADB3" stroke-width="1.5"/>
  <line x1="128" y1="178" x2="136" y2="178" stroke="#A8ADB3" stroke-width="1.5"/>
  <text x="162" y="178" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="19" font-weight="500" fill="#2B2B2B">index.js</text>

  <!-- row 3: routes/ (folder) -->
  <path d="M124 219 q0 -2 2 -2 h8 l3 3 h13 q2 0 2 2 v15 q0 2 -2 2 h-24 q-2 0 -2 -2 z" fill="#E8720C"/>
  <text x="162" y="234" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="19" font-weight="600" fill="#2B2B2B">routes/</text>

  <!-- row 4: users.js (document icon) -->
  <rect x="168" y="272" width="20" height="24" rx="3" fill="#FFFFFF" stroke="#A8ADB3" stroke-width="2"/>
  <line x1="172" y1="280" x2="184" y2="280" stroke="#A8ADB3" stroke-width="1.5"/>
  <line x1="172" y1="285" x2="184" y2="285" stroke="#A8ADB3" stroke-width="1.5"/>
  <line x1="172" y1="290" x2="180" y2="290" stroke="#A8ADB3" stroke-width="1.5"/>
  <text x="206" y="290" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="19" font-weight="500" fill="#2B2B2B">users.js</text>

  <!-- row 5: public/ (folder) -->
  <path d="M80 331 q0 -2 2 -2 h8 l3 3 h13 q2 0 2 2 v15 q0 2 -2 2 h-24 q-2 0 -2 -2 z" fill="#E8720C"/>
  <text x="118" y="346" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="19" font-weight="600" fill="#2B2B2B">public/</text>

  <!-- row 6: index.html (document icon) -->
  <rect x="124" y="384" width="20" height="24" rx="3" fill="#FFFFFF" stroke="#A8ADB3" stroke-width="2"/>
  <line x1="128" y1="392" x2="140" y2="392" stroke="#A8ADB3" stroke-width="1.5"/>
  <line x1="128" y1="397" x2="140" y2="397" stroke="#A8ADB3" stroke-width="1.5"/>
  <line x1="128" y1="402" x2="136" y2="402" stroke="#A8ADB3" stroke-width="1.5"/>
  <text x="162" y="402" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="19" font-weight="500" fill="#2B2B2B">index.html</text>

  <!-- row 7: docs/ (folder) -->
  <path d="M80 443 q0 -2 2 -2 h8 l3 3 h13 q2 0 2 2 v15 q0 2 -2 2 h-24 q-2 0 -2 -2 z" fill="#E8720C"/>
  <text x="118" y="458" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="19" font-weight="600" fill="#2B2B2B">docs/</text>

  <!-- row 8: api.md (document icon) -->
  <rect x="124" y="496" width="20" height="24" rx="3" fill="#FFFFFF" stroke="#A8ADB3" stroke-width="2"/>
  <line x1="128" y1="504" x2="140" y2="504" stroke="#A8ADB3" stroke-width="1.5"/>
  <line x1="128" y1="509" x2="140" y2="509" stroke="#A8ADB3" stroke-width="1.5"/>
  <line x1="128" y1="514" x2="136" y2="514" stroke="#A8ADB3" stroke-width="1.5"/>
  <text x="162" y="514" font-family="Inter, 'Noto Sans', 'DejaVu Sans', sans-serif" font-size="19" font-weight="500" fill="#2B2B2B">api.md</text>
</svg>
```

한국어 한 줄 설명 예: Node.js 웹 프로젝트 트리 9행을 행 높이 56px·들여쓰기 44px 고정 규칙으로 배치했고, 최상위는 오렌지 실선 스파인, 자식은 점선 커넥터로 연결했습니다.

## 완료 전 확인

- 행 높이(56px), 들여쓰기(44px), 아이콘–라벨 간격(12px), 카드 패딩(32px)을 모든 행에 동일하게 적용했는가?
- 그림 속 모든 이름이 영어인가? 트리를 15행 이내로 다듬었는가?
- 폴더는 오렌지 폴더 아이콘 + 끝 슬래시, 파일은 종류에 맞는 아웃라인 아이콘인가?
- 스파인/커넥터 규칙(실선 스파인 + 폴더 접점 오렌지 원 + 자식 점선)을 지켰는가?
- SVG가 단일 루트, 인라인 속성, 외부 참조 없음, 오픈 라이선스 폰트 지정 조건을 만족하는가?
- 이미지 프롬프트를 복사해 바로 쓸 수 있는 한 블록으로 출력하고, SVG 파일 경로를 알려줬는가?
