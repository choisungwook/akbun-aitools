---
name: akbun-draw-boundary-architecture
description: 시스템 아키텍처를 경계(조직, 네트워크, 실행 환경 등)는 점선 박스로, 그 안의 컴포넌트는 역할별 색 박스로 그리는 flat SVG 그림을 만든다. 데이터가 저장되는 경로는 실선, 조회 경로는 점선으로 구분한다. 특정 벤더나 제품에 묶이지 않는 추상 표현을 쓴다. Trigger on: "아키텍처 그려줘", "구조 시각화", "데이터 흐름 그림", "경계 나눠서 그려줘", "architecture diagram", "boundary diagram", or any request to draw system structure or data flow in this style.
disable-model-invocation: true
---

# 경계 아키텍처 그림

한 장에 하나의 질문만 답하는 설명용 SVG를 만든다. "무엇이 어느 경계 안에 있고, 데이터가 어느 방향으로 흐르나"가 3초 안에 읽혀야 한다.

## 먼저 정할 것

그리기 전에 세 가지를 한 줄씩 정한다. 정하지 못하면 그리지 말고 질문부터 다시 받는다.

1. 이 그림이 답하는 질문 한 줄 (예: "저장소는 왜 혼자 데이터를 받지 못하나")
2. 경계 목록: 소유, 네트워크, 실행 환경, 신뢰 영역처럼 점선 박스가 될 것
3. 흐름 목록: 저장·쓰기 경로(실선)와 조회·읽기 경로(점선)

## 추상화 규칙

- 그림 안 라벨은 역할로 쓴다: 서비스, 처리기, 수집기, 저장소, 조회 화면, 사용자, 게이트웨이, 큐
- 사용자가 준 자료에 제품명이 있어도, 사용자가 이름을 넣으라고 하지 않으면 역할 이름으로 바꾼다
- 경계 라벨도 역할로 쓴다: "소스 영역 A", "중앙 영역", "외부 제공자", "실행 환경"
- 특정 벤더의 아이콘, 로고, 색은 쓰지 않는다

## 캔버스

- `viewBox="0 0 680 H"`, `width="100%"`. 가로 680은 바꾸지 않는다. 내용이 좁으면 가운데에 둔다
- H는 가장 아래 요소 + 40px
- 안전 영역: x 30~650, y 30~(H-30)
- 루트 `<svg>`에 `role="img"`, 첫 자식으로 `<title>`(2~4단어)과 `<desc>`(한 문장 요약)
- 배경은 투명. 그라데이션, 그림자, blur, 이미지 아이콘은 쓰지 않는다

## 도형 규칙

| 요소 | 모양 |
|---|---|
| 경계 | `rx="8"`, fill 없음, stroke `#888780`, `stroke-dasharray="4 4"`, 왼쪽 위에 12px 라벨 |
| 컴포넌트 | `rx="4"` 사각형, 높이 44~64, 제목 14px + 부제 12px 두 줄 |
| 외부가 운영하거나 선택 사항인 컴포넌트 | 컴포넌트 테두리에 `stroke-dasharray="4 3"` |
| 화살표 | stroke `#888780`, 1px, 끝에 삼각형 marker 하나 |
| 저장·쓰기 경로 | 실선 |
| 조회·읽기 경로 | `stroke-dasharray="3 3"` |
| 화살표 라벨 | 12px, 선 위 10px, 3~6글자 동사 ("긁기", "넣기", "조회") |

- 한 가로줄에 컴포넌트는 4개까지. 넘으면 줄을 나누거나 그림을 둘로 나눈다
- 같은 줄의 박스 사이 간격은 20px 이상
- 경계 박스끼리 60px 이상 띄워 화살표 라벨 자리를 남긴다

## 색은 의미로만 쓴다

한 그림에 색 ramp는 회색 + 최대 2개까지 쓴다. 순서대로 돌려 쓰지 않는다.

| 의미 | ramp | 라이트 fill / stroke / 제목 / 부제 | 다크 fill / stroke / 제목 / 부제 |
|---|---|---|---|
| 중립(서비스, 사용자, 입력) | gray | #F1EFE8 / #5F5E5A / #444441 / #5F5E5A | #444441 / #B4B2A9 / #F1EFE8 / #B4B2A9 |
| 직접 운영, 상태 없음 | teal | #E1F5EE / #0F6E56 / #085041 / #0F6E56 | #085041 / #5DCAA5 / #E1F5EE / #5DCAA5 |
| 저장, 상태 있음 | coral | #FAECE7 / #993C1D / #712B13 / #993C1D | #712B13 / #F0997B / #FAECE7 / #F0997B |
| 외부가 운영 | purple | #EEEDFE / #534AB7 / #3C3489 / #534AB7 | #3C3489 / #AFA9EC / #EEEDFE / #AFA9EC |

- 색 박스 위 글자는 같은 ramp의 진한 단계만 쓴다. 검정이나 회색을 쓰지 않는다
- 색이 의미를 가지면 그림 아래에 한 줄 범례를 둔다

다크 모드는 SVG 안 `<style>`의 class와 media query로 처리한다. 아래는 SVG `<style>`에 그대로 넣는 CSS다.

```css
.n-gray rect{fill:#F1EFE8;stroke:#5F5E5A}.n-gray .th{fill:#444441}.n-gray .ts{fill:#5F5E5A}
.n-teal rect{fill:#E1F5EE;stroke:#0F6E56}.n-teal .th{fill:#085041}.n-teal .ts{fill:#0F6E56}
.n-coral rect{fill:#FAECE7;stroke:#993C1D}.n-coral .th{fill:#712B13}.n-coral .ts{fill:#993C1D}
.n-purple rect{fill:#EEEDFE;stroke:#534AB7}.n-purple .th{fill:#3C3489}.n-purple .ts{fill:#534AB7}
.th{font:500 14px sans-serif;fill:#2C2C2A}.ts{font:400 12px sans-serif;fill:#5F5E5A}
@media (prefers-color-scheme:dark){
.n-gray rect{fill:#444441;stroke:#B4B2A9}.n-gray .th{fill:#F1EFE8}.n-gray .ts{fill:#B4B2A9}
.n-teal rect{fill:#085041;stroke:#5DCAA5}.n-teal .th{fill:#E1F5EE}.n-teal .ts{fill:#5DCAA5}
.n-coral rect{fill:#712B13;stroke:#F0997B}.n-coral .th{fill:#FAECE7}.n-coral .ts{fill:#F0997B}
.n-purple rect{fill:#3C3489;stroke:#AFA9EC}.n-purple .th{fill:#EEEDFE}.n-purple .ts{fill:#AFA9EC}
.th{fill:#F1EFE8}.ts{fill:#B4B2A9}}
```

## 글자 규칙

- 한국어 라벨을 기본으로 쓴다
- 제목은 14px weight 500, 부제와 라벨은 12px weight 400. 11px 미만은 쓰지 않는다
- 부제는 5단어 이내. 설명은 그림 밖 본문에 쓴다
- 모든 `<text>`에 `th` 또는 `ts` class를 붙인다
- 가운데 정렬 글자는 `text-anchor="middle"`에 박스 중심 x를 준다

## 레이아웃 패턴

질문 종류에 맞춰 하나를 고른다.

| 질문 | 배치 |
|---|---|
| 경계를 넘는 흐름 | 소스 경계를 왼쪽에 세로로 쌓고, 중앙 경계를 오른쪽에 둔다 |
| 두 방식 비교 | 같은 구도를 위아래 두 줄로 반복하고, 바뀐 컴포넌트만 색을 바꾼다. 각 줄 위에 14px 제목 |
| 역할 분리(쓰기·읽기) | 쓰기 경로를 위쪽 줄, 읽기 경로를 아래쪽 줄에 두고, 저장소를 오른쪽에 세로로 쌓는다 |
| 한 경계 안의 계층 | 위에서 아래로 입력 → 처리 → 저장을 한 줄씩 둔다 |

## 뼈대

새 그림은 아래 SVG 뼈대에서 시작한다.

```svg
<svg width="100%" viewBox="0 0 680 220" role="img" xmlns="http://www.w3.org/2000/svg">
<title>저장소 앞의 수집기</title>
<desc>소스 영역의 수집기가 서비스를 긁어 중앙 영역 저장소에 넣는다.</desc>
<defs>
<style>/* 위 CSS */</style>
<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#888780"/></marker>
</defs>
<rect x="30" y="30" width="360" height="120" rx="8" fill="none" stroke="#888780" stroke-dasharray="4 4"/>
<text class="ts" x="44" y="50">소스 영역</text>
<g class="n-gray"><rect x="48" y="66" width="100" height="60" rx="4"/><text class="th" x="98" y="90" text-anchor="middle">서비스</text><text class="ts" x="98" y="110" text-anchor="middle">지표 노출</text></g>
<g class="n-teal"><rect x="224" y="66" width="150" height="60" rx="4"/><text class="th" x="299" y="90" text-anchor="middle">수집기</text><text class="ts" x="299" y="110" text-anchor="middle">직접 운영</text></g>
<line x1="222" y1="96" x2="150" y2="96" stroke="#888780" marker-end="url(#a)"/>
<text class="ts" x="160" y="86">긁기</text>
<rect x="450" y="30" width="200" height="120" rx="8" fill="none" stroke="#888780" stroke-dasharray="4 4"/>
<text class="ts" x="464" y="50">중앙 영역</text>
<g class="n-coral"><rect x="470" y="66" width="160" height="60" rx="4"/><text class="th" x="550" y="90" text-anchor="middle">저장소</text><text class="ts" x="550" y="110" text-anchor="middle">상태 있음</text></g>
<line x1="374" y1="96" x2="468" y2="96" stroke="#888780" marker-end="url(#a)"/>
<text class="ts" x="384" y="86">넣기</text>
<text class="ts" x="30" y="186">실선: 저장 경로 · 점선: 조회 경로</text>
</svg>
```

## 완성 전 점검

하나라도 어기면 고친 뒤 낸다.

1. 모든 요소가 x 0~680, y 0~H 안에 있다. 음수 좌표가 없다
2. 박스끼리, 라벨끼리, 라벨과 선이 겹치지 않는다. 의도한 겹침은 박스 안 제목뿐이다
3. 화살표 끝이 대상 박스 테두리 2px 앞에서 멈춘다
4. 색 ramp가 회색 + 2개 이하이고, 색마다 의미가 범례에 있다
5. 그림 안에 문단 설명이 없다. 설명은 본문에 쓴다
6. 제품명, 벤더명이 사용자 요청 없이 들어가 있지 않다
7. 다크 모드에서 모든 글자가 읽힌다

## PPT 편집용 출력 (선택)

사용자가 PowerPoint에서 개체를 하나씩 고치겠다고 요청할 때만 만든다. 요청이 없으면 만들지 않는다. 기본 SVG는 그대로 두고 `<주제>-ppt.svg`를 따로 만든다.

PowerPoint의 "도형으로 변환"은 CSS class, media query, marker를 제대로 옮기지 못한다. 그래서 아래처럼 바꾼다.

- `<style>`을 쓰지 않는다. 색은 각 `<rect>`, `<text>`, `<line>`에 `fill`, `stroke` 속성으로 직접 쓴다. 값은 색 표의 라이트 열을 쓴다
- 다크 모드는 넣지 않는다
- 글자는 `font-family`, `font-size`, `font-weight` 속성으로 직접 쓴다. 폰트는 PowerPoint에 설치된 OFL 폰트 이름을 쓴다(예: `Pretendard`, `Noto Sans KR`)
- 화살촉은 `<marker>` 대신 선 끝에 삼각형 `<path>`를 따로 그린다. 선은 삼각형 밑변에서 멈춘다
- 컴포넌트는 `<g>`로 묶어 변환 후에도 박스와 글자가 함께 움직이게 한다
- 좌표, 크기, 레이아웃은 기본 SVG와 같게 둔다

아래는 PPT 편집용 컴포넌트 1개와 화살표 1개의 예시다.

```svg
<g><rect x="224" y="66" width="150" height="60" rx="4" fill="#E1F5EE" stroke="#0F6E56"/>
<text x="299" y="90" text-anchor="middle" font-family="Pretendard" font-size="14" font-weight="500" fill="#085041">수집기</text>
<text x="299" y="110" text-anchor="middle" font-family="Pretendard" font-size="12" fill="#0F6E56">직접 운영</text></g>
<line x1="374" y1="96" x2="461" y2="96" stroke="#888780"/>
<path d="M461,92 L468,96 L461,100 z" fill="#888780"/>
```

## 산출물

- `<주제>.svg` 파일 하나. 요청하면 같은 내용의 HTML 한 장에 SVG를 inline으로 넣는다
- PPT 편집용을 요청하면 `<주제>-ppt.svg`를 추가로 만든다
- 본문에는 그림이 답하는 질문 한 줄과, 그림으로 못 담은 주의사항만 쓴다
