---
name: akbun-draw-network-relationship
description: >
  첨부한 아키텍처/네트워크 그림이나 컴퍼넌트 설명을 받아, 컴퍼넌트 사이의 네트워크 흐름(트래픽 방향)을
  손그림 스타일로 다시 그리는 이미지 생성 프롬프트를 만든다. 애플리케이션/주체 컴퍼넌트(client, server,
  microservice 등)는 네모박스, 네트워크를 중계하는 컴퍼넌트(proxy, gateway, load balancer, sidecar 등)는
  주황색 네모박스, 애플리케이션→네트워크 컴퍼넌트의 중요한 연결은 초록 네모박스로 강조한다. 모든
  글씨(주석 포함)와 화살표는 검은색으로 통일한다. 같은 논리적 그룹(cluster, node, namespace, VPC 등)은
  필요하면 큰 박스로 감싼다. 이 skill은 그림을 직접 그리지 않고 GPT image, nano-banana 같은 이미지
  생성 모델에 그대로 넣을 영어 프롬프트만 만든다. 사용자가 SVG나 Figma/Canva 편집을 요청하면 같은
  그림을 편집 가능한 텍스트로 담은 SVG 파일도 함께 만든다.
  Trigger on: "네트워크 흐름 그림", "네트워크 관계도", "컴퍼넌트 네트워크 흐름", "트래픽 흐름 그림",
  "아키텍처 흐름 프롬프트", "이 그림 네트워크 흐름으로", "네트워크 흐름 SVG", "network flow prompt",
  "network relationship diagram", "traffic flow figure", "network flow svg", "figma 네트워크 svg",
  "canva 네트워크 svg", or any request to turn an architecture/network picture or component list into an
  image-generation prompt (and optionally an editable SVG) that shows how traffic flows between components.
---

# 네트워크 흐름 그림 프롬프트 생성

## 이 skill이 하는 일

컴퍼넌트 사이에 트래픽이 어떻게 흐르는지를 보여주는 "네트워크 흐름 그림"의 **이미지 생성 프롬프트**를 만든다. 입력은 보통 첨부한 아키텍처/네트워크 그림이거나, 컴퍼넌트와 연결을 적은 설명이다. 결과물은 그림이 아니라, GPT image나 nano-banana 같은 이미지 생성 모델에 그대로 붙여넣을 **영어 프롬프트 한 덩어리**다.

왜 영어인가: 이미지 생성 모델은 영어 글자를 가장 정확히 렌더링한다. 그래서 프롬프트 자체와 그림 속 모든 텍스트(컴퍼넌트 이름/주석/그룹 라벨)를 영어로 쓴다. (SKILL 설명은 한국어, 산출물 프롬프트는 영어다.)

이 skill은 그림을 직접 그리지 않는다. 프롬프트만 만들어 사용자에게 보여주면, 사용자나 다른 agent가 그 프롬프트로 그림을 그린다. `akbun-generateimage-code`가 "코드 설명 그림"을 만드는 것과 짝이 되는, "네트워크 흐름 그림" 버전이다.

사용자가 SVG, Figma, Canva, 벡터, 편집 가능한 파일을 언급하면 프롬프트에 더해 **같은 그림의 SVG 파일**도 만든다(아래 `SVG 산출물 (옵션)` 참고). SVG는 Figma/Canva로 가져와 박스·화살표·글씨를 직접 편집하는 연동 작업용이다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록(```text)에 담아, 그대로 복사해 붙여넣을 수 있게 한다.
2. **한국어 한 줄 설명** — 컴퍼넌트를 어떻게 분류했고 어떤 연결을 강조했는지 1~2문장.

사용자가 SVG(또는 Figma/Canva 편집)를 요청한 경우에만 하나를 추가한다.

- **SVG 파일 (옵션)** — 작업 디렉터리에 `<주제-slug>-network-flow.svg`로 저장하고 경로를 알려준다.

## 컴퍼넌트 분류 (이 skill의 핵심)

그림이 한눈에 읽히려면 "무엇이 일을 하는 주체인가"와 "무엇이 트래픽을 중계하는가"를 색으로 구분해야 한다. 모든 컴퍼넌트를 아래 두 종류 중 하나로 분류한다.

- **애플리케이션/주체 컴퍼넌트** → 평범한 **네모박스(검정/회색 외곽선, 흰 배경)**. 일을 시작하거나 받는 주체다. 예: client, server, App A, microservice, browser, mobile app, worker, endpoint 역할의 database/cache.
- **네트워크 컴퍼넌트(트래픽을 중계하는 것)** → **주황색 네모박스**. 자기 일을 하기보다 트래픽을 받아 다른 곳으로 넘기는 중간자다. 예: proxy, reverse proxy, sidecar, API gateway, ingress/egress gateway, load balancer, CNI, service mesh data plane(ztunnel, Envoy, waypoint proxy), NAT, firewall, CDN edge, message broker가 단순 중계 역할일 때.

주황색은 "여기서 트래픽이 한 번 꺾인다/검사된다/암호화된다"는 신호다. 독자가 흐름을 따라갈 때 주황 박스만 보면 트래픽이 거쳐가는 길목을 알 수 있게 한다. 애매하면 "이 컴퍼넌트를 빼도 출발지와 도착지가 직접 통신하나?"를 물어본다. 빼면 통신이 끊기는 중계자면 네트워크 컴퍼넌트다.

## 논리적 그룹 (옵션, skill이 판단)

같은 경계 안에 있는 컴퍼넌트들은 큰 박스로 감싸면 흐름이 훨씬 잘 읽힌다. 그룹의 예: kubernetes cluster/node/namespace, VPC/subnet, trust domain, 물리 서버, 데이터센터, on-prem vs cloud.

그룹 박스로 감쌀지는 skill이 판단한다. 기준은 단순하다 — **경계를 넘는 연결이 그림의 핵심 메시지일 때** 감싼다(예: 클러스터 A의 앱이 클러스터 B의 앱과 mesh로 통신). 컴퍼넌트가 몇 개뿐이고 경계가 의미를 더하지 않으면 감싸지 않는다. 감쌀 때는 그룹 위쪽에 영어 라벨을 단다(예: "Cluster A", "VPC (10.0.0.0/16)"). 그룹 박스는 얇은 검정 외곽선으로 그려 안의 컴퍼넌트 박스와 구분한다.

## 연결과 주석

- **연결은 방향 화살표**로 그린다. 트래픽이 흐르는 방향을 화살표 머리로 표시한다. 양방향이면 양쪽 화살표. **모든 화살표는 검정색으로 통일한다.** 강조는 화살표 색이 아니라 박스 색으로 한다(아래 참고).
- **연결 위 주석**(프로토콜·identity·포트·암호화처럼 그 연결을 설명하는 짧은 정보)은 **검은색 글씨**로 화살표 옆에 단다. 예: `mTLS`, `HTTP/2`, `gRPC`, `:443`, `spiffe://trust/svcA`. 첨부 그림에 주석이 있으면 그 위치와 내용을 그대로 따른다.
- **모든 글씨는 검은색이다.** 제목·컴퍼넌트 이름·주석·그룹 라벨 전부. 색은 글씨가 아니라 박스에만 쓴다(주황 네트워크 박스, 초록 강조 박스).
- 주석은 그 연결을 이해하는 데 필요한 것만 단다. 모든 화살표에 라벨을 달면 시끄러워지므로, 의미 있는 연결에만 붙인다.

## 중요한 애플리케이션→네트워크 연결 강조 (초록색)

그림에서 독자가 꼭 봐야 할 핵심 경로 — 보통 **애플리케이션이 네트워크 컴퍼넌트로 트래픽을 넘기는 첫 구간**(예: 앱의 트래픽이 sidecar/CNI에 캡처되는 지점, client가 gateway로 진입하는 지점) — 은 **초록색**으로 강조한다. 화살표와 글씨는 검정으로 두고, 그 구간을 **초록 네모박스로 감싼다**(화살표나 글씨를 초록으로 칠하지 않는다).

이 강조는 1~2개로 제한한다. 초록은 "이 흐름의 출발점/관문이 여기다"라는 한두 곳의 신호여야 효과가 있다. 너무 많이 칠하면 강조가 사라진다.

## 작업 순서

1. **입력 파악.** 첨부한 그림이나 컴퍼넌트 설명을 읽는다. 그림이 있으면 거기 있는 컴퍼넌트·화살표·주석·그룹 박스를 그대로 읽어낸다. 텍스트 설명만 있으면 컴퍼넌트와 연결을 목록으로 정리한다.
2. **컴퍼넌트 분류.** 각 컴퍼넌트를 애플리케이션/주체(네모박스) vs 네트워크 컴퍼넌트(주황 박스)로 나눈다.
3. **그룹 판단.** 논리적 그룹을 큰 박스로 감쌀지 결정한다(위 기준).
4. **연결 정리.** 화살표의 출발→도착과 방향을 적고, 주석이 필요한 연결에 검은색 라벨을 붙인다.
5. **핵심 경로 선정.** 애플리케이션→네트워크 컴퍼넌트의 중요한 연결 1~2개를 골라 초록 박스로 강조한다.
6. **제목 결정.** 그림 상단 제목을 영어로 짧게 정한다(예: "Ambient Mesh Traffic Flow"). 아이콘/로고는 없다.
7. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채워 영어 프롬프트를 완성한다.
8. **SVG 조립 (옵션).** 사용자가 SVG/Figma/Canva를 요청했으면 아래 `SVG 산출물 (옵션)` 규칙에 따라 같은 그림을 SVG로 그려 저장한다.
9. **출력.** 영어 프롬프트 블록 + 한국어 한 줄 설명(+ SVG를 만들었으면 파일 경로)을 출력한다.

## 아이콘/로고를 넣지 않는 이유

제품 로고(kubernetes, Envoy, AWS 아이콘 등)는 넣지 않는다. 유명한 것은 이미지 모델이 그럭저럭 그리지만, 덜 알려진 컴퍼넌트는 로고를 제대로 못 그려 결과가 일관되지 않는다. 컴퍼넌트는 이름이 적힌 박스로만 표현한다.

## 비주얼 스타일 (레퍼런스에 고정)

모든 프롬프트는 아래 스타일을 그대로 묘사한다. 첨부 레퍼런스의 화이트보드 손그림 분위기를 따른다.

- **배경**: 깨끗한 흰색 또는 아주 옅은 종이색. 격자 없음.
- **선**: 손으로 그린 듯 살짝 떨리는 마커 선. 깔끔하지만 손그림 느낌.
- **폰트**: 친근한 손글씨/마커 폰트, 모든 글자 영어. **모든 글씨는 검은색**(제목/컴퍼넌트 이름/주석/그룹 라벨).
- **애플리케이션/주체 박스**: 검정~진회색 외곽선의 네모, 흰 배경, 안에 컴퍼넌트 이름.
- **네트워크 컴퍼넌트 박스**: 주황색(`#E8870C` 계열) 외곽선의 네모, 아주 옅은 주황 배경 가능.
- **그룹 박스**: 큰 네모, 얇은 검정 외곽선, 위쪽에 그룹 라벨.
- **연결 화살표**: 방향 화살표는 **모두 검정색**으로 통일한다(강조도 화살표 색으로 하지 않는다).
- **연결 주석**: 화살표 옆 **검은색 글씨**(프로토콜/identity/포트 등).
- **강조(핵심 경로)**: **초록색**(`#2FA84F` 계열) 네모박스. 1~2곳만. (화살표나 글씨는 초록으로 칠하지 않는다.)
- **전체 톤**: 깔끔하고 친근하며 여백이 넉넉. 화살표가 서로 겹치지 않게 가독성 우선.
- **비율**: 가로형 16:9 또는 4:3(컴퍼넌트가 좌우로 흐르면 16:9).

## 레이아웃 (배치 원칙)

- **흐름 방향**: 트래픽의 주된 진행 방향을 **왼쪽→오른쪽**으로 둔다(출발 주체가 왼쪽, 최종 도착이 오른쪽). 레퍼런스처럼 양쪽에 그룹이 있으면 좌측 그룹 → 가운데 중계 → 우측 그룹 순으로 배치한다.
- **그룹**: 같은 그룹 컴퍼넌트는 한 박스 안에 모으고, 박스 사이를 가로지르는 화살표가 흐름의 핵심이 되게 한다.
- **네트워크 컴퍼넌트 위치**: 주황 박스는 보통 두 애플리케이션(또는 두 그룹) 사이의 길목에 둔다. 트래픽이 그 박스를 거쳐 가는 게 한눈에 보이게 한다.
- **주석 위치**: 주석은 해당 화살표 바로 위나 아래에 둬서 어느 연결을 설명하는지 분명히 한다.
- **겹침 금지**: 박스끼리, 화살표끼리, 글자끼리 겹치지 않게 여백을 충분히 둔다.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. 그룹을 쓰지 않으면 GROUPS 줄을 지운다. 사용하지 않는 줄은 지운다.

```text
A horizontal hand-drawn whiteboard-style diagram showing how network traffic flows between
components, drawn with slightly wobbly marker lines on a clean white background, in a friendly
handwritten marker font. All text is in English, and ALL text and ALL arrows are BLACK.

TITLE: a short title at the top in black handwritten marker font, reading exactly: "<TITLE>".

COMPONENTS:
- Application/actor components, drawn as plain rectangles with a dark (near-black) hand-drawn
  outline and white fill, each labeled inside: <list app components, e.g. "App A", "App B", "Client">.
- Network components (things that relay/route/proxy traffic), drawn as rectangles with an ORANGE
  (#E8870C) hand-drawn outline, each labeled inside: <list network components, e.g. "ztunnel",
  "App D waypoint proxy", "CNI", "API gateway">.

GROUPS: enclose related components inside large rectangles with a thin dark outline and a label at
the top of each box: <e.g. left box labeled "Cluster A" contains App A, App C, App B, CNI, ztunnel;
right box labeled "Cluster B" contains App B, App D, App C, CNI, ztunnel>. (Delete this line if no grouping.)

FLOW (all arrows are BLACK and show traffic direction, left to right):
<describe each arrow: from which component to which, e.g. "an arrow from ztunnel (left) to the
App D waypoint proxy in the middle, then from the waypoint proxy to ztunnel (right)">.

CONNECTION LABELS: write these short labels in BLACK text next to the arrow they describe:
<e.g. "mTLS" on the ztunnel-to-waypoint arrow; "spiffe://trust/svcA" below it; "spiffe://trust/svcD"
near the waypoint>.

HIGHLIGHT (the key application-to-network path): keep all arrows and all text black; draw a GREEN
(#2FA84F) rounded rectangle around <the key path/region, e.g. "App A, the CNI and ztunnel it flows
through">. Do not color any arrow or any text green. Keep the green to this one path so it stands out.

STYLE: clean, friendly hand-drawn whiteboard sketch, generous spacing, arrows and labels never
overlapping, very legible. 16:9 aspect ratio.

DO NOT: add any product logos or icons (components are labeled boxes only). No watermarks, no extra
UI chrome. Do not misspell the component names or labels. Do not let arrows or text overlap. Do not
color any text or arrow — color appears only on box outlines (orange network boxes, green highlight box).
```

## SVG 산출물 (옵션)

사용자가 SVG, Figma, Canva, 벡터, 편집 가능한 파일을 언급했을 때만 만든다. 언급이 없으면 프롬프트만 출력한다. SVG는 이미지 프롬프트와 **같은 다이어그램**(같은 컴퍼넌트 분류·그룹·화살표·주석·강조)을 벡터로 그린 것이다. 손그림의 떨리는 선은 SVG에서 재현하지 않는다 — SVG의 목적은 분위기가 아니라 Figma/Canva에서 박스·화살표·글씨를 편집하는 것이므로, 둥근 모서리의 깔끔한 도형으로 그려 편집성을 우선한다.

Figma/Canva 호환을 위해 아래를 지킨다.

- SVG 1.1 기본 요소만 쓴다: `rect`, `circle`, `ellipse`, `path`, `polygon`, `line`, `text`, `g`.
- `filter`, `mask`, `foreignObject`, `marker`, 외부 이미지 참조, 임베디드 폰트는 쓰지 않는다. 화살표 머리는 `marker` 대신 작은 `polygon`으로 직접 그린다.
- 텍스트는 `text` 요소로 남겨 가져온 뒤 바로 편집할 수 있게 한다. 그림 속 텍스트는 프롬프트와 똑같이 전부 영어다.
- 폰트는 저작권 없는 폰트를 사용한다(예: SIL OFL): 라틴 손글씨 `Patrick Hand`, 대체 `Gaegu`(개구체), `Nanum Pen Script`. 셋 다 Google Fonts에서 무료다. Figma/Canva에 해당 폰트가 없으면 fallback으로 표시되며, 텍스트가 편집 가능하므로 원하는 폰트로 바꾸면 된다.

스타일 키트 (비주얼 스타일을 SVG 값으로 옮긴 것):

- 배경: `<rect>` 전체를 `#FFFFFF`로 채운다.
- 애플리케이션/주체 박스: `rect`(둥근 모서리 `rx` 12~16), `stroke="#2B2B2B"`, `stroke-width` 5~7, `stroke-linejoin="round"`, 흰 배경.
- 네트워크 컴퍼넌트 박스: 같은 `rect`에 `stroke="#E8870C"`, 배경은 아주 옅은 주황 `#FDF3E7`.
- 그룹 박스: 얇은(3~4) `#2B2B2B` 외곽선의 큰 `rect`, 왼쪽 위 안쪽에 그룹 라벨 `text`.
- 화살표: 검정 `line`(또는 `path`) + 검정 `polygon` 화살표 머리. 모두 `#2B2B2B`.
- 글씨: 모든 `text`(제목/컴퍼넌트 이름/주석/그룹 라벨)는 `fill="#2B2B2B"`. 연결 주석은 화살표 바로 위/아래에 둔다.
- 강조(핵심 경로): `fill="none"`, `stroke="#2FA84F"`의 둥근 `rect`로 해당 구간을 감싼다. 1~2곳만.
- 캔버스: 16:9(예: `viewBox="0 0 1600 900"`). 겹침 금지 원칙은 SVG에서도 동일하다.

## SVG 예시

작은 입력("client가 API gateway를 거쳐 VPC 안 app server로 들어가는 흐름, gateway 진입 구간 강조")을 위 스타일 키트로 그린 SVG다. 컴퍼넌트 수가 많아도 같은 요소(박스·화살표 머리·주석·초록 강조)를 반복하면 된다.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">
  <!-- palette: bg #FFFFFF / ink #2B2B2B (all text & arrows) / network box #E8870C (fill #FDF3E7) / highlight box #2FA84F -->
  <rect width="1600" height="900" fill="#FFFFFF"/>

  <text x="800" y="120" text-anchor="middle" fill="#2B2B2B" font-size="64"
        font-family="'Patrick Hand', Gaegu, 'Nanum Pen Script', sans-serif">Client Traffic Flow</text>

  <!-- group box: VPC -->
  <rect x="640" y="280" width="840" height="400" rx="18" fill="none" stroke="#2B2B2B" stroke-width="4"/>
  <text x="676" y="344" fill="#2B2B2B" font-size="40"
        font-family="'Patrick Hand', Gaegu, 'Nanum Pen Script', sans-serif">VPC</text>

  <!-- application/actor boxes -->
  <g fill="#FFFFFF" stroke="#2B2B2B" stroke-width="6" stroke-linejoin="round">
    <rect x="120" y="400" width="280" height="140" rx="16"/>
    <rect x="1150" y="400" width="280" height="140" rx="16"/>
  </g>

  <!-- network component box (orange) -->
  <rect x="730" y="400" width="290" height="140" rx="16" fill="#FDF3E7"
        stroke="#E8870C" stroke-width="6" stroke-linejoin="round"/>

  <!-- component labels (editable text) -->
  <g fill="#2B2B2B" font-size="44" text-anchor="middle"
     font-family="'Patrick Hand', Gaegu, 'Nanum Pen Script', sans-serif">
    <text x="260" y="486">Client</text>
    <text x="875" y="486">API Gateway</text>
    <text x="1290" y="486">App Server</text>
  </g>

  <!-- arrows: black lines + polygon heads (no marker element) -->
  <g stroke="#2B2B2B" stroke-width="6" stroke-linecap="round" fill="#2B2B2B">
    <line x1="400" y1="470" x2="696" y2="470"/>
    <polygon points="730,470 692,452 692,488" stroke="none"/>
    <line x1="1020" y1="470" x2="1116" y2="470"/>
    <polygon points="1150,470 1112,452 1112,488" stroke="none"/>
  </g>

  <!-- connection labels (black, like all text) -->
  <g fill="#2B2B2B" font-size="38" text-anchor="middle"
     font-family="'Patrick Hand', Gaegu, 'Nanum Pen Script', sans-serif">
    <text x="560" y="436">HTTPS :443</text>
    <text x="1100" y="436">mTLS</text>
  </g>

  <!-- green highlight: the key client-to-gateway entry path -->
  <rect x="90" y="360" width="950" height="230" rx="24" fill="none" stroke="#2FA84F" stroke-width="6"/>
</svg>
```

## 예시 (gold reference)

이 예시는 위 스타일을 그대로 적용한 완성 프롬프트다. 새 프롬프트의 품질 기준으로 삼는다.

입력 예: Istio ambient mesh 흐름 그림 한 장. 왼쪽 클러스터(App A/C/B, CNI, ztunnel), 가운데 App D waypoint proxy, 오른쪽 클러스터(App B/D/C, CNI, ztunnel). 화살표에 mTLS와 spiffe identity 주석. App A → CNI → ztunnel 캡처 경로는 초록 박스.

skill이 한 분류(자동): App A/B/C/D는 애플리케이션(네모박스). CNI, ztunnel, App D waypoint proxy는 트래픽을 중계하므로 네트워크 컴퍼넌트(주황 박스). 두 클러스터를 그룹 박스로 감쌌다. 핵심 경로(App A의 트래픽이 CNI를 거쳐 ztunnel에 캡처되는 구간)를 초록 박스로 강조했다. 글씨와 화살표는 전부 검정이다.

출력 프롬프트:

```text
A horizontal hand-drawn whiteboard-style diagram showing how network traffic flows between
components, drawn with slightly wobbly marker lines on a clean white background, in a friendly
handwritten marker font. All text is in English, and ALL text and ALL arrows are BLACK.

TITLE: a short title at the top in black handwritten marker font, reading exactly: "Ambient Mesh Traffic Flow".

COMPONENTS:
- Application/actor components, drawn as plain rectangles with a dark (near-black) hand-drawn
  outline and white fill, each labeled inside: "App A", "App C", "App B" (left), and "App B",
  "App D", "App C" (right).
- Network components (things that relay/route/proxy traffic), drawn as rectangles with an ORANGE
  (#E8870C) hand-drawn outline, each labeled inside: "CNI" and "ztunnel" (left), "App D waypoint
  proxy" (middle), "CNI" and "ztunnel" (right).

GROUPS: enclose related components inside two large rectangles with a thin dark outline. The left
box contains App A, App C, App B, CNI, and ztunnel. The right box contains App B, App D, App C,
CNI, and ztunnel. The App D waypoint proxy sits in the middle, between the two boxes.

FLOW (all arrows are BLACK and show traffic direction, left to right): an arrow from the left
ztunnel to the App D waypoint proxy in the middle, then an arrow from the waypoint proxy to the
right ztunnel, then into the right CNI and on to App D.

CONNECTION LABELS: write these short labels in BLACK text next to the arrow they describe: "mTLS"
above the ztunnel-to-waypoint arrow and above the waypoint-to-ztunnel arrow; "spiffe://trust/svcA"
below the left ztunnel; "spiffe://trust/svcD" below the waypoint proxy area; "spiffe://trust/svcD"
near the right ztunnel.

HIGHLIGHT (the key application-to-network path): keep all arrows and all text black. Draw a GREEN
(#2FA84F) rounded rectangle around App A together with the left CNI and ztunnel it flows through,
showing App A's traffic being captured into the mesh. Draw a matching green rectangle around the
right ztunnel, CNI and App D. Do not color any arrow or any text green. Keep the green to these
capture regions so they stand out.

STYLE: clean, friendly hand-drawn whiteboard sketch, generous spacing, arrows and labels never
overlapping, very legible. 16:9 aspect ratio.

DO NOT: add any product logos or icons (components are labeled boxes only). No watermarks, no extra
UI chrome. Do not misspell the component names or labels. Do not let arrows or text overlap. Do not
color any text or arrow — color appears only on box outlines (orange network boxes, green highlight box).
```

한국어 한 줄 설명: App들은 네모박스로, 트래픽을 중계하는 CNI·ztunnel·waypoint proxy는 주황 박스로 구분하고, App A가 CNI를 거쳐 ztunnel에 캡처되는 핵심 경로는 초록 박스로 강조했습니다. mTLS·spiffe identity 주석을 포함해 글씨와 화살표는 모두 검정입니다.

## 완료 전 확인

- 그림 속 모든 텍스트(제목/컴퍼넌트 이름/주석/그룹 라벨)가 영어인가?
- 애플리케이션/주체는 검정 외곽선 네모, 트래픽을 중계하는 네트워크 컴퍼넌트는 주황 네모로 분류했는가?
- 연결 위 주석(프로토콜·identity 등)을 검은색 글씨로, 의미 있는 연결에만 달았는가?
- 모든 글씨와 화살표를 검정색으로 통일했는가? (색은 주황 네트워크 박스와 초록 강조 박스에만 쓰였는가?)
- 애플리케이션→네트워크 컴퍼넌트의 핵심 경로를 초록 박스로 1~2곳만 강조했는가?
- 논리적 그룹은 경계를 넘는 연결이 핵심일 때만 박스로 감쌌는가?
- 로고/아이콘 없이 이름이 적힌 박스로만 표현했는가? (DO NOT에 로고 금지를 넣었는가?)
- 화살표·박스·글자가 겹치지 않게 배치를 지시했는가?
- 프롬프트를 그대로 복사해 이미지 모델에 붙여넣을 수 있는 한 블록으로 출력했는가?
- SVG는 사용자가 요청했을 때만 만들었는가? 만들었다면 — 기본 요소만 쓰고, 화살표 머리를 `marker` 없이 `polygon`으로 그리고, 텍스트가 편집 가능한 `text`(저작권 없는 폰트)로 남아 있으며, 프롬프트와 같은 분류·강조를 담았는가? 파일 경로를 알려줬는가?
