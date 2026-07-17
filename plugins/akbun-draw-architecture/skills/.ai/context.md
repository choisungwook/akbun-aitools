# AI Context

## 작업 맥락

akbun-draw-architecture는 아키텍처를 그리는 목적의 skill 모음이다. akbun-writing에서 분리했다. draw.io 기반 AWS VPC·Kubernetes 네트워크 다이어그램과, 하이레벨 컴퍼넌트 아키텍처·네트워크 흐름 그림의 이미지 생성 프롬프트를 만든다.

## 용어 정리

- topology: 자연어, 사진, YAML, 기존 다이어그램에서 추출한 네트워크 구성과 연결 관계이다. 다이어그램 skill은 입력 형식보다 topology 정규화를 우선한다.
- reference image: 그대로 복제할 대상이 아니라 레이아웃, 스타일, 구조를 판단하는 참고 이미지이다.
- 확인 필요: 가정으로 처리하기 어렵거나 다음 작업자가 다시 확인해야 하는 불확실성을 표시하는 말이다.
