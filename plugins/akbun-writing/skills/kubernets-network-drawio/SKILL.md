---
name: kubernets-network-drawio
description: draw kubernetes network with draw.io
---

<what-to-do>

사용자가 제공한 Kubernetes 서비스 네트워크 정보를 draw.io 다이어그램과 PNG 파일로 만든다.

입력은 자연어, 사진 또는 스크린샷, YAML, 기존 `.drawio` 파일, 또는 이들의 조합을 모두 허용한다. 입력을 topology로 해석하고, 명확한 오타는 고치고, 작업을 계속할 수 있는 수준의 conservative assumptions를 적용한다. 아직 확정할 수 없는 모호함은 `확인 필요`로 남긴다.

사용자가 경로를 지정하지 않으면 기본 산출물은 `~/Downloads`에 만든다.

- `~/Downloads/<name>.drawio`
- `~/Downloads/<name>.drawio.png`

draw.io Desktop CLI만 사용한다. draw server, web editor 변환, MCP server 변환은 사용하지 않는다.

의미 있는 다이어그램을 만들 수 있으면 긴 인터뷰로 멈추지 말고 파일 생성까지 진행한다. 질문은 빠진 정보가 네트워크 의미를 바꿔서 안전하게 표현할 수 없을 때만 한다. 예를 들어 사진이 읽히지 않아 topology를 복구할 수 없거나, Service의 대상 workload/Pod를 어떤 입력에서도 추론할 수 없는 경우만 질문한다.

</what-to-do>

<supporting-info>

## Workflow

1. `references/drawio-cli-and-xml.md`를 읽고 draw.io CLI, export, XML 유효성 규칙을 확인한다.
2. `references/kubernetes-network-diagram-rules.md`를 읽고 topology, 입력 처리, layout, validation 규칙을 확인한다.
3. 사용자가 준 모든 입력을 하나의 정규화된 topology로 합친다.
4. 구조가 명확한데 라벨만 빠진 경우 보수적인 이름을 채우고 assumptions에 기록한다.
5. 아직 해결되지 않은 모호함은 `확인 필요` 목록에 남긴다. 그래도 의미 있는 다이어그램이면 계속 진행하고 최종 보고에 포함한다.
6. 필요하면 `assets/kubernetes-network-template.drawio`를 출발점으로 사용해 `.drawio` XML을 만들거나 수정한다.
7. `scripts/validate_drawio_xml.py`로 `.drawio` 파일의 validation을 실행한다.
8. `scripts/export_drawio.sh`로 PNG를 export한다.
9. export된 PNG를 눈으로 확인한다. main flow, Kubernetes boundary, LB/domain 위치, ingress controller 이름, Service-to-workload 또는 Service-to-Pod 매핑, external call, y축 정렬을 확인한다.
10. 최종 보고에는 산출물 경로, validation 명령, 눈으로 확인한 결과, assumptions, `확인 필요`를 포함한다.

## 입력 처리

### 자연어

요청 문장에서 Kubernetes 영역, 외부 actor, LB/domain, ingress controller, Service, workload 또는 Pod, 분기, 외부 호출을 추출한다. `servic`는 `service`, `doamin`은 `domain`처럼 의도가 명확한 오타는 라벨에 고쳐 반영한다.

사용자가 짧은 자연어로 요청해도 YAML을 요구하지 않는다. 자연어를 기본 입력으로 보고 YAML과 같은 topology model로 정규화한다.

### 사진 또는 스크린샷

사진은 topology와 layout 근거로 사용한다. boundary, actor, LB/domain label, ingress controller label, Service box, workload 또는 Pod box, external system, edge 방향, edge label, row 정렬을 추출한다.

사진의 일부 텍스트가 읽히지 않으면 읽히는 구조는 유지한다. 필요한 경우 neutral label을 사용하고 읽히지 않은 항목은 `확인 필요`로 남긴다. 사진이 자연어 또는 YAML과 충돌하면 값은 명시적인 YAML을 우선하고, layout은 사진을 우선한다. 충돌 내용은 최종 보고에 남긴다.

### YAML

YAML은 선택 사항이다. YAML이 제공되면 사용자가 넘긴 YAML 파일 또는 YAML 형식의 텍스트를 읽는다. 이름, route mapping, domain, draw flag처럼 명시적인 값은 YAML을 가장 우선한다. YAML에 빠진 값은 자연어 또는 사진에서 보완한다. `example.yaml`은 실제 입력이 아니라 작성 예시로만 참고한다.

### 기존 draw.io

사용자가 기존 `.drawio` 파일을 제공하면 관련 없는 cell은 보존하고, 요청에 포함된 네트워크 아키텍처만 수정한다. 복사된 draw.io XML에는 오래된 ID, 잘못된 geometry, 끊어진 edge가 있을 수 있으므로 수정 후 반드시 validation을 실행한다.

## Topology model

모든 다이어그램은 가능한 한 아래 개념을 해석한다.

- Kubernetes 영역: EKS, k3s, kind, vanilla Kubernetes, 또는 사용자가 지정한 이름
- 외부 actor: User, Client, Mobile App, system caller, 또는 안정적인 ID를 가진 여러 actor
- 진입점: external managed LB, in-cluster ingress controller, 또는 둘 다
- Domain 매핑: LB 또는 route 근처에 표시할 domain 0개, 1개, 또는 여러 개
- Ingress controller: 선택 사항이지만 그릴 때는 `nginx ingress controller`, `aws-load-balancer-controller`, `Traefik`처럼 controller 이름을 포함한다.
- Service: 하나 이상의 Kubernetes Service
- Target: workload 또는 Pod. workload가 지정되면 사용자가 Pod 수준 flow를 요청하지 않는 한 Pod는 생략한다.
- Branch: Shopping Assistant, Loyalty Program 같은 service-to-workload branch
- External call: workload 또는 Pod에서 Kubernetes boundary 밖의 OpenAI, google.com, S3, partner API 같은 external system으로 나가는 호출

## Decision rules

- 완벽한 입력을 기다리기보다 assumptions를 두고 유용한 다이어그램을 만드는 쪽을 우선한다.
- 막혔을 때도 필요한 질문만 최소한으로 묻는다.
- actor가 여러 개이고 route map이 없으면 모든 actor가 같은 LB/domain으로 들어오는 것으로 그리고 assumptions에 남긴다.
- domain이 여러 개이고 actor-domain mapping이 불명확하면 모든 domain을 LB 근처에 두고 mapping은 `확인 필요`로 남긴다.
- LB 위치가 불명확하면 텍스트나 사진에서 가장 덜 오해되는 위치를 고른다. 근거가 전혀 없으면 external managed LB로 그리고 위치를 `확인 필요`로 남긴다.
- ingress controller가 언급됐지만 이름이 없으면 흐름상 필요할 때만 그리고 라벨은 `ingress controller (확인 필요: name)`으로 둔다.
- Service target이 Deployment, StatefulSet, Job 같은 workload이면 workload를 그리고 Pod는 기본으로 생략한다.
- 사용자가 Service-to-Pod 흐름을 명시하면 Pod를 그리고 Service와 같은 y축에 둔다.
- workload가 많으면 네트워크 흐름에 필요한 workload만 그린다. replica Pod를 모두 나열하지 않는다.
- 외부 호출이 있으면 external system을 Kubernetes boundary 밖에 두고 workload 또는 Pod에서 연결한다.

## Layout contract

다이어그램은 느슨한 노드 그래프가 아니라 기준 이미지에 가까운 Kubernetes 네트워크 아키텍처처럼 보여야 한다.

- main flow는 왼쪽에서 오른쪽으로 `Actor -> LB/domain -> optional ingress controller -> Service -> workload 또는 Pod` 순서다.
- 같은 flow row의 컴포넌트는 center y가 같아야 한다.
- Service와 직접 연결된 workload 또는 Pod는 center y가 같아야 한다.
- branch row는 main row의 위나 아래로 갈 수 있지만, branch 안의 row 정렬은 맞춰야 한다.
- Kubernetes resource는 Kubernetes boundary 안에 둔다.
- external managed LB와 external system은 사용자가 명확히 다르게 말하지 않는 한 Kubernetes boundary 밖에 둔다.
- domain label은 설명하는 LB 또는 route 근처에 둔다.
- Kubernetes 컴포넌트는 가능하면 `shape=mxgraph.kubernetes.icon2`와 적절한 `prIcon`을 사용한다.

## Commands

Export:

```bash
bash scripts/export_drawio.sh ~/Downloads/kubernetes-network.drawio png ~/Downloads/kubernetes-network.drawio.png
```

Validation:

```bash
uv run python scripts/validate_drawio_xml.py assets/kubernetes-network-template.drawio
```

draw.io Desktop CLI가 sandboxed terminal에서 `Abort trap`으로 실패하면 macOS GUI 권한으로 다시 실행한다. 그래도 실패하면 Computer Use로 draw.io Desktop을 열어 수동 export한다.

## 최종 응답

최종 응답은 짧고 구체적으로 작성한다. 아래 내용을 포함한다.

- `.drawio` 경로
- `.png` 경로
- validation 명령과 결과
- 눈으로 확인한 레이아웃 결과
- assumptions
- `확인 필요` 항목 또는 `확인 필요: 없음`

</supporting-info>
