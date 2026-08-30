# Domain Language

This document preserves the stable language and boundaries of the AWS VPC foundation skill.

## Scope

A **VPC subnet diagram** shows VPC and Availability Zone boundaries, subnet tiers, CIDR labels, and optional Internet Gateway and NAT Gateway placement. It is the **VPC foundation layer** of a larger AWS diagram. Workloads, load balancers, endpoints, managed services, hybrid links, and application traffic belong to later layers.

## Terms

- **VPC count:** Number of independent VPC foundations to draw. Never assume one.
- **Subnet tier:** Subnets with the same network role, such as public, private, application, or database.
- **Tier subnet count:** Requested number of subnets in each tier within one VPC. A total subnet count is not sufficient.
- **Uneven AZ placement:** Valid but flagged placement when a tier's subnet count differs from the Availability Zone count. Do not silently rebalance it.
- **AZ column layout:** Each Availability Zone is a vertical dashed container parented to its VPC. Tiers stack inside each AZ column.
- **Topology intake:** Required values collected before drawing: VPC count, name and CIDR for each VPC, AZ count, tier subnet counts and CIDRs, Internet Gateway presence, and NAT Gateway presence.
- **Intake interview:** A hard gate before XML creation or export. Missing required topology values cause one consolidated question instead of silent defaults.
- **VPC structure reuse:** A later VPC may copy the first VPC's AZ count, subnet tiers, Internet Gateway setting, and NAT Gateway setting, but keeps its own name and CIDRs.
- **Multi-VPC stack layout:** Multiple VPC foundations stack vertically. This skill does not invent VPC-to-VPC connectivity.
- **Network CIDR label:** VPC and subnet-group names carry their CIDR on the same visible line. Do not hide it or split it into an unrelated text cell.
- **NAT Gateway placement:** When enabled, place one NAT Gateway per public subnet unless the user explicitly chooses another count. Never place one in a private subnet.
- **Internet Gateway placement:** When enabled, place one Internet Gateway per VPC. Public subnets without one are allowed only with `확인 필요` recorded.
- **Out-of-scope resource:** Workloads, ALB or NLB, VPC Endpoint, Route 53, Direct Connect, on-premises networks, managed services, and application traffic flows.
- **Workload handoff area:** Empty space left in subnets for a later workload skill.
- **Empty subnet body:** Subnet boxes stay mostly empty; NAT Gateways are the only default resource icons allowed inside them.

## Default CIDR proposal

When the user does not know the address plan, propose and confirm this `10.x` plan instead of selecting random ranges:

- VPC: `10.0.0.0/16`
- Public subnets: `10.0.1.0/24` through `10.0.3.0/24`
- Private application subnets: `10.0.11.0/24` through `10.0.13.0/24`
- Private database subnets: `10.0.21.0/24` through `10.0.23.0/24`

## Routing examples

- An EKS request starts here only for the VPC, AZ, subnet, CIDR, Internet Gateway, and NAT Gateway foundation. Cluster and node-group resources belong to a workload skill.
- A cost-saving single NAT Gateway layout is used only when the user explicitly selects it.
- Missing topology values trigger the intake interview; known values are not replaced with defaults.
- A tier with fewer subnets than AZs remains uneven and is reported as `확인 필요`.

