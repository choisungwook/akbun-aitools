# SVG 작성 규칙 (Figma/Canva 연동)

책 삽화 스타일 SVG를 만드는 규칙이다. 목표는 "이미지 모델 없이도 디자인 툴에서 편집 가능한
같은 스타일의 벡터"다. `assets/example-icon-strip.svg`가 품질 기준이다.

## 캔버스

레이아웃별 viewBox를 고정으로 쓴다.

| 레이아웃 | viewBox |
|---|---|
| `flow-stack` | `0 0 1200 1500` (4:5) 또는 `0 0 1200 1200` (1:1) |
| `zoom-detail` | `0 0 1600 1200` |
| `poster-card` | `0 0 1600 1200` |
| `dialog-scene` | `0 0 1600 1200` |
| `icon-strip` | `0 0 1600 600` |

- 사방 여백 10%를 지킨다. 예: `0 0 1600 600`이면 콘텐츠는 x 160~1440, y 60~540 안에 둔다.
- `width`/`height` 속성은 viewBox와 같은 값으로 넣는다(Canva가 크기를 읽는다).

## 팔레트 (고정 — monogray와 동일)

배경을 포함해 아래 색만 쓴다. `akbun-draw-poster-monogray`와 같은 팔레트다.

| 용도 | 색 |
|---|---|
| 종이 배경 | `#F4F2ED` |
| 잉크 아웃라인·텍스트 | `#3A3A3A` |
| 밝은 회색 면 | `#E3E3E3` |
| 중간 회색 면 | `#C9C9C9` |
| 어두운 화면 면(모니터 등) | `#5A5A5A` |
| 오렌지 포인트 | `#E8833A` |

## 손그림 느낌 내는 법

- 모든 선은 `stroke-linecap="round"` `stroke-linejoin="round"`.
- 아웃라인 두께는 캔버스 짧은 변의 1~1.5%(예: 600px 높이면 7~9px). 그림 전체에서 비슷하게
  유지하고, 강조 화살표만 살짝 굵게 한다.
- 사각형은 `rx`로 모서리를 둥글린다(두께의 1.5~2배).
- 요소(아이콘, 블록)마다 `transform="rotate(±0.5~1.5 cx cy)"`로 아주 살짝 기울여 손그림
  느낌을 낸다. 텍스트도 ±1도 안에서 기울일 수 있다.
- 완벽한 대칭을 피한다. 반짝임 선, 김, 점선 같은 잔선은 길이를 조금씩 다르게 그린다.
- 그룹 음영(flow-stack)은 `<pattern>`의 사선 스트라이프로 해칭 질감을 낸다. 필터(blur 등)는
  쓰지 않는다 — Canva가 필터를 무시할 수 있다.

## 텍스트

- 텍스트는 **아웃라인으로 변환하지 않는다**. `<text>` 요소로 남겨야 Figma/Canva에서 문구를
  고칠 수 있다.
- 폰트는 SIL OFL 무료 폰트만 지정한다.

  한글 손글씨 기본 지정(monogray와 동일 스택):

  ```xml
  <text font-family="Gaegu, 'Nanum Pen Script', 'Patrick Hand', sans-serif" ...>
  ```

  영어 세리프 제목(poster-card)은 `'Nanum Myeongjo', serif`에 `letter-spacing`을 넓게 준다.
- 라벨은 `text-anchor="middle"`로 대상의 중심 x에 맞춘다.
- 폰트 크기: 라벨은 캔버스 짧은 변의 7~9%, 제목은 10~12%.

## 구조 (레이어)

Figma/Canva에서 레이어로 다루기 쉽게 의미 단위로 `<g id="...">`를 나눈다.

구조 예시:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 600" width="1600" height="600">
  <rect id="paper" width="1600" height="600" fill="#F4F2ED"/>
  <g id="icon-1">...</g>
  <g id="icon-2">...</g>
  <g id="accent">...</g>
  <g id="labels">...</g>
</svg>
```

- 외부 이미지(`<image href>`), 외부 CSS, 스크립트를 넣지 않는다. 순수 벡터만 쓴다.
- `<style>` 블록 대신 인라인 속성을 쓴다(Canva 호환).

## Figma / Canva 안내

SVG를 건넬 때 아래를 함께 안내한다.

- **Figma**: 파일을 캔버스에 드래그하면 벡터로 열린다. Gaegu 등 Google Fonts는 Figma에
  내장되어 있어 그대로 보인다.
- **Canva**: 업로드 > SVG로 가져온다. 폰트가 없으면 기본 폰트로 대체되므로, 손글씨 느낌을
  유지하려면 Google Fonts에서 Gaegu(OFL)를 받아 Canva 브랜드 폰트로 업로드하라고 안내한다.
