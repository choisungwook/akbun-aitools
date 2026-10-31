# Reference Image Is Not a Pixel Target

Scope: repo (모든 그리기 skill과 `akbun-draw-explainer-svg`의 스타일 토큰)

## Decision

참고 이미지·영상은 재사용할 스타일(색·선·여백·구성 문법)의 출처로만 쓴다. 완료 판정은 픽셀 유사도가 아니라 규칙 검사(XML·SVG 검사 스크립트, 렌더 결과 확인)로 한다. 참고 자료의 피사체·장면·문구·캐릭터는 산출물(skill, 토큰, 예시)에 옮기지 않고, 예시는 다른 소재로 만든다.

## Reason

처음에는 `akbun-drawio-aws-vpc`(VPC 다이어그램)에만 둔 결정이었다. 이후 `akbun-draw`의 그림체 skill과 `akbun-draw-explainer-svg` 토큰(`ink-hatch`, `marker-wireframe`)도 같은 방식으로 참고 이미지에서 규칙만 뽑아 만들었으므로 범위를 저장소 전체로 넓혔다. 픽셀을 맞추면 예시 하나에 과적합해 소재가 바뀔 때 깨지고, 원본 피사체를 옮기면 모방이 남는다. 트레이드오프는 참고 자료와 첫눈에 덜 닮아 보인다는 것이다.
