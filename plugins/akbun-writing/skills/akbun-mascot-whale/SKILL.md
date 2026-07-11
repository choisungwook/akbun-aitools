---
name: akbun-mascot-whale
description: >
  akbun 마스코트인 통통한 고래 캐릭터의 표준 외형 스펙. 다른 skill이 akbun 마스코트를
  그릴 때 이 캐릭터 정의를 참조한다.
---

# akbun 마스코트 고래 캐릭터

## 이 skill이 하는 일

akbun 마스코트인 **통통한 고래 캐릭터**의 외형을 정의하는 단일 기준(canonical spec)이다.
다른 skill(포스터, 웹툰, 삽화, 카드뉴스 등)이 "akbun 마스코트"를 그릴 때 이 스펙을 참조한다.

이 skill은 **캐릭터만** 정의한다. 레이아웃, 구도, 배경, 주제, 텍스트, 캔버스 크기는 정하지 않는다 —
그것은 이 캐릭터를 불러다 쓰는 skill의 책임이다.

## 캐릭터 스펙 (고정)

### 몸

- **콩 모양(bean shape)의 둥글고 통통한 몸통.** 가로로 살짝 긴 타원에 가깝다.
- **배는 흰색, 등은 밝은 회색.** 배와 등의 경계는 부드러운 곡선이다.
- **작은 옆지느러미 2개.** 몸통에 비해 아주 작아서 귀여움을 만든다.
- **납작한 꼬리지느러미.** 몸 뒤쪽에 작게 붙는다.

### 얼굴

- **까만 점 눈 2개.** 홍채·흰자 없이 점으로만 찍는다.
- **작은 곡선 입.** 기본은 옅은 미소.
- **(선택) 뺨에 연회색 동그라미 패치.** 혈색 표현이며 생략해도 된다.

### 비율과 인상

- 머리·몸 구분이 없는 한 덩어리 실루엣. 전체적으로 낮고 넓은 물방울 느낌.
- 눈·입은 몸통 앞쪽 1/3 안에 모아 아기 같은(kawaii) 인상을 만든다.
- 디테일을 억제한다: 주름, 비늘, 그림자, 질감을 그리지 않는다.

### 선과 색

- **두껍고 끝이 둥근 검은 외곽선**(`#1A1A1A`, 자를 대지 않은 손그림 느낌).
- 기본 팔레트는 흑백이다: 배 `#FFFFFF`, 등 `#D9D9D9`, 뺨 패치 `#F0F0F0`, 외곽선 `#1A1A1A`.
- 이 캐릭터를 쓰는 skill의 그림체가 다르면 **팔레트와 렌더링 기법(선 굵기, 연필·수채·낙서·마커
  채색 등)은 그 skill에 맞춰 치환**할 수 있다. 형태, 비율, 점 눈, 작은 곡선 입은 바꾸지 않는다.

## 표정·포즈 어휘

역할은 표정과 소품으로 표현한다. 자주 쓰는 어휘는 다음과 같고, 같은 문법으로 새 포즈를 만들어도 된다.

- **생각**: 지느러미를 턱에 댄다.
- **신남**: 머리 위로 물줄기 분수를 뿜는다.
- **진지·전문가**: 안경을 쓴다.
- **지침·곤란**: 처진 눈매에 땀방울 하나.
- **작업 중**: 노트북, 돋보기, 렌치 같은 소품을 든다.
- **안내**: 지느러미로 대상을 가리킨다.

소품을 함께 그릴 때는 소품을 캐릭터 키의 60~100% 크기로 크게 그려 실루엣만으로 읽히게 한다.

## 이미지 생성 프롬프트 블록 (재사용)

다른 skill이 이미지 생성 프롬프트를 만들 때, 캐릭터 묘사 자리에 아래 영어 블록을 그대로 끼워 넣는다.

```text
a cute kawaii whale mascot: chubby bean-shaped body, white belly, light gray back,
two tiny side fins, small flat tail, two black dot eyes, a small curved smile,
optional light gray cheek patches. Thick rounded hand-drawn black outlines, simple
geometric shapes, no shading, no texture. Its role is shown by expression and props
(thinking with a fin on its chin, spouting water when excited, wearing glasses when
serious, a single sweat drop when tired, holding a big prop when working).
```

## SVG로 그릴 때

캐릭터를 SVG로 직접 그리는 skill은 기본 도형 5~8개로 조립한다.

- `ellipse` 1개 — 몸통(콩 모양은 살짝 회전하거나 `path`로 아랫배를 부풀린다)
- `path` — 꼬리지느러미와 옆지느러미, 배(흰색) 영역
- `circle` 2개 — 점 눈
- `path` 1개 — 곡선 입
- (선택) `circle` — 뺨 패치

정밀함보다 실루엣과 표정이 읽히는 게 중요하다. 외곽선은 `stroke="#1A1A1A"`에 굵기 3~5,
`stroke-linecap="round"`를 쓴다.

## 하지 않는 것

- 레이아웃·구도·배경·텍스트를 정하지 않는다. 참조하는 skill이 정한다.
- 고래를 사실적으로 그리지 않는다. 항상 위 스펙의 단순한 캐릭터다.
- 형태·비율·점 눈·곡선 입을 변형하지 않는다. 팔레트·렌더링 기법 치환만 허용한다.

## 완료 전 확인 (참조하는 skill용)

- 콩 모양 몸통 + 흰 배 + 밝은 회색 등 + 작은 지느러미 + 점 눈 + 곡선 입인가?
- 두껍고 둥근 손그림 외곽선을 썼는가? 그림자·질감이 없는가?
- 역할이 표정·소품으로 표현됐는가? 소품이 캐릭터 키의 60% 이상인가?
- 팔레트를 바꿨다면 톤 치환만 했고 형태는 그대로인가?
