---
name: akbun-draw-component
description: >
  사용자가 남긴 코드나 소프트웨어 컴퍼넌트를 분석해, 하이레벨 아키텍처 또는 컴퍼넌트 연관관계
  다이어그램의 이미지 생성 프롬프트를 만든다. 꼭 필요한 컴퍼넌트만 남겨 큰 그림(big picture)으로
  추상화하고, 연관관계의 설명은 화살표 라벨에 넣는다. 논리적 경계(cluster, node, namespace, VPC 등)는
  점선 박스로 감싼다. 이 skill은 그림을 직접 그리지 않고, 이미지 생성 AI agent가 프롬프트를 받아
  이미지를 생성한다.
  Trigger on: "컴퍼넌트 그림", "아키텍처 그림", "구조도", "연관관계 그림", "하이레벨 아키텍처",
  "이 코드 구조 그려줘", "component diagram", "architecture diagram prompt", "high-level architecture",
  or any request to turn code or a set of software components into a high-level
  architecture/relationship diagram prompt.
---

# 하이레벨 컴퍼넌트 아키텍처 그림 프롬프트 생성

## 이 skill이 하는 일

사용자가 남긴 코드나 소프트웨어 컴퍼넌트를 분석해, **하이레벨 아키텍처 또는 컴퍼넌트 연관관계 다이어그램**의 이미지 생성 프롬프트를 만든다. 결과물은 그림이 아니라, GPT image나 nano-banana 같은 **이미지 생성 AI agent가 받아 그대로 그릴 영어 프롬프트 한 덩어리**다.

이 skill은 아키텍트의 시선으로 그린다. 함수·클래스·파일 수준의 세부가 아니라, "이 시스템은 어떤 컴퍼넌트로 이루어져 있고 서로 어떻게 엮이는가"를 처음 보는 사람도 한눈에 이해할 수 있는 **큰 뷰**로 추상화한다. 연관관계의 설명은 화살표에 라벨로 붙인다.

왜 영어인가: 이미지 생성 모델은 영어 글자를 가장 정확히 렌더링한다. 그래서 프롬프트 자체와 그림 속 모든 텍스트(컴퍼넌트 이름/화살표 라벨/경계 라벨)를 영어로 쓴다. (SKILL 설명은 한국어, 산출물 프롬프트는 영어다.)

`akbun-generateimage-code`(코드 설명 그림), `akbun-draw-network-relationship`(네트워크 트래픽 흐름 그림)과 짝이 되는, "하이레벨 컴퍼넌트 아키텍처" 버전이다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **영어 이미지 생성 프롬프트** — 한 개의 코드 펜스 블록(```text)에 담아, 그대로 복사해 이미지 생성 AI agent에 붙여넣을 수 있게 한다.
2. **한국어 한 줄 설명** — 어떤 컴퍼넌트를 남기고 무엇을 합쳤는지, 어떤 관계를 화살표로 그렸는지 1~2문장.

## 추상화 원칙 (이 skill의 핵심)

이 skill의 목표는 상세 설계도가 아니라 **정말 필요한 것만 남긴 큰 그림**이다. 처음 보는 사람이 10초 안에 구조를 파악할 수 있어야 한다.

- **컴퍼넌트는 3~8개로 제한한다.** 그 이상이면 아직 덜 추상화한 것이다. 역할이 같은 것들은 하나로 합친다(예: 여러 worker 프로세스 → "Workers" 박스 하나, 여러 마이크로서비스 → 역할 단위 박스).
- **함수/클래스/파일은 그리지 않는다.** 박스 하나는 배포 단위·프로세스·서비스·저장소처럼 "따로 존재한다"고 말할 수 있는 것이어야 한다. 예: API server, scheduler, agent/daemon, database, message queue, external API, CLI.
- **그림의 메시지에 기여하지 않는 컴퍼넌트는 뺀다.** 로깅, 설정 로더, 유틸리티처럼 어디에나 있는 것은 특별한 이유가 없으면 그리지 않는다. "이 박스를 지우면 그림이 설명하는 이야기가 깨지는가?"를 기준으로 남긴다.
- **화살표도 핵심 관계만 그린다.** 모든 상호작용을 다 그리면 큰 그림이 사라진다. 구조를 이해하는 데 필요한 관계만 남긴다.

## 컴퍼넌트와 경계

- **컴퍼넌트**는 이름이 적힌 둥근 네모박스로 그린다. 기본은 흰 배경에 얇은 검정 외곽선이다.
- **이 그림의 주인공인 컴퍼넌트 1~2개**는 옅은 초록(pale green) 배경으로 칠해 눈에 띄게 한다. 주인공은 사용자가 분석을 요청한 대상이거나, 그림이 설명하려는 동작의 중심이다.
- **논리적 경계**(cluster, node, namespace, VPC, 프로세스 경계, on-prem vs cloud 등)는 **점선 둥근 네모박스**로 감싸고, 박스 안 왼쪽 위에 경계 이름을 적는다. 경계는 중첩할 수 있다(예: Cluster 안에 Node, Node 안에 namespace).
- 경계 박스는 그림 이해에 도움이 될 때만 쓴다. 컴퍼넌트가 몇 개뿐이고 경계가 의미를 더하지 않으면 감싸지 않는다.

## 화살표와 관계 라벨

연관관계의 설명은 화살표에 넣는다. 이것이 이 그림의 정보량을 결정한다.

- 관계는 **점선 방향 화살표**로 그린다. 화살표 머리가 관계의 방향(의존/호출/배포가 향하는 쪽)을 가리킨다.
- **모든 화살표에는 그 관계를 설명하는 짧은 영어 라벨**을 이탤릭으로 단다. 한 단어~한 구절이면 충분하다. 예: `install`, `configure pod traffic redirection`, `push config`, `stores jobs`, `deploys`, `reads secrets`.
- 라벨은 "무엇을 한다"가 드러나는 동사구로 쓴다. `uses` 같은 정보 없는 라벨은 피하고, 무엇을 위해 쓰는지 적는다(예: `uses` 대신 `reads schema`).
- 근거 없는 관계는 그리지 않는다. 코드·manifest·설정·문서에서 확인한 관계만 화살표로 만든다.

## 레이아웃 방향

방향은 top-down이든 left-right든 상관없다. **처음 보는 사람에게 잘 읽히는 쪽**을 고른다.

- 계층·포함 관계가 중심이면(제어 평면 → 데이터 평면, 상위 → 하위) **top-down**.
- 처리 흐름·파이프라인이 중심이면(입력 → 처리 → 출력) **left-right**.
- 어느 쪽이든 시선이 자연스럽게 한 방향으로 흐르게 배치하고, 화살표가 서로 교차하지 않게 한다.

## 작업 순서

1. **입력 파악.** 사용자가 남긴 코드(repo, 디렉터리, 파일)나 컴퍼넌트 설명을 읽는다. 코드가 있으면 배포 단위·프로세스·외부 의존성을 기준으로 컴퍼넌트 후보를 찾는다. README, manifest 파일(`package.json`, `go.mod`, Helm chart, Kubernetes manifest 등), 진입점(main, cmd/), 설정 파일이 좋은 신호다. 여러 디렉터리를 훑어야 하면 병렬 탐색이나 `Explore` 서브에이전트를 써도 된다.
2. **추상화.** 위 `추상화 원칙`대로 컴퍼넌트를 3~8개로 줄인다. 역할이 같은 것은 합치고, 그림의 메시지와 무관한 것은 뺀다.
3. **관계 정리.** 컴퍼넌트 사이의 핵심 관계를 찾아 방향과 라벨(짧은 영어 동사구)을 정한다. 근거가 있는 관계만 남긴다.
4. **경계와 주인공 결정.** 논리적 경계로 감쌀 그룹이 있는지, 옅은 초록으로 칠할 주인공 컴퍼넌트 1~2개가 무엇인지 정한다.
5. **방향 결정.** top-down인지 left-right인지 위 `레이아웃 방향` 기준으로 고른다.
6. **제목 결정.** 그림 상단 제목을 영어로 짧게 정한다(예: "How Istio CNI Works"). 아이콘/로고는 없다.
7. **프롬프트 조립.** 아래 `프롬프트 템플릿`의 빈칸을 채워 영어 프롬프트를 완성한다.
8. **출력.** 영어 프롬프트 블록 + 한국어 한 줄 설명을 출력한다.

## 아이콘/로고를 넣지 않는 이유

제품 로고(kubernetes, AWS 아이콘 등)는 넣지 않는다. 유명한 것은 이미지 모델이 그럭저럭 그리지만, 덜 알려진 컴퍼넌트는 로고를 제대로 못 그려 결과가 일관되지 않는다. 컴퍼넌트는 이름이 적힌 박스로만 표현한다.

## 비주얼 스타일 (레퍼런스에 고정)

모든 프롬프트는 아래 스타일을 그대로 묘사한다. 공식 문서의 아키텍처 그림처럼 깔끔하고 절제된 다이어그램 스타일이다.

- **배경**: 깨끗한 흰색. 격자 없음.
- **컴퍼넌트 박스**: 둥근 네모, 얇은 검정 외곽선, 흰 배경, 안에 컴퍼넌트 이름. 주인공 1~2개만 옅은 초록(`#DCE8D4` 계열) 배경.
- **경계 박스**: 점선(dashed) 둥근 네모, 얇은 검정 선, 박스 안 왼쪽 위에 경계 이름. 중첩 가능.
- **화살표**: 점선(dotted) 검정 화살표, 작은 화살표 머리. 관계 라벨은 화살표 옆에 **이탤릭체 영어**로 단다.
- **폰트**: 깔끔한 산세리프. 모든 글자 영어. 컴퍼넌트 이름은 정자체, 화살표 라벨은 이탤릭.
- **전체 톤**: 절제되고 차분하며 여백이 넉넉. 색은 옅은 초록 강조 외에 쓰지 않는다.
- **비율**: top-down이면 세로 여유가 있는 4:3, left-right이면 16:9.

## 프롬프트 템플릿

아래 영어 템플릿의 `<...>`를 채워 완성한다. 경계를 쓰지 않으면 BOUNDARIES 줄을 지운다. 사용하지 않는 줄은 지운다.

```text
A clean, minimal software architecture diagram in the style of official documentation figures,
drawn with thin black lines on a plain white background. All text is in English, in a clean
sans-serif font.

TITLE: a short title at the top, reading exactly: "<TITLE>".

LAYOUT: the diagram reads <top-to-bottom / left-to-right>: <one sentence describing the overall
flow, e.g. "the control plane at the top configures the components inside the node below">.
Generous spacing; no arrows or labels overlap.

BOUNDARIES: dashed rounded rectangles with a thin black line, each labeled in the top-left corner
inside the box, nested as follows: <e.g. an outer box labeled "Cluster" contains a box labeled
"Node"; inside the Node box there are two side-by-side boxes labeled "App namespace" and
"istio-system">. (Delete this line if no boundaries.)

COMPONENTS (rounded rectangles with a thin black outline, name centered inside):
- "<component name>" — white fill, placed <where>.
- "<component name>" — PALE GREEN (#DCE8D4) fill (this is a key component), placed <where>.
  ... (one line per component; mark 1–2 key components with the pale green fill)

RELATIONSHIPS (thin dotted black arrows with small arrowheads; each label is written in italic
next to its arrow):
- A dotted arrow from "<from>" to "<to>", labeled "<short verb phrase>".
  ... (one line per arrow; every arrow has a label describing the relationship)

STYLE: minimal, calm, uncluttered, very legible, generous whitespace. The only color is the pale
green fill on the key components. <4:3 / 16:9> aspect ratio.

DO NOT: add any product logos or icons (components are labeled boxes only). No watermarks, no
extra text beyond the title, component names, boundary labels, and arrow labels. Do not misspell
any label. Do not let boxes, arrows, or text overlap.
```

## 예시 (gold reference)

이 예시는 위 스타일을 그대로 적용한 완성 프롬프트다. 새 프롬프트의 품질 기준으로 삼는다.

입력 예:

```text
istio CNI 관련 코드/manifest. istiod, sidecar 주입, istio-cni DaemonSet, CNI plugin 설치 흐름.
```

skill이 한 추상화(자동): 코드 세부를 걷어내고 Istiod, User pod, Sidecar proxy, CNI Network Plugin, Istio CNI DaemonSet 다섯 컴퍼넌트만 남겼다. Cluster > Node > (App namespace, istio-system) 경계를 점선 박스로 중첩했다. 이 그림의 주인공인 CNI Network Plugin과 Istio CNI DaemonSet을 옅은 초록으로 칠하고, 관계 설명(`install`, `configure pod traffic redirection` 등)을 화살표 라벨로 달았다. 제어 평면이 위, 노드 내부가 아래인 top-down이다.

출력 프롬프트:

```text
A clean, minimal software architecture diagram in the style of official documentation figures,
drawn with thin black lines on a plain white background. All text is in English, in a clean
sans-serif font.

TITLE: a short title at the top, reading exactly: "How Istio CNI Works".

LAYOUT: the diagram reads top-to-bottom: Istiod at the top configures the pod below, and the CNI
components at the bottom of the node set up pod networking. Generous spacing; no arrows or labels
overlap.

BOUNDARIES: dashed rounded rectangles with a thin black line, each labeled in the top-left corner
inside the box, nested as follows: an outer box labeled "Cluster" contains a box labeled "Node";
inside the Node box there is a box labeled "App namespace" in the upper area and a box labeled
"istio-system" in the lower-right area.

COMPONENTS (rounded rectangles with a thin black outline, name centered inside):
- "Istiod" — white fill, placed at the top, inside the Cluster box but above the Node box.
- "User pod" — white fill, inside the App namespace box.
- "Sidecar proxy" — white fill, nested inside the User pod box.
- "CNI Network Plugin" — PALE GREEN (#DCE8D4) fill (this is a key component), placed in the
  lower-left area of the Node box, outside the namespace boxes.
- "Istio CNI DaemonSet" — PALE GREEN (#DCE8D4) fill (this is a key component), inside the
  istio-system box.

RELATIONSHIPS (thin dotted black arrows with small arrowheads; each label is written in italic
next to its arrow):
- A dotted arrow from "Istiod" down to "Sidecar proxy", with no label (it simply points into the
  pod it configures).
- A dotted arrow from "Istio CNI DaemonSet" to "CNI Network Plugin", labeled "install".
- A dotted arrow from "CNI Network Plugin" up to the "User pod" box, labeled "configure pod
  traffic redirection".

STYLE: minimal, calm, uncluttered, very legible, generous whitespace. The only color is the pale
green fill on the key components. 4:3 aspect ratio.

DO NOT: add any product logos or icons (components are labeled boxes only). No watermarks, no
extra text beyond the title, component names, boundary labels, and arrow labels. Do not misspell
any label. Do not let boxes, arrows, or text overlap.
```

한국어 한 줄 설명: 코드 세부를 걷어내고 다섯 컴퍼넌트만 남긴 뒤 Cluster > Node > namespace 경계를 점선으로 중첩했고, 주인공인 CNI 컴퍼넌트 두 개를 옅은 초록으로 칠하고 `install`, `configure pod traffic redirection` 관계를 화살표 라벨로 달았습니다.

## 완료 전 확인

- 그림 속 모든 텍스트(제목/컴퍼넌트 이름/경계 라벨/화살표 라벨)가 영어인가?
- 컴퍼넌트를 3~8개로 추상화했는가? 함수/클래스/파일 수준을 그리지 않았는가?
- 모든 화살표에 그 관계를 설명하는 짧은 라벨(이탤릭 영어 동사구)을 달았는가?
- 근거 없는 컴퍼넌트나 관계를 만들지 않았는가?
- 논리적 경계는 이해에 도움이 될 때만 점선 박스로 감쌌는가?
- 주인공 컴퍼넌트 1~2개만 옅은 초록으로 칠했는가?
- 방향(top-down 또는 left-right)이 처음 보는 사람에게 자연스럽게 읽히는가? 화살표가 교차하지 않는가?
- 로고/아이콘 없이 이름이 적힌 박스로만 표현했는가?
- 프롬프트를 그대로 복사해 이미지 생성 AI agent에 붙여넣을 수 있는 한 블록으로 출력했는가?
