# AI Context

## 작업 맥락

akbun-draw는 소재·글·코드를 고정 스타일의 이미지 생성 프롬프트와 Figma/Canva용 SVG로 만드는 skill 모음이다. 각 skill은 그림체·색감만 고정하고 소재·구도는 입력에 맞춘다. `akbun-draw-webtoon-c`와 `akbun-draw-cartoon-b`만 표준 고래 마스코트를 참조한다.

## 용어 정리

- reference image: 피사체를 복제하지 않고 레이아웃·스타일·구조만 판단하는 참고 이미지다.
- book illustration layout: monogray 팔레트와 고정 레이아웃 5종을 쓰는 삽화다. `akbun-draw-book-illustration`이 프롬프트와 SVG를 만든다.
- essay-toon: 상단 내레이션과 고래 마스코트의 감정 장면 하나로 구성한 가로형 1컷이다. `akbun-draw-webtoon-c`가 담당한다.
- storytelling illustration: 크림 종이·잉크 외곽선·마커 채색으로 장면당 메시지 하나를 그리는 삽화다. `akbun-draw-storytellingimage`가 담당한다.
- documentary-toon: 거친 흑백 잉크선과 하단 자막으로 실화를 서술하는 3:4 프레임이다. `akbun-draw-webtoon-d`가 담당한다.
- presentation architecture: 16:9 차콜 캔버스에 흰색 구조선과 제한된 노랑·빨강 강조를 쓰는 시스템 구성도다. `akbun-draw-system-architecture`가 이미지·생성 프롬프트를 만들며, 요청 시 편집 가능한 PPTX로 제공한다.
