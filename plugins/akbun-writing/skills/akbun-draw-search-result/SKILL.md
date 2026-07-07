---
name: akbun-draw-search-result
description: >
  내용·이미지를 받아 웹브라우저 검색결과 화면(검색바, 탭, 주황 테두리 추천 스니펫, 검색결과 목록) 스타일
  그림을 만드는 두 가지 산출물을 생성한다. (1) GPT image나 nano-banana 같은 이미지 생성 모델에 그대로
  붙여넣을 영어 프롬프트, (2) Figma나 Canva로 가져갈 수 있는 SVG 코드. 사용자가 검색어·스니펫 문구를 주지
  않으면 내용을 분석해 skill이 문구를 만든다.
  Trigger on: "검색결과 그림", "검색결과 스타일 이미지", "구글 검색 스타일", "검색화면 이미지",
  "추천 스니펫 그림", "search result image", "SERP illustration",
  or any request to draw content as a web search results page.
---

# 검색결과 화면 스타일 이미지 프롬프트 + SVG 생성

## 이 skill이 하는 일

개념이나 문장을 **웹브라우저 검색결과 화면 한 장**으로 보여주는 그림을 만든다. 검색바에 질문이 있고,
그 답이 주황 테두리 **추천 스니펫(원박스)** 안에 형광펜 강조로 들어 있으며, 아래에 일반 검색결과가
이어지는 화면이다. "검색하면 이렇게 나온다"는 형식 자체가 개념을 정의처럼 각인시키기 때문에, 블로그
도입부·용어 정의 카드·발표 슬라이드에 어울린다.

이 skill은 그림을 직접 그리지 않는다. 항상 두 가지 산출물을 만든다.

1. **영어 이미지 생성 프롬프트** — GPT image, nano-banana 같은 이미지 생성 모델에 그대로 붙여넣는다.
2. **SVG 코드** — Figma나 Canva에 import해 직접 편집할 수 있는 벡터 파일이다. 이미지 모델이 한국어
   글자를 틀리게 그릴 때, SVG가 글자 깨짐 없는 대안이 된다.

`akbun-generateimage-code`(코드 figure), `akbun-draw-sketchbook-card`(개념 카드)와 짝이 되는
"검색결과 화면" 버전이다.

## 결과물 형식

항상 세 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 코드 블록 하나에 담아 그대로 복사할 수 있게 한다.
2. **SVG 코드** — 코드 블록 하나에 담고, 파일로 저장을 요청받으면 `.svg` 파일로도 저장한다.
3. **한국어 한 줄 설명** — 어떤 검색어와 스니펫 문구를 만들었는지 1~2문장.

## 입력 다루기

- **검색어·스니펫·결과 문구가 이미 있으면 그대로 쓴다.** 사용자가 적어준 문구는 요약하거나 다듬지 않는다.
- **주제나 글, 이미지만 있으면 skill이 문구를 만든다.** 내용을 분석해 (1) 질문형 검색어 한 줄,
  (2) 정의형 답변 문장 1~2줄과 그 안에서 강조할 핵심 구절, (3) 그럴듯한 출처·일반 결과 2개를 만든다.
- **검색어는 질문형**으로 만든다. "~가 무엇인가요", "~는 어떻게 하나요"처럼 사용자가 실제로 검색할 법한
  문장이어야 화면이 자연스럽다.
- **스니펫 답변은 정의 문장**으로 만든다. "X란 ~하는 Y입니다." 골격이 기본이고, 강조 구절은 정의의
  핵심(동작·범위·차별점)을 담은 연속된 한 구절로 고른다.
- **일반 결과 2개는 성격을 다르게** 만든다. 예: 공식 문서/블로그 하나 + 위키·커뮤니티 하나. 실존하지 않는
  사이트여도 되지만 URL 형태(`https://... › path`)는 지킨다.

## 레이아웃 (레퍼런스에 고정)

모든 산출물(프롬프트와 SVG 모두)은 아래 배치를 그대로 따른다. 배치와 상하좌우 간격은 바꾸지 않는다.

- **바깥 프레임**: 흰 배경 위에 얇은 진회색 둥근 사각형 테두리 하나가 화면 전체를 감싼다. 캔버스와 프레임
  사이 여백은 사방 모두 캔버스 짧은 변의 약 5%다. 비율은 가로형 약 5:4다.
- **헤더 행** (프레임 안 최상단): 왼쪽에 검색엔진 워드마크, 오른쪽으로 완전히 둥근 알약형 검색바.
  검색바 안 왼쪽에 검색어, 오른쪽 끝에 아이콘 5개(✕ 지우기, 세로 구분선, 키보드, 마이크, 렌즈)와
  파란 돋보기가 나란히 있다.
- **탭 행** (헤더 아래): `전체 동영상 이미지 쇼핑 뉴스 도서 웹 ⋮ 더보기`가 왼쪽 정렬로 늘어서고,
  첫 탭(전체)만 파란색 + 밑줄로 활성 표시한다. 탭 행 아래에 아주 연한 가로 구분선이 프레임 폭 전체를
  가로지른다.
- **추천 스니펫 박스** (탭 아래, 이 그림의 주인공): 본문 폭의 약 95%를 차지하는 둥근 사각형을
  **주황색(#E8710A) 굵은 테두리**로 두른다. 안에는 굵은 글씨의 답변 문장 1~2줄이 있고, 핵심 구절 위에
  연회색 형광펜 하이라이트가 칠해져 있다. 문장 끝에 작은 회색 날짜가 붙는다.
- **스니펫 출처** (박스 바로 아래): 원형 파비콘(사이트 이니셜 한 글자) + 사이트 이름 / URL 경로
  (`https://... › path` + ⋮) 두 줄, 그 아래 큰 파란색 문서 제목 한 줄.
- **피드백 행** (출처 아래): 가는 점선 구분선이 본문 왼쪽에서 약 65% 지점까지 이어지고, 점선 오른쪽에
  작은 회색 텍스트 `? 추천 스니펫 정보 • ⚑ 의견`이 붙는다.
- **일반 검색결과 2개** (아래로 차례대로): 각 결과는 원형 파비콘 + 사이트 이름 / URL 두 줄 → 파란 제목
  한 줄 → 회색 스니펫 1~2줄(날짜로 시작, `2024. 8. 21. —` 또는 `5일 전 —` 형태) 순서다. 결과 사이
  세로 간격은 넉넉하게 둔다.
- **읽는 순서**: 검색바(질문) → 주황 박스(답) → 아래 결과들. 시선이 위에서 아래로 한 번에 흐른다.

## 비주얼 스타일 (레퍼런스에 고정)

- **배경/프레임**: 흰 배경, 진회색(#202124) 얇은 프레임 테두리.
- **검색바**: 흰 채움 + 연회색(#DFE1E5) 테두리의 알약형. 그림자는 쓰지 않는다.
- **텍스트 색**: 본문 검정(#202124), 결과 제목 파랑(#1A0DAB), 활성 탭·돋보기 파랑(#1A73E8/#4285F4),
  URL·스니펫 회색(#4D5156), 날짜·보조 회색(#70757A), 비활성 탭·아이콘 회색(#5F6368).
- **추천 스니펫**: 주황(#E8710A) 테두리, 채움 없음. 답변은 굵은 글씨, 핵심 구절 뒤에 연회색(#E2E2E2)
  형광펜 사각형.
- **파비콘**: 단색 원 안에 흰색 이니셜 한 글자. 로고를 그리지 않는다(이미지 모델이 로고를 일관되게
  그리지 못한다).
- **전체 톤**: 실제 스크린샷처럼 깔끔하고 대비가 높으며 여백이 넉넉하다. 장식 요소를 더하지 않는다.

## 폰트 규칙

- 저작권 걱정이 없는 폰트만 쓴다. 기본은 **Noto Sans KR**(SIL OFL)이고, `Pretendard`(OFL)로 바꿔도 된다.
- SVG에는 `font-family="'Noto Sans KR','Noto Sans',sans-serif"`처럼 fallback까지 지정한다. Figma/Canva에
  같은 이름의 폰트가 설치되어 있어야 그대로 보인다.
- 이미지 프롬프트에는 폰트 이름 대신 "clean geometric sans-serif (like Noto Sans)"로 스타일만 지정한다.

## SVG 작성 규칙 (Figma/Canva 호환)

- 기준 캔버스는 `viewBox="0 0 1200 940"`이다. 아래 예시 SVG의 좌표를 그대로 쓰고 텍스트만 바꾸는 것이
  기본이다. 줄 수가 늘어나 좌표를 옮길 때도 요소 간 간격 비율은 유지한다.
- `<rect>`, `<circle>`, `<line>`, `<path>`, `<text>`만 쓴다. **filter, mask, foreignObject, 외부 이미지,
  웹폰트 `@import`는 쓰지 않는다** — Figma/Canva import에서 깨지는 대표 원인이다.
- 형광펜 하이라이트는 텍스트 **앞에** 그린 연회색 `<rect>`다. 폭은 대략 `글자 수 × font-size`로 잡고,
  렌더링해 볼 수 있으면 확인 후 조정한다.
- 완성 SVG는 가능하면 브라우저나 렌더러로 한 번 확인한다.

전체 gold reference SVG는 이 skill의 `assets/example-search-result.svg`에 있다. 새 SVG를 만들 때 이
파일을 읽어 텍스트 슬롯만 바꾸는 방식을 우선한다.

## 작업 순서

1. **입력 파악.** 검색어·스니펫·결과 문구가 있으면 그대로 쓰고, 없으면 내용(글·이미지)을 분석해 만든다.
2. **문구 확정.** 질문형 검색어, 정의형 답변(강조 구절 포함), 출처 1개, 일반 결과 2개를 확정한다.
   답변은 2줄, 스니펫은 결과당 2줄을 넘기지 않는다.
3. **이미지 프롬프트 조립.** 아래 `프롬프트 템플릿`의 슬롯을 채운다. 그림에 들어갈 모든 텍스트는
   `reading exactly: "..."`로 철자까지 지정한다.
4. **SVG 조립.** `assets/example-search-result.svg`를 바탕으로 텍스트와 하이라이트 폭을 바꾼다.
5. **출력.** 영어 프롬프트 블록 + SVG 블록 + 한국어 한 줄 설명을 출력한다.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. 검색엔진 워드마크는 사용자가 지정하지 않으면 `Google`을 쓴다.

```text
A clean illustration of a web search results page, drawn like a crisp browser screenshot,
inside a thin dark rounded-rectangle frame on a white background. Landscape, about 5:4.

HEADER ROW (top of the frame): the search engine wordmark on the left, reading exactly:
"<ENGINE NAME>". To its right, a fully rounded pill-shaped search bar with a thin light-gray
outline. Inside the pill, left-aligned, the search query reading exactly: "<QUERY>". At the
right end of the pill, small gray icons in a row: a clear "x", a thin vertical divider, a
keyboard icon, a microphone icon, a camera lens icon, and a blue magnifying glass.

TAB ROW (below the header): small left-aligned category tabs reading exactly:
"전체  동영상  이미지  쇼핑  뉴스  도서  웹  ⋮ 더보기". Only the first tab is active: blue text
with a short blue underline. A very light horizontal divider line runs across the frame below
the tabs.

FEATURED SNIPPET (below the tabs, the hero of the image): a wide rounded rectangle outlined in
bold orange (#E8710A), no fill, spanning almost the full content width. Inside, a bold answer
sentence over <1-2> lines, reading exactly: "<ANSWER SENTENCE>". The key phrase
"<HIGHLIGHT PHRASE>" is marked with a light-gray highlighter background, like a marker pen.
At the end of the sentence, a small gray date reading exactly: "<DATE>".

SNIPPET SOURCE (directly below the box): a small solid-color circle favicon with the white
letter "<INITIAL 1>", next to it two small lines — the site name reading exactly: "<SITE 1>"
and the URL breadcrumb reading exactly: "<URL 1>" with a tiny ⋮ at the end — then below, a
larger blue link title reading exactly: "<TITLE 1>".

FEEDBACK ROW: a fine dotted divider line from the left edge of the content to about 65% of its
width; to the right of it, tiny gray text with a small circled "?" icon and a small flag icon,
reading exactly: "추천 스니펫 정보 • 의견".

ORGANIC RESULTS (two results stacked below, with generous vertical spacing). Each result has:
a solid-color circle favicon with a white initial, the site name, a gray URL breadcrumb with a
tiny ⋮, a larger blue link title, and one or two lines of gray snippet text starting with a
gray date.
Result 2 — favicon letter "<INITIAL 2>", site name reading exactly: "<SITE 2>", URL reading
exactly: "<URL 2>", title reading exactly: "<TITLE 2>", snippet reading exactly: "<SNIPPET 2>".
Result 3 — favicon letter "<INITIAL 3>", site name reading exactly: "<SITE 3>", URL reading
exactly: "<URL 3>", title reading exactly: "<TITLE 3>", snippet reading exactly: "<SNIPPET 3>".

STYLE: flat vector screenshot style, white background, black body text (#202124), blue link
titles (#1A0DAB), gray URLs and snippets (#4D5156), clean geometric sans-serif lettering
(like Noto Sans), high contrast, generous spacing, very legible.

DO NOT: misspell or alter any of the quoted text. No browser chrome beyond the described frame
(no address bar, no scrollbars, no ads). No site logos — favicons are plain letter circles.
No extra text beyond what is listed above. No drop shadows, no watermarks.
```

## 예시 (gold reference)

이 예시는 위 레이아웃과 스타일을 그대로 적용한 완성본이다. 새 산출물의 품질 기준으로 삼는다.

입력 예:

```text
쿠버네티스 파드 개념을 블로그 도입부에 쓸 검색결과 화면으로 만들어 주세요.
```

skill이 한 판단: 문구가 없으므로 skill이 만들었다. 검색어는 질문형 "쿠버네티스에서 파드가 무엇인가요",
답변은 정의형 한 문장으로 하고 핵심 구절 "쿠버네티스에서 생성하고 관리할 수 있는 배포 가능한 가장 작은
컴퓨팅 단위"에 형광펜을 칠했다. 출처는 공식 문서, 일반 결과는 기술 블로그 + 위키로 성격을 나눴다.

출력 이미지 프롬프트:

```text
A clean illustration of a web search results page, drawn like a crisp browser screenshot,
inside a thin dark rounded-rectangle frame on a white background. Landscape, about 5:4.

HEADER ROW (top of the frame): the search engine wordmark on the left, reading exactly:
"Google". To its right, a fully rounded pill-shaped search bar with a thin light-gray outline.
Inside the pill, left-aligned, the search query reading exactly: "쿠버네티스에서 파드가
무엇인가요". At the right end of the pill, small gray icons in a row: a clear "x", a thin
vertical divider, a keyboard icon, a microphone icon, a camera lens icon, and a blue
magnifying glass.

TAB ROW (below the header): small left-aligned category tabs reading exactly:
"전체  동영상  이미지  쇼핑  뉴스  도서  웹  ⋮ 더보기". Only the first tab is active: blue text
with a short blue underline. A very light horizontal divider line runs across the frame below
the tabs.

FEATURED SNIPPET (below the tabs, the hero of the image): a wide rounded rectangle outlined in
bold orange (#E8710A), no fill, spanning almost the full content width. Inside, a bold answer
sentence over two lines, reading exactly: "파드란 쿠버네티스에서 생성하고 관리할 수 있는 배포
가능한 가장 작은 컴퓨팅 단위입니다.". The key phrase "쿠버네티스에서 생성하고 관리할 수 있는
배포 가능한 가장 작은 컴퓨팅 단위" is marked with a light-gray highlighter background, like a
marker pen. At the end of the sentence, a small gray date reading exactly: "2023. 5. 12.".

SNIPPET SOURCE (directly below the box): a small solid-color circle favicon with the white
letter "K", next to it two small lines — the site name reading exactly: "Kubernetes Docs" and
the URL breadcrumb reading exactly: "https://kubernetes.io › docs › concepts" with a tiny ⋮ at
the end — then below, a larger blue link title reading exactly: "파드(Pod) 개념 이해하기".

FEEDBACK ROW: a fine dotted divider line from the left edge of the content to about 65% of its
width; to the right of it, tiny gray text with a small circled "?" icon and a small flag icon,
reading exactly: "추천 스니펫 정보 • 의견".

ORGANIC RESULTS (two results stacked below, with generous vertical spacing). Each result has:
a solid-color circle favicon with a white initial, the site name, a gray URL breadcrumb with a
tiny ⋮, a larger blue link title, and one or two lines of gray snippet text starting with a
gray date.
Result 2 — favicon letter "C", site name reading exactly: "cloudlab.kr", URL reading exactly:
"https://cloudlab.kr › ... › 쿠버네티스 기술 블로그", title reading exactly: "쿠버네티스 파드
완벽 가이드 - 클라우드랩", snippet reading exactly: "2024. 8. 21. — 파드 안에 컨테이너를
배치하는 기준. 2. 사이드카 패턴으로 로그를 모으는 방법. 3. 파드와 디플로이먼트의 정의와 정확한
차이.".
Result 3 — favicon letter "W", site name reading exactly: "위키백과", URL reading exactly:
"https://ko.wikipedia.org › wiki › 쿠버네티스", title reading exactly: "쿠버네티스", snippet
reading exactly: "5일 전 — 쿠버네티스는 컨테이너화된 애플리케이션의 배포와 스케일링을
자동화하는 오픈소스 플랫폼으로, 컨테이너 오케스트레이션의 사실상 표준이며 ...".

STYLE: flat vector screenshot style, white background, black body text (#202124), blue link
titles (#1A0DAB), gray URLs and snippets (#4D5156), clean geometric sans-serif lettering
(like Noto Sans), high contrast, generous spacing, very legible.

DO NOT: misspell or alter any of the quoted text. No browser chrome beyond the described frame
(no address bar, no scrollbars, no ads). No site logos — favicons are plain letter circles.
No extra text beyond what is listed above. No drop shadows, no watermarks.
```

출력 SVG: 같은 내용의 완성 SVG가 `assets/example-search-result.svg`에 있다. 실제 출력 시에는 이 파일
내용을 코드 블록으로 함께 보여준다.

한국어 한 줄 설명: 파드 개념을 질문형 검색어와 주황 박스 속 정의 문장으로 바꾸고, 핵심 구절에 형광펜을
칠한 검색결과 화면을 이미지 프롬프트와 Figma/Canva용 SVG로 만들었습니다.

## 완료 전 확인

- 사용자가 준 문구를 바꾸지 않고 그대로 넣었는가? (문구가 없을 때만 skill이 만든다)
- 프롬프트와 SVG가 같은 텍스트를 담고 있는가?
- 그림 속 모든 텍스트를 프롬프트에 `reading exactly: "..."`로 철자까지 지정했는가?
- 레이아웃 순서(헤더 → 탭 → 주황 스니펫 박스 → 출처 → 점선 피드백 행 → 일반 결과 2개)와 넉넉한
  상하좌우 간격을 지켰는가?
- SVG에 filter/mask/foreignObject/외부 이미지 없이 기본 도형과 텍스트만 썼는가? 폰트는 Noto Sans KR 등
  저작권 없는 폰트로 지정했는가?
- 프롬프트와 SVG를 각각 그대로 복사할 수 있는 한 블록으로 출력했는가?
