# 16:9 설명 SVG는 칠판 그림체 skill 하나만 남긴다

Scope: akbun-draw / akbun-draw-chalkboard

## Decision

`akbun-draw-explainer-svg` 라우터를 칠판 그림체 하나만 그리는 `akbun-draw-chalkboard` skill로 바꾸고, `clay-isometric`·`marker-wireframe` 토큰은 지운다. 그림체는 여전히 `styles/chalkboard.json` 토큰과 `check_style_svg.py`가 정하고 검사하며, 토큰은 구도를 고정하지 않는다. 0007의 "정적 그림체는 토큰 하나로 라우터에 추가" 결정을 대체한다.

## Reason

실제로 쓰는 그림체가 칠판 하나로 줄었고, 라우터 표·스타일 선택 단계·토큰 추가 절차가 쓰지 않는 그림체를 위해 남아 있었다. 스타일 skill 이름 규칙(끝에 스타일 단어 하나)과도 맞춘다. 트레이드오프는 새 정적 SVG 그림체를 다시 만들 때 공통 캔버스·검수 규칙을 그 skill에 복사하거나 라우터를 되살려야 한다는 것이다.
