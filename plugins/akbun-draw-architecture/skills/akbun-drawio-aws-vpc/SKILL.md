---
name: akbun-drawio-aws-vpc
description: >
  draw.io Desktop CLI로 AWS VPC 기초 다이어그램을 `.drawio` XML로 만들고 PNG/SVG/PDF로 export한다.
  draw server나 MCP server를 사용하지 않고, macOS의 draw.io Desktop CLI와 AWS icon pack(mxgraph.aws4)을 사용한다.
  이 skill은 VPC, Availability Zone, public/private/application/db subnet, Internet Gateway, NAT Gateway만 그린다.
  ALB/NLB, workload, VPC Endpoint, Route 53, Direct Connect, on-premises network, managed service는 다른 skill의 책임이다.
  Trigger on: "draw.io AWS VPC", "drawio aws vpc", "AWS VPC 기초 그려줘", "AWS VPC subnet 그려줘",
  "VPC subnet diagram", "public subnet private subnet", "AZ dashed container", "IGW NAT Gateway".
---

# draw.io CLI로 AWS VPC Subnet 다이어그램 생성

## 핵심 원칙

- draw.io Desktop CLI만 사용한다. draw server, web editor 변환, MCP server 변환을 사용하지 않는다.
- macOS 기본 CLI 경로는 `/Applications/draw.io.app/Contents/MacOS/draw.io`다.
- AWS icon pack은 `mxgraph.aws4` stencil을 사용한다.
- 이 skill의 책임은 VPC, AZ, subnet, IGW, NAT GW까지다.
- workload, ALB/NLB, VPC Endpoint, Route 53, Direct Connect, on-premises network, managed service, application traffic flow는 그리지 않는다.
- 사용자가 기준 이미지를 주지 않아도 완료할 수 있어야 한다. 기본 검증은 XML 정적 검증, CLI export, PNG 육안 확인이다.
- 상세 레이아웃 규칙은 `references/aws-vpc-diagram-rules.md`를 따른다.

## Topology intake

그리기 전에 반드시 확인한다. 사용자는 interview 답변이나 YAML로 정보를 제공할 수 있다. 아래 정보가 하나라도 빠져 있으면 XML 작성, 템플릿 복사, PNG export를 시작하지 말고 intake interview를 먼저 한다.

1. VPC 개수
2. VPC별 이름과 CIDR
3. VPC별 AZ 개수
4. VPC별 tier별 subnet 개수: 예 `public 2`, `application 2`, `db 2`
5. subnet CIDR
6. IGW 여부
7. NAT GW 여부

규칙:

- 여러 VPC를 그릴 때는 VPC마다 독립적으로 묻는다.
- 두 번째 VPC부터는 첫 번째 VPC의 AZ 수, subnet tier, IGW 여부, NAT GW 여부를 복사할 수 있다.
- CIDR을 사용자가 모르면 `10.x` 기반 기본 CIDR을 제안하고 확인받는다.
- tier별 subnet 개수가 AZ 수와 다르면 허용하되 `확인 필요`로 표시한다.
- public subnet이 있는데 IGW가 없으면 허용하되 `확인 필요`로 표시한다.

### Intake interview hard gate

- 사용자가 필요한 정보를 모두 주지 않았으면 다이어그램을 그리지 않는다.
- 기본값은 자동 적용하지 않는다. 기본값은 반드시 "제안"하고 사용자의 확인을 받는다.
- 질문은 사용자가 그대로 답하기 쉬운 구조로 한다.
- 사용자가 "기본값으로" 또는 "제안해줘"라고 답하면 `10.x` 기반 CIDR과 2 AZ 예시를 제안하고 다시 확인한다.
- 사용자가 YAML을 제공하면 `README.md`의 YAML format과 `example.yaml`을 기준으로 읽는다.
- YAML에 필수 값이 모두 있으면 추가 질문 없이 그린다.
- YAML에 빠진 값이 있으면 빠진 값만 질문하고, 임의로 채우지 않는다.

최소 질문 템플릿:

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

단일 VPC 답변 예시:

```text
VPC 1개
이름: VPC
CIDR: 10.0.0.0/16
AZ: 2개
subnet: public 2, application 2, db 2
subnet CIDR: 기본값 제안
IGW: yes
NAT GW: yes
```

Multi-VPC 추가 질문:

```text
두 번째 VPC부터는 첫 번째 VPC의 AZ/subnet/IGW/NAT 구조를 복사할 수 있습니다.

VPC 2는 VPC 1 구조를 복사할까요?
- 복사한다면 VPC 2 이름과 CIDR만 알려주세요.
- 다르면 VPC 2의 AZ, subnet tier별 개수, IGW, NAT GW 여부를 따로 알려주세요.
```

## 작업 순서

1. `references/drawio-cli-and-xml.md`를 읽고 CLI 위치, export 옵션, XML 필수 규칙을 확인한다.
2. `references/aws-vpc-diagram-rules.md`를 읽고 VPC/subnet-only scope, AZ dashed container, CIDR label, IGW/NAT 배치 규칙을 확인한다.
3. topology intake로 VPC 개수, tier별 subnet 개수, AZ 수, CIDR, IGW 여부, NAT GW 여부를 확정한다. 필요한 값이 빠져 있으면 intake interview만 하고 멈춘다.
4. 새 다이어그램은 `assets/aws-vpc-template.drawio`를 출발점으로 복사하거나 같은 규칙으로 XML을 작성한다.
5. `scripts/validate_drawio_xml.py`로 XML 구조와 스킬 레이아웃 규칙을 검증한다.
6. `scripts/export_drawio.sh`로 PNG를 export한다.
7. export PNG를 열어 VPC, AZ dashed container, subnet tier, CIDR label, IGW/NAT 위치, 빈 workload handoff area를 눈으로 확인한다.
8. Codex sandbox에서 `Abort trap`이 나면 draw.io Desktop CLI를 macOS GUI 권한으로 다시 실행한다. 그래도 실패하면 computer-use로 draw.io Desktop을 열어 export한다.

## 빠른 실행

템플릿 export:

```bash
bash scripts/export_drawio.sh assets/aws-vpc-template.drawio png /tmp/aws-vpc.drawio.png
```

XML 및 레이아웃 검증:

```bash
python3 scripts/validate_drawio_xml.py assets/aws-vpc-template.drawio
```

## XML 작성 규칙

- `<mxfile><diagram><mxGraphModel><root>` 구조를 사용한다.
- `<mxCell id="0"/>`, `<mxCell id="1" parent="0"/>`를 반드시 넣는다.
- visible cell은 고유 `id`를 갖고 `vertex="1"` 또는 `edge="1"` 중 하나만 갖는다.
- 이 skill은 traffic flow edge를 그리지 않는다.
- 라벨 값은 plain text 한 줄만 사용한다. `<br>`, HTML tag, HTML entity 기반 줄바꿈을 쓰지 않는다.
- VPC와 subnet group label에는 이름과 CIDR을 한 줄로 함께 넣는다.
- XML comment를 넣지 않는다.
- group nesting은 `VPC -> AZ dashed container -> Subnet -> NAT Gateway` 순서를 우선한다.
- AWS Cloud group은 그리지 않는다.
- AZ dashed container는 VPC group의 자식으로 두되, VPC 상단과 하단 경계를 넘어가게 그린다.
- IGW는 VPC에 붙는 리소스로 VPC group의 자식으로 두되, VPC 상단 경계선에 걸쳐 배치한다.
- IGW는 AZ column 사이 중앙 통로에 두고, AZ 세로 dashed boundary와 겹치지 않게 한다.

## 산출물

- 원본: `<name>.drawio`
- export: `<name>.drawio.png`
- 최종 보고에는 export PNG 경로, 실행한 검증 명령, 눈으로 확인한 레이아웃 상태, `확인 필요` 항목을 포함한다.
