# 분석 JSON 작성 계약

`analysis.json`은 분석의 유일한 원본이다. HTML과 draw.io는 JSON에서 생성하며 역동기화하지 않는다. 정확한 필드는 `schemas/analysis.schema.json`, 최소 형태는 `examples/analysis.example.json`을 따른다.

## 분석 범위

### 컴포넌트

| kind | 의미 |
|---|---|
| `service` | 독립 실행·배포되는 애플리케이션 |
| `component` | 서비스보다 작지만 아키텍처 경계로 설명할 가치가 있는 프로세스·작업 |
| `datastore` | DB 또는 영구 데이터 저장소 |
| `message-broker` | Kafka, RabbitMQ, SQS 같은 메시지 전달 경계 |
| `external-system` | 현재 또는 선택된 프로젝트 밖의 API·시스템 |

소스 import, 라이브러리, 클래스, 함수 호출은 기록하지 않는다. 컴포넌트의 `role`은 구현 기술이 아니라 비즈니스 책임을 1~2문장으로 쓴다.

`importance`는 HTML 첫 화면의 정보량을 제어한다.

- `core`: 외부 진입점, 핵심 호출 경로, 공유 저장소·브로커처럼 첫 화면에 필요한 컴포넌트
- `supporting`: 근거는 있지만 기본 화면에서는 접어도 되는 보조 컴포넌트

모든 컴포넌트는 역할과 경계를 증명하는 `evidence`가 최소 1개 필요하다. `owned_paths`는 증분 갱신에서 변경 파일을 컴포넌트에 매핑할 수 있는 최소 디렉터리·파일 목록이다.

## 관계와 방향

| kind | source → target |
|---|---|
| `http` | 호출자 → HTTP 서버 |
| `grpc` | 호출자 → gRPC 서버 |
| `db-read`, `db-write` | 실행 컴포넌트 → datastore |
| `external-api` | 호출자 → external-system |
| `event-publish`, `queue-produce` | 발행자·생산자 → message-broker |
| `event-subscribe`, `queue-consume` | message-broker → 구독자·소비자 |

모든 관계에는 실제 호출·읽기·쓰기·발행·구독을 증명하는 `evidence`가 최소 1개 필요하다. 설정에 URL이 있다는 이유만으로 실제 호출 관계를 만들지 않는다. 호출 코드와 설정이 나뉘어 있으면 근거를 둘 다 기록한다.

`details`는 관계를 확인하는 과정에서 직접 발견한 값만 넣는다. 세부정보만 찾기 위한 추가 전면 검색은 하지 않는다.

- HTTP: `method`, `path`
- gRPC: `grpc_service`, `grpc_method`
- DB: `database`, `table`
- 메시지: `broker`, `topic`, `queue`
- 외부 API: `provider`, `endpoint`

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
