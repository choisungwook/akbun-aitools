# AWS VPC Subnet draw.io 레이아웃 가이드

이 문서는 AWS VPC 기초 레이어를 draw.io로 그리기 위한 규칙이다. 목표는 전체 AWS 아키텍처가 아니라, 다른 skill이 workload를 배치하기 전에 필요한 VPC, AZ, subnet, IGW, NAT GW 기반을 안정적으로 만드는 것이다.

## Scope

이 skill이 그리는 것:

- VPC boundary
- Availability Zone dashed container
- public/private/application/db 같은 subnet tier
- VPC와 subnet CIDR label
- Internet Gateway
- NAT Gateway

이 skill이 그리지 않는 것:

- ALB/NLB
- EC2, EKS, ECS, Lambda, RDS 같은 workload 또는 data resource
- VPC Endpoint
- Route 53
- Direct Connect, VPN, Transit Gateway, on-premises network
- managed service box
- application traffic flow edge

## Topology intake

그리기 전에 반드시 사용자에게 확인한다. 사용자는 interview 답변이나 YAML로 정보를 제공할 수 있다. 아래 값이 하나라도 빠져 있으면 XML 작성, 템플릿 복사, PNG export를 시작하지 않는다.

- VPC 개수
- VPC별 이름과 CIDR
- VPC별 AZ 개수
- VPC별 tier별 subnet 개수
- subnet CIDR
- IGW 여부
- NAT GW 여부

YAML을 제공받으면 `README.md`의 YAML format과 `example.yaml`을 기준으로 읽는다. YAML에 필수 값이 모두 있으면 추가 질문 없이 그린다. 빠진 값이 있으면 빠진 값만 질문한다.

사용자에게 물어볼 때는 다음 템플릿을 사용한다:

```text
다이어그램을 그리기 전에 VPC 정보를 확인해야 합니다.

1. VPC는 몇 개입니까?
2. 각 VPC의 이름과 CIDR은 무엇입니까? 모르면 10.x 대역으로 제안할까요?
3. 각 VPC의 AZ는 몇 개입니까?
4. 각 VPC의 subnet tier별 개수는 어떻게 됩니까? 예: public 2, application 2, db 2
5. subnet CIDR은 직접 지정하시겠습니까, 기본값으로 제안할까요?
6. IGW를 그릴까요? VPC별 yes/no로 알려주세요.
7. NAT GW를 그릴까요? yes이면 public subnet마다 1개를 그립니다.
```

여러 VPC를 그릴 때:

- VPC마다 독립적으로 확인한다.
- 두 번째 VPC부터는 첫 번째 VPC의 AZ 수, subnet tier, IGW 여부, NAT GW 여부를 복사할 수 있다.
- 이름과 CIDR은 VPC별로 따로 확정한다.

CIDR을 모르면 기본 제안을 한다:

```text
VPC 1: 10.0.0.0/16
Public A: 10.0.1.0/24
Public B: 10.0.2.0/24
Application A: 10.0.11.0/24
Application B: 10.0.12.0/24
DB A: 10.0.21.0/24
DB B: 10.0.22.0/24
```

여러 VPC의 CIDR을 사용자가 모르면 다음 `10.x.0.0/16` 대역을 제안하고 `확인 필요`로 표시한다.

## Layout

- 기본은 AZ column layout이다.
- AWS Cloud group은 그리지 않는다.
- AZ는 VPC group의 자식으로 두되, VPC 상단과 하단 경계를 넘어가는 세로 dashed container로 그린다.
- 각 AZ container 안에 subnet tier를 위에서 아래로 쌓는다.
- IGW가 들어갈 중앙 통로를 확보하기 위해 AZ column 사이 gap을 충분히 둔다.
- 여러 VPC는 draw.io page 위에 세로로 쌓는다.
- VPC 간 연결은 그리지 않는다.
- subnet 내부는 workload handoff area로 비워 둔다.
- NAT Gateway만 public subnet 안에 배치할 수 있다.
- IGW는 VPC group의 자식으로 두되, VPC 내부 중앙에 넣지 않고 VPC 상단 경계선에 걸쳐 배치한다.
- 별도 회색 page background rectangle은 그리지 않는다.

기본 2 AZ 구조:

```text
VPC 10.0.0.0/16
  Internet Gateway
  AZ A dashed container
    Public Subnet A 10.0.1.0/24
      NAT Gateway A
    Application Subnet A 10.0.11.0/24
    DB Subnet A 10.0.21.0/24
  AZ B dashed container
    Public Subnet B 10.0.2.0/24
      NAT Gateway B
    Application Subnet B 10.0.12.0/24
    DB Subnet B 10.0.22.0/24
```

## Typography

- Title: `fontSize=18;fontStyle=1;fontColor=#232F3E`
- VPC label with CIDR: `fontSize=10;fontStyle=1;fontColor=#248814`
- AZ label: `fontSize=12;fontStyle=1;fontColor=#545B64`
- Subnet label with CIDR: `fontSize=10;fontStyle=1`
- Icon label: `fontSize=12;fontColor=#232F3E`

Label rules:

- VPC와 subnet label은 이름과 CIDR을 한 줄에 넣는다.
- 별도 CIDR text cell을 만들지 않는다.
- `<br>`, HTML tag, HTML entity 줄바꿈을 쓰지 않는다.

## Sizing

- IGW/NAT icon: `48x48`
- VPC minimum size: `700x620`
- AZ container minimum width: `300`
- AZ container minimum height: `520`
- AZ container는 VPC top/bottom boundary를 모두 넘어야 한다.
- IGW 주변에는 AZ 세로 경계선이 지나가지 않아야 한다.
- IGW icon 좌우에는 AZ 세로 경계선과 최소 40px 이상 여유를 둔다.
- subnet minimum size: `240x100`
- group border와 내부 subnet 사이 padding: `25-35px`
- subnet 안쪽은 나중에 workload를 넣을 수 있게 넓게 비워 둔다.

## Placement Rules

### Internet Gateway

- topology intake에서 IGW 여부를 확인한다.
- `IGW yes`이면 VPC마다 IGW 1개를 그린다.
- IGW는 VPC group의 자식으로 둔다.
- IGW는 subnet 안에 넣지 않는다.
- IGW icon은 VPC 상단 경계선에 걸쳐지도록 배치한다.
- IGW icon은 AZ column 사이 중앙 통로에 배치하고, AZ 세로 dashed boundary와 겹치지 않게 한다.
- IGW label까지 읽히도록 AZ column 사이 중앙 통로를 충분히 넓힌다.
- public subnet이 있는데 `IGW no`이면 `확인 필요`로 표시한다.

### NAT Gateway

- topology intake에서 NAT GW 여부를 확인한다.
- `NAT GW yes`이면 public subnet마다 NAT Gateway 1개를 그린다.
- NAT Gateway는 public subnet의 자식으로 둔다.
- NAT Gateway는 private/application/db subnet에 넣지 않는다.
- 사용자가 NAT GW 1개만 원한다고 명시하면 예외로 허용하고 `확인 필요`로 표시한다.

### Uneven AZ Placement

- tier별 subnet 개수가 AZ 수와 달라도 그릴 수 있다.
- 해당 tier가 일부 AZ에만 있으면 `확인 필요`로 표시한다.
- 자동으로 subnet을 추가하거나 제거하지 않는다.

## Cell ID Convention

설명적인 ID를 사용한다.

- Title: `txt-title`
- VPC group: `grp-vpc-main`, `grp-vpc-network`
- AZ group: `grp-az-a`, `grp-az-b`
- Subnet group: `grp-subnet-public-a`, `grp-subnet-app-a`, `grp-subnet-db-a`
- IGW: `svc-igw-main`
- NAT GW: `svc-nat-public-a`

## Style Quick Reference

VPC group:

```text
sketch=0;outlineConnect=0;fontColor=#248814;fontSize=10;fontStyle=1;container=1;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#248814;fillColor=none;verticalAlign=top;align=left;spacingLeft=36;spacingTop=8;whiteSpace=wrap;html=1;pointerEvents=0;
```

AZ dashed container:

```text
rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#879196;strokeWidth=1;dashed=1;dashPattern=6 4;fontColor=#545B64;fontSize=12;fontStyle=1;verticalAlign=top;align=left;spacingLeft=12;spacingTop=8;container=1;collapsible=0;recursiveResize=0;pointerEvents=0;
```

Public subnet:

```text
sketch=0;outlineConnect=0;fontColor=#248814;fontSize=10;fontStyle=1;container=1;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#7AA116;fillColor=#F2F6E8;verticalAlign=top;align=left;spacingLeft=36;spacingTop=8;whiteSpace=wrap;html=1;pointerEvents=0;
```

Application/Private/DB subnet:

```text
sketch=0;outlineConnect=0;fontColor=#147EBA;fontSize=10;fontStyle=1;container=1;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#00A4A6;fillColor=#E6F6F7;verticalAlign=top;align=left;spacingLeft=36;spacingTop=8;whiteSpace=wrap;html=1;pointerEvents=0;
```

Dedicated AWS resource icon:

```text
sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#8C4FFF;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.<SHAPE_NAME>;
```

## PNG Export Considerations

- 별도 회색 rounded background rectangle을 만들지 않는다.
- draw.io page의 기본 흰 배경 위에 title과 VPC boundary를 직접 배치한다.
- content가 page 밖에 떠 있으면 안 된다.
