---
name: akbun-cardnews-b
description: >
  사용자의 글과 이미지(또는 주제만)로 인스타그램 카드뉴스 표지·내용 페이지를 구성하고,
  이미지 생성 AI agent용 영어 프롬프트와 Figma/Canva에서 편집 가능한 SVG를 만든다.
---

# 카드뉴스 생성 (표지 + 내용 페이지 + 이미지 프롬프트 + SVG)

## 이 skill이 하는 일

사용자가 준 글과 이미지를 고정 레이아웃의 인스타그램 카드뉴스로 만든다. 표지 한 장과 내용 페이지 여러 장으로 구성되며, 결과물은 세 가지다: 카드뉴스 카피(구성안), 배경 사진을 만들 이미지 생성 AI agent용 프롬프트, 그리고 Figma나 Canva로 가져가 편집할 수 있는 SVG 파일.

레이아웃은 `references/layout-spec.md`에 고정되어 있다.

- **표지**: 사진 전체 채움(full-bleed) + 왼쪽 위 브랜드 마크 + 왼쪽 아래 2줄 큰 흰색 제목 + 아래 중앙 핸들
- **내용 페이지**: 상단 50% 사진 + 하단 50% 검정 패널(번호 제목 + 본문 문단, 핵심 문장은 굵게 + 밑줄)

## 결과물

항상 세 가지를 출력한다.

1. **카드뉴스 구성안** — 표지 제목(2줄), 각 내용 페이지의 번호 제목·본문·강조 문장을 한국어로 정리한 표 또는 목록.
2. **이미지 생성 프롬프트** — 페이지별 배경 사진을 만드는 영어 프롬프트. 코드 블록 하나에 한 페이지씩, 그대로 복사해 이미지 생성 AI agent에 붙여넣을 수 있게 한다.
3. **SVG 파일** — `cover.svg`, `page-01.svg`, `page-02.svg`, … 형태로 작업 디렉터리에 생성한다.

## 입력 다루기

- **글을 줬으면 그대로 쓴다.** 사용자의 문장을 요약하거나 다듬지 않고 레이아웃에 맞게 줄만 나눈다. 페이지 분량을 넘치면 페이지를 나눈다.
- **글 없이 주제·자료(이미지, 링크, 메모)만 줬으면 skill이 카피를 쓴다.** 내용을 분석해 표지 제목과 내용 페이지 본문을 만들고, 그 다음 이미지 프롬프트·SVG 작업까지 진행한다. 카피는 짧은 단문 위주로, 페이지마다 핵심 문장 1개를 강조 처리한다.
- **이미지를 줬으면 배경 사진으로 쓴다.** 이 경우 해당 페이지의 이미지 생성 프롬프트는 생략하고, SVG에 이미지를 넣는다.
- **이미지가 없으면 이미지 생성 프롬프트로 대신한다.** SVG에는 placeholder를 남긴다.

## 작업 순서

1. **입력 파악.** 글/이미지/주제 중 무엇이 있는지 확인한다. 글이 없으면 카피를 먼저 만든다.
2. **페이지 설계.** 표지 1장 + 내용 페이지 N장으로 나눈다. 내용 페이지는 `1.`, `2.`, … 번호 제목을 붙이고, 페이지당 문단 2~3개로 제한한다.
3. **구성안 출력.** 페이지별 제목·본문·강조 문장을 정리해 보여준다.
4. **이미지 프롬프트 작성.** 이미지가 없는 페이지마다 아래 `이미지 프롬프트 규칙`에 따라 영어 프롬프트를 만든다.
5. **SVG 생성.** `assets/cover-template.svg`, `assets/content-template.svg`를 복사한 뒤 `references/layout-spec.md`의 좌표를 지키며 텍스트를 교체한다.
6. **출력.** 구성안 + 프롬프트 + 생성한 SVG 파일 경로를 정리해 알려준다.

## 이미지 프롬프트 규칙

- 프롬프트는 **영어**로 쓰고, 페이지당 코드 블록 하나로 출력한다.
- 사진 안에 **글자를 넣지 않는다**. 텍스트는 전부 SVG 레이어가 담당한다.
- **표지 사진**: 세로형 4:5. 피사체를 중앙~오른쪽에 배치하고, **왼쪽 위(로고 자리)와 왼쪽 아래(제목 자리)는 비교적 비어 있게** 구도를 지정한다. 따뜻한 톤의 인물·사물 에디토리얼 사진이 기본이다.
- **내용 페이지 사진**: 가로로 잘리는 상단 절반(1080×675, 8:5)에 맞게, 피사체가 프레임 세로 중앙에 오는 구도를 지정한다.
- 프롬프트 끝에 공통 제약을 붙인다: `no text, no watermark, no logo in the photo`.

표지 프롬프트 뼈대는 다음과 같다.

```text
Editorial portrait photograph, 4:5 vertical. <SUBJECT AND SCENE — one or two sentences>.
The subject is positioned center-right; the upper-left and lower-left areas of the frame
stay clean and uncluttered to leave room for overlaid text. Warm natural tones, soft
window light, shallow depth of field. no text, no watermark, no logo in the photo.
```

## SVG 생성 규칙 (Figma/Canva 호환)

- 캔버스는 `viewBox="0 0 1080 1350"` 고정. 좌표·크기·여백은 `references/layout-spec.md`를 그대로 따른다.
- **텍스트는 `<text>`/`<tspan>`으로만** 넣는다. `foreignObject`, 외부 CSS, `@font-face` import는 Figma가 지원하지 않으므로 쓰지 않는다.
- **밑줄 강조는 `<line>`으로 직접 긋는다** (`text-decoration`은 가져오기 시 유실될 수 있다). 밑줄 길이는 강조 텍스트 폭에 맞춘다.
- 폰트는 저작권 무료 폰트만 지정한다: `font-family="Pretendard, 'Noto Sans KR', sans-serif"` (둘 다 SIL OFL).
- 사용자 이미지 파일이 있으면 base64 data URI로 `<image ... preserveAspectRatio="xMidYMid slice">`에 임베드한다. 없으면 템플릿의 placeholder `rect`를 남기고, Figma/Canva에서 교체하라고 안내한다.
- 파일명은 `cover.svg`, `page-01.svg`, `page-02.svg`, … 로 저장한다.

## 예시 (gold reference)

이 예시는 이 skill의 품질 기준이다. 템플릿(`assets/`)에도 같은 예시가 들어 있다.

입력 예는 주제만 있는 경우다.

```text
"메모 습관" 주제로 카드뉴스 만들어줘. 계정명은 akbun.
```

skill이 한 판단: 글이 없으므로 카피를 직접 썼다. 표지 제목은 짧은 첫 줄 + 긴 둘째 줄 구성인 "메모를 / 시작했습니다"로 잡았다. 내용 페이지 1은 제목 "1. 기록이 기억을 이긴다"에 문단 3개를 넣고, 문단마다 핵심 문장("이제는 적어두는 사람이 이긴다.", "생각은 사라지지만 기록은 남는다.")을 굵게 + 밑줄로 강조했다. 이미지가 없으므로 표지 사진 프롬프트를 만들었다.

표지 사진 프롬프트 출력 예다.

```text
Editorial portrait photograph, 4:5 vertical. A person at a wooden desk by a window,
pausing with a pen over an open notebook, seen from a slight side angle. The subject is
positioned center-right; the upper-left and lower-left areas of the frame stay clean and
uncluttered to leave room for overlaid text. Warm natural tones, soft window light,
shallow depth of field. no text, no watermark, no logo in the photo.
```

SVG 출력은 `assets/cover-template.svg`(표지)와 `assets/content-template.svg`(내용 페이지 1)를 이 카피로 채운 것과 같다.

## 완료 전 확인

- 사용자가 준 글을 바꾸지 않고 그대로 넣었는가? (주제만 받았을 때만 skill이 카피를 쓴다)
- 레이아웃 좌표·여백·폰트 크기가 `references/layout-spec.md`와 일치하는가?
- 사진 프롬프트에 텍스트 금지와 여백(로고·제목 자리) 구도를 지정했는가?
- SVG가 `<text>`/`<tspan>`/`<line>`만 쓰고, 폰트가 Pretendard/Noto Sans KR(무료)로 지정됐는가?
- 구성안·프롬프트·SVG 파일 경로 세 가지를 모두 출력했는가?
