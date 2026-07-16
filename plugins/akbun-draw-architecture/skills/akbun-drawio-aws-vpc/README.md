# AWS VPC Subnet Diagram Input

## Interview

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

## YAML

```yaml
diagram:
  title: Basic AWS Multi VPC
  output_name: basic-aws-multi-vpc

vpcs:
- id: service-vpc
  name: Service VPC
  cidr: 10.0.0.0/16
  azs:
  - id: a
    name: Availability Zone A
  - id: b
    name: Availability Zone B
  internet_gateway:
    enabled: true
  nat_gateway:
    enabled: true
    placement: per_public_subnet
  subnet_tiers:
  - name: public
    label: Public Subnet
    subnets:
    - name: Public Subnet A
      az: a
      cidr: 10.0.1.0/24
    - name: Public Subnet B
      az: b
      cidr: 10.0.2.0/24
  - name: application
    label: Application Subnet
    subnets:
    - name: Application Subnet A
      az: a
      cidr: 10.0.11.0/24
    - name: Application Subnet B
      az: b
      cidr: 10.0.12.0/24
  - name: db
    label: DB Subnet
    subnets:
    - name: DB Subnet A
      az: a
      cidr: 10.0.21.0/24
    - name: DB Subnet B
      az: b
      cidr: 10.0.22.0/24

- id: network-vpc
  name: Network VPC
  cidr: 10.10.0.0/16
  azs:
  - id: a
    name: Availability Zone A
  - id: b
    name: Availability Zone B
  internet_gateway:
    enabled: false
  nat_gateway:
    enabled: false
    placement: per_public_subnet
  subnet_tiers:
  - name: private
    label: Private Subnet
    subnets:
    - name: Private Subnet A
      az: a
      cidr: 10.10.11.0/24
    - name: Private Subnet B
      az: b
      cidr: 10.10.12.0/24
```

## 참고자료

- https://www.drawio.com/doc/faq/ai-drawio-generation
