---
name: akbun-draw-chalkboard
description: 시스템 아키텍처·기술 개념을 다크 그린 칠판 위 분필 선 그림체로, 설명 영상·슬라이드·블로그용 16:9(1920×1080) raw SVG로 그린다. styles/chalkboard.json 디자인 토큰이 색·선·글꼴·효과·여백(스타일)만 고정하고, 요소 수·배치·화살표 방향(구도)은 입력 내용에 맞춰 자유롭게 정한다. 결과는 Claude Artifacts나 브라우저에서 바로 여는 SVG 코드 또는 디자인 토큰 맵이다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-chalkboard

## 이 skill이 하는 일

기술 개념·시스템 구조·동작 흐름을 **16:9 SVG 한 장**으로 그린다. 그림체는 다크 그린 칠판 위 분필 선이고 [styles/chalkboard.json](styles/chalkboard.json) 디자인 토큰이 정한다. 이 문서는 캔버스·검수 규칙만 담는다. 이미지 생성 모델용 프롬프트가 아니라 SVG 코드를 직접 쓴다.

- 고정하는 것(토큰): 배경, 팔레트와 색의 의미, 선 굵기, 모서리, 글꼴, 허용 효과(그라데이션·발광·그림자·패턴), 최소 여백 비율.
- 고정하지 않는 것(입력이 정함): 구성 요소 수, 위치, 크기 비율, 화살표 방향, 흐름이 되돌아오는지, 제목 유무. 토큰에는 구도 규칙이 없고, 같은 스타일로 그린 두 그림의 배치가 달라도 된다.

## 스타일

| 짧은 이름 | 컨셉 | 토큰 | 예시 |
|---|---|---|---|
| chalkboard | 다크 그린 칠판 위 분필 선, 수식·이론 | [styles/chalkboard.json](styles/chalkboard.json) | [references/chalkboard.svg](references/chalkboard.svg) |

- 예시를 렌더한 PNG는 저장소 `imgs/akbun-draw-chalkboard.png`다. 예시의 배치를 기본값으로 쓰지 않는다.

## 토큰 파일 형식

`styles/chalkboard.json`의 키와 뜻:

| 키 | 뜻 |
|---|---|
| `id`, `concept` | 식별자와 한 줄 컨셉 |
| `canvas` | `viewBox`(항상 `0 0 1920 1080`), `aspectRatio`, `negativeSpaceRatio`, `edgeMarginPx`(가장자리 안쪽에 요소를 두지 않는 폭), `captionMarginPx`(자막 영역 경계에서 띄우는 폭), `centerTolerancePx`(내용 중심이 그릴 영역 중심에서 벗어나도 되는 폭) |
| `colors` | 이름→hex. SVG에 쓰는 hex는 이 값(과 `effects` 안의 hex)뿐이다 |
| `colorRoles` | 색 이름→의미. 같은 그림에서 같은 의미는 같은 색 |
| `typography` | `fonts.ui`·`fonts.mono`(모두 SIL OFL)와 용도별 크기·굵기·색, `textOpacity` |
| `geometry` | 선 굵기, 모서리, 거칠기, 점선, 화살표 머리 |
| `effects` | `chalk` filter 문자열(그대로 복사), `allowedDefs`(`<defs>`에 둘 수 있는 것), 금지 목록 |
| `rules` | 반드시 지키는 문장. 전부 적용한다 |
| `checks` | 검사 스크립트가 읽는 값: `forbidElements`, `strokeWidthRange`(null이면 검사 안 함), `minNegativeSpacePct` |

## 공통 규칙

토큰의 `rules`가 더 좁게 정하면 토큰을 따른다.

- `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080">`로 시작한다. `width`·`height`는 넣지 않는다.
- 배경은 캔버스 전체를 덮는 `<rect class="bg" width="1920" height="1080">` 하나다. 배경 그라데이션·모눈·흐린 장식·halo처럼 내용이 아닌 요소에만 `class="bg"`를 붙인다. 검사 스크립트는 `class="bg"`를 여백·자막·가장자리 계산에서 뺀다.
- 가운데 정렬: `class="bg"`가 아닌 모든 요소의 bounding box 합집합의 중심을 그릴 영역의 중심에 맞춘다. 그릴 영역은 기본이 캔버스 전체(중심 960, 540)이고, 자막 영역이 있으면 그 오른쪽 나머지다. 허용 오차는 가로·세로 각각 `centerTolerancePx`. 좌표를 다 정한 뒤 중심 오차만큼 전체를 `translate`로 옮기면 된다.
- 자막 영역: 사용자가 "왼쪽 30%"처럼 비율을 주면 `x < 1920 × 비율`에 `class="bg"`가 아닌 요소의 bounding box가 들어가지 않고, 그 경계에서 `captionMarginPx`만큼 더 띄운다. 발광·그림자 번짐도 경계를 넘지 않게 한다. 말이 없으면 자막 영역을 두지 않고 캔버스 전체에 가운데 정렬한다.
- 가장자리 `edgeMarginPx` 안에는 요소를 두지 않는다.
- 여백(배경·장식만 보이는 면적)은 `minNegativeSpacePct` 이상이다. 세는 법: `class="bg"`가 아닌 모든 요소의 bounding box 합집합을 8px 격자로 세어 덮이지 않은 칸의 비율.
- 위치 이동은 `translate`만 쓴다(`matrix`·`scale`·`rotate`·`skew`는 검사가 bounding box를 못 센다). `path`는 절대 좌표 `M L Q C T S Z`만 쓴다(`H V A`·소문자 명령은 못 센다). `<defs>` 안 pattern·filter 문자열은 bounding box를 세지 않으므로 토큰 그대로 복사한다.
- `<image>`와 외부 `href`는 쓰지 않는다. 글자는 `<text>`로 남기고 `<path>`나 이미지로 바꾸지 않는다. 글꼴은 토큰의 `typography.fonts`뿐이며(모두 SIL OFL: Inter, JetBrains Mono, Noto Sans KR) 한국어가 있으면 첫 글꼴은 그대로 두고 한국어 글꼴이 대체로 남게 한다.
- 글자 길이: 이름은 영어 3단어 또는 한국어 10글자 이하, 설명 한 줄은 영어 6단어 또는 한국어 16글자 이하. 세는 법: 영어로만 된 줄은 공백으로 나눈 단어 수, 한국어가 한 글자라도 있으면 공백을 뺀 모든 글자 수(숫자·기호·번호 포함). 글자 폭 추정은 영어·숫자·기호 한 글자 0.6 × 크기, 한글 한 글자 1.0 × 크기(검사 스크립트도 같은 값을 쓴다).
- 실제 제품 로고·마스코트·상표 모양을 그리지 않는다. 제품은 이름 글자와 일반 도형(상자·원통·톱니·판·큐브)으로 나타낸다. 화면의 주소·키 값이 예시면 문서용 값(`example.com`, `203.0.113.0/24`)을 쓴다.
- 구성 요소(상자·블록·노드·카드 같은 개체. 화살표·글자·제목은 세지 않는다)는 3~9개로 줄인다. 전·후 비교처럼 패널을 나누면 패널마다 센다. 더 많으면 묶음으로 감싸거나 그림을 나눈다. 묶는 방법·방향은 입력이 정한다.

## 작업 흐름

`<skill>`은 이 `SKILL.md`가 있는 디렉터리, 출력 폴더는 사용자가 정한 곳(없으면 현재 디렉터리)이다.

1. **입력 분석.** 기술 개념에서 핵심 엔티티를 입력·처리·결과로 나눠 뽑고, 관계(흐름·참조·소속·상태 변화)를 적는다. 자막 영역 비율, 제목 유무, 한국어·영어를 정한다.
2. **토큰 읽기.** `styles/chalkboard.json`을 읽는다. `colorRoles`로 엔티티마다 색을 배정하고 `rules`를 전부 체크리스트로 옮긴다.
3. **레이아웃 설계.** 토큰의 크기 범위 안에서 요소 크기와 좌표(px 정수)를 정한다. 흐름 방향·되돌아오는 화살표·분기는 내용대로 그린다. 전체 bounding box를 계산해 그릴 영역 가운데에 오도록 좌표를 옮긴다.
4. **SVG 작성.** 공통 규칙대로 시작하고 `<defs>`에는 토큰 `allowedDefs`에 있는 것만 둔다.
5. **검수.** `uv run --python 3.12 <skill>/scripts/check_style_svg.py --style chalkboard [--caption-left 30] <출력>/out.svg`. 오류 0건이 될 때까지 고친다. 그다음 눈 검수.
6. **출력.** 결과물 형식대로 낸다.

## 검수

스크립트가 보는 것: viewBox, `forbidElements`, 팔레트 밖 hex, 첫 글꼴, `strokeWidthRange`, 자막 영역 침범과 `captionMarginPx`, `edgeMarginPx`, 여백 비율, 내용 중심 오차(`centerTolerancePx`). 건너뛴 요소(상대 좌표·`H V A` path, 크기 없는 use, `matrix`·`scale`·`rotate`·`skew` transform)가 있으면 개수를 출력하므로 0이 되게 고친다.

스크립트가 못 보는 것은 렌더해 한 번 보고 확인한다.

- 알려진 제품 로고·마스코트·공식 아키텍처 아이콘·특정 채널의 화면과 닮아 보이지 않는가. 닮았으면 다른 일반 도형으로 바꾼다.
- 토큰 `rules`의 개수·비율 규칙(강조 채움 면적, 발광 개수, 강조색 요소 비율)을 좌표로 계산해 지켰는가.
- 요소끼리 겹치지 않는가(발광·그림자 포함), 글자가 도형 밖으로 넘치지 않는가, 글자 길이 제한을 지켰는가, 화살표 끝이 대상 외곽선에 닿는가.

## 결과물 형식

1. SVG 코드 한 덩어리(코드 펜스 하나, 언어 `svg`).
2. 한국어 설명 1~2문장: 엔티티와 배치, 색에 준 의미. 사용자가 "SVG만"이라고 하면 1만 낸다.
3. 사용자가 "토큰만" 또는 "디자인 토큰 맵"을 요청하면 SVG 대신 `styles/chalkboard.json`을 그대로 낸다. 편집용 색 변수가 필요하면 `colors`를 `--이름: 값;` 형식의 CSS 변수 블록으로도 함께 낸다.

## 예시 (gold reference)

입력 예다.

```text
akbun-draw-chalkboard로 EKS Auto Mode 동작 원리를 그려줘. 개발자가 Pod(2 CPU, 4GB)를 배포하면 엔진이 감지해서 EC2 노드를 자동으로 만들고 슬롯에 결합해.
```

이 입력으로 그린 결과가 [references/chalkboard.svg](references/chalkboard.svg)다(자막 영역 없이 캔버스 가운데 정렬). 배치는 예시일 뿐이고, 스타일은 색·선·효과에서만 드러나야 하며 배치는 내용과 모델이 정한다.
