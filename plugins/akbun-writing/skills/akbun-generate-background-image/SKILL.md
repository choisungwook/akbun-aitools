---
name: akbun-generate-background-image
description: >
  카드뉴스 등 세로형 카드의 페이지별 배경 사진을 만드는 이미지 생성 AI agent용 영어 프롬프트를
  만든다. 페이지 종류(표지/내용)에 맞는 구도와 여백을 지정한다.
---

# 카드뉴스 배경 사진 프롬프트 생성

## 이 skill이 하는 일

카드뉴스 페이지의 **배경 사진**을 만드는 이미지 생성 AI agent용 **영어 프롬프트**를 만든다. 입력은 카드뉴스 구성안(제목·본문)이거나, 장면을 설명하는 주제 한 줄일 수 있다. 결과물은 사진이 아니라, GPT image나 nano-banana 같은 이미지 생성 모델·agent에 그대로 붙여넣을 **영어 프롬프트**다.

`akbun-draw-cardnews-A`(표지·내용 페이지 구조 + SVG 생성)와 짝이 되는 skill이다. `akbun-draw-cardnews-A`는 구조와 텍스트 레이어를 만들고, 이 skill은 그 뒤에 깔릴 배경 사진 프롬프트를 만든다. 사진 위 텍스트는 SVG 레이어가 담당하므로 **사진 안에는 글자를 넣지 않는다**.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 프롬프트** — 페이지당 코드 블록 하나. 그대로 복사해 이미지 생성 AI agent에 붙여넣을 수 있게 한다.
2. **한국어 한 줄 설명** — 각 페이지 사진이 어떤 장면·구도인지 1~2문장.

## 페이지 종류별 구도

카드뉴스 레이아웃은 사진이 놓이는 영역과 그 위에 텍스트가 얹히는 자리가 정해져 있다. 프롬프트는 그 자리를 비워 두도록 구도를 지정한다.

- **표지 사진**: 세로형 4:5(1080×1350). 피사체를 **중앙~오른쪽**에 두고, **왼쪽 아래(제목 자리)는 비교적 비어 있게** 잡는다. 따뜻한 톤의 인물·사물 에디토리얼 사진이 기본이다.
- **내용 페이지 사진**: 페이지 **상단 절반(1080×675, 약 8:5)**만 보인다. 피사체가 그 가로 프레임의 **세로 중앙**에 오도록 잡는다. 아래쪽은 검정 패널이 덮으므로 하단 디테일에 의존하지 않는다.

## 공통 규칙

- 프롬프트는 **영어**로 쓰고, 페이지당 코드 블록 하나로 출력한다.
- 사진 안에 **글자를 넣지 않는다**. 텍스트는 카드뉴스 SVG 레이어가 담당한다.
- 프롬프트 끝에 공통 제약을 붙인다: `no text, no watermark, no logo in the photo`.
- 여러 페이지의 사진은 **톤·조명·색감을 통일**한다. 시리즈로 읽히도록 같은 라이팅·팔레트 문구를 재사용한다.

## 작업 순서

1. **입력 파악.** 카드뉴스 구성안이 있으면 페이지별 제목·본문에서 장면을 뽑는다. 주제만 있으면 장면을 정한다.
2. **페이지 종류 판단.** 각 페이지가 표지인지 내용 페이지인지 정해 알맞은 구도 템플릿을 고른다.
3. **장면 결정.** 페이지마다 피사체 하나와 배경을 한두 문장으로 정한다. 텍스트가 얹힐 자리는 비운다.
4. **프롬프트 조립.** 아래 템플릿의 빈칸을 채운다.
5. **출력.** 페이지별 영어 프롬프트 블록 + 한국어 한 줄 설명을 출력한다.

## 프롬프트 템플릿

표지 사진 템플릿이다.

```text
Editorial portrait photograph, 4:5 vertical. <SUBJECT AND SCENE — one or two sentences>.
The subject is positioned center-right; the lower-left area of the frame stays clean and
uncluttered to leave room for overlaid text. Warm natural tones, soft window light,
shallow depth of field. no text, no watermark, no logo in the photo.
```

내용 페이지 사진 템플릿이다.

```text
Photograph, wide 8:5 horizontal crop. <SUBJECT AND SCENE — one or two sentences>. The main
subject sits in the vertical center of the frame so it stays visible when only the top half
is shown. <SAME TONE/LIGHTING PHRASE AS THE COVER for a consistent series>. no text, no
watermark, no logo in the photo.
```

## 예시 (gold reference)

이 예시는 이 skill의 품질 기준이다.

입력 예는 카드뉴스 구성안이다.

```text
표지 제목: 메모를 / 시작했습니다
내용 1. 기록이 기억을 이긴다 — 기록 습관이 바뀌었다. 이제는 적어두는 사람이 이긴다.
```

skill이 한 판단: 표지는 "메모를 시작하는 사람"이 필요해 창가 책상에서 노트를 펴고 펜을 든 인물을 골랐고, 왼쪽 아래 제목 자리를 비웠다. 내용 페이지는 같은 톤(따뜻한 자연광)으로 손과 노트를 클로즈업해 상단 크롭에서도 피사체가 보이도록 세로 중앙에 배치했다.

표지 프롬프트 출력이다.

```text
Editorial portrait photograph, 4:5 vertical. A person at a wooden desk by a window, pausing
with a pen over an open notebook, seen from a slight side angle. The subject is positioned
center-right; the lower-left area of the frame stays clean and uncluttered to leave room for
overlaid text. Warm natural tones, soft window light, shallow depth of field. no text, no
watermark, no logo in the photo.
```

내용 페이지 프롬프트 출력이다.

```text
Photograph, wide 8:5 horizontal crop. A close-up of a hand writing a short note in an open
notebook on a wooden desk, a coffee cup slightly out of focus beside it. The main subject
sits in the vertical center of the frame so it stays visible when only the top half is shown.
Warm natural tones, soft window light, shallow depth of field. no text, no watermark, no logo
in the photo.
```

한국어 한 줄 설명: 표지는 창가에서 노트를 펴고 펜을 든 인물을 중앙~오른쪽에 두고 제목 자리를 비웠고, 내용 페이지는 같은 따뜻한 자연광 톤으로 노트에 적는 손을 세로 중앙에 클로즈업했습니다.

## 완료 전 확인

- 페이지마다 표지/내용 구도를 올바로 골랐는가? (표지=4:5, 내용=8:5 상단 크롭)
- 텍스트가 얹힐 자리(표지 왼쪽 아래)를 비우도록 구도를 지정했는가?
- 사진 안에 글자를 넣지 말라는 제약(`no text ...`)을 모든 프롬프트에 붙였는가?
- 여러 페이지의 톤·조명·색감을 통일했는가?
- 페이지별 영어 프롬프트 블록 + 한국어 한 줄 설명을 출력했는가?
