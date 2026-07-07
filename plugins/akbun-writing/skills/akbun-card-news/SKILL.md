---
name: akbun-card-news
description: >
  사용자가 준 이미지와 글(또는 주제)로 세로형 카드뉴스(표지+내용 페이지)를 구성하고,
  각 페이지의 사진을 만들 이미지 생성 AI 프롬프트와 Figma/Canva로 가져갈 수 있는
  페이지별 SVG를 생성한다.
---

# 카드뉴스 생성

## 이 skill이 하는 일

사용자가 준 이미지와 글을 SNS용 세로형(4:5) **카드뉴스**로 만든다. 카드뉴스는 사진 위에 헤드라인이 올라간 **표지 1장**과, 베이지 배경 위에 인용문·사진·캡션이 배치된 **내용 페이지 여러 장**으로 구성된다. 레이아웃과 상하좌우 간격은 `references/layout-spec.md`에 고정되어 있으며 임의로 바꾸지 않는다.

결과물은 완성 이미지가 아니라 세 가지 산출물이다.

1. **카드 구성안** — 페이지별로 어떤 유형(표지/인용/사진+캡션)에 어떤 텍스트가 들어가는지 정리한 표
2. **이미지 생성 AI 프롬프트** — 사진이 필요한 페이지마다, GPT image나 nano-banana 같은 이미지 생성 모델에 그대로 붙여넣을 영어 프롬프트
3. **페이지별 SVG 파일** — Figma나 Canva에 import해 편집을 이어갈 수 있는 SVG. `assets/`의 템플릿을 기반으로 텍스트를 채워 생성한다

## 입력 다루기

- **글을 줬으면 그대로 쓴다.** 사용자가 준 헤드라인, 인용문, 캡션은 문구를 바꾸지 않고 페이지에 배치만 한다. 줄 수 제한을 넘으면 글을 줄이지 말고 페이지를 나눈다.
- **글이 없으면 skill이 글을 만든다.** 사용자가 준 이미지·자료·주제를 분석해 표지 헤드라인(질문형 권장), 서브 문단, 내용 페이지의 질문 라벨·인용문·캡션을 먼저 작성한다. 작성한 글로 바로 이미지 프롬프트와 SVG 작업까지 진행한다.
- **이미지를 줬으면 그 이미지를 쓸 자리를 정한다.** 사용자가 준 사진은 표지 배경이나 내용 페이지 사진 자리에 배치하고, 그 페이지는 이미지 생성 프롬프트를 만들지 않는다. 사진이 부족한 페이지에만 프롬프트를 만든다.

## 페이지 유형

카드뉴스는 아래 네 유형을 조합한다. 각 유형의 정확한 좌표·크기·폰트 크기는 `references/layout-spec.md`를 따른다.

- **표지 (cover)**: full-bleed 사진 + 어두운 오버레이 위에 왼쪽 상단 헤드라인(serif, 밝은 색)과 서브 문단. 항상 1페이지.
- **인용 카드 — 사진 포함 (quote-photo)**: 베이지 배경, 우측 상단 사진, 하단에 질문 라벨 + 왼쪽으로 매달린 따옴표가 있는 큰 serif 인용문 + 출처(이름 bold, 직함).
- **인용 카드 — 텍스트 전용 (quote-only)**: 사진 없이 질문 라벨이 맨 위로 올라가고 인용문이 페이지를 채운다. 인용문이 길 때 사용.
- **사진 + 캡션 (photo-caption)**: 상단 큰 사진 + 하단 sans 설명 문단. 현장·상황 설명에 사용.

기본 구성은 표지 1장 + 내용 2~4장이다. 인용 카드와 사진+캡션 카드를 번갈아 배치하면 리듬이 좋다.

## 폰트 규칙

저작권 걱정 없는 오픈 라이선스 폰트만 쓴다.

- **serif (헤드라인·인용문)**: Noto Serif KR — SIL OFL
- **sans (라벨·캡션·출처)**: Pretendard — SIL OFL, 대체로 Noto Sans KR

SVG의 `font-family`에는 위 폰트를 지정하고, 사용자에게 Figma/Canva에서 같은 폰트를 설치·선택해야 동일하게 보인다는 점을 알려준다.

## 이미지 생성 프롬프트 규칙

사진이 필요한 페이지마다 영어 프롬프트를 하나씩 만든다.

- **비율을 명시한다.** 표지는 4:5 세로, 내용 페이지 사진은 배치 영역 비율(quote-photo는 약 5:4 가로, photo-caption은 약 4:3 가로)을 적는다.
- **톤을 통일한다.** 전체 카드뉴스가 한 세트로 보이도록 모든 프롬프트에 같은 무드를 적는다. 기본 무드는 따뜻하고 차분한 다큐멘터리 필름 사진(muted warm tones, soft natural light, documentary film photography style)이며, 베이지 배경(#E8E0D1)과 어울려야 한다.
- **텍스트 없는 사진을 요구한다.** 글자는 SVG 레이어가 담당하므로 프롬프트에 `no text, no watermark`를 넣는다.
- **표지 사진은 텍스트 자리를 비운다.** 상단 1/3은 단순한 배경(벽, 하늘 등)이 되도록 장면을 지시한다.

## SVG 생성 규칙 (Figma/Canva 연동)

페이지마다 SVG 파일을 하나씩 만든다. `assets/`의 템플릿을 읽고 텍스트와 좌표를 교체해 사용자의 작업 디렉터리에 `card-01-cover.svg`, `card-02-quote.svg`처럼 페이지 순서로 저장한다.

- SVG 1.1 문법만 쓴다. `viewBox="0 0 1080 1350"`, `<rect>`·`<text>`·`<tspan>`·`<image>`만 사용하고 `foreignObject`, CSS 클래스, 외부 리소스 참조는 쓰지 않는다.
- 텍스트는 outline으로 바꾸지 않고 `<text>`로 남긴다. Figma/Canva에서 텍스트 레이어로 편집할 수 있어야 한다.
- 자동 줄바꿈이 없으므로 `references/layout-spec.md`의 글자 수 기준으로 줄을 나눠 `<tspan>`을 배치한다. 어절 중간에서 끊지 않는다.
- 사진 자리는 `id="photo-placeholder"`인 회색 `<rect>`로 남긴다. 사용자가 이미지 파일을 이미 줬고 로컬 경로가 있으면, rect 대신 base64 data URI를 넣은 `<image>`로 교체해도 된다(Figma는 지원, Canva는 래스터화될 수 있음을 안내).
- 각 요소의 `id`는 템플릿의 것을 유지한다. Figma에서 레이어 이름으로 남는다.

## 작업 순서

1. **입력 파악.** 사용자가 준 글·이미지·주제를 확인하고, 글이 없으면 글부터 작성한다.
2. **페이지 구성.** 표지 1장 + 내용 페이지 유형과 순서를 정하고 구성안 표를 만든다.
3. **줄바꿈 설계.** 각 텍스트를 layout-spec의 글자 수 기준으로 줄 단위로 나눈다. 최대 줄 수를 넘으면 페이지를 나눈다.
4. **이미지 프롬프트 작성.** 사진이 필요한 페이지마다 통일된 무드의 영어 프롬프트를 만든다.
5. **SVG 생성.** 템플릿 기반으로 페이지별 SVG 파일을 저장한다.
6. **출력.** 구성안 표 + 프롬프트 블록들 + 생성한 SVG 파일 경로 목록 + 폰트 안내를 출력한다.

## 예시 (gold reference)

동네 카페 로스터 인터뷰를 카드뉴스로 만드는 예다. 새 카드뉴스의 품질 기준으로 삼는다.

입력 예:

```text
어라운드 커피 로스터 김하늘 인터뷰로 카드뉴스 만들어줘.
인터뷰 내용: 원두는 볶기 전에 생두 냄새부터 맡는다, 산지가 같아도 해마다 향이 달라서
그 차이를 기록하는 게 일의 절반이다. 지난봄에 이웃 스무 명과 로스팅 클래스를 열었다.
```

skill이 만든 구성안:

| 페이지 | 유형 | 내용 |
|---|---|---|
| 1 | cover | 헤드라인 "좋은 원두는 어떻게 고르나요?" + 서브 "10년 차 로스터 김하늘 님을 만나…" |
| 2 | quote-photo | 라벨 "원두는 어떻게 고르나요?" + 인용 "볶기 전에 생두 냄새부터 맡아요…" — 김하늘, 로스터 |
| 3 | photo-caption | 로스팅 클래스 사진 + 캡션 "지난봄, 어라운드 커피는 작은 로스팅 클래스를 열어…" |

2페이지 사진의 이미지 생성 프롬프트 예:

```text
A candid documentary photograph of a coffee roaster in an apron, standing beside a small
drum coffee roasting machine, holding a handful of green coffee beans up to smell them.
Warm muted tones, soft natural window light, shallow depth of field, film photography
style. The photo should pair well with a warm beige (#E8E0D1) editorial layout.
Landscape 5:4 aspect ratio. No text, no watermark.
```

SVG는 `assets/quote-photo-template.svg`의 텍스트를 위 문구로 채워 `card-02-quote.svg`로 저장한다. 완성된 템플릿 예시는 `assets/` 폴더의 네 파일을 그대로 참고한다.

## 완료 전 확인

- 사용자가 준 글을 바꾸지 않고 그대로 배치했는가? (글이 없을 때만 skill이 작성)
- 레이아웃 좌표·간격·폰트 크기가 `references/layout-spec.md`와 일치하는가?
- 모든 페이지가 1080x1350(4:5)이고 색 토큰(#E8E0D1, #211D1A, #F4EFE6)을 지켰는가?
- 폰트가 Noto Serif KR / Pretendard(오픈 라이선스)로 지정되어 있는가?
- 이미지 프롬프트가 비율·통일된 무드·`no text, no watermark`를 포함하는가?
- SVG가 Figma/Canva에서 열리는 문법(SVG 1.1, text/tspan, foreignObject 없음)인가?
- 인용문·캡션 줄바꿈이 어절 단위이고 최대 줄 수를 넘지 않는가?
