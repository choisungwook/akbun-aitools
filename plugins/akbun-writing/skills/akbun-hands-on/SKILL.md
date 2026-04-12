---
name: akbun-hands-on
description: "Generate short, terse, bullet-heavy hands-on markdown skeletons for akbun's GitHub repos. This is the first stage of a 2-step workflow: akbun-hands-on writes the skeleton (commands, environment, steps, verification), then akbun-writing later expands it with personal narrative, failures, team context, and reflection — like turning a screenplay into a movie. Make sure to use this skill whenever the user asks for a hands-on document, lab guide, practice note, reproducible step-by-step markdown, github 실습 문서, 핸즈온 뼈대, 실습 뼈대, skeleton markdown, or 각본, even if they don't explicitly say 'skeleton'. Also trigger when the user says things like '명령어 위주로 짧게 정리해줘', 'github에 올릴 실습 노트 만들어줘', '핸즈온 초안', or any request where the user wants a concise command-first markdown that another skill will flesh out later. Trigger keywords: '핸즈온 뼈대', 'hands-on 뼈대', 'akbun 핸즈온', '실습 뼈대', '실습 문서', '핸즈온 문서', '핸즈온 초안', '각본', 'github 실습', 'skeleton', 'lab guide', 'practice notes'."
---

# akbun 스타일 hands-on 뼈대

## 이 skill의 자리

이것은 2단계 워크플로의 **1단계**다. 역할 분리가 핵심이다.

- **1단계 (여기, akbun-hands-on)**: 뼈대 — 명령어, 환경, 단계, 검증, 링크. 재현 가능한 사실만 담는다.
- **2단계 (akbun-writing)**: 살 — 왜 이 실습을 했는지, 무엇을 잘못했고, 뭘 깨달았는지, 누구와 상의했는지. 서사와 감정.

사용자는 이 흐름을 "소설 → 영화 각본 → 영화"에 비유한다. akbun-hands-on이 각본이고, akbun-writing이 영화 제작이다. 각본이 카메라 워크와 감독의 해석까지 다 써버리면 영화 만들 자리가 없어진다. **뼈대는 의도적으로 비워둔다.**

## 원칙

### 재현 가능성이 전부다

실습 문서에서 명령어가 돌아가지 않으면 그 위에 어떤 서사를 붙여도 글 전체가 무너진다. 뼈대에는 검증된 명령어만 넣는다. 추측으로 쓰지 않고, 환경 버전을 명시해서 미래의 재현 조건을 박아둔다.

### 짧게, 단답형으로

뼈대 단계에서는 문단을 쓰지 않는다. bullet과 번호 목록으로 단계를 나열하고, 설명이 필요하면 한 줄로 끝낸다. 이유는 간단하다 — **긴 문단은 서사가 끼어들 자리**인데, 서사는 2단계가 담당하기 때문이다. 1단계가 미리 풀어쓰면 2단계가 덧붙일 여백이 사라진다.

### 확장 hook을 심는다

akbun-writing이 나중에 어디에 살을 붙일지 알 수 있도록, `<!-- akbun-writing: ... -->` HTML 주석으로 확장 포인트를 표시한다. 2단계는 이 주석 자리에 경험과 반성을 덧붙이고 주석 자체는 지운다.

흔히 쓰이는 hook:

- `<!-- akbun-writing: 왜 이 실습을 했는지 배경 추가 -->`
- `<!-- akbun-writing: 실패와 재시도 이야기 추가 -->`
- `<!-- akbun-writing: 팀 토론 / 사람 맥락 추가 -->`
- `<!-- akbun-writing: 깨달음 / 반성 추가 -->`
- `<!-- akbun-writing: 다음에 공부할 것 추가 -->`

## 뼈대 구조 (template)

아래 구조를 기본으로 삼는다. 실습 내용에 따라 섹션을 더하거나 빼도 되지만, **목적 / 환경 / 단계 / 검증 / 참고자료**는 거의 항상 있다.

다음은 `akbun-hands-on`이 생성해야 할 뼈대의 예시 구조다.

````markdown
# 제목 (무엇을 하는지 한 줄로)

## 목적

- 이 실습에서 달성할 것을 한 줄로

<!-- akbun-writing: 왜 이 실습을 했는지 배경 추가 -->

## 환경

| 항목 | 값 |
|---|---|
| OS | macOS 15 |
| 도구 버전 | terraform 1.9.0 |
| 클라우드 | AWS ap-northeast-2 |

## 사전 준비

- 준비 사항 1
- 준비 사항 2

## 단계

1. 첫 단계 설명 한 줄

   ```sh
   command
   ```

2. 두 번째 단계 설명 한 줄

   ```sh
   command
   ```

<!-- akbun-writing: 중간에 실패했던 경험이 있으면 여기 추가 -->

## 검증

검증 명령어와 기대 결과.

```sh
verify-command
```

기대 결과:

- 출력 1
- 출력 2

<!-- akbun-writing: 검증 중 만난 예상 외 결과가 있으면 추가 -->

## 참고자료

- 공식 문서: https://...
- 관련 repo: https://github.com/choisungwook/...
````

## 2단계의 일은 2단계에 맡긴다

뼈대 단계에서 **하지 말아야 할 것들**이 있다. 이건 경직된 금지 목록이 아니라 **역할 분리**다. 각본이 감독의 일까지 다 해버리면 영화를 만들 여지가 없어진다.

- **문단으로 서술하지 않는다** — 긴 문단은 서사가 들어올 자리다. 서사는 2단계에서 붙는다. 뼈대는 bullet과 번호 목록으로 끝낸다.
- **"저는/제가" 같은 1인칭 서사를 쓰지 않는다** — 1인칭은 2단계의 목소리다. 뼈대는 명령어와 결과만 담는다.
- **감정 표현을 넣지 않는다** — "식은땀", "운이 좋게" 같은 표현은 2단계에서 사람 맥락을 덧붙일 때 쓴다.
- **시간/사건 묘사를 넣지 않는다** — "어느 날", "추석이 끝나고" 같은 도입부는 2단계의 몫이다.
- **검증되지 않은 명령어를 쓰지 않는다** — 이건 역할 분리와 무관한 뼈대의 근본 원칙이다. 재현 가능성이 무너지면 2단계가 고칠 수 없다.
- **4단계 이상 nested 구조를 만들지 않는다** — 깊은 계층은 흐름을 끊는다. 복잡하면 파일을 나누고 `README.md`에 인덱스를 둔다.

## 작성 규칙

- 본문은 한국어로 작성한다. 명령어·도구명·경로·URL은 영어 그대로.
- 모든 코드 블록 앞에 한 줄 설명을 붙인다 (프로젝트 markdown 규칙).
- 모든 코드 블록에 언어 태그를 명시한다 (```sh,```yaml, ```hcl,```json).
- 한 파일에는 한 가지 실습만 담는다.
- 실습이 여러 단계로 쪼개지면 디렉터리를 나누고 `README.md`에 인덱스 테이블을 둔다 (프로젝트 kubernetes 규칙과 동일한 원칙).
- 단계의 명령어는 복사 붙여넣으면 그대로 동작해야 한다.
- Kubernetes manifest 예제가 포함되면 `manifests/` 디렉터리에 배치하고 `apiVersion`, `kind`, `metadata`, `spec` 순서를 따른다.

## Bad vs Good 예시

같은 주제("mysql docker 컨테이너에 sakila 샘플 로드")로 나쁜 뼈대와 좋은 뼈대를 대조한다.

### 나쁜 뼈대 (서사가 섞임)

아래는 akbun-hands-on이 **생성하지 말아야 할** 예시다.

````markdown
# MySQL docker에 sakila 로드

어느 날 MySQL 샘플 데이터가 필요해서 sakila를 찾아봤습니다.
저는 docker로 MySQL을 실행하는 게 편하다고 생각했습니다.
운이 좋게도 공식 이미지가 있어서 금방 시작할 수 있었습니다.

```sh
docker run -d mysql:8
```

잘 돌아갔습니다.
````

이 뼈대가 나쁜 이유:

- "어느 날", "저는", "운이 좋게" 같은 서사가 1단계에 미리 들어가 있다. 2단계가 덧붙일 자리가 없다.
- 명령어가 불완전하다 (`-e MYSQL_ROOT_PASSWORD`, 포트 매핑, 이미지 버전 pin 없음).
- 검증 단계가 없다. 재현 가능성이 무너진다.
- 목적/환경 섹션이 없다.

### 좋은 뼈대 (역할이 분리됨)

아래는 akbun-hands-on이 **생성해야 할** 예시다.

````markdown
# MySQL docker container에 sakila sample data 로드

## 목적

- MySQL docker container를 띄우고 sakila sample database를 로드한다

<!-- akbun-writing: 왜 sakila가 필요했는지 배경 추가 -->

## 환경

| 항목 | 값 |
|---|---|
| OS | macOS 15 |
| Docker | 27.3.1 |
| MySQL image | mysql:8.0.40 |

## 단계

1. MySQL container 실행

   ```sh
   docker run -d \
     --name mysql-sakila \
     -e MYSQL_ROOT_PASSWORD=rootpw \
     -p 3306:3306 \
     mysql:8.0.40
   ```

2. sakila dump 다운로드 및 압축 해제

   ```sh
   curl -LO https://downloads.mysql.com/docs/sakila-db.tar.gz
   tar -xzf sakila-db.tar.gz
   ```

3. dump를 container에 복사 후 import

   ```sh
   docker cp sakila-db/sakila-schema.sql mysql-sakila:/tmp/
   docker cp sakila-db/sakila-data.sql mysql-sakila:/tmp/
   docker exec -i mysql-sakila mysql -uroot -prootpw -e "source /tmp/sakila-schema.sql"
   docker exec -i mysql-sakila mysql -uroot -prootpw -e "source /tmp/sakila-data.sql"
   ```

<!-- akbun-writing: 중간에 실패했던 경험이 있으면 여기 추가 -->

## 검증

`sakila` database의 테이블이 로드되었는지 확인한다.

```sh
docker exec -i mysql-sakila mysql -uroot -prootpw -e "USE sakila; SHOW TABLES;"
```

기대 결과:

- `actor`, `film`, `customer` 등 16개 테이블 출력

## 참고자료

- MySQL sakila 공식 문서: https://dev.mysql.com/doc/sakila/en/
- sakila-db 다운로드: https://downloads.mysql.com/docs/sakila-db.tar.gz
````

이 뼈대가 좋은 이유:

- 목적 / 환경 / 단계 / 검증 / 참고자료 구조가 명확하다.
- 명령어가 완결되어 복사 붙여넣으면 동작한다.
- `<!-- akbun-writing: ... -->` hook이 2단계에서 덧붙일 자리를 남긴다.
- 1인칭 서사와 감정 표현이 없다 — 2단계가 붙일 여백이 그대로 남아 있다.

## 2단계로 넘기기

뼈대가 완성되면 사용자에게 다음을 알린다.

> 뼈대 완료. akbun-writing skill로 넘겨서 경험과 깨달음을 덧붙이시겠어요? 뼈대 안에 `<!-- akbun-writing: ... -->` 주석으로 확장 포인트를 표시해뒀습니다.

사용자가 동의하면 akbun-writing skill을 이어서 호출한다. 2단계에서는 주석 위치에 1인칭 서사, 시간 마커, 사람 맥락, 감정 표현을 덧붙이고 주석 자체는 지운다. 글의 첫 섹션(목적)과 마지막 섹션(참고자료) 사이에 배경 섹션이 새로 끼어들 수 있다.

## 관련 skill

- **akbun-writing** — 이 skill의 2단계. 뼈대 위에 서사와 깨달음을 덧붙인다.
- **akbun-blog-post-template** — 최종 블로그 글의 목차/구조 템플릿을 제공한다. 2단계 확장 시 참고.
- **akbun-style-reviewer** (agent) — 2단계 결과물이 akbun 스타일을 따르는지 검토한다.
