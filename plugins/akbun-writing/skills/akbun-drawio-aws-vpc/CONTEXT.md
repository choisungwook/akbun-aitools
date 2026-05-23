# AWS VPC Subnet Diagram Skill

이 컨텍스트는 AWS 아키텍처 다이어그램에서 VPC, Availability Zone, subnet, Internet Gateway, NAT Gateway만으로 구성된 VPC 기초 레이어의 경계와 역할을 명확히 하기 위해 존재한다. 이 skill은 workload, ALB/NLB, VPC Endpoint, Direct Connect, on-premises network를 그리지 않는다.

## Language

**VPC subnet diagram**:
An AWS diagram layer that shows VPC boundaries, Availability Zone boundaries, subnet tiers, CIDR labels, and optional Internet Gateway and NAT Gateway placement.
_Avoid_: full AWS architecture diagram, workload diagram, hybrid network diagram

**VPC foundation layer**:
The reusable base layer of a broader AWS architecture diagram. It contains one or more VPCs, their Availability Zones, subnet tiers, CIDR labels, and optional IGW/NAT GW resources.
_Avoid_: workload layer, load balancer layer, managed service layer

**VPC count**:
The number of VPC foundations this skill must draw.
_Avoid_: assuming one VPC

**Subnet tier**:
A named group of subnets with the same network role, such as public, private, application, or db.
_Avoid_: anonymous subnet, random subnet box

**Tier subnet count**:
The number of subnets requested for each subnet tier within a VPC, such as public 2, application 2, and db 2.
_Avoid_: total-only subnet count, ambiguous subnet count

**Uneven AZ placement**:
A valid but flagged subnet layout where a tier's subnet count does not match the AZ count, causing that tier to appear in only some AZ columns.
_Avoid_: silently balancing subnets, rejecting valid uneven layouts

**AZ column layout**:
A VPC foundation layer layout where each Availability Zone is a vertical dashed container parented to the VPC and drawn beyond the VPC's top and bottom boundaries. Subnet tiers are stacked inside each AZ column.
_Avoid_: tier-only column layout, hiding AZ boundaries

**Topology intake**:
The required questions this skill asks before drawing a VPC subnet diagram: VPC count, tier subnet count per VPC, AZ count, CIDR ranges, Internet Gateway presence, and NAT Gateway presence. For multiple VPCs, each VPC is asked independently, but later VPCs may reuse the first VPC structure with different names or CIDR ranges.
_Avoid_: silent topology guess, drawing before VPC/subnet requirements are known

**Intake interview**:
The mandatory question-and-answer step that happens before XML creation or export. If any required topology intake value is missing, the skill asks for it and waits instead of drawing from silent defaults.
_Avoid_: implicit defaults, drawing first and asking later

**VPC structure reuse**:
The multi-VPC intake shortcut where the first VPC's AZ count, subnet tiers, IGW setting, and NAT GW setting can be copied to another VPC while still allowing that VPC to use its own name and CIDR ranges.
_Avoid_: forcing repeated answers, assuming all VPC CIDRs are identical

**Multi-VPC stack layout**:
The layout rule for multiple VPCs where each VPC foundation layer is stacked vertically on the draw.io page.
_Avoid_: horizontal multi-VPC sprawl, drawing VPC-to-VPC connectivity

**Network CIDR label**:
A visible single-line VPC or subnet group label that includes the network boundary name and CIDR in the same label so that later workload placement can preserve the intended address plan.
_Avoid_: hidden CIDR, separate implementation note, separate CIDR text cell, multiline CIDR label

**Default CIDR proposal**:
The fallback address plan this skill proposes when the user has not provided CIDR ranges. It uses `10.0.0.0/16` for the VPC, `10.0.1.0/24` through `10.0.3.0/24` for public subnets, `10.0.11.0/24` through `10.0.13.0/24` for private app subnets, and `10.0.21.0/24` through `10.0.23.0/24` for private db subnets.
_Avoid_: random CIDR, non-10.x default, unconfirmed address plan

**NAT Gateway placement**:
The optional NAT Gateway placement selected during topology intake. When enabled, this skill draws one NAT Gateway per public subnet unless the user explicitly requests a different count.
_Avoid_: drawing NAT Gateway without user confirmation, placing NAT Gateway in private subnets

**Internet Gateway placement**:
The optional Internet Gateway placement selected during topology intake. When enabled, this skill draws one Internet Gateway per VPC. If public subnets exist but IGW is disabled, the skill marks that combination as "확인 필요".
_Avoid_: drawing IGW without user confirmation, per-subnet Internet Gateway

**Out-of-scope resource**:
Any AWS or external component that this skill intentionally does not draw, including workload resources, ALB/NLB, VPC Endpoint, Route 53, Direct Connect, on-premises network, managed services, and application traffic flows.
_Avoid_: partial workload drawing, hidden architecture expansion

**Workload handoff area**:
The empty space inside subnets where a separate skill can later place workload resources.
_Avoid_: drawing placeholder workload icons, guessing workload architecture

**Empty subnet body**:
The layout rule that subnet boxes remain mostly empty so a later skill can place workload resources. NAT Gateway icons are the only default resource icons allowed inside subnet boxes.
_Avoid_: placeholder workload icons, decorative subnet filler

## Example Dialogue

Developer: "EKS 아키텍처를 그리고 싶은데 이 skill을 써야 하나요?"

Domain expert: "네. EKS를 그리기 전에 이 skill로 VPC, AZ, public/private/db subnet, CIDR, IGW, NAT Gateway만 그립니다. EKS cluster와 node group은 별도 workload skill이 workload handoff area에 배치합니다."

Developer: "NAT Gateway 개수도 사용자에게 물어보나요?"

Domain expert: "네. 이 skill은 NAT Gateway 여부를 topology intake에서 확인합니다. 사용자가 원하면 public subnet마다 NAT Gateway 1개를 배치합니다. NAT Gateway 1개만 쓰는 비용 절약형 구조는 사용자가 명시할 때만 적용합니다."

Developer: "Internet Gateway도 물어보나요?"

Domain expert: "네. 이 skill은 IGW 여부도 topology intake에서 확인합니다. 사용자가 원하면 VPC마다 Internet Gateway 1개를 배치합니다. public subnet이 있는데 IGW가 없으면 확인 필요로 표시합니다."

Developer: "ALB나 VPC Endpoint도 이 skill에서 그리나요?"

Domain expert: "아니요. ALB, NLB, VPC Endpoint, Route 53, workload, Direct Connect, on-prem은 out-of-scope resource입니다. 다른 skill이 나중에 그립니다."

Developer: "사용자가 subnet 구조를 말하지 않으면 기본값으로 그려도 되나요?"

Domain expert: "아니요. 그리기 전 topology intake로 VPC 개수, tier별 subnet 개수, AZ 수, CIDR 대역, IGW 여부, NAT Gateway 여부를 확인합니다. CIDR을 모르면 10.x 기반 default CIDR proposal을 제안합니다."

Developer: "사용자가 VPC 정보를 안 주고 그냥 그려달라고 하면 어떻게 하나요?"

Domain expert: "intake interview를 먼저 합니다. 필요한 값이 빠져 있으면 XML 작성이나 export를 시작하지 않고 질문한 뒤 기다립니다."

Developer: "VPC가 여러 개면 같은 질문을 VPC마다 반복하나요?"

Domain expert: "VPC마다 독립적으로 확인합니다. 다만 두 번째 VPC부터는 첫 번째 VPC의 AZ 수, subnet tier, IGW 여부, NAT GW 여부를 복사할 수 있고, 이름과 CIDR은 VPC별로 따로 확정합니다."

Developer: "VPC가 여러 개면 가로로 나란히 놓나요?"

Domain expert: "아니요. multi-VPC stack layout을 사용해서 VPC foundation layer를 페이지에 세로로 쌓습니다. AWS Cloud 박스와 VPC 간 연결은 그리지 않습니다."

Developer: "AZ는 2개인데 public subnet은 1개만 있으면 어떻게 하나요?"

Domain expert: "그릴 수 있습니다. 다만 tier별 subnet 개수가 AZ 수와 다르면 uneven AZ placement로 보고 확인 필요를 표시합니다."

Developer: "CIDR은 어떻게 표시하나요?"

Domain expert: "VPC와 subnet group label에 한 줄로 표시합니다. 별도 text cell로 CIDR을 분리하지 않습니다."

Developer: "subnet은 tier별로 가로로 나열하나요, AZ별로 나열하나요?"

Domain expert: "AZ column layout을 사용합니다. 예를 들어 2 AZ면 VPC에 속한 AZ A와 AZ B 세로 dashed container를 만들고, AZ container가 VPC 상하 경계를 넘게 그립니다. 각 AZ column 안에는 public, private, db subnet을 위에서 아래로 쌓습니다."

Developer: "workload를 넣을 공간은 어떻게 남기나요?"

Domain expert: "empty subnet body를 유지합니다. public subnet에는 NAT Gateway가 들어갈 수 있지만, private/application/db subnet은 기본적으로 비워 둡니다. 별도 skill이 그 공간에 EC2, EKS, RDS 같은 workload를 배치합니다."
