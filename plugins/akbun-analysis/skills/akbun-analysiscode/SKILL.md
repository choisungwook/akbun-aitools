---
name: akbun-analysiscode
description: 소스코드가 어떤 비즈니스를 위해 쓰였고 그 비즈니스에 어떤 코드가 엮여 있는지를 file:line 근거와 함께 분석해 OS 표준 경로의 analysis.json에 저장하고, 비즈니스 흐름·서비스 관계도·API 관계도를 가진 인터랙티브 HTML과 선택적 draw.io를 생성·증분 갱신하는 skill. 코드베이스 구조/아키텍처 시각화, 업무 흐름별 코드 추적, API 목록 정리, HTTP·gRPC·DB 읽기/쓰기·외부 API·이벤트·큐 관계 파악, 컴포넌트 역할 설명, 변경 영향 가능성 평가 요청에 사용한다. "이 코드 관계도를 그려줘", "이 기능이 어떤 코드를 쓰는지 보여줘", "서비스 호출 구조를 분석해줘", "이 변경이 어디에 영향 줄까?" 같은 요청은 저장된 JSON의 신선도를 먼저 확인한다.
disable-model-invocation: true
---

# akbun-analysiscode

이 skill은 코드 품질을 평가하지 않는다. **어떤 비즈니스를 위해 코드가 쓰였고 그 비즈니스에 어떤 코드가 함께 엮여 있는지**를 근거 기반으로 한 번 분석하고 재사용한다. `analysis.json`만 분석 원본이며 HTML과 draw.io는 파생 산출물이다.

## 실행 순서

모든 요청에서 가장 먼저 저장 위치와 신선도를 확인한다.

```bash
python3 <skill-dir>/scripts/locate_analysis.py <project-root>
```

출력의 `mode`에 따라 진행한다.

- `initial`: 최초 분석을 수행한다.
- `reuse`: 코드를 전면 탐색하지 않고 `paths.analysis`를 먼저 읽는다.
- `incremental`: `changed_files`, `affected_component_ids`, `affected_flow_ids`, `unmapped_changed_files`만 중심으로 갱신한다.
- `full`: 마지막 분석 commit을 현재 Git에서 찾을 수 없거나 저장된 schema_version이 낡았으므로 전면 재분석한다. 서비스 경계가 크게 바뀐 경우에도 전면 재분석한다.

저장 위치는 `$AKBUN_ANALYSIS_HOME` override가 우선이며, 기본값은 macOS `~/Library/Application Support/akbun-analysis`, Windows `%APPDATA%/akbun-analysis`, Linux `${XDG_DATA_HOME:-~/.local/share}/akbun-analysis`다. 프로젝트 저장소에는 산출물을 만들지 않는다.

```text
<store-root>/
  projects.json
  projects/<project-id>/
    analysis.json
    analysis.html
    analysis.drawio  # 사용자가 요청한 뒤부터 존재
```

## 최초 분석

`references/analysis-format.md`, `schemas/analysis.schema.json`, `examples/analysis.example.json`을 읽는다.

### 1. 비즈니스를 먼저 찾는다

컴포넌트가 아니라 업무에서 시작한다. 라우팅 테이블, 이벤트 구독 설정, 스케줄러 등록, CLI 명령을 훑어 **외부에서 들어오는 요청 목록**을 모으고, 이름과 처리 내용으로 도메인(주문, 결제, 회원)과 그 아래 플로우(주문 생성, 주문 취소)로 묶는다.

`description`은 코드가 아니라 업무를 설명한다. "OrderService.create를 호출한다"가 아니라 "고객이 주문을 요청하면 결제를 승인받고 확정한다"로 쓴다.

### 2. 플로우마다 진입점부터 끝까지 따라간다

각 플로우의 `entry`에서 시작해 호출을 실제로 따라간다. **한 단계에서 멈추지 않는다.** 핸들러가 무언가를 호출하면 그 대상을 열고, 그것이 또 호출하면 다시 연다. DB·브로커·외부 시스템에 닿거나 더 나갈 곳이 없을 때까지 간다.

각 단계를 `layer`로 분류한다. 이 다섯 단계가 최대 depth 5의 근거다.

| layer | 무엇을 찾는가 |
|---|---|
| `entrypoint` | 컨트롤러, 핸들러, 컨슈머, 스케줄 잡 |
| `application` | 유스케이스, 서비스 조율자, 트랜잭션 경계 |
| `domain` | 업무 규칙·정책 판단이 있는 곳 |
| `infrastructure` | 리포지토리, 클라이언트, 발행자 구현 |
| `external` | DB, 브로커, 외부 시스템 |

계층을 건너뛰는 플로우는 있어도 되지만, 서비스에서 곧바로 DB로 끝나는 2단계만 나왔다면 중간 계층을 아직 열어보지 않은 것이다. 다시 따라간다.

`module`로 만들 단위는 **그 플로우를 말로 설명할 때 이름을 부를 만한 단계**다. 클래스 하나, 함수 하나를 기계적으로 옮기지 않는다. 유틸리티, DTO, 라이브러리 wrapper는 컴포넌트가 아니다.

### 3. 관계와 근거를 기록한다

`code-call`, HTTP/gRPC 호출, DB 읽기·쓰기, 외부 API, 이벤트 발행·구독, 큐 생산·소비만 기록한다. import, 라이브러리 의존, 타입 참조는 관계가 아니다.

모든 컴포넌트와 관계에 실제 `file:line` 근거를 최소 1개 넣는다. 근거가 없으면 관계도에 넣지 않는다.

근거 확인 중 발견한 method/path, gRPC service/method, DB/table, broker/topic/queue, 외부 endpoint, 호출 function만 `details`에 넣는다. 세부정보만 찾기 위한 추가 전면 검색은 하지 않는다.

플로우의 `steps`는 관계 id를 **실행 순서대로** 담는다. 각 스텝은 이미 그 플로우에서 도달한 컴포넌트에서 출발해야 하며, 검증기가 이 순서를 강제한다.

### 4. API 목록을 만든다

1단계에서 모은 진입점과, 관계를 따라가며 본 호출 주소를 `apis`에 정리한다. 라우트 등록, gRPC 서비스 정의, 클라이언트의 요청 경로, 토픽 이름이 근거다.

- 외부 사용자·외부 시스템·스케줄러가 직접 부르면 `entrypoint: true`
- 내부 서비스끼리만 부르면 `entrypoint: false`
- 다른 프로젝트가 제공하는 주소면 `provider_project_id`를 함께 넣는다

주소가 확인된 관계에는 `api`로 그 id를 연결한다. **다른 repo를 부르는 관계는 반드시 연결한다.** 관계도에서 어느 도메인·경로로 나가는지가 이 값으로 보인다.

### 5. origin을 붙인다

모든 컴포넌트에 `origin`을 넣는다. HTML 노드 왼쪽 상단 아이콘이 여기서 나온다.

- 서비스·외부 시스템이면 `{"type": "git", "label": "<repo 이름>"}`
- DB·캐시·버킷·브로커면 `{"type": "database", "engine": "<redis|rds|dynamodb|s3|kafka|...>", "label": "<인스턴스·토픽 이름>"}` — engine은 배포 매니페스트, 커넥션 문자열, SDK import에서 확인한 값만 쓴다
- 현재 코드베이스 안의 module이면 `{"type": "code", "label": "<디렉터리 경로>"}`

### 6. 저장한다

JSON에는 근거가 확인된 모든 컴포넌트를 넣고 첫 화면에 필요한 항목만 `importance: core`로 둔다.

최종 저장 경로를 직접 수정하지 말고 별도 candidate JSON을 만든다. candidate를 검증하고 오류가 가리키는 항목만 수정한다.

```bash
python3 <skill-dir>/scripts/validate_analysis.py <candidate.json> <project-root>
```

검증 성공 후 candidate를 전달한다. 이 명령이 동적 project metadata를 현재 값으로 교체하고 JSON과 self-contained HTML을 갱신하며, 기존 `analysis.drawio`가 있으면 함께 덮어쓴다.

```bash
python3 <skill-dir>/scripts/commit_analysis.py <project-root> <candidate.json>
```

## 증분 갱신

`locate_analysis.py`가 마지막 분석 commit, 현재 HEAD, 작업 트리 지문을 비교한다.

1. 기존 `analysis.json`을 candidate로 복사한다.
2. `affected_component_ids`의 역할·근거·들어오고 나가는 관계만 다시 확인한다.
3. `affected_flow_ids`의 플로우가 여전히 같은 순서로 성립하는지 확인한다. 단계가 끼어들거나 빠졌으면 `steps`를 고친다.
4. `unmapped_changed_files`에서 새 진입점, 새 서비스, 배포 경계, 공용 설정 변경 가능성을 확인한다. 새 진입점이면 어느 비즈니스에 속하는지 판단해 플로우를 추가한다. 관계 없는 변경이면 JSON을 늘리지 않는다.
5. 삭제되거나 이동된 근거, 사라진 관계, 새 관계를 candidate에 반영한다.
6. `layout`은 건드리지 않는다. candidate에 없으면 commit이 저장된 배치를 그대로 이어받는다.
7. 검증 후 `commit_analysis.py`로 전달한다.

## 저장된 분석 활용

업무·구조·역할·관계 질문은 `analysis.json`만 필요한 범위로 읽고, 세부 확인은 evidence가 가리키는 파일만 연다. "이 기능이 무슨 코드를 쓰나" 류의 질문은 해당 플로우의 `steps`를 따라 답한다. 저장 내용과 코드가 다르면 증분 갱신한 뒤 답한다.

영향 가능 컴포넌트는 다음 명령으로 탐색한다. 출력의 `possible_affected_flows`가 영향받을 수 있는 업무 흐름이다.

```bash
python3 <skill-dir>/scripts/trace_impact.py <analysis.json> <component-id>
```

그래프 결과를 장애 범위나 실제 리스크로 단정하지 않는다. 리스크 결론 전에 변경 코드와 반환된 관계 근거를 확인한다.

## 여러 프로젝트

사용자가 다른 프로젝트 경로를 명시한 경우에만 프로젝트 간 분석을 활성화한다.

1. 각 프로젝트에서 `locate_analysis.py`를 실행하고 독립된 `analysis.json`을 최신 상태로 만든다.
2. 현재 JSON의 `related_project_ids`에 함께 표시할 프로젝트만 넣는다.
3. 프로젝트 간 관계에는 `target_project_id`를 넣는다.
4. commit 시 선택된 JSON들을 결합해 현재 프로젝트 HTML과 기존 draw.io에 표시한다.

## HTML과 draw.io

`analysis.html`은 외부 CDN·서버 없이 로컬 브라우저에서 열린다. 왼쪽 사이드바 위의 경계선 메뉴로 세 화면을 고른다.

- **비즈니스**: 도메인 > 플로우 2단 ToC. 항목을 고르면 그 업무에 쓰인 코드만 진입점부터 좌→우 체인으로 그리고, 화살표에 실행 순번을 붙인다.
- **서비스 관계도**: `module`을 접어 서비스·저장소·외부 시스템 사이 관계만 남긴 화면. 접힌 관계는 점선으로 그리고 클릭하면 지나온 모든 근거를 보여준다. 깊이 선택으로 1~5단계까지 조절한다.
- **API 관계도**: 호출 주소가 확인된 관계만 남긴 화면. 왼쪽에 진입점과 내부 호출로 나눈 API 목록이 나열되고, 엣지 위에 주소가 그려진다.

세 화면 공통 기능은 다음과 같다.

- 컴포넌트 왼쪽 상단 `origin` 아이콘(git / DB engine별 / code)
- 관계 유형 필터, 검색
- 노드 드래그 이동, 휠 확대, 배경 드래그 이동
- 선택 컴포넌트의 들어오고 나가는 관계 강조, 관계별 세부정보와 `file:line` 근거 표시
- "자동 배치"로 되돌리기, "배치 복사"로 현재 배치를 JSON으로 복사

사용자가 배치를 저장해 달라고 하면 "배치 복사" 결과를 받아 `analysis.json`의 `layout`에 그대로 넣고 다시 commit한다. 배치를 직접 만들어내지 않는다.

draw.io는 사용자가 요청했을 때 처음 생성한다. 서비스 관계도 1장과 플로우별 1장씩 페이지로 나뉜다. JSON → draw.io 단방향이라 draw.io의 사람 수정 내용은 JSON으로 가져오지 않는다.

산출물만 다시 만들 때는 각각 다음 명령을 사용한다.

```bash
python3 <skill-dir>/scripts/render_analysis.py <analysis.json> <analysis.html>
python3 <skill-dir>/scripts/export_drawio.py <analysis.json> <analysis.drawio>
```

## 완료 보고

사용자에게 다음을 짧게 알린다.

- 분석 모드: 최초/재사용/증분
- 비즈니스·플로우 수와 가장 깊은 플로우의 단계 수
- API 수와 그중 진입점 수
- 컴포넌트·관계 수, 분석 commit
- `analysis.json`, `analysis.html`, 존재하면 `analysis.drawio` 절대 경로
- 검증 경고 또는 아직 근거를 확인하지 못한 범위
