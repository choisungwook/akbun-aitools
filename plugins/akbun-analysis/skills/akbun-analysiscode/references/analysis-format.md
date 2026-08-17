# 분석 JSON 작성 계약

`analysis.json`은 분석의 유일한 원본이다. HTML과 draw.io는 JSON에서 생성하며 역동기화하지 않는다. 정확한 필드는 `schemas/analysis.schema.json`, 최소 형태는 `examples/analysis.example.json`을 따른다.

## 분석 목적

이 분석은 코드 품질을 평가하지 않는다. **어떤 비즈니스를 위해 이 코드가 쓰였고, 그 비즈니스에 어떤 코드가 함께 엮여 있는지**를 남긴다. 그래서 `businesses`가 1급 정보이고 `components`와 `relationships`는 그 비즈니스를 구성하는 재료다.

## 비즈니스

`businesses`는 도메인 > 플로우 2단이다. HTML 왼쪽 ToC가 이 구조 그대로 렌더링된다.

| 단위 | 의미 |
|---|---|
| 도메인(business) | 주문, 결제, 회원처럼 업무 영역 한 덩어리 |
| 플로우(flow) | "주문 생성", "결제 승인"처럼 진입점 하나에서 시작해 끝나는 업무 시나리오 |

플로우의 `entry`는 그 시나리오가 시작되는 컴포넌트 id다. `steps`는 관계 id를 **실행 순서대로** 담은 배열이며 HTML은 이 순서를 화살표 위 번호로 그린다.

```json
{
  "id": "order.create",
  "name": "주문 생성",
  "description": "고객이 주문을 요청하면 결제를 승인받고 주문을 확정 상태로 저장한다.",
  "trigger": "POST /orders",
  "entry": "order-api",
  "steps": ["order-api-calls-place-order", "place-order-calls-order-repository"]
}
```

`steps`의 각 관계는 **이미 이 플로우에서 도달한 컴포넌트에서 출발**해야 한다. 첫 스텝의 source는 `entry`이고, 이후 스텝의 source는 앞선 스텝이 도달한 컴포넌트 중 하나다. 검증기가 이 순서를 강제한다.

`description`은 코드가 아니라 업무를 설명한다. "OrderService.create를 호출한다"가 아니라 "고객이 주문을 요청하면 결제를 승인받고 확정한다"로 쓴다.

## API

`apis`는 이 프로젝트가 제공하거나 부르는 호출 주소 목록이다. HTML의 API 관계도 화면이 이 목록을 그대로 왼쪽에 나열하고, 부하분석은 `entrypoint: true`인 API를 요청량 입력 단위로 쓴다.

```json
{
  "id": "post-orders",
  "name": "주문 생성",
  "protocol": "http",
  "method": "POST",
  "path": "/orders",
  "provider": "order-api",
  "entrypoint": true,
  "flow_ids": ["order.create"],
  "evidence": [{"path": "services/order-api/handler/order.go", "line": 18, "description": "라우트 등록"}]
}
```

`protocol`에 따라 필요한 필드가 다르다. `http`·`graphql`은 `path`, `grpc`는 `grpc_service`와 `grpc_method`, `event`·`queue`는 `topic`이 필요하다.

`entrypoint`는 **시스템 밖에서 직접 들어오는가**를 뜻한다. 외부 사용자·외부 시스템·스케줄러가 부르면 true, 내부 서비스끼리만 부르면 false다. 다른 프로젝트가 제공하는 주소는 `provider_project_id`를 함께 넣는다.

관계가 어떤 API를 부르는지 알면 relationship에 `api`로 그 id를 넣는다. 다른 repo를 부르는 관계일수록 중요하다. HTML이 이 값으로 엣지 위에 주소를 그린다.

## 컴포넌트

| kind | 의미 |
|---|---|
| `service` | 독립 실행·배포되는 애플리케이션 |
| `module` | 서비스 안에서 업무 흐름의 한 단계를 맡는 코드 경계(핸들러, 유스케이스, 리포지토리, 클라이언트) |
| `component` | 서비스보다 작지만 별도 프로세스·작업인 것 |
| `datastore` | DB 또는 영구 데이터 저장소 |
| `message-broker` | Kafka, RabbitMQ, SQS 같은 메시지 전달 경계 |
| `external-system` | 현재 또는 선택된 프로젝트 밖의 API·시스템 |

`module`은 업무 흐름의 depth를 만드는 단위다. 클래스 하나, 함수 하나를 그대로 옮기지 않는다. **그 플로우를 설명할 때 이름을 부를 만한 단계**만 `module`로 만든다.

### layer

`layer`는 그 컴포넌트가 흐름의 어느 단계에 있는지다. 다섯 단계가 전부이며 이것이 최대 depth 5의 근거다.

| layer | 의미 |
|---|---|
| `entrypoint` | 요청·이벤트·스케줄이 들어오는 지점 |
| `application` | 유스케이스 조율, 트랜잭션 경계 |
| `domain` | 업무 규칙·정책 판단 |
| `infrastructure` | 저장소·클라이언트·발행자 구현 |
| `external` | DB, 브로커, 외부 시스템 |

한 플로우는 `entrypoint`에서 시작해 `external`에서 끝나는 것이 자연스럽다. 계층을 건너뛰어도 되지만 되돌아가지는 않는다.

### origin

`origin`은 HTML 노드 왼쪽 상단 아이콘의 근거다. 이 컴포넌트가 어디 소속인지 나타낸다.

| type | 언제 | 필드 |
|---|---|---|
| `git` | 서비스나 외부 시스템처럼 저장소 단위로 구분되는 것 | `label`에 repo 이름 |
| `database` | DB·캐시·버킷·브로커 | `engine` 필수, `label`에 인스턴스·토픽 이름 |
| `code` | 현재 코드베이스 안의 module | `label`에 디렉터리 경로 |

`engine`은 `postgres`, `mysql`, `rds`, `aurora`, `redis`, `dynamodb`, `mongodb`, `elasticsearch`, `s3`, `kafka`, `rabbitmq`, `sqs`, `sns`, `other` 중 하나다. HTML이 engine별로 아이콘 모양과 색을 다르게 그린다.

### capacity

`capacity`는 부하분석의 출발값이다. 배포 매니페스트에서 확인한 값만 `source: "manifest"`로 넣는다.

```json
{"replicas": 3, "cpu_millicores": 1000, "memory_mib": 1024, "max_replicas": 10, "source": "manifest"}
```

`cpu_millicores`와 `memory_mib`는 **레플리카 1대 기준**이다. k8s면 `spec.replicas`, `resources.limits`(없으면 `requests`), HPA의 `maxReplicas`를 본다. 확인할 수 없으면 `capacity`를 아예 넣지 않는다. 근거 없이 채워야 할 때만 `source: "assumed"`를 쓴다. HTML은 이 값을 슬라이더 기본값으로 띄우고 사용자가 다른 값으로 바꿔볼 수 있게 한다.

### 나머지

`role`은 구현 기술이 아니라 비즈니스 책임을 1~2문장으로 쓴다.

`importance`는 `core`(첫 화면에 필요) 또는 `supporting`(접어도 되는 보조)이다.

모든 컴포넌트는 역할과 경계를 증명하는 `evidence`가 최소 1개 필요하다. `owned_paths`는 증분 갱신에서 변경 파일을 컴포넌트에 매핑할 수 있는 최소 디렉터리·파일 목록이다.

## 관계와 방향

| kind | source → target |
|---|---|
| `code-call` | 호출하는 코드 경계 → 호출당하는 코드 경계 (같은 코드베이스 안) |
| `http` | 호출자 → HTTP 서버 |
| `grpc` | 호출자 → gRPC 서버 |
| `db-read`, `db-write` | 실행 컴포넌트 → datastore |
| `external-api` | 호출자 → external-system |
| `event-publish`, `queue-produce` | 발행자·생산자 → message-broker |
| `event-subscribe`, `queue-consume` | message-broker → 구독자·소비자 |

모든 관계에는 실제 호출·읽기·쓰기·발행·구독을 증명하는 `evidence`가 최소 1개 필요하다. 설정에 URL이 있다는 이유만으로 실제 호출 관계를 만들지 않는다. 호출 코드와 설정이 나뉘어 있으면 근거를 둘 다 기록한다.

`details`는 관계를 확인하는 과정에서 직접 발견한 값만 넣는다. 세부정보만 찾기 위한 추가 전면 검색은 하지 않는다.

- 코드 호출: `function`
- HTTP: `method`, `path`
- gRPC: `grpc_service`, `grpc_method`
- DB: `database`, `table`
- 메시지: `broker`, `topic`, `queue`
- 외부 API: `provider`, `endpoint`

## load

`load`는 이 관계를 지날 때 요청이 얼마나 증폭되는지다. 부하가 선형이 아닌 이유가 여기 담긴다.

```json
{"fan_out": 3, "fan_out_note": "주문 항목마다 INSERT 를 반복한다.", "sync": true, "crypto": "tls"}
```

| 필드 | 의미 |
|---|---|
| `fan_out` | 부모 요청 1건당 이 관계가 실행되는 횟수. 기본 1 |
| `fan_out_note` | `fan_out`이 1보다 크면 필수. 무엇이 반복시키는지 적는다 |
| `sync` | 호출자가 응답을 기다리는가. 기본은 메시지 계열만 false |
| `crypto` | `none`, `tls`, `mtls`, `field`, `kms` 중 하나 |

`fan_out`을 1보다 크게 쓰려면 **반복시키는 것이 코드에 보여야 한다.** 반복문 안의 호출, 목록을 순회하는 조회, 배치 크기만큼 나가는 요청이 근거다. 짐작으로 배수를 올리지 않는다. 목록 길이가 가변이면 코드나 설정에서 확인 가능한 대표값을 쓰고 그 근거를 `fan_out_note`에 적는다. N+1 호출이 바로 이 값으로 드러난다.

`crypto`는 전송 구간의 TLS/mTLS, 애플리케이션의 필드 단위 암복호화, KMS 호출을 구분한다. 각 종류의 CPU 비용은 사용자가 화면에서 조절하므로 여기서는 종류만 정한다.

## 근거

근거 경로는 프로젝트 루트 기준 상대 경로다. `line`과 선택적인 `end_line`은 현재 분석 대상 파일에 실제로 존재해야 한다. 설명은 그 범위가 무엇을 증명하는지 적는다.

```json
{
  "path": "services/order/client/payment.go",
  "line": 28,
  "end_line": 34,
  "description": "PaymentService.Charge gRPC 호출"
}
```

근거가 없는 추측은 JSON과 관계도에 넣지 않는다. 이름이나 같은 디렉터리에 있다는 사실만으로 호출 관계를 만들지 않는다.

## layout

`layout`은 사용자가 HTML에서 노드를 드래그해 옮긴 위치다. 화면 상태이지 분석 결과가 아니므로 직접 만들지 않는다. 사용자가 HTML의 "배치 복사"로 넘겨준 JSON만 그대로 넣는다.

```json
{
  "layout": {
    "service": {"order-api": {"x": 400, "y": 120}},
    "flow:order.create": {"place-order": {"x": 320, "y": 200}}
  }
}
```

뷰 id는 서비스 화면이 `service`, 업무 흐름이 `flow:<flow-id>`, 도메인 전체가 `business:<business-id>`다. `commit_analysis.py`는 candidate에 `layout`이 없으면 저장된 배치를 그대로 이어받으므로 증분 갱신에서 사용자 배치가 사라지지 않는다.

## 여러 프로젝트

각 프로젝트는 독립적인 `analysis.json`을 유지한다. 사용자가 함께 볼 프로젝트를 지정했을 때만 현재 JSON의 `related_project_ids`에 상대 project id를 넣는다.

다른 프로젝트 컴포넌트를 호출하는 관계는 현재 프로젝트 JSON에 기록하고 `target_project_id`를 지정한다. 상대 프로젝트가 선택되지 않았거나 분석되지 않았으면 HTML은 외부 프로젝트 자리표시자로 보여준다.

```json
{
  "id": "order-calls-payment",
  "source": "order-api",
  "target": "payment-api",
  "target_project_id": "payment-platform-89abcdef",
  "kind": "grpc",
  "label": "결제 승인",
  "details": {"grpc_service": "PaymentService", "grpc_method": "Charge"},
  "evidence": [{"path": "services/order/payment.go", "line": 28, "description": "Charge 호출"}]
}
```

## 영향 가능성

동기 호출·DB·외부 API는 대상이 바뀌면 호출자가 영향을 받을 가능성이 있다. 메시지는 발행자·생산자에서 구독자·소비자 방향으로 계약 변경이 전파될 가능성이 있다.

그래프 도달 결과는 영향 **가능성**이지 장애 범위, 인과관계, 리스크 증명이 아니다. 리스크 결론 전에는 변경 코드와 각 관계 근거를 다시 확인한다.
