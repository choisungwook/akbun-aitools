---
name: akbun-draw-template-comedy
description: 사용자가 고른 akbun-draw 그림체를 그대로 쓰면서, 주제 하나를 다정한 한국어 제목 한 줄과 그 뒤 웃긴 속사정을 보여 주는 두 캐릭터 개그 한 컷(한쪽은 모른 채 사소한 버릇을 계속하고, 다른 쪽은 바로 뒤에서 무표정으로 과장된 동작에 얼어붙음)으로 만드는 개그 템플릿. 모델은 comedy spec(JSON)만 쓰고, 스크립트가 스타일 skill의 그림체 문장과 연출·개그 라이브러리로 영어 프롬프트를 조립·검사한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-template-comedy

## 목적

주제 하나를 "제목 + 개그 한 컷"으로 만든다. 제목은 다정하고 점잖은 한국어 문장이고, 그림은 그 문장이 감추고 있던 웃긴 사정을 보여 준다. 제목과 그림이 어긋나는 데서 웃음이 난다. 제목은 그림 안에 쓰지 않고 영상·글 제목으로 그림 밖에 둔다.

그림체는 새로 정하지 않고 사용자가 고른 akbun-draw 캐릭터 그림체 skill(예: [akbun-draw-wash](../akbun-draw-wash/SKILL.md), [akbun-draw-moss](../akbun-draw-moss/SKILL.md), [akbun-draw-bori](../akbun-draw-bori/SKILL.md), [akbun-draw-storybook-vintage](../akbun-draw-storybook-vintage/SKILL.md))의 것을 그대로 쓴다. 이 skill이 정하는 것은 연출(두 캐릭터의 관계, 얼굴은 무표정·몸만 과장, 일이 벌어지기 직전의 정지)과 개그 유형이다. 무엇을 소재로 할지(상황·사물·장소)는 입력에 맞춰 정한다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체 | 스타일 skill의 `references/style.jsonl`·`palettes.jsonl` | 사용자가 말한 스타일 skill. 캐릭터를 그리는 그림체만 쓴다(사진풍 sena·juno, 다이어그램·글자·모션 skill은 맞지 않는다). 말하지 않았으면 spec을 쓰기 전에 선택지 질문 도구로 묻는다. 여러 장이어도 그림체는 하나 |
| 연출(한 컷·두 캐릭터·무표정·정지) | [references/staging.jsonl](references/staging.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다 |
| 개그 유형 | [references/gags.jsonl](references/gags.jsonl) | 제목의 반전이 가장 잘 보이는 `id` 하나. 여러 장이면 같은 유형을 연달아 2장 넘게 쓰지 않는다 |
| spec·제목 예시 | [references/example/](references/example/) | 형식만 본다. 제목·소재를 그대로 쓰지 않는다. 예시 넷은 그림체가 모두 다르다 |

라이브러리에 없는 개그 유형이 필요하면 spec에 지어내지 말고, gags.jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. 제목과 속사정 정하기

입력 주제에서 두 가지를 정한다.

- 제목: 서로 배려·인내·관계에 대한 다정하고 담담한 한국어 문장 하나. 상황(누가 무엇을 하는지)은 말해도 되지만 그림 속 반전(참는 쪽의 동작·쥔 사물·속마음)은 말하지 않는다. 웃음은 그림이 맡는다.
- 속사정: 그 다정함 뒤에서 실제로 벌어지는 일. 버릇을 가진 쪽이 모르는 쪽이고, 그 버릇 때문에 기다리거나 듣거나 빌려주는 쪽이 참는 쪽이다. 실제로 해를 끼치는 장면은 고르지 않는다.

그림마다 `<id>`(영어 소문자·하이픈 짧은 이름)를 붙인다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `comedy-output/<작업명>/`. spec은 그 폴더의 `01_<id>.json` …이다.

| 키 | 값 |
|---|---|
| `title` | 제목. 한글이 들어간 8~30자(공백·문장부호 포함, 경계 포함) |
| `gag` | gags.jsonl의 `id` |
| `style` | 스타일 skill 이름(`akbun-draw-…`). 스크립트가 그 skill의 `references/style.jsonl`을 그림체 문장으로 넣는다 |
| `palette` | 스타일 skill `palettes.jsonl`의 `id`. 빼면 첫 줄(기본 팔레트) |
| `fill` | 팔레트가 채우지 못한 `{자리표시자}` 값. 검사가 "fill에 값 필요"로 알려 줄 때만 쓴다(예: bori의 `season`·`line`, moss의 `canvas`). 비율 자리표시자는 `"landscape 16:9"`를 쓴다. 스크립트가 비율 문구를 지우고 FORMAT 줄 하나만 남긴다 |
| `style_text` | 스타일 skill에 `references/style.jsonl`이 없을 때만. 그 skill의 그림체·선·색·질감 규칙을 영어 10단어 이상으로 옮긴다 |
| `prop` | gags.jsonl 줄의 `prop`이 `true`면 참는 쪽이 쥐는 사물, 영어 2단어 이상. `overhead-hold`·`mutual-hold`는 크기·무게가 어이없는 생활 사물(예: 자동차 바퀴만 한 프라이팬), `white-knuckle`은 손에 든 평범한 사물로 휘거나 금 갈 수 있는 것. `false`면 `""` |
| `endurer` | 참는 쪽 `{"look", "action"}`. `look`은 종·색을 담은 영어 4단어 이상. 옷을 입힐지, 어떤 종을 쓸지는 스타일 skill의 캐릭터 규칙(라이브러리가 있으면 그 안에서)을 따른다. `action`은 영어 3단어 이상으로, 무엇을 얼마나 참아 왔는지 |
| `unaware` | 모르는 쪽 `{"look", "action"}`. `action`은 태연히 계속하는 사소한 버릇. `endurer`와 다른 `look` |
| `setting` | 어디인지 영어 한 구절. 의미 없으면 `""`(배경은 스타일 skill이 정함) |

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 검사에 걸리면 프롬프트를 쓰지 않고 FAIL 이유를 보여 준다. spec을 고쳐 다시 돌린다.

spec을 검사하고 spec 옆에 같은 이름의 `.txt` 프롬프트를 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/comedy_prompt.py build comedy-output/<작업명>/01_<id>.json
```

검사만 하려면 `build` 대신 `check`를 쓴다. 검사는 위 표의 수치, 영어(ASCII), 폰트 낱말을 본다. 스타일 skill 고유의 금지 낱말 검사는 하지 않으므로 `look`·`action`은 그 skill의 금지 목록을 직접 지킨다. 그림체 문장은 [akbun-draw-template-cartoon](../akbun-draw-template-cartoon/SKILL.md)의 `cartoon_prompt.py`와 같은 함수로 읽는다.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/comedy_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 만든다. 명령은 template-cartoon의 4단계와 같고, 프롬프트 파일은 `01_<id>.txt`, 비율은 landscape 16:9다.

여러 장이면 결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다.

- 참는 쪽 얼굴이 무표정이고(땀방울 하나 정도), 몸 동작만 과장돼 있다.
- 모르는 쪽이 참는 쪽을 보지 않는다(`mutual-hold`는 둘이 마주 보되 숨긴 사물을 보지 않는다).
- 아무도 맞거나 다치지 않았다(`white-knuckle`의 쥔 사물이 휘거나 금 간 것은 된다).
- 고른 스타일 skill의 그림체이고, 두 캐릭터의 동작이 배경에 묻히지 않고, 글자가 없으며, 알려진 캐릭터와 닮지 않았다.

## 결과 보고

그림마다 제목, 스타일 skill·팔레트, spec 파일, 프롬프트 파일, 검사 결과, 고른 개그 유형을 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다.

## 하지 말 것

- 제목을 그림 안에 쓰거나, 제목에서 반전을 미리 말하는 것.
- 실제로 때리거나 다치는 순간, 피·무기를 그리는 것.
- 이 skill에서 그림체·색 규칙을 새로 만드는 것. 바꿀 것이 있으면 스타일 skill의 jsonl을 고친다.
- 프롬프트 문장을 손으로 고치는 것. 바꿀 것이 있으면 spec이나 jsonl을 고친다.
