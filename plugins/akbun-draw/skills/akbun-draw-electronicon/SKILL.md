---
name: akbun-draw-electronicon
disable-model-invocation: true
description: >
  Electron.js 데스크톱 앱의 앱 아이콘(설치 아이콘·dock·작업표시줄 아이콘)을 akbun 고래
  마스코트로 만드는 skill. 사용자와 짧은 인터뷰로 앱의 핵심 기능을 확인한 뒤, 그 기능을
  상징하는 소품을 든 고래 아이콘의 이미지 생성 프롬프트를 만들고, 생성된 이미지를 KB 수준으로
  압축해 icon.png/.icns/.ico로 적용하는 방법까지 안내한다. 사용자가 electron 아이콘, 앱 아이콘,
  데스크톱 앱 아이콘, 설치 이미지 교체, app icon을 언급하면 이 skill을 사용한다.
---

# Electron 앱 아이콘 프롬프트 생성

## 이 skill이 하는 일

Electron.js 앱의 기본 아이콘을 대체할 **akbun 고래 마스코트 아이콘 1개**를 만든다.
결과물은 이미지 생성 모델(GPT image, nano-banana 등)에 그대로 붙여넣는 **영어 프롬프트 1개**와,
생성된 이미지를 **KB 수준으로 압축해 Electron에 적용하는 절차**다. 그림을 직접 그리지 않는다.

아이콘은 16px에서도 읽혀야 하므로, 포스터·카드뉴스와 달리 요소를 극단적으로 줄인다:
고래 1마리 + 앱 기능을 상징하는 소품 1개 + 단색 배경. 텍스트는 넣지 않는다.

## 작업 순서

1. **인터뷰.** 아래 인터뷰 질문으로 앱의 핵심 기능을 파악한다.
2. **소품·포즈 결정.** 기능을 상징하는 소품 하나와 고래 포즈를 정해 사용자에게 한 줄로 보여준다.
3. **프롬프트 조립.** 아래 템플릿을 채워 프롬프트 한 블록을 출력한다.
4. **팁 덧붙이기.** 출력 맨 끝에 `파일 크기 줄이기 (KB 수준)`의 압축 팁과 Electron 적용
   절차를 붙인다. 프롬프트만 출력하고 끝내지 않는다 — 사용자는 생성된 이미지를 받아
   바로 압축·적용해야 하므로 이 팁이 항상 함께 전달돼야 한다.

## 인터뷰 질문

사용자가 이미 답을 줬으면 그 항목은 묻지 않는다. 한 번에 묶어서 짧게 묻는다.

1. **앱이 하는 일이 무엇인가?** 한두 문장이면 충분하다.
2. **아이콘에 담을 대표 기능 하나는?** 기능이 여러 개면 사용자가 하나를 고르게 한다.
   아이콘에는 개념 하나만 들어간다 — 두 개를 합치면 16px에서 아무것도 안 읽힌다.
3. **배경색 취향이 있는가?** 없으면 skill이 앱 성격에 맞는 단색을 하나 제안한다.

## 아이콘 스타일 스펙 (고정)

- **비율 1:1, 1024×1024로 생성.** Electron/electron-builder가 요구하는 원본 크기다.
- **캐릭터는 `akbun-mascot-whale` skill의 캐릭터 스펙을 그대로 따른다** — 콩 모양 몸통,
  흰 배, 밝은 회색 등, 작은 지느러미, 점 눈 2개, 곡선 입, 두껍고 둥근 손그림 외곽선.
- **소품은 크게.** 기능을 상징하는 소품 1개를 고래 키의 60~100% 크기로 그린다.
  소품 실루엣만으로 기능이 읽혀야 한다.
- **배경은 단색 1가지.** 그라디언트·패턴·질감·그림자를 넣지 않는다. 플랫 컬러만 쓴다
  (이게 파일 크기를 KB 수준으로 만드는 핵심이기도 하다).
- **여백.** 고래+소품을 캔버스 중앙에 두고, 가장자리에서 캔버스의 약 12%를 비운다.
  macOS는 아이콘을 둥근 사각형(squircle)으로 자르므로 모서리에 요소를 두지 않는다.
- **텍스트 금지.** 글자는 작은 크기에서 깨진다.

## 프롬프트 템플릿

`<...>`를 인터뷰 결과로 채운다.

```text
ONE flat app icon, perfect square 1:1, 1024x1024, solid <BACKGROUND COLOR> background,
no gradients, no textures, no shadows, no text.

CHARACTER: a cute kawaii whale mascot: chubby bean-shaped body, white belly, light gray
back, two tiny side fins, small flat tail, two black dot eyes, a small curved smile.
Thick rounded hand-drawn black outlines, simple geometric shapes, flat colors only.

SCENE: the whale is centered, <POSE — e.g. holding / sitting on / pointing at>
a big <PROP that symbolizes the app's function>, drawn as large as the whale itself,
recognizable by silhouette alone. Only the whale and this one prop — nothing else.

COMPOSITION: character and prop grouped in the center, generous empty margin (about 12%
of the canvas) on all sides so nothing is cut when the icon is masked to a rounded square.
The design must stay readable when shrunk to 16x16 pixels.

DO NOT: add text or letters, add a second prop or character, use gradients or textures,
add background scenery, or let anything touch the canvas edges.
```

## 파일 크기 줄이기 (KB 수준)

이 섹션의 내용은 **매번 출력의 맨 끝에 팁으로 덧붙여** 사용자에게 전달한다.

이미지 생성 모델은 출력 파일 크기를 지정할 수 없어서 1024px PNG가 보통 1~2MB로 나온다.
하지만 위 스펙(플랫 단색, 질감 없음)은 압축이 아주 잘 되므로, 아래 후처리로 수십 KB까지 줄어든다.

색상 수를 줄여 PNG를 압축한다(무손실에 가깝다, 보통 원본의 5~10% 크기):

```bash
pngquant --quality 65-90 --output icon.png --force generated.png
```

pngquant가 없으면 macOS 기본 도구로 크기만 줄여도 효과가 크다(512px이면 Electron에 충분하다):

```bash
sips -Z 512 generated.png --out icon.png
```

## Electron 적용 방법

electron-builder 기준 절차를 안내한다. `build/` 디렉터리에 아이콘을 두면 자동으로 집는다.

플랫폼별 아이콘을 원본 PNG 하나에서 생성한다:

```bash
npx electron-icon-builder --input=icon.png --output=build
```

- 결과: `build/icons/`에 `icon.icns`(macOS), `icon.ico`(Windows), 각 크기 PNG(Linux)가 생긴다.
- `package.json`의 `build.mac.icon`, `build.win.icon`, `build.linux.icon`이 기본 경로와 다르면 지정한다.
- electron-forge를 쓰면 `packagerConfig.icon`에 확장자 없이 `"./build/icons/icon"`을 지정한다.

## 예시 (gold reference)

입력 예:

```text
마크다운 노트를 로컬에 저장하는 Electron 앱이야. 아이콘 만들어줘.
```

skill이 한 판단: 대표 기능은 "노트 작성"이므로 소품을 큰 연필 한 자루로 정하고,
차분한 앱 성격에 맞춰 배경을 크림색(#FFF6E3)으로 제안했다.

출력 프롬프트:

```text
ONE flat app icon, perfect square 1:1, 1024x1024, solid warm cream (#FFF6E3) background,
no gradients, no textures, no shadows, no text.

CHARACTER: a cute kawaii whale mascot: chubby bean-shaped body, white belly, light gray
back, two tiny side fins, small flat tail, two black dot eyes, a small curved smile.
Thick rounded hand-drawn black outlines, simple geometric shapes, flat colors only.

SCENE: the whale is centered, hugging a big yellow pencil as large as the whale itself,
recognizable by silhouette alone. Only the whale and this one prop — nothing else.

COMPOSITION: character and prop grouped in the center, generous empty margin (about 12%
of the canvas) on all sides so nothing is cut when the icon is masked to a rounded square.
The design must stay readable when shrunk to 16x16 pixels.

DO NOT: add text or letters, add a second prop or character, use gradients or textures,
add background scenery, or let anything touch the canvas edges.
```

## 완료 전 확인

- 인터뷰로 대표 기능 **하나**를 확정했는가? (여러 기능을 한 아이콘에 섞지 않았는가?)
- 고래가 `akbun-mascot-whale` 스펙 그대로인가? 소품이 고래 키의 60% 이상인가?
- 배경이 단색이고 텍스트·그라디언트·질감이 없는가?
- 가장자리 여백(약 12%)을 지정했는가?
- 출력 맨 끝에 파일 크기 압축 팁과 Electron 적용 절차를 덧붙였는가?
