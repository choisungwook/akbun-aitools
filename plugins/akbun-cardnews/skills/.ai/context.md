# AI Context

## 작업 맥락

akbun-cardnews는 사용자의 이미지·글(또는 주제)을 SNS 카드뉴스로 만드는 skill 모음이다. 산출물은 페이지별 한국어 카피, 이미지 생성 AI용 영어 프롬프트, Figma/Canva로 불러올 수 있는 1080x1350 SVG 세 가지다. 레이아웃 수치는 `references/layout-spec.md`가 단일 기준이며 임의로 바꾸지 않는다.

## 용어 정리

- 카드뉴스: 표지 1장 + 내용 페이지 N장으로 구성된 4:5 세로형 SNS 이미지 시리즈다.
- 표지(cover): 전체 배경 사진 + 좌하단 제목 최대 3줄 + 하단 스크림 구조의 1페이지다.
- 내용 페이지(content page): 상단 2/3 사진 + 하단 1/3 흰색 정보 패널 구조의 페이지다.
- placeholder: SVG에서 실제 사진 대신 두는 회색 rect다. 사용자가 이미지를 주면 base64 `<image>`로 교체한다.
- 편집 가능 SVG: 텍스트를 path로 아웃라인화하지 않고 `<text>`로 남긴 SVG다. Figma/Canva에서 텍스트 레이어로 열린다.
