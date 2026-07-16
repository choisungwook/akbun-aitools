---
name: akbun-generateimage-code
description: >
  코드 내용을 포인트로 짚어 설명하는 블로그용 그림(figure)의 이미지 생성 프롬프트를 만든다.
  springboot, python, kubernetes manifest, bash 실행결과 같은 코드를 받아서, GPT image나 nano-banana 같은
  이미지 생성 모델에 그대로 넣을 영어 프롬프트를 만든다. 이 skill은 그림을 직접 그리지 않고, 다른 agent나
  이미지 모델이 그릴 프롬프트만 생성한다. 강조할 부분(초록 박스/화살표/콜아웃)은 skill이 자동으로 판단한다.
  Trigger on: "코드 그림 프롬프트", "코드 설명 그림", "코드 figure", "코드 일러스트", "이 코드 그림으로 설명",
  "블로그 코드 이미지", "코드 이미지 프롬프트", "code figure prompt", "code illustration prompt",
  or any request to turn code into an explanatory blog figure prompt.
---

# 코드 설명 그림 프롬프트 생성

## 이 skill이 하는 일

블로그 글에 넣을 "코드 설명 그림"의 **이미지 생성 프롬프트**를 만든다. 결과물은 그림이 아니라, GPT image
또는 nano-banana 같은 이미지 생성 모델에 그대로 붙여넣을 **영어 프롬프트 한 덩어리**다.

왜 영어인가: GPT image, nano-banana 같은 이미지 생성 모델은 영어 글자를 가장 정확히 렌더링한다. 그래서
프롬프트 자체와 그림 속 모든 텍스트(제목/코드/콜아웃)를 영어로 쓴다. (SKILL 설명은 한국어, 산출물 프롬프트는 영어다.)

이 skill은 그림을 직접 그리지 않는다. 프롬프트만 만들어서 사용자에게 보여주면, 사용자나 다른 agent가 그
프롬프트로 그림을 그린다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록(```text)에 담아, 그대로 복사해 붙여넣을 수 있게 한다.
2. **한국어 한 줄 설명** — 무엇을 강조했고 왜 그것을 골랐는지 1~2문장.

## 작업 순서

1. **코드와 맥락 파악.** 사용자가 준 코드(springboot/java, python, kubernetes manifest, bash 실행결과 등)와,
   이 그림이 들어갈 블로그 글의 주제를 읽는다. 글 제목이나 핵심 메시지가 있으면 그림 제목에 반영한다.
2. **강조할 포인트 자동 선정.** 사용자가 따로 지정하지 않아도 skill이 핵심을 고른다. "이 코드에서 독자가
   딱 봐야 할 1~3곳은 어디인가"를 기준으로 고른다. 선정 기준은 아래 `강조 포인트 고르기`를 따른다.
3. **코드 줄이기.** 이미지 모델은 긴 코드를 글자 깨짐 없이 그리지 못한다. 핵심을 보여주는 최소 줄(보통 4~12줄)만
   남기고 나머지는 잘라낸다. 잘라낸 자리는 `# ...` 또는 `...` 한 줄로 표시할 수 있다.
4. **그림 제목 결정.** 제목은 영어로 짧게(예: "Conntrack Exhaustion in Kubernetes"). 아이콘/로고는 넣지 않는다.
5. **콜아웃 라벨 작성.** 강조 지점마다 짧은 영어 라벨(2~4단어)을 만든다. 예: "conntrack config",
   "conntrack error".
6. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채워 영어 프롬프트를 완성한다.
7. **출력.** 영어 프롬프트 블록 + 한국어 한 줄 설명을 출력한다.

## 강조 포인트 고르기 (skill이 자동 판단)

독자가 글의 메시지를 이해하려면 코드에서 무엇을 봐야 하는지를 기준으로 1~3곳을 고른다. 너무 많이 강조하면
그림이 시끄러워지므로 **최대 3개**로 제한한다.

좋은 강조 후보:

- 글의 주제와 직결되는 설정값/파라미터 (예: `maxPerCore`, `min` 같은 conntrack 튜닝 값)
- 문제의 원인이나 증상을 보여주는 줄 (예: `nf_conntrack: table full, dropping packet` 에러 로그)
- springboot: 핵심 어노테이션(`@Transactional`, `@Async`), 빈 설정, 중요한 프로퍼티
- python: 함정이 되는 한 줄(가변 기본 인자, 동기/비동기 경계), 핵심 함수 호출
- kubernetes manifest: `resources.limits/requests`, `securityContext`, `probe`, 셀렉터/라벨 매칭
- bash 실행결과: 의미 있는 출력 한 줄(에러, 카운트, 상태) — 명령어와 결과를 함께 보여줄 때 효과적

코드 블록 한 곳을 묶어 강조할 때는 **초록 박스 + 화살표 + 콜아웃**을 함께 쓰고, 한 줄(특히 bash 결과/에러)을
강조할 때도 같은 조합을 쓴다. 레퍼런스 이미지처럼 "설정 블록"과 "그 결과 에러"를 한 그림에 함께 담으면
인과 관계가 잘 드러난다.

## 아이콘/로고를 넣지 않는 이유

제목 옆에 기술 로고(아이콘)를 넣지 않는다. kubernetes처럼 유명한 것은 이미지 모델이 로고를 잘 그리지만,
덜 알려진 기술은 로고를 제대로 그리지 못해 결과가 일관되지 않기 때문이다. 헤더는 제목 텍스트만 둔다.

## 비주얼 스타일 (레퍼런스에 고정)

모든 프롬프트는 아래 스타일을 그대로 묘사한다. 이 스타일은 바꾸지 않는다.

- **창**: 둥근 모서리의 다크 코드 에디터/터미널 창. 배경은 따뜻한 거의 검정(near-black, `#2A2622` 계열).
- **창 장식**: 좌측 상단에 macOS 신호등 점 3개(빨강/노랑/초록).
- **제목**: 친근한 둥근 손글씨/마커 폰트, 흰색. 아이콘/로고 없이 제목 텍스트만.
- **코드**: 모노스페이스, 다크 배경 위 신택스 하이라이트.
  - keys/identifiers: 핑크 `#E06C9F`
  - strings/values: 따뜻한 오렌지 `#E5A86B`
  - numbers: 보라 `#A78BFA`
  - 기호/구두점: 밝은 회색
- **강조 박스**: 채움 없는 둥근 사각형 외곽선, 밝은 초록 `#7EE787`.
- **화살표**: 손으로 그린 듯한 곡선 화살표, 밝은 노랑 `#FFE600`. 콜아웃에서 강조 지점으로 향한다.
- **콜아웃 라벨**: 흰색 둥근 사각형 박스 안에 진한 굵은 글씨(영어).
- **전체 톤**: 깔끔하고 친근하며 대비가 높고 여백이 넉넉. 가독성 우선.
- **비율**: 가로형 4:3.

## 레이아웃 (배치, 레퍼런스에 고정)

일관성을 위해 모든 그림은 같은 3-zone 배치를 따른다. 이 배치는 바꾸지 않는다.

- **세로 3구역**: 위에서부터 (1) 헤더, (2) 코드, (3) 코드 아래 여백. 전체적으로 여백을 넉넉히 둔다.
- **헤더 (상단)**: 제목 텍스트만 왼쪽 정렬로 둔다(아이콘/로고 없음). 제목이 길면 두 줄로 줄바꿈한다.
  헤더 위쪽에 충분한 패딩을 둔다.
- **코드 (좌측 컬럼)**: 코드는 창의 왼쪽 약 60% 폭에 **왼쪽 정렬 한 컬럼**으로 둔다. 소스 순서대로 위→아래로
  흐른다. 논리적으로 다른 묶음(예: YAML 설정 ↔ shell 출력) 사이에는 빈 줄로 간격을 둔다.
- **콜아웃 (우측 여백)**: 흰 콜아웃 박스는 창의 **오른쪽 약 35% 여백**에 띄운다. 각 콜아웃은 자신이 가리키는
  코드 영역과 **세로 높이를 맞추고**, 대상의 위→아래 순서 그대로 위에서 아래로 쌓는다. 원인/설정 콜아웃을 위에,
  결과/에러 콜아웃을 아래에 둔다. 코드와 콜아웃 박스가 겹치지 않게 한다.
- **화살표**: 각 노랑 곡선 화살표는 강조 영역의 **오른쪽 가장자리에서 출발해** 바깥쪽 콜아웃 박스로 향한다.
- **읽는 순서**: 왼쪽 위 → 아래. 인과(설정 → 에러)가 위에서 아래로 자연스럽게 읽히게 배치한다.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. 사용하지 않는 콜아웃 줄은 지운다.

```text
A horizontal blog illustration drawn in the style of a dark code editor screenshot,
hand-annotated like a teacher circling the important parts.

WINDOW: a rounded-corner dark editor window on a warm near-black background (#2A2622).
Three macOS traffic-light dots (red, yellow, green) in the top-left corner.

LAYOUT: use three zones with generous whitespace. (1) HEADER at the top: a large left-aligned
title only, no icon or logo (the title may wrap to two lines), with ample top padding. (2) CODE
in a single left-aligned column occupying the left ~60% of the window, flowing top-to-bottom in
source order, with a blank-line gap between logical groups. (3) CALLOUT label boxes floating in
the right ~35% margin, each vertically aligned with the code region it points to and stacked in
the same top-to-bottom order as their targets (cause/config above, effect/error below). Code
never overlaps a callout box.

HEADER: a large title written in a friendly, rounded handwritten marker font, in white, with no
icon or logo. The title reads exactly: "<TITLE>".

CODE: monospaced source code on the dark background, syntax-highlighted. Render this code
EXACTLY as written, character for character, with correct spelling and indentation:
<CODE LINES>
Syntax colors: keys/identifiers in pink (#E06C9F), strings/values in warm orange (#E5A86B),
numbers in purple (#A78BFA), punctuation in light gray.

HIGHLIGHTS: draw a rounded-rectangle outline, no fill, in bright green (#7EE787) around: <REGION 1>.
<draw a second green rounded-rectangle outline around: <REGION 2>.>

ANNOTATIONS: hand-drawn curved arrows in bright yellow (#FFE600). Each arrow starts at the right
edge of its highlighted region and curves rightward to a white rounded callout label box (dark
bold English text inside) in the right margin.
Callout 1 label: "<LABEL 1>" pointing to <REGION 1>.
<Callout 2 label: "<LABEL 2>" pointing to <REGION 2>.>

STYLE: clean, friendly, high-contrast, generous spacing, very legible. 4:3 aspect ratio.

DO NOT: add any text other than the title, the code shown above, and the callout labels.
Do not misspell or alter the code. No logos or icons. No watermarks, no extra UI chrome, no menu bars.
```

## 예시 (gold reference)

이 예시는 위 `비주얼 스타일`을 그대로 적용한 완성 프롬프트다. 새 프롬프트의 품질 기준으로 삼는다.

입력 예:

```text
글 주제: 쿠버네티스에서 conntrack table이 가득 차서 패킷이 드롭되는 문제
코드: kube-proxy conntrack 설정 + /var/log/messages 에러 로그
```

skill이 고른 강조(자동): (1) conntrack 튜닝 설정 블록, (2) conntrack table full 에러 로그. 두 곳을 골라
"설정 → 그 결과 에러"의 인과를 한 그림에 담았다.

출력 프롬프트:

```text
A horizontal blog illustration drawn in the style of a dark code editor screenshot,
hand-annotated like a teacher circling the important parts.

WINDOW: a rounded-corner dark editor window on a warm near-black background (#2A2622).
Three macOS traffic-light dots (red, yellow, green) in the top-left corner.

LAYOUT: use three zones with generous whitespace. (1) HEADER at the top: a large left-aligned
title only, no icon or logo (the title may wrap to two lines), with ample top padding. (2) CODE
in a single left-aligned column occupying the left ~60% of the window, flowing top-to-bottom in
source order, with a blank-line gap between the YAML config and the shell output. (3) CALLOUT
label boxes floating in the right ~35% margin, each vertically aligned with the code region it
points to and stacked top-to-bottom (conntrack config above, conntrack error below). Code never
overlaps a callout box.

HEADER: a large title written in a friendly, rounded handwritten marker font, in white, with no
icon or logo. The title reads exactly: "Conntrack Exhaustion in Kubernetes".

CODE: monospaced source code on the dark background, syntax-highlighted. Render this code
EXACTLY as written, character for character, with correct spelling and indentation:
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
conntrack:
  maxPerCore: 32768
  min: 131072
  tcpCloseWaitTimeout: 60s
  tcpEstablishedTimeout: 24h

$ tail -f /var/log/messages | grep conntrack
nf_conntrack: table full, dropping packet
Syntax colors: keys/identifiers in pink (#E06C9F), strings/values in warm orange (#E5A86B),
numbers in purple (#A78BFA), punctuation in light gray.

HIGHLIGHTS: draw a rounded-rectangle outline, no fill, in bright green (#7EE787) around the
whole "conntrack:" block (maxPerCore, min, tcpCloseWaitTimeout, tcpEstablishedTimeout).
Draw a second green rounded-rectangle outline around the line "nf_conntrack: table full, dropping packet".

ANNOTATIONS: hand-drawn curved arrows in bright yellow (#FFE600). Each arrow starts at the right
edge of its highlighted region and curves rightward to a white rounded callout label box (dark
bold English text inside) in the right margin.
Callout 1 label: "conntrack config" pointing to the conntrack block.
Callout 2 label: "conntrack error" pointing to the nf_conntrack error line.

STYLE: clean, friendly, high-contrast, generous spacing, very legible. 4:3 aspect ratio.

DO NOT: add any text other than the title, the code shown above, and the callout labels.
Do not misspell or alter the code. No logos or icons. No watermarks, no extra UI chrome, no menu bars.
```

한국어 한 줄 설명: conntrack 튜닝 설정 블록과 그로 인한 `table full` 에러 로그 두 곳을 강조해, 설정과 증상의
인과를 한 그림에 담았습니다.

## 완료 전 확인

- 그림 속 모든 텍스트(제목/코드/콜아웃)가 영어인가?
- 코드는 4~12줄 수준으로 짧고, 글자가 깨지지 않을 만큼 핵심만 남겼는가?
- 강조는 1~3개로 제한했는가? 각 강조에 초록 박스 + 노랑 화살표 + 흰 콜아웃이 연결됐는가?
- 3-zone 배치를 지켰는가? 헤더(제목만) 상단, 코드 좌측 컬럼, 콜아웃 우측 여백, 화살표는 코드→콜아웃 방향인가?
- 헤더에 아이콘/로고 없이 제목 텍스트만 있는가? (DO NOT에 "No logos or icons"를 넣었는가?)
- 프롬프트를 그대로 복사해 이미지 모델에 붙여넣을 수 있는 한 블록으로 출력했는가?
