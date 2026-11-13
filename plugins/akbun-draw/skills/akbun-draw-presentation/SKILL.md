---
name: akbun-draw-presentation
description: >
  아무 개념·흐름·비교·질문을 akbun-presentation-paper 논문형식 발표 슬라이드 한 장처럼 보이는 16:9
  이미지로 그리는 영어 이미지 생성 프롬프트를 만든다. 라이트(흰 내용 슬라이드 + "N. 섹션명" 헤더 + ■/-
  불릿 + 검정 얇은 선 다이어그램 + ①②③ 마커 + 노랑 포인트·빨강 문제 강조)가 기본이고, 다크 표지·섹션
  표지와 다크 스텝 변형을 고를 수 있다. 고정하는 것은 색·글꼴 느낌·선·여백·슬라이드 틀이고, 무엇을
  그릴지는 입력에 맞춰 정한다. 덱(.pptx)과 대본은 만들지 않는다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-presentation

## 목적

블로그·영상·SNS에 넣을 그림을 akbun 논문형식 발표 슬라이드 한 장처럼 그리는 16:9 영어 프롬프트를 만든다. 이미지 생성 도구에 그대로 붙여 넣는다.

덱 전체가 필요하면 `akbun-presentation-paper`, 덱에 끼울 제목 없는 시각자료는 `akbun-presentation-visual`을 쓴다. 이 skill은 슬라이드 틀(헤더·불릿·페이지 번호)까지 그림 안에 넣은 완성 한 장을 만든다.

## 슬라이드 유형 고르기

입력이 무엇을 말하는지 보고 하나를 고른다. 여러 장이면 같은 유형을 연달아 3장 넘게 쓰지 않는다.

| 유형 | 고르는 때 | 배경 | 화면 구성 |
|---|---|---|---|
| `content` | 구조·과정을 설명 | 흰색 | 왼쪽 위 헤더, 그 아래 불릿 2~4줄, 아래 본문 영역에 다이어그램 하나 |
| `steps` | 순서가 핵심 | 흰색 | 헤더, 왼쪽→오른쪽 같은 크기 스텝 박스 3~5개와 ①②③ 마커 |
| `compare` | 전후·A/B | 흰색 | 헤더, 세로 2열, 열마다 위에 라벨, 다른 점 한 곳만 강조색 |
| `code` | 코드·설정이 주인공 | 흰색 | 헤더, 왼쪽 어두운 코드 패널, 굵은 검정 화살표, 오른쪽 다이어그램 |
| `question` | 궁금증을 던짐 | 흰색 | 빈 흰 화면 가운데 굵은 질문 2~4줄만 |
| `section` | 장을 여는 표지 | 다크 | 왼쪽 노란 세로 바, 그 오른쪽 굵은 흰 섹션 제목, 아래 `- 부제` 한 줄 |
| `cover` | 전체 표지 | 다크 | 가운데 굵은 제목, 핵심 키워드만 노랑 |

변형은 기본 `light`. 사용자가 다크를 원하거나 밤·라이트닝 토크 분위기를 말하면 `dark-step`을 쓴다. `section`·`cover`는 `light`에서도 다크 배경이다.

## 스타일 값

### light

- 배경: 내용 슬라이드 `#FFFFFF`, 표지·섹션 표지 `#212022`
- 글자·도형선 `#000000`, 캡션·출처 `#7F7F7F`
- 포인트 `#FFC000`: 섹션 세로 바, 표지 키워드, 다이어그램의 주인공 하나
- 문제·에러 `#FF0000`: 빨간 점선 화살표, 빨간 X, 빨간 박스 중 한 곳
- 박스 채움: 앱·워크로드 `#FFF2CC`, 인프라 리소스 `#E2EFDA`, 묶음 영역 `#F2F2F2`, 나머지 흰색
- 박스: 검정 얇은 테두리(1~2px), 모서리 반지름 6~10px(1920px 폭 기준), 가운데 라벨
- 논리 경계(노드·클러스터·호스트): 채움 없는 얇은 검정 둥근 사각형, 라벨은 안쪽 왼쪽 위
- 화살표: 정상 흐름은 검정 실선 + 작은 채운 삼각 머리, 주목할 경로는 빨간 점선
- 코드 패널: 배경 `#1E1E1E`, 기본 글자 `#D4D4D4`, 키 `#569CD6`, 문자열 `#CE9178`, 고정폭 글꼴
- 헤더: 왼쪽 위 굵은 검정 `N. Section Name` (Title Case)
- 불릿: `■` 메인, 들여 쓴 `-` 서브, 문장부호 없는 짧은 명사구
- 페이지 번호: 오른쪽 아래 작은 숫자, 흰 배경은 검정, `section`은 흰색 (`cover` 제외)
- 글꼴 느낌: 깔끔한 산세리프 고딕, 코드만 고정폭

### dark-step

- 전 슬라이드 배경 `#252525`, 글자 `#EBEBEB`, 도형선 `#FFFFFF`, 포인트 `#FFC000`, 문제 `#FF0000`. 노랑 위 글자만 배경색 `#252525`로 쓰고 이 5색 밖은 쓰지 않는다
- 박스는 채움 없는 흰 테두리, 주인공 박스 하나만 노랑 채움 + `#252525` 굵은 라벨
- 논리 경계는 흰 점선 사각형, 화살표는 흰 실선
- 순서 마커는 채운 작은 원: 정상은 노랑 원 + `#252525` 숫자, 문제는 빨강 원 + 흰 숫자
- 헤더 한 줄과 메시지 한 줄만 쓰고 페이지 번호·푸터는 넣지 않는다
- 노랑·빨강 면적은 화면의 5% 미만

### 공통

- 한 장에 핵심 메시지 하나, 다이어그램 하나, 박스 3~7개, 흐름 5단계 이하. 셀 때 화살표와 글자는 박스로 세지 않는다
- 강조(노랑 주인공·빨강 문제)는 합쳐서 2곳 이하
- 바깥 5%는 비운다. 글자·도형·선이 차지하는 면적은 바깥 5%를 뺀 영역의 60% 이하, 평면 벡터 느낌
- 금지: 사진, 캐릭터, 3D, 그림자, 그라데이션, 네온, 장식 패턴, 워터마크, 실제 제품 로고

## 글자

- 언어는 사용자가 정한 것을 따르고, 없으면 영어. 기술 용어(pod, TTL, iptables)는 번역하지 않는다
- 박스 라벨은 20자, 화살표 라벨은 4단어 이내(공백 포함 글자 수, 경계 포함)
- 불릿은 줄마다 8단어 이내, 질문은 줄마다 6단어 이내
- 그림에 넣을 모든 문자열을 프롬프트에 큰따옴표로 정확히 나열하고 그 밖의 글자는 만들지 말라고 쓴다
- 입력에 없는 수치·컴퍼넌트·인과관계를 만들지 않는다. 예시가 필요하면 `Scenario:`로 시작하는 문자열로 가정임을 드러낸다

## 작업 흐름

1. 입력에서 메시지 한 줄, 유형, 변형, 보여 줄 박스·관계·순서·문제 지점을 정한다. 안전하게 추론할 수 있으면 묻지 않는다.
2. 아래 골격을 채워 프롬프트를 쓴다. 골격은 `light`의 `content` 기준이다. 유형 표와 변형에 없는 줄(불릿·페이지 번호·DIAGRAM 등)은 지우고, COMPOSITION·STYLE의 배치·선 색 문장은 고른 유형·변형 값으로 바꾼다. 대괄호와 선택지를 남기지 않고, 고른 변형의 hex만 옮긴다.
3. 여러 장이 같은 시스템을 설명하면 첫 장의 배치·박스 크기·라벨 위치를 COMPOSITION에 그대로 다시 쓰고 마커·강조·불릿만 바꾼다.
4. 사용자가 이미지까지 요청했을 때만 생성한다. 생성했으면 라벨 철자, 겹침, 잘림, 색 문법, 강조 개수를 확인하고 틀린 곳만 고쳐 한 번 다시 만든다.

프롬프트 골격이다.

```text
Create a 16:9 image that looks like a single slide from a clean technical conference presentation.

MESSAGE
One idea only: "..."

SLIDE FRAME
- Slide type: ...
- Background: ...
- Header (top-left, bold, black): "..."
- Bullets (below header, ■ main, indented - sub): "...", "..."
- Page number (bottom-right, small): "..."

DIAGRAM
- Boxes with exact labels and fills: ...
- Boundaries: ...
- Arrows with direction and exact short labels: ...
- Order markers: ...
- Emphasis (at most two): ...

COMPOSITION
Keep the outer 5% empty. Header and bullets occupy the upper area; the diagram fills the remaining body
area. Read left to right with no crossing arrows. Every box, label, marker and line stays separate,
legible and uncropped. Generous whitespace.

STYLE
Flat vector-like presentation graphics. Clean sans-serif Korean/Latin gothic type, monospace only for
code. Exact colors: ... Thin black outlines, slightly rounded boxes, small solid triangle arrowheads.

TEXT
Render only these exact strings: "...", "...". Preserve spelling. No other text, title, legend,
URL or paragraph.

DO NOT
No invented components, metrics or claims. No photos, characters, 3D, shadows, gradients, neon,
decorative patterns, watermarks, product logos, overlapping or cropped elements.
```

## 결과 보고

장마다 고른 유형·변형, 메시지 한 줄, 프롬프트 하나(`text` 코드블록)를 적는다. 이미지를 만들었으면 경로와 확인 결과를, 아니면 "이미지 생성하지 않음"을 적는다.

## 완료 전 확인

- 메시지가 하나이고 박스·흐름·강조 개수가 위 범위 안인가?
- 고른 변형의 hex만 썼고 다른 색을 섞지 않았는가?
- 그림에 들어갈 문자열이 전부 큰따옴표로 나열됐고 입력에 근거가 있는가?
- 슬라이드 틀(헤더·불릿·페이지 번호)이 유형 표와 맞는가?
