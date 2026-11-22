---
name: akbun-draw-mermaid-database-garam
description: 데이터베이스 권한 실습(GRANT·소유자·Role)을 Mermaid flowchart LR 관계도로 그리는 스타일 garam. 베이지 둥근 노드·테라코타 글자·파란 알약 테두리 화살표 라벨·화살표 위 GRANT SQL 글씨 테마(frontmatter CSS)를 붙이고, DB는 subgraph, 테이블 노드는 스키마.테이블과 소유자, 관리자와 권한 받는 Role은 별도 노드, GRANT 화살표에는 실제 SQL을 적고 이미 부여된 권한은 실선, 이제 검증할 SQL은 점선으로 그린다. 조회·변경 결과는 실습에서 확인하도록 그림에서 비운다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-mermaid-database-garam

## 목적

DB 권한 실습 글·발표에 넣을 Mermaid 관계도를 만든다. 독자가 그림만 보고 "누가, 어떤 권한을, 어느 객체에 대해, 누구에게 줬고, 이제 무엇을 시도하는가"를 읽을 수 있어야 한다. 시도의 결과(성공·실패·에러 메시지·조회 행)는 독자가 실습에서 직접 확인할 몫이므로 그리지 않는다.

이 skill이 고정하는 것은 아래 그리기 규칙과 [references/theme.md](references/theme.md)의 테마(CSS)다. 어떤 DB·Role·테이블·SQL을 넣을지는 입력 시나리오에서 정한다.

## 입력에서 뽑을 것

| 뽑을 것 | 예 |
|---|---|
| DB 이름 | `billing` |
| 테이블(스키마 포함)과 소유자 | `billing.invoices`, 소유자 `app_owner` |
| 관리자(GRANT를 실행하는 Role) | `postgres` |
| 권한을 받는 Role | `report_reader` |
| 이미 실행한 GRANT SQL | `GRANT SELECT ON TABLE billing.invoices TO report_reader` |
| 이제 검증할 SQL | `UPDATE billing.invoices ...` |

입력에 없는 이름·SQL은 지어내지 않는다. 스키마가 빠졌으면 PostgreSQL 기본인 `public`을 쓰고 그렇게 가정했다고 한 줄 알린다.

## 그리기 규칙

1. 코드 맨 위에 [references/theme.md](references/theme.md)의 frontmatter를 그대로 붙이고, 그 다음 줄이 `flowchart LR`.
2. DB는 DB마다 `subgraph <id>["<DB 이름> 데이터베이스"]` 하나로 묶고, 그 DB에 속한 테이블 노드만 안에 둔다. 스키마는 subgraph로 나누지 않고 테이블 이름에 적는다. 관리자·Role 노드는 subgraph 밖에 둔다.
3. 테이블 노드 라벨은 두 줄. 첫 줄 `스키마.테이블`, 둘째 줄 `소유자: <Role>`. 줄바꿈은 `<br/>`.
4. 그림에 나오는 Role(GRANT를 실행하는 쪽, 권한 받는 쪽, 검증할 SQL을 실행하는 쪽)마다 노드 하나를 subgraph 밖에 둔다. 같은 Role은 역할이 겹쳐도(소유자가 직접 GRANT) 노드 하나로 쓰고, 다른 Role은 합치지 않는다. 라벨은 GRANT를 실행하는 Role만 `관리자 <Role>`, 나머지는 Role 이름만 쓴다.
5. GRANT 화살표는 관리자 → 권한 받는 Role. 라벨은 실행한 SQL 그대로(`GRANT <권한> ON <객체 종류> <스키마.객체> TO <Role>`)를 `<code>`로 감싸고(`-->|"<code>GRANT ...</code>"|`) 끝 세미콜론은 뺀다. 테마가 `<code>` 라벨만 테두리 없이 화살표 위 글씨로 올리고, 나머지 라벨은 알약 테두리로 둔다. 화살표 출발 노드가 "누가", SQL이 "어떤 권한·어느 객체·누구에게"를 말한다.
6. 권한이 걸린 대상은 권한 받는 Role → 테이블 실선 화살표로 잇고 라벨은 `<객체 종류> 권한의 대상`처럼 짧게 쓴다.
7. 선 종류는 상태를 뜻한다. 이미 부여·실행된 것은 실선 `-->`, 이제 검증할 SQL은 점선 `-.->`. 점선은 그 SQL을 실행하는 Role 노드(4번) → 대상 테이블로 긋고, 라벨은 `<도구·단계> · <SQL 동사> 시도`처럼 무엇을 시도하는지만 쓴다(예: `Flyway V3 · ALTER TABLE 시도`, `UPDATE billing.invoices 시도`).
8. 결과는 비운다. 라벨·노드·주석 어디에도 `성공`, `실패`, `ERROR`, `permission denied`, 조회 결과 행, ✅·❌ 같은 표시를 넣지 않는다.
9. 코드 순서는 GRANT 화살표 줄(관리자·권한 받는 Role 노드를 그 줄에서 정의) → DB `subgraph`와 테이블 노드 → 권한 대상 실선 → 검증 점선이다. 노드 id는 짧은 영문·숫자(예: `Admin`, `M2`, `Shop`, `T`)이고, 라벨은 큰따옴표로 감싼다(`["..."]`, `-->|"..."|`). SQL의 괄호·콜론·점이 Mermaid 문법과 충돌하지 않게 하기 위해서다.
10. 테마 밖의 색·`classDef`·`style`을 노드마다 따로 넣지 않는다.

검증할 SQL이 여러 개면 점선을 SQL마다 하나씩, GRANT가 여러 개면 GRANT마다 화살표 하나를 쓴다.

## 출력

테마 frontmatter부터 시작하는 `mermaid` 코드 블록 하나를 낸다. 블록 위에 무엇을 그린 그림인지 한 줄, 블록 아래에 가정한 것(예: 스키마 `public`)이 있으면 한 줄. 형식 예시는 [references/example.md](references/example.md)이고, 소재는 그대로 쓰지 않는다.

## 검수

- [ ] 테마 frontmatter가 그대로 있고, 이어서 `flowchart LR`이며 DB subgraph 안에 테이블만 있다.
- [ ] 모든 테이블 노드에 `스키마.테이블`과 `소유자:`가 있다.
- [ ] GRANT 라벨이 `<code>`로 감싼 실제 실행 가능한 SQL이다.
- [ ] 이미 부여된 것은 실선, 검증할 SQL은 점선이다.
- [ ] 결과(성공·실패·에러·조회 행)가 그림에 없다.
- [ ] Mermaid 렌더러(예: `mmdc`, mermaid.live)에서 문법 오류 없이 그려진다.
