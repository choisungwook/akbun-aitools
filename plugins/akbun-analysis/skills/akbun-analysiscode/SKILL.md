---
name: akbun-analysiscode
description: 소스코드에서 서비스·컴포넌트 수준의 실제 호출 관계를 file:line 근거와 함께 분석해 OS 표준 경로의 analysis.json에 저장하고, 로컬 브라우저용 인터랙티브 HTML과 선택적 draw.io 관계도를 생성·증분 갱신하는 skill. 코드베이스 구조/아키텍처 시각화, HTTP·gRPC·DB 읽기/쓰기·외부 API·이벤트·큐 관계 파악, 컴포넌트 역할 설명, 변경 영향 가능성·리스크 평가 요청에 사용한다. "이 코드 관계도를 그려줘", "서비스 호출 구조를 분석해줘", "이 변경이 어디에 영향 줄까?" 같은 요청은 저장된 JSON의 신선도를 먼저 확인한다.
---

# akbun-analysiscode

서비스·컴포넌트 관계를 한 번 근거 기반으로 분석하고 재사용한다. `analysis.json`만 분석 원본이며 HTML과 draw.io는 파생 산출물이다.

## 실행 순서

모든 요청에서 가장 먼저 저장 위치와 신선도를 확인한다.

```bash
python3 <skill-dir>/scripts/locate_analysis.py <project-root>
```

출력의 `mode`에 따라 진행한다.

- `initial`: 최초 분석을 수행한다.
- `reuse`: 코드를 전면 탐색하지 않고 `paths.analysis`를 먼저 읽는다.
- `incremental`: `changed_files`, `affected_component_ids`, `unmapped_changed_files`만 중심으로 갱신한다.
- `full`: 마지막 분석 commit을 현재 Git에서 찾을 수 없으므로 전면 재분석한다.

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

1. 배포 매니페스트, 실행 엔트리포인트, 라우팅·클라이언트, DB 연결, 메시지 설정을 탐색해 실제 아키텍처 경계를 찾는다.
2. `service`, `component`, `datastore`, `message-broker`, `external-system`만 기록한다. import, 라이브러리, 클래스, 함수 호출은 제외한다.
3. HTTP/gRPC 호출, DB 읽기·쓰기, 외부 API, 이벤트 발행·구독, 큐 생산·소비 관계만 기록한다.
4. 모든 컴포넌트와 관계에 실제 `file:line` 근거를 최소 1개 넣는다. 근거가 없으면 관계도에 넣지 않는다.
5. 근거 확인 중 발견한 method/path, gRPC service/method, DB/table, broker/topic/queue, 외부 endpoint만 `details`에 넣는다. 세부정보만 찾기 위한 추가 전면 검색은 하지 않는다.
6. JSON에는 근거가 확인된 모든 컴포넌트를 넣고 첫 화면에 필요한 항목만 `importance: core`로 둔다.
7. 최종 저장 경로를 직접 수정하지 말고 별도 candidate JSON을 만든다. commit이 동적 project metadata를 현재 값으로 교체한다.
8. candidate를 검증하고 오류가 가리키는 항목만 수정한다.

```bash
python3 <skill-dir>/scripts/validate_analysis.py <candidate.json> <project-root>
```

9. 검증 성공 후 candidate를 전달한다. 이 명령이 JSON과 self-contained HTML을 갱신하며, 기존 `analysis.drawio`가 있으면 함께 덮어쓴다.

```bash
python3 <skill-dir>/scripts/commit_analysis.py <project-root> <candidate.json>
```

## 증분 갱신

`locate_analysis.py`가 마지막 분석 commit, 현재 HEAD, 작업 트리 지문을 비교한다.

1. 기존 `analysis.json`을 candidate로 복사한다.
2. `affected_component_ids`의 역할·근거·들어오고 나가는 관계만 다시 확인한다.
3. `unmapped_changed_files`에서 새 서비스, 배포 경계, 공용 설정 변경 가능성을 확인한다. 관계 없는 변경이면 JSON을 늘리지 않는다.
4. 삭제되거나 이동된 근거, 사라진 관계, 새 관계를 candidate에 반영한다.
5. 검증 후 `commit_analysis.py`로 전달한다.

전면 재분석은 서비스 경계가 크게 바뀌었거나 분석 계약 자체가 달라진 경우에만 한다.

## 저장된 분석 활용

구조·역할·관계 질문은 `analysis.json`만 필요한 범위로 읽고, 세부 확인은 evidence가 가리키는 파일만 연다. 저장 내용과 코드가 다르면 증분 갱신한 뒤 답한다.

영향 가능 컴포넌트는 다음 명령으로 탐색한다.

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

`analysis.html`은 외부 CDN·서버 없이 로컬 브라우저에서 열린다. 기본 화면은 core 컴포넌트만 표시하며 다음 기능을 제공한다.

- 컴포넌트 검색과 supporting 표시
- 관계 유형 필터
- 선택 컴포넌트의 들어오고 나가는 관계 강조
- 관계별 세부정보와 `file:line` 근거 표시

draw.io는 사용자가 요청했을 때 처음 생성한다.

```bash
python3 <skill-dir>/scripts/export_drawio.py <analysis.json> <analysis.drawio>
```

JSON → draw.io 단방향이다. draw.io의 사람 수정 내용을 JSON으로 가져오지 않으며 이후 증분 갱신은 같은 `analysis.drawio`를 덮어쓴다.

HTML이나 draw.io만 다시 만들 때는 각각 다음 명령을 사용한다.

```bash
python3 <skill-dir>/scripts/render_analysis.py <analysis.json> <analysis.html>
python3 <skill-dir>/scripts/export_drawio.py <analysis.json> <analysis.drawio>
```

## 완료 보고

사용자에게 다음을 짧게 알린다.

- 분석 모드: 최초/재사용/증분
- 컴포넌트·관계 수와 분석 commit
- `analysis.json`, `analysis.html`, 존재하면 `analysis.drawio` 절대 경로
- 검증 경고 또는 아직 근거를 확인하지 못한 범위
