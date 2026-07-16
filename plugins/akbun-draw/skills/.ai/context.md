# AI Context

## 작업 맥락

akbun-draw는 소재·글·코드를 akbun 고정 스타일의 이미지 생성 프롬프트와 Figma/Canva 편집용 SVG로 만드는 이미지 그리기 skill 모음이다. akbun-writing에서 분리했다. 각 skill은 그림체·색감(스타일)을 고정하고 소재·구도는 입력에 맞춰 자유롭게 정한다. 캐릭터가 필요한 skill은 `akbun-mascot-whale`의 표준 외형 스펙을 참조한다.

## 용어 정리

- reference image: 그대로 복제할 대상이 아니라 레이아웃, 스타일, 구조를 판단하는 참고 이미지이다.
- book illustration layout(책 삽화 레이아웃): `akbun-draw-poster-monogray`와 같은 팔레트(진회색 잉크+플랫 회색+오렌지 포인트 하나+off-white)를 쓰되, 구도를 자유롭게 두지 않고 참고 이미지에서 뽑은 고정 레이아웃 5종(flow-stack, zoom-detail, poster-card, dialog-scene, icon-strip)과 상하좌우 간격에 맞춰 배치한다. `akbun-draw-book-illustration`이 담당하며, 산출물은 이미지 프롬프트와 편집 가능한 SVG 두 가지다. 스타일만 필요하고 구도가 자유로우면 monogray, 정해진 레이아웃·간격이 필요하면 이 skill을 쓴다.
- essay-toon(에세이툰): 가로형(16:10) 1컷 페이지 형식으로, 상단의 굵은 손글씨 내레이션이 이야기를 끌고 그림은 감정 한 장면만 보여준다. 주인공은 플랫 채색한 akbun 고래 마스코트, 배경 인물은 채색 없는 선화 실루엣이다. `akbun-draw-webtoon-c`가 담당한다(a: 3~4컷 스틱피겨, b: 세로형 파스텔 치비와 구분).
