---
name: akbun-draw-moss
description: 굵고 매끈한 올리브 잉크 선, 그늘 없는 단색 면, 무늬 없는 세이지 단색 배경, 화면에 딱 하나만 칠하는 이끼 초록 강조색으로 동물·식물·사물의 조용하고 엉뚱한 한 순간을 그리는 이미지 생성 프롬프트 스타일 moss. 모델은 spec(JSON)만 쓰고, 스크립트가 references의 스타일·팔레트·캔버스 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-moss

## 목적

아무 소재를 moss 그림체로 그리는 영어 이미지 생성 프롬프트를 만든다. 이 skill이 고정하는 것은 선·채색·색 수·강조색 쓰는 법·배경 무늬·얼굴 그리는 법이고, 무엇을 그릴지(소재·행동·소품)는 입력에 맞춰 정한다.

모델은 프롬프트 문장을 직접 쓰지 않는다. spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다. 그래서 몇 장을 만들어도 같은 그림체가 나온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체(선·채색·강조·배경·얼굴·소재·질감·분위기) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 spec이 이 규칙과 어긋나지 않게만 한다 |
| 색 | [references/palettes.jsonl](references/palettes.jsonl) | 사용자가 정하지 않으면 `moss`. `brick`·`pond`의 `use`에 적힌 주제 낱말이 입력에 하나라도 있으면 그 `id`, 둘 다 있으면 `moss` |
| 캔버스 | [references/canvases.jsonl](references/canvases.jsonl) | 사용자가 비율(정사각형·세로·가로)을 말하면 그 비율의 `id`, 쓰임만 말하면 그 `use`의 `id`, 아무 말이 없으면 `wide` |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 소재를 그대로 쓰지 않는다 |

라이브러리에 없는 팔레트·캔버스가 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. spec 쓰기

입력에서 한 순간을 정한다(여러 장이면 장마다). 사람이 나오는 이야기면 사람 역할을 동물·식물·사물이 맡는다. 출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `moss-output/<작업명>/`, 파일 이름은 `01_<id>.json`(`<id>`는 영어 소문자·하이픈).

| 키 | 값 |
|---|---|
| `palette`, `canvas` | jsonl의 `id` |
| `moment` | 어떤 순간인지 영어 6~30단어(공백으로 나눈 단어 수, a·the도 세고, 하이픈으로 이은 말은 한 단어, 경계 포함). 그림에 글자·숫자가 없으므로 시각·소리는 시계 바늘·달·진동 선 같은 그림으로 쓴다 |
| `subjects` | 1~3개(경계 포함). `[{"what": 무엇인지 영어 2단어 이상, "doing": 무엇을 하는지 영어 2단어 이상}]`. 사물에 얼굴을 붙일지는 `what`에 적는다. 생김새는 소재마다 다르게 정하고, 배치·위치는 쓰지 않는다 |
| `props` | 소재 곁의 사물 영어 구절 0~4개, 중복 없이 |
| `accent_on` | 강조색을 칠할 것 하나. `subjects`의 `what`이나 `props` 한 항목 안에 들어 있는 말(대소문자 무시)이어야 한다. 소재가 들고 있는 소품이어도 된다 |

### 2. 프롬프트 조립

spec을 채점하고 프롬프트 파일을 쓰는 명령이다. `<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

```bash
uv run --python 3.12 python -I <skill>/scripts/moss_prompt.py build moss-output/<작업명>/01_<id>.json -o moss-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 이것도 본다: 모델이 쓴 글은 영어(ASCII)만, 사람을 뜻하는 낱말(human·person·people·man·woman·boy·girl·child 등)과 스타일을 깨는 낱말(3d·photorealistic·realistic·anime·gradient·neon·shading·glossy·watercolor) 없음.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/moss_prompt.py --selftest
```

### 3. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 프롬프트 파일 전문을 그대로 넣어 만든다.

codex CLI를 쓸 때, 프롬프트 파일이 있는 폴더에서 내장 이미지 생성으로 PNG를 만드는 명령이다. 모델은 사용자 설정의 기본값을 쓴다. `<비율>`은 캔버스의 비율(`wide` 16:9, `square`·`badge` 1:1, `portrait` 4:5)이다.

```bash
cd moss-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read 01_<id>.txt. Use your built-in image generation tool with that file's full text as the prompt, exactly, aspect <비율>. Save the result as 01_<id>.png here. Reply with the path only." < /dev/null
```

`< /dev/null`이 없으면 codex가 입력을 기다리며 멈춘다. 여러 장은 장마다 따로 돌린다.

결과마다(여러 장이면 한 장으로 붙여 한 번만 보고) 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다.

- 선이 순검정이 아니라 팔레트 ink 색이고, 굵기가 고르며 흔들리지 않는다.
- 면에 그늘·그라데이션이 없다.
- 강조색이 `accent_on` 하나에만 있다.
- 배경이 종이색 한 가지 단색이고 구름·무늬가 없다.
- 사람이 없고, 글자가 없다.
- 알려진 캐릭터·마스코트와 닮지 않았다. 닮았으면 `subjects`의 생김새를 바꿔 build부터 다시 하고, 무엇을 바꿨는지 결과 보고에 적는다.

## 결과 보고

장마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 팔레트·캔버스를 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다. 프롬프트는 한 개의 `text` 코드블록으로도 보여 준다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 사람을 그리는 것, 알려진 캐릭터를 따라 하는 것.
- 강조색을 둘 이상에 칠하는 것.
