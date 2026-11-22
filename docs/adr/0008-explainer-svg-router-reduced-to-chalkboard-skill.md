# 16:9 설명 SVG는 칠판 그림체 skill 하나만 남긴다

Scope: akbun-draw / akbun-draw-chalkboard

## Decision

`akbun-draw-explainer-svg` 라우터를 칠판 그림체 하나만 그리는 `akbun-draw-chalkboard` skill로 바꾸고, `clay-isometric`·`marker-wireframe` 토큰은 지운다. 그림체는 여전히 `styles/chalkboard.json` 토큰과 `check_style_svg.py`가 정하고 검사하며, 토큰은 구도를 고정하지 않는다. 토큰은 색·선·글꼴·효과·여백만 고정한다. 구도 문장이 스타일 규칙에 섞이면 시험에서 응답 흐름을 생략하는 결과가 나왔기 때문이다.

## Reason

실제로 쓰는 그림체가 칠판 하나로 줄었고, 라우터 표·스타일 선택 단계·토큰 추가 절차가 쓰지 않는 그림체를 위해 남아 있었다. 스타일 skill 이름 규칙(끝에 스타일 단어 하나)과도 맞춘다. 트레이드오프는 새 정적 SVG 그림체를 다시 만들 때 공통 캔버스·검수 규칙을 그 skill에 복사하거나 라우터를 되살려야 한다는 것이다.
