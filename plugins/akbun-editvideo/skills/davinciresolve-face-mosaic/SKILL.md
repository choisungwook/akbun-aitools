---
name: davinciresolve-face-mosaic
description: DaVinci Resolve에서 필요한 영역만 얼굴 모자이크 처리하고 배경은 보존할 때 사용한다.
disable-model-invocation: true
---

# davinciresolve-face-mosaic

- 대상 클립에 새 `Mosaic Blur` 노드를 만들고 강도 기본값은 `0.400`으로 둔다.
- 기본 마스크는 얼굴 주변만 감싸는 사각형이다. Fusion에서 Polygon/Polyline Mask(Pen Tool)를 쓸 수 있으면 얼굴 윤곽을 따라 펜으로 그린 마스크를 우선 사용하고, 불가능하면 사각형을 얼굴에 타이트하게 맞춘다. 배경이나 몸 전체를 포함하는 큰 마스크는 피한다.
- 마스크를 Mosaic Blur의 `Effect Mask`에 연결한다. 이미지 흐름은 반드시 `MediaIn → Mosaic Blur → MediaOut`이어야 한다. 마스크를 Mosaic Blur의 이미지 입력에 꽂거나 MediaIn을 끊지 않는다.
- 움직임이 있으면 마스크를 클립 구간에 맞춰 추적·키프레임하고, 시작·중간·끝에서 얼굴을 놓치거나 배경을 가리지 않는지 확인한다.
- 미리보기에서 모자이크 적용 범위와 노드 연결을 확인한다. `0.400`은 기본 시작값이며 얼굴이 식별되면 필요한 만큼만 높인다.
