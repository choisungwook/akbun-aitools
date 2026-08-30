# akbun 발표 시각자료 스타일

슬라이드에 삽입할 16:9 래스터 시각자료의 단일 스타일 기준이다. 슬라이드의 제목·페이지 번호·링크 푸터는
호출자가 편집 가능한 요소로 올리므로 이미지에 넣지 않는다.

## 공통 캔버스

- 비율: 16:9, 평면 벡터 다이어그램처럼 선명한 고해상도 이미지
- 안전 영역: 바깥 5%, 상단 18%와 하단 8%는 비워 제목과 캡션이 들어갈 공간을 확보
- 밀도: 이미지당 중심 다이어그램 하나, 컴퍼넌트 3~7개, 흐름 5단계 이하
- 방향: 왼쪽→오른쪽이 기본이며, 계층 구조는 위→아래 허용
- 형태: 단순 사각형·둥근 사각형·선·화살표·원형 숫자 마커만 사용
- 금지: 사진, 캐릭터, 3D, 그림자, 그라데이션, 네온, 장식 패턴, 워터마크, 범례, 불필요한 로고

## 라이트 샌드위치

- 배경 `#FFFFFF`, 기본 텍스트·도형선 `#000000`, 캡션 회색 `#7F7F7F`
- 주인공·순서 포인트 `#FFC000`, 문제·에러·병목 `#FF0000`
- workload·앱 채움 `#FFF2CC`, infrastructure resource 채움 `#E2EFDA`, 그룹 채움 `#F2F2F2`
- 컴퍼넌트는 흰색 또는 역할별 옅은 채움과 검정 1~2px 테두리, 중앙 라벨
- 논리 경계는 채움 없는 얇은 검정 둥근 사각형, 라벨은 경계 안쪽 좌상단
- 정상 흐름은 검정 실선과 작은 삼각 화살촉, 관리·문제 흐름은 빨간 점선
- 문제 지점은 빨간 X 또는 빨간 테두리 중 하나만 사용

## 다크 스텝

- 배경 `#252525`, 본문 `#EBEBEB`, 도형선 `#FFFFFF`, 포인트 `#FFC000`, 문제 `#FF0000`
- 컴퍼넌트는 채움 없는 흰색 1~2px 사각형과 옅은 회색 라벨
- 주인공 컴퍼넌트 하나만 노랑 채움과 검정 굵은 라벨
- 논리 경계는 채움 없는 흰색 점선 사각형, 라벨은 경계선 좌상단 가까이 배치
- 정상 흐름은 흰색 실선, 문제 흐름은 빨간 실선 또는 점선
- 순서 마커는 작은 원: 정상은 노랑 원+검정 숫자, 문제는 빨강 원+흰 숫자
- 노랑과 빨강은 전체 면적의 5% 미만

## 텍스트

- 사용자가 지정한 언어를 따르고, 미지정이면 기술 라벨은 영어로 쓴다.
- 제목·헤더·페이지 번호·긴 설명·URL은 이미지에 넣지 않는다.
- 컴퍼넌트 라벨은 20자, 관계 라벨은 4단어 이내로 줄인다.
- 프롬프트에 표시할 모든 문자열을 따옴표로 정확히 열거하고 다른 텍스트를 만들지 말라고 지시한다.
- 숫자·단위·고유명사는 원본 표기를 유지한다.

## 유형별 구성

- 시스템 구조: 컴퍼넌트와 경계를 먼저 배치하고 핵심 요청·응답만 연결
- 과정: 같은 크기의 스텝을 한 방향으로 배치하고 순서 마커 사용
- 비교: 좌우 2열, 같은 기준을 같은 높이에 놓고 차이 한 곳만 강조
- 문제 흐름: 정상 구도를 유지한 채 실패 경로와 영향 지점만 빨강으로 변경
- Figure 단순화: 원본의 축·범례·수치 의미를 유지하고 장식만 제거; 지원되지 않는 해석을 추가하지 않음

## 프롬프트 골격

아래 골격을 입력에 맞게 완성한다. 대괄호 토큰이나 선택지를 남기지 않는다.

```text
Create a clean 16:9 explanatory visual for a technical presentation.

MESSAGE
The visual must communicate one idea: "..."

CONTENT
- Visual type: ...
- Components or comparison subjects, with exact labels: ...
- Directed relationships or ordered steps, with exact short labels: ...
- Supported problem or emphasis: ...
- Facts, values, and units that must remain exact: ...

COMPOSITION
Keep the outer 5% clear. Reserve the top 18% and bottom 8% as empty background for an editable
slide title and caption. Place one central diagram in the remaining area. Use a left-to-right or
top-to-bottom reading direction with no crossing arrows. Keep every box, label, marker, and line
separate and legible. If this belongs to a sequence, preserve the supplied reference image's exact
layout and change only the listed emphasis, marker, or state.

VISUAL STYLE
Describe either the light-sandwich or dark-step rules from this document with exact colors,
fills, outlines, arrows, and markers. Flat vector-like rendering, generous whitespace, calm and
precise technical presentation style.

TEXT
Render only the exact component, relationship, value, and marker strings listed above. Preserve
their spelling. Do not add a title, footer, URL, legend, or explanatory paragraph.

DO NOT
No invented components, relationships, failures, metrics, or causal claims. No photos, characters,
3D, shadows, gradients, neon, decorative patterns, watermarks, extra UI, overlapping elements,
cropped labels, crossing arrows, or extra text.
```
