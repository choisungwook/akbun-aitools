---
name: akbun-draw-illust-wash
description: 흰 종이 위 끊어 겹친 검정 펜 선과 성긴 빗금, 선 밖으로 살짝 번지는 채도 낮은 수채·색연필 칠, 화면 대부분을 칠하지 않은 종이로 남기는 여백, 사람처럼 행동하는 무표정 오리지널 동물로 한 장면을 그리는 이미지 생성 프롬프트 스타일 wash. 모델은 장면 spec(JSON)만 쓰고, 스크립트가 references의 스타일·팔레트·캐릭터 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-illust-wash

## 목적

아무 장면을 wash 그림체로 그리는 16:9 영어 이미지 생성 프롬프트를 만든다. 이미지 생성 도구에 그대로 붙여 넣는다. 이 skill이 고정하는 것은 선·칠·종이 여백·색·캐릭터 그림체와 담담한 분위기이고, 무엇을 그릴지(장면·소품·배치)는 입력에 맞춰 정한다.

모델은 프롬프트 문장을 직접 쓰지 않는다. spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다. 그래서 몇 장을 만들어도 같은 그림체가 나온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체(종이 여백·선·칠·캐릭터·분위기) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 장면이 이 규칙과 어긋나지 않게만 한다 |
| 색 | [references/palettes.jsonl](references/palettes.jsonl) | 기본 `paper-wash`. 장면의 시간·장소가 다른 줄의 `use`와 맞을 때만 그 `id` |
| 캐릭터 | [references/characters.jsonl](references/characters.jsonl) | 장면에 필요한 수(1~4, 경계 포함)만큼 `id`. 사람이 나오는 요청(손님·동료·승객)도 이 동물들이 그 역할을 맡는다. 여러 장이면 같은 캐릭터를 다시 써서 이어지게 한다 |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 소재를 그대로 쓰지 않는다 |

라이브러리에 없는 캐릭터·팔레트가 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다. 새 캐릭터는 개·고양이가 아니고, 흰 털 뭉치 모양이 아니며, 알려진 캐릭터와 닮지 않은 종으로만 더한다.

## 작업 흐름

### 1. 장면 정하기

입력에서 장면 하나를 정한다(여러 장이면 장면마다). 글만 있으면 가장 일상적인 한 순간을 고르고, 지어낸 장면임을 결과에 밝힌다. 장면마다 `<id>`(영어 소문자·하이픈 짧은 이름, 예: `rainy-bus-stop`)를 붙인다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `wash-output/<작업명>/`.

| 키 | 값 |
|---|---|
| `palette` | palettes.jsonl의 `id` |
| `scene` | 어떤 상황인지 영어 6~40단어(공백으로 나눈 수, 경계 포함). 캐릭터별 행동은 `action`에만 쓴다 |
| `setting` | 어디인지 영어 한 구절. 장소가 의미 없으면 `""`(흰 종이만) |
| `characters` | `[{"id", "action"}]` 1~4개, `id` 중복 없이. `action`은 영어 3단어 이상 |
| `props` | 장소·행동을 알아보게 하는 사물 영어 구절 0~6개, 중복 없이. 종이 여백이 이 스타일의 핵심이므로 장소를 채우지 않고 꼭 필요한 것만 |

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/wash_prompt.py build wash-output/<작업명>/01_<id>.json -o wash-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 모델이 쓴 글이 영어(ASCII)인지, 금지 낱말(dog·puppy·poodle·sheepdog·cat·kitten·human·person·people·man·woman·boy·girl·child·fluffy·white fur, 3d·photorealistic·realistic·anime·chibi·gradient·neon·vector·cel shading)이 없는지 본다. 사람 역할은 `passengers`·`customers`처럼 쓰지 않고 캐릭터로 맡긴다.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/wash_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 프롬프트 파일 전문을 그대로 넣어 만든다.

codex CLI를 쓸 때, 프롬프트 파일이 있는 폴더에서 내장 이미지 생성으로 PNG를 만드는 명령이다. 모델은 사용자 설정의 기본값을 쓴다.

```bash
cd wash-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read 01_<id>.txt. Use your built-in image generation tool with that file's full text as the prompt, exactly, landscape 16:9. Save the result as 01_<id>.png here. Reply with the path only." < /dev/null
```

`< /dev/null`이 없으면 codex가 입력을 기다리며 멈춘다. 여러 장은 장마다 이 명령을 따로 돌린다.

여러 장이면 결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다. 알려진 캐릭터·마스코트와 닮았으면 그 캐릭터 `id`를 다른 것으로 바꿔 build부터 다시 한다.

- 화면 대부분이 칠하지 않은 흰 종이이고, 배경 상자·전체 칠이 없다.
- 선이 매끈한 벡터 선이 아니라 끊어 겹친 펜 선이고, 칠이 투명하게 얼룩진다.
- 개·고양이·흰 털 뭉치 동물·사람이 없고, 알려진 캐릭터와 닮지 않았다.
- 그림 안에 글자가 없다.

## 결과 보고

장면마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 팔레트·캐릭터를 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다. 프롬프트는 한 개의 `text` 코드블록으로도 보여 준다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 개·고양이·흰 털 뭉치 동물·사람을 장면에 넣는 것, 알려진 캐릭터·영상 장면을 따라 하는 것.
- 그림 안에 글자(제목·자막·말풍선 글)를 넣는 것.
