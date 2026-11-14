---
name: akbun-draw-diagram-haru
description: 흰 화면 위 거의 검정 잉크 한 줄 외곽선의 빈 사각형·원통과 그것을 감싸는 점선 경계, 둥근 손글씨 이름, 속 빈 삼각형 머리의 강조색 화살표(곡선 실선, 점선), 화살표 옆 작은 강조색 이름으로 시스템 구조·흐름을 아이콘 없이 화면 가운데에 그리는 손그림 다이어그램 이미지 생성 프롬프트 스타일 haru. 모델은 다이어그램 spec(JSON)만 쓰고, 스크립트가 references의 스타일·팔레트·배치·도형·화살표 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-diagram-haru

## 목적

시스템 구조·요청 흐름·전후 비교를 haru 그림체로 그리는 16:9 영어 이미지 생성 프롬프트를 만든다. 이미지 생성 도구에 그대로 붙여 넣는다. 이 skill이 고정하는 것은 선·채움·글씨·화살표 모양·색·여백·가운데 정렬이고, 무엇을 몇 개 어떻게 잇는지(도형·화살표·배치)는 입력에 맞춰 정한다.

모델은 프롬프트 문장을 직접 쓰지 않는다. spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다. 그래서 몇 장을 만들어도 같은 그림체가 나온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체(선·채움·글씨·화살표 머리·여백·가운데 정렬·금지 요소) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다 |
| 색 | [references/palettes.jsonl](references/palettes.jsonl) | 기본 `ink-blue`. 그림 전체의 주제가 각 줄의 `use`와 맞을 때만 다른 `id`(낱말 하나가 겹친다고 바꾸지 않는다) |
| 배치 | [references/layouts.jsonl](references/layouts.jsonl) | 내용이 가장 잘 읽히는 `id` 하나. 중심 하나에 여럿이 붙으면 `hub`, 순서대로 흐르면 `row`·`column`, 위→아래 계층이면 `layers`, 왼쪽→오른쪽 단계(mermaid `flowchart LR`)면 `columns`, 되돌아오면 `loop`, 전후·A/B면 `split`. 여러 장이면 같은 배치를 연달아 3장 넘게 쓰지 않는다 |
| 도형 | [references/shapes.jsonl](references/shapes.jsonl) | 각 줄의 `ko` 설명대로 역할에 맞는 `id`. 이름이 무엇인지는 `label`이 말하고 도형은 역할만 나타낸다 |
| 경계 | [references/groups.jsonl](references/groups.jsonl) | 고르지 않는다. spec에 `groups`가 있으면 스크립트가 넣는다 |
| 화살표 | [references/edges.jsonl](references/edges.jsonl) | 요청·호출은 `call`, 응답·비동기 이벤트·구독·끌어오기는 `sync`, 같은 두 도형 사이 양방향 동기화는 `sync-pair`. 화살표는 모두 강조색이고, 흐름이 어디서 시작하는지는 선 색이 아니라 `step` 1로 나타낸다 |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다(`03`이 `groups`·`columns` 예시). 소재를 그대로 쓰지 않는다 |

라이브러리에 없는 도형·화살표·팔레트가 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. 내용 줄이기

입력에서 도형이 될 개체(서비스·저장소·사용자)와 그 사이 관계, 개체를 감싸는 경계(VPC·subnet·호스트·프로세스)를 뽑는다. 입력이 다이어그램(mermaid 등)이면 노드는 도형, subgraph는 `groups`, edge는 화살표로 1:1 옮기고, 합치거나 뺀 노드·edge는 결과 보고에 적는다. 입력 설명이 실제 동작과 다르면(예: 응답이 중간 서버를 건너뜀) 실제 동작대로 그리고 결과 보고에 적는다. 화살표·글자·경계는 개체로 세지 않는다. 배치가 허용하는 수보다 많으면 그림을 나누고, 나눌 수 없을 때만 합친다. 그림마다 `<id>`(영어 소문자·하이픈 짧은 이름, 예: `login-flow`)를 붙인다.

### 2. spec 쓰기

위 표대로 고르고 spec JSON을 쓴다. 아래 표에 없는 키(예: `icon`)를 쓰면 감점된다. 출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `haru-output/<작업명>/`.

| 키 | 값 |
|---|---|
| `palette`, `layout` | jsonl의 `id` |
| `subject` | 무엇을 설명하는 그림인지 영어 6~30단어(공백으로 나눈 단어 수, 경계 포함) |
| `nodes` | `[{"id", "label", "shape", "half"?, "tier"?, "col"?}]`. 개수는 배치의 `nodes` 범위(경계 포함), `groups`가 있으면 상한 +3. `id`는 spec 안에서만 쓰는 영어 짧은 이름, 중복 없이. `label`은 1~2줄 목록, 줄마다 1~12자(공백 포함). `half`는 `split`일 때만 `left`·`right`로, `tier`는 `layers`일 때만 1~4(1이 맨 위, 2개 층 이상), `col`은 `columns`일 때만 1~4(1이 맨 왼쪽, 2개 열 이상)로 모든 도형에 붙이고, 다른 배치에서는 쓰지 않는다. 두 판에 같은 이름 도형이 있어도 된다(화살표는 도형 번호로 가리킨다) |
| `groups` | `[{"id", "label", "members"}]` 0~4개. 점선 경계 사각형이 `members`(도형 `id` 또는 다른 묶음 `id`)를 감싼다. `id`는 도형 `id`와 겹치지 않게, `label`은 1줄 목록 1~20자. 멤버는 한 묶음에만 속하고, 순환 없이 3단계까지 중첩된다 |
| `edges` | `[{"from", "to", "kind", "label"?, "step"?}]` 1~12개. `from`·`to`는 서로 다른 도형·묶음 `id`(묶음이면 경계선에서 나가거나 들어온다). `label`은 1~14자, 그림 전체에서 5개까지이므로 화살표만 보고 뜻을 알 수 없는 곳에 먼저 붙인다. `step`은 화살표가 순서대로 일어나는 흐름일 때 그 순서대로 1부터 빠짐없이 붙이는 정수로, 선 가운데에 강조색 원 안 강조색 번호로 그려진다. 순서와 무관한 화살표(저장소 동기화 등)에는 붙이지 않고, 2개 미만이면 쓰지 않는다. 모든 도형에 화살표가 하나 이상 닿아야 한다(도형이 속한 묶음이나 그 바깥 묶음에 닿아도 된다) |
| `notes` | `[{"node", "text"}]` 0~2개. 도형 바로 아래 작은 강조색 메모, 1~32자. 이름과 화살표로 안 보이는 사실(담는 것·수치·조건)이 있을 때만 |

글자(`label`·`text`)는 영어 또는 한글만, 큰따옴표 없이 쓴다. 이미지 생성 모델은 짧은 영어를 가장 정확히 쓰므로 제품·기술 이름은 영어로 두고(12자가 넘으면 두 줄로 나누거나 줄임말), 한글은 메모처럼 꼭 필요한 곳에만 쓴다. 실제 제품은 로고·아이콘 없이 이름 글자로만 나타낸다.

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/haru_prompt.py build haru-output/<작업명>/01_<id>.json -o haru-output/<작업명>/01_<id>.txt
```

프롬프트를 쓰지 않고 채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 금지 낱말(logo·trademark·mascot·3d·isometric·photorealistic·realistic·gradient·neon·shadow)이 모델이 쓴 글에 없는지도 본다.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/haru_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 프롬프트 파일 전문을 그대로 넣어 만든다.

codex CLI를 쓸 때, 프롬프트 파일이 있는 폴더에서 내장 이미지 생성으로 PNG를 만드는 명령이다. 모델은 사용자 설정의 기본값을 쓴다.

```bash
cd haru-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read 01_<id>.txt. Use your built-in image generation tool with that file's full text as the prompt, exactly, landscape 16:9. Save the result as 01_<id>.png here. Reply with the path only." < /dev/null
```

`< /dev/null`이 없으면 codex가 입력을 기다리며 멈춘다. 여러 장은 장마다 이 명령을 따로 돌린다.

이미지 모델은 프롬프트만으로 가운데 정렬을 지키지 못하므로, 생성한 장마다 그림 덩어리를 캔버스 가운데로 옮긴다(가운데가 어긋났다고 다시 생성하지 않는다). 아래 명령은 PNG를 제자리에서 고치고(`-o`로 다른 파일), 전후 왼·오른·위·아래 여백과 좌우·상하 차이를 출력한다.

```bash
uv run --python 3.12 --with pillow python -I <skill>/scripts/haru_prompt.py center haru-output/<작업명>/01_<id>.png
```

center를 마친 뒤, 여러 장이면 결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다. 글자가 두 번 연속 틀리면 그 `label`을 더 짧은 영어로 바꿔 build부터 다시 한다.

- 도형 안이 비어 있고(흰색) 색 면·그림자·3D가 없다.
- 화살표 머리가 속 빈 삼각형이고, 선과 머리가 모두 강조색이다. 검정 화살표가 없다.
- 아이콘·그림 문자가 없다.
- center 뒤에도 그림이 한쪽으로 치우쳐 보이지 않는다. 치우쳐 보이면 가장자리 얼룩이 그림으로 잡힌 것이므로 다시 생성한다.
- `groups`가 있으면 경계가 멤버만 감싸고, 안쪽 경계가 바깥 경계 안에 있으며, 경계선이 도형을 가로지르지 않는다.
- spec에 없는 글자(제목·범례·설명)가 없고, 있는 글자의 철자와 `step` 번호가 맞다.
- 실제 제품 로고·마스코트·캐릭터와 닮은 그림이 없다.

## 결과 보고

그림마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 팔레트·배치, 원본에서 합치거나 뺀 노드·edge(없으면 "없음")를 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다. 프롬프트는 한 개의 `text` 코드블록으로도 보여 준다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 그림에 제목·범례·아이콘·장식 낙서·캐릭터·실제 제품 로고를 넣는 것.
