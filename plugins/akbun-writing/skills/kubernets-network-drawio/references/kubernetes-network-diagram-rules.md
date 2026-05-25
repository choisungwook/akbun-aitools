# Kubernetes Network draw.io 레이아웃 가이드

이 문서는 Kubernetes로 배포된 서비스의 네트워크 호출 흐름을 draw.io로 그리기 위한 규칙이다. 목표는 모든 Kubernetes 리소스를 나열하는 것이 아니라, 외부 호출이 어떤 LB/Ingress를 지나 어떤 Service와 Pod에 도달하고, Pod가 어떤 외부 서비스를 호출하는지 안정적으로 보여주는 것이다.

## Scope

이 skill이 그리는 것:

- 외부 호출 주체: User, Client, Mobile App
- Kubernetes 영역: EKS, k3s, kind, vanilla Kubernetes
- LB 또는 Ingress entrypoint: AWS NLB/ALB 같은 외부 managed LB 또는 cluster 내부 ingress controller
- optional ingress controller
- Kubernetes Service
- Workload 또는 Pod
- Deployment, StatefulSet, Job 같은 보조 workload
- Workload 또는 Pod에서 외부 서비스로 나가는 호출: google.com, LLM API, S3 같은 외부 component
- traffic flow edge
- 자연어, 사진, YAML 입력 해석
- `~/Downloads` 기본 산출물 저장

이 skill이 그리지 않는 것:

- VPC subnet foundation
- Route table, NAT Gateway, IGW 같은 AWS network foundation
- 모든 replica pod 나열
- 모든 Kubernetes control plane component
- container 내부 process
- port 번호, protocol detail, endpoint IP

## Layout

- 기본은 left-to-right traffic flow layout이다.
- 기준 이미지는 `~/Downloads/kubernetes-ref.png`다.
- cluster 바깥 provider boundary가 필요하면 큰 외곽 container로 그린다.
- Kubernetes cluster 영역은 큰 orange boundary로 그린다.
- 외부 managed LB는 cluster boundary 바깥, provider boundary 안쪽에 둘 수 있다.
- cluster 내부 ingress controller는 cluster boundary 안쪽에 둔다.
- main ingress flow는 한 줄에 둔다.
- main ingress flow 순서는 `Actor -> LB/domain -> optional Ingress Controller -> Service -> workload 또는 Pod`다.
- Service와 직접 연결된 workload 또는 Pod의 center y는 반드시 같아야 한다.
- main flow의 LB, ingress controller, Service, workload 또는 Pod center y는 반드시 같아야 한다.
- branch flow는 main pod에서 위/아래 service row로 갈 수 있다.
- branch row에서도 Service와 Pod의 center y는 같아야 한다.
- Workload 또는 Pod에서 외부 서비스로 나가는 호출은 cluster boundary 바깥의 external box로 연결한다.
- 외부 호출 edge는 빨간색 계열을 사용한다.
- storage나 bucket으로 나가는 job flow는 녹색 계열을 사용할 수 있다.
- 컴포넌트가 삐뚤어져 보이지 않도록 같은 row의 x/y 좌표를 grid 단위로 맞춘다.

## Topology intake

사용자는 자연어, 사진, 또는 선택 사항인 YAML로 정보를 제공할 수 있다. 입력이 불완전해도 가능한 구조를 먼저 만들고, 다이어그램 의미가 바뀔 수 있는 값만 `확인 필요`로 표시한다.

- cluster 표시 이름과 종류
- 외부 호출 actor. 여러 개이면 actor별 `id`와 `label`
- LB 이름, 위치, domain 매핑
- ingress controller 별도 표시 여부와 controller 이름
- service-workload 또는 service-pod 매핑
- workload 또는 pod 외부 호출 대상
- optional workload

## Input Modes

자연어, 사진, YAML을 모두 허용한다. 여러 입력이 함께 오면 명시적인 YAML 값을 우선하고, 사진은 레이아웃 기준으로 사용하며, 자연어는 누락된 의도와 라벨을 보완하는 데 사용한다.

### 자연어

- 사용자가 쓴 오타는 문맥상 명확하면 고쳐서 라벨에 반영한다.
- 불명확한 component type, edge 방향, actor-domain 매핑은 `확인 필요`로 질문한다.

### 사진

- 사진에서 boundary, actor, LB/domain, ingress controller, Service, workload/Pod, external component, edge label을 추출한다.
- 사진의 상대 배치와 y축 정렬을 우선 반영한다.
- 텍스트가 흐리거나 edge 방향이 애매하면 추측하지 않는다.
- 사진 속 component가 Kubernetes 리소스인지 외부 시스템인지 애매하면 `확인 필요`로 질문한다.

### YAML

- YAML은 선택 사항이다.
- YAML을 제공하면 사용자가 넘긴 YAML 파일 또는 YAML 형식의 텍스트를 읽는다.
- YAML에 없는 값은 자연어와 사진에서 보완한다.
- YAML, 사진, 자연어가 충돌하면 YAML을 우선하되, 충돌 사실을 최종 보고에 남긴다.

## Output Path

- 사용자가 경로를 지정하지 않으면 원본은 `~/Downloads/<name>.drawio`, PNG는 `~/Downloads/<name>.drawio.png`로 만든다.
- `<name>`을 사용자가 지정하지 않으면 cluster와 대표 service 이름으로 짧은 slug를 만든다. 예: `k3s-chatbot-network`.
- 사용자가 다른 경로를 명시하면 그 경로를 우선한다.

정말 멈춰야 할 때만 다음 템플릿에서 필요한 질문만 골라 묻는다:

```text
다이어그램을 그리기 전에 Kubernetes 네트워크 정보를 확인해야 합니다.

1. Kubernetes 영역은 무엇으로 표시할까요? 예: EKS, k3s, kind
2. 외부 호출 actor는 무엇입니까? 여러 개이면 actor별 이름을 알려주세요.
3. LB는 외부 managed component입니까, cluster 내부 ingress controller입니까? domain이 있으면 함께 알려주세요.
4. Ingress controller를 별도 컴포넌트로 그릴까요? yes이면 controller 이름은 무엇입니까?
5. Service -> workload 또는 Service -> Pod 연결은 어떤 이름으로 그릴까요?
6. Workload 또는 Pod가 호출하는 외부 서비스가 있습니까? 예: google.com, LLM API
7. StatefulSet, Job, Deployment 같은 보조 workload도 그릴까요?
```

사용자가 "예시처럼"이라고 하면 다음 기본 구조를 제안하고 확인한다:

```text
AWS provider boundary
  EKS cluster boundary
    nginx ingress controller
    chatbot-svc -> chatbot-ui deployment
    rag-svc -> rag application deployment
    model-svc -> llama model deployment
    vector database sts
    fine-tuning job
  AWS NLB outside EKS
  S3 bucket outside EKS
external LLM API outside AWS
```

## YAML Format

YAML은 선택 사항이다. 사용자가 자연어로 요청하면 YAML을 요구하지 않는다. YAML을 제공하면 사용자가 넘긴 YAML 파일 또는 YAML 형식의 텍스트를 다음 필드 기준으로 읽는다.

```yaml
cluster:
  name: k3s

entrypoint:
  actors:
    - id: web
      label: Web user
    - id: mobile
      label: Mobile app
  lb:
    name: k3s ingress/LB
    location: in_cluster
    domains:
      - app.example.com
      - mobile.example.com
  ingress_controller:
    enabled: true
    name: nginx ingress controller

services:
  - id: chatbot
    name: chatbotui service
    target:
      type: deployment
      name: chatbotui deployment
      draw_pod: false
    branches:
      - label: Shopping Assistant
        target:
          type: deployment
          name: RAG application deployment
          draw_pod: false
        calls:
          - type: statefulset
            name: qdrant sts
          - type: external
            name: OpenAI model
      - label: Loyalty program
        target:
          type: deployment
          name: Fine-tuned model deployment
          draw_pod: false
```

규칙:

- `actors`가 여러 개이면 `id`를 edge id에 사용하고, `label`을 화면에 표시한다.
- actor별 domain이나 LB가 다르면 `routes`를 추가로 물어본다. 별도 `routes`가 없으면 모든 actor가 같은 LB/domain으로 들어오는 것으로 그린다.
- `lb.domains`는 하나 또는 여러 개를 허용한다. 여러 domain이 actor별로 매핑되는지 불명확하면 `확인 필요`로 질문한다.
- `ingress_controller.enabled: true`이면 `ingress_controller.name`이 필요하다.
- `target.type`이 `deployment`, `statefulset`, `job` 같은 workload이면 Pod는 기본으로 그리지 않는다.
- Pod까지 그려야 하면 `draw_pod: true` 또는 `pod.name`을 명시한다.

## Cell ID Convention

설명적인 ID를 사용한다.

- Title: `txt-title`
- Provider boundary: `grp-provider-aws`
- Cluster boundary: `grp-cluster-main`
- Namespace boundary: `grp-namespace-default`
- External actor: `actor-user`
- External managed LB: `net-lb-main`
- Ingress controller: `k8s-ingress-controller-main`
- Ingress resource: `k8s-ingress-main`
- Kubernetes Service: `k8s-service-chatbot`
- Kubernetes workload: `k8s-workload-rag`, `k8s-workload-vector-db`
- Kubernetes Pod: `k8s-pod-chatbot`
- External system: `ext-google`, `ext-llm-api`, `ext-s3`
- Flow edge: `flow-main-user-lb`, `flow-main-service-pod`, `flow-external-pod-google`

## Style Quick Reference

Provider boundary:

```text
rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#E91E63;strokeWidth=2;fontColor=#232F3E;fontSize=18;fontStyle=1;verticalAlign=top;align=left;spacingLeft=56;spacingTop=20;container=1;collapsible=0;recursiveResize=0;pointerEvents=0;
```

Kubernetes cluster boundary:

```text
rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#F28C28;strokeWidth=2;fontColor=#232F3E;fontSize=18;fontStyle=1;verticalAlign=top;align=left;spacingLeft=56;spacingTop=24;container=1;collapsible=0;recursiveResize=0;pointerEvents=0;
```

Namespace boundary:

```text
rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#879196;strokeWidth=1;dashed=1;dashPattern=6 4;fontColor=#545B64;fontSize=12;fontStyle=1;verticalAlign=top;align=left;spacingLeft=12;spacingTop=8;container=1;collapsible=0;recursiveResize=0;pointerEvents=0;
```

Kubernetes icon:

```text
aspect=fixed;sketch=0;html=1;dashed=0;whitespace=wrap;verticalLabelPosition=bottom;verticalAlign=top;fillColor=#2875E2;strokeColor=#ffffff;points=[[0.005,0.63,0],[0.1,0.2,0],[0.9,0.2,0],[0.5,0,0],[0.995,0.63,0],[0.72,0.99,0],[0.5,1,0],[0.28,0.99,0]];shape=mxgraph.kubernetes.icon2;prIcon=<ICON>;
```

Common `prIcon` values:

- `ing`: Ingress
- `svc`: Service
- `pod`: Pod
- `deploy`: Deployment
- `sts`: StatefulSet
- `job`: Job

External managed LB:

```text
ellipse;whiteSpace=wrap;html=1;aspect=fixed;perimeter=ellipsePerimeter;fillColor=#F3F0FF;strokeColor=#8B5CF6;strokeWidth=2;fontColor=#6D28D9;fontSize=14;fontStyle=1;verticalLabelPosition=bottom;verticalAlign=top;align=center;
```

External system:

```text
rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#E53935;strokeWidth=2;fontColor=#D32F2F;fontSize=18;fontStyle=1;align=center;verticalAlign=middle;
```

Main flow edge:

```text
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=#2F6FDB;strokeWidth=2;
```

External call edge:

```text
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=#E53935;strokeWidth=2;
```

## Assumption and ambiguity handling

- 의미가 명확한 오타는 조용히 고쳐서 라벨에 반영한다.
- 구조는 명확하지만 이름이 빠진 경우 neutral label을 쓰고 최종 보고의 assumptions에 남긴다.
- 구조 자체가 불명확하면 `확인 필요`로 남긴다.
- `확인 필요`가 있어도 네트워크 의미가 크게 바뀌지 않으면 draw.io와 PNG를 생성한다.
- Service target, LB 위치, edge 방향처럼 네트워크 의미를 바꾸는 값이 전혀 추론되지 않으면 그 값만 질문한다.

## Validation Expectations

- `scripts/validate_drawio_xml.py`를 반드시 실행한다.
- XML 공식 구조 검증을 통과해야 한다.
- Kubernetes icon을 하나 이상 사용해야 한다.
- cluster boundary가 하나 이상 있어야 한다.
- LB와 Service가 하나 이상 있어야 한다.
- Pod 또는 workload가 하나 이상 있어야 한다.
- `Actor -> LB -> optional ingress controller -> Service -> workload 또는 Pod` 경로가 있어야 한다.
- 모든 Service는 적어도 하나의 workload 또는 Pod로 연결되어야 한다.
- 모든 Service -> workload/Pod edge는 source/target center y가 같아야 한다.
- `flow-main-` edge는 source/target center y가 같아야 한다.
- external system이 있으면 workload 또는 Pod에서 external system으로 향하는 edge가 있어야 한다.
- reference-like structure score가 95% 이상이어야 한다.
- 최종 산출물은 기본적으로 `~/Downloads`에 `.drawio`와 `.drawio.png`가 모두 있어야 한다.
