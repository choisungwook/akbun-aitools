---
name: akbun-repo-relation-sketch
description: >
  둘 이상의 git repo를 입력받아 repo 사이의 연관관계를 손그림(스케치) 스타일 다이어그램으로 시각화하고,
  이미지 생성 AI용 영어 프롬프트(.md)와 렌더링한 .svg를 ~/Downloads에 만든다.
  사용자가 여러 git repo의 관계도/연관도/관계 다이어그램을 그려 달라고 명시적으로 요청할 때만 사용한다.
---

# 여러 git repo 연관관계 손그림 시각화

여러 git repo를 입력받아, repo 사이의 연관관계를 첨부 이미지 같은 손그림 스타일 다이어그램으로 만든다. 각 repo는 박스가 되고, repo 사이의 관계는 핵심 키워드를 라벨로 단 화살표로 그린다.

## 핵심 원칙

- repo는 노드(박스), 관계는 라벨이 달린 방향 화살표다. 라벨은 그 관계의 핵심 키워드 한두 단어다(예: `imports`, `deploys`, `calls`, `shared auth`).
- 다이어그램 안의 모든 글씨는 영어로 쓴다. 사용자와의 대화는 한국어로 한다.
- 산출물은 `~/Downloads`에 바로 흩어두지 않는다. `~/Downloads/<name>/` 디렉터리를 먼저 만들고 두 산출물을 그 안에 모은다.
  1. `~/Downloads/<name>/<name>-image-prompt.md` — 다른 이미지 생성 AI가 같은 그림을 그리도록 지시하는 영어 프롬프트.
  2. `~/Downloads/<name>/<name>.svg` — `scripts/render_sketch_svg.py`로 렌더링한 손그림 스타일 SVG.
- SVG는 직접 손으로 작성하지 않는다. 반드시 relation model(JSON)을 만든 뒤 `scripts/render_sketch_svg.py`에 넘겨서 만든다. 그래야 레이아웃, 손그림 효과, 색이 매번 일관된다.
- 의미 있는 다이어그램을 만들 수 있으면 긴 인터뷰로 멈추지 말고 산출물 생성까지 진행한다.

## 워크플로

### 1. repo 목록과 키워드/관계 입력 받기

사용자에게 분석할 repo들의 경로(또는 git URL)를 받는다. 사용자가 키워드나 관계를 함께 주면 그대로 쓴다. 입력 형태는 둘 중 하나다.

- **사용자가 관계를 직접 줌**: `A --(imports)--> B` 처럼 repo 쌍과 라벨을 주면 그대로 model에 넣는다. 자동 추출을 건너뛴다.
- **사용자가 repo만 줌**: 다음 단계에서 자동 추출한다.

### 2. 관계 자동 추출 (사용자가 관계를 주지 않은 경우)

각 repo에서 핵심 키워드와 repo 사이 관계를 추론한다. 아래 신호를 본다. 추측이 아니라 파일에 있는 근거로만 판단한다.

- **핵심 키워드**: `README`의 첫 단락과 제목, manifest 파일(`package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, `pom.xml` 등), 최상위 디렉터리 이름, `.git/config`의 remote 이름. repo마다 2~4개의 키워드를 뽑는다(언어/역할/도메인).
- **repo 사이 관계와 그 라벨**:
  - 의존성: 한 repo의 manifest가 다른 repo의 패키지/모듈명을 참조하면 `imports` / `depends on`.
  - 호출: README나 코드에서 다른 repo의 서비스/API를 호출하면 `calls`.
  - 배포: infra/IaC repo가 다른 repo를 배포 대상으로 두면 `deploys`.
  - 문서 참조: 한 repo의 README가 다른 repo를 명시적으로 링크/언급하면 `references`.
  - 공유: 공통 라이브러리/스키마/인증을 같이 쓰면 `shared <keyword>`.
- 근거가 약한 관계는 만들지 않는다. 라벨은 그 관계를 한두 단어로 압축한 영어 키워드여야 한다.

여러 repo를 빠르게 훑어야 하면 `Explore` 서브에이전트나 병렬 탐색을 써도 된다.

### 3. relation model 확인받기

추출한 결과를 사용자가 한눈에 검토할 수 있게 노드와 화살표를 짧게 요약해서 보여준다. 예: `platform-api --(imports)--> platform-core`. 사용자가 라벨을 고치거나 관계를 추가/삭제하면 반영한다. 사용자가 관계를 직접 준 경우에는 이 확인을 생략하고 바로 진행한다.

확정한 model을 JSON으로 만든다. 스키마는 `assets/example-relation.json`과 같다.

```json
{
  "name": "platform",
  "title": "How the platform repos relate",
  "nodes": [
    {"id": "core", "label": "platform-core", "keywords": ["go", "library"]},
    {"id": "api", "label": "platform-api", "keywords": ["rest", "grpc"]}
  ],
  "edges": [
    {"from": "api", "to": "core", "label": "imports", "direction": "forward", "emphasize": true}
  ]
}
```

필드 규칙:

- `name`은 파일명에 쓰인다(소문자, 하이픈). `title`은 그림 상단 제목이며 영어로 쓴다.
- `edges[].label`은 그 관계의 핵심 키워드(영어). `direction`은 `forward`(기본), `back`, `both` 중 하나.
- 가장 중요한 관계 하나둘에 `"emphasize": true`를 주면 주황색 굵은 화살표로 강조된다(첨부 이미지의 강조 화살표처럼).

### 4. 출력 디렉터리 만들기

먼저 산출물을 모을 디렉터리를 만든다. `<name>`은 model의 `name`(소문자, 하이픈)을 쓴다.

```bash
mkdir -p ~/Downloads/<name>
```

### 5. 이미지 생성 AI용 영어 프롬프트 만들기

`references/image-prompt-template.md`를 읽고, 확정한 model을 그 템플릿에 채워 `~/Downloads/<name>/<name>-image-prompt.md`로 저장한다. 이 프롬프트는 nano-banana, DALL-E 같은 이미지 생성 AI가 같은 손그림 다이어그램을 그리도록 영어로 정확히 묘사한다. 노드 박스 하나하나, 화살표 하나하나와 그 라벨을 빠짐없이 적는다.

### 6. SVG 렌더링하기

확정한 JSON을 임시 파일로 저장한 뒤 렌더러를 실행한다. 출력 경로를 생략하면 `~/Downloads/<name>/<name>.svg`에 만들어진다(디렉터리는 렌더러가 없으면 자동 생성한다).

```bash
python3 scripts/render_sketch_svg.py /tmp/<name>-relation.json
```

### 7. 결과 보고

만든 디렉터리와 두 파일의 경로를 사용자에게 알려준다.

- `~/Downloads/<name>/<name>-image-prompt.md`
- `~/Downloads/<name>/<name>.svg`

## 손그림 스타일

렌더러가 자동으로 적용하는 스타일이라 직접 SVG를 만들 필요는 없지만, 이미지 프롬프트를 쓸 때 같은 분위기로 묘사하기 위해 알아둔다. 격자 없는 따뜻한 종이 배경, 손글씨 느낌 폰트, 약간 떨리는 손그림 선과 화살표, 라벨 뒤의 형광펜 하이라이트, 강조 화살표는 따뜻한 주황색. 자세한 규칙과 색은 `references/image-prompt-template.md`에 있다.
