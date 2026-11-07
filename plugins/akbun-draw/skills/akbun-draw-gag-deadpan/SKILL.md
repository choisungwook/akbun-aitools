---
name: akbun-draw-gag-deadpan
description: 다정한 에세이 같은 한국어 제목 한 줄과, 그 제목 뒤의 웃긴 속사정을 보여 주는 두 캐릭터 개그 한 컷(한쪽은 모른 채 사소한 버릇을 계속하고, 다른 쪽은 바로 뒤에서 무표정으로 과장된 동작에 얼어붙음)을 akbun-draw-illust-wash 그림체로 만드는 이미지 생성 프롬프트 skill deadpan. 모델은 gag spec(JSON)만 쓰고, 스크립트가 연출·개그·그림체 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-gag-deadpan

## 목적

주제 하나를 "제목 + 개그 한 컷"으로 만든다. 제목은 다정하고 점잖은 한국어 문장이고, 그림은 그 문장이 감추고 있던 웃긴 사정을 보여 준다. 제목과 그림이 어긋나는 데서 웃음이 난다. 제목은 그림 안에 쓰지 않고 영상·글 제목으로 그림 밖에 둔다.

그림체(선·칠·색·캐릭터)는 [akbun-draw-illust-wash](../akbun-draw-illust-wash/SKILL.md)의 라이브러리를 그대로 쓴다. 이 skill이 더하는 것은 연출(두 캐릭터의 관계, 얼굴은 무표정·몸만 과장, 일이 벌어지기 직전의 정지)과 개그 유형이다. 무엇을 소재로 할지(상황·사물·장소)는 입력에 맞춰 정한다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 연출(한 컷·두 캐릭터·무표정·정지) | [references/staging.jsonl](references/staging.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다 |
| 개그 유형 | [references/gags.jsonl](references/gags.jsonl) | 제목의 반전이 가장 잘 보이는 `id` 하나. 여러 장이면 같은 유형을 연달아 2장 넘게 쓰지 않는다 |
| 그림체·색·캐릭터 | akbun-draw-illust-wash의 [style](../akbun-draw-illust-wash/references/style.jsonl)·[palettes](../akbun-draw-illust-wash/references/palettes.jsonl)·[characters](../akbun-draw-illust-wash/references/characters.jsonl) | 색은 기본 `paper-wash`, 장소가 다른 줄의 `use`와 맞을 때만 그 `id`. 캐릭터는 서로 다른 `id` 둘 |
| spec·제목 예시 | [references/example/](references/example/) | 형식만 본다. 제목·소재를 그대로 쓰지 않는다 |

라이브러리에 없는 개그 유형이 필요하면 spec에 지어내지 말고, gags.jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. 제목과 속사정 정하기

입력 주제에서 두 가지를 정한다.

- 제목: 서로 배려·인내·관계에 대한 다정하고 담담한 한국어 문장 하나. 상황(누가 무엇을 하는지)은 말해도 되지만 그림 속 반전(참는 쪽의 동작·쥔 사물·속마음)은 말하지 않는다. 웃음은 그림이 맡는다.
- 속사정: 그 다정함 뒤에서 실제로 벌어지는 일. 버릇을 가진 쪽이 모르는 쪽이고, 그 버릇 때문에 기다리거나 듣거나 빌려주는 쪽이 참는 쪽이다. 실제로 해를 끼치는 장면은 고르지 않는다.

그림마다 `<id>`(영어 소문자·하이픈 짧은 이름)를 붙인다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `deadpan-output/<작업명>/`.

| 키 | 값 |
|---|---|
| `title` | 제목. 한글이 들어간 8~30자(공백·문장부호 포함, 경계 포함) |
| `gag` | gags.jsonl의 `id` |
| `palette` | illust-wash palettes.jsonl의 `id` |
| `prop` | gags.jsonl 줄의 `prop`이 `true`면 참는 쪽이 쥐는 사물, 영어 2단어 이상. `overhead-hold`·`mutual-hold`는 크기·무게가 어이없는 생활 사물(예: 자동차 바퀴만 한 프라이팬), `white-knuckle`은 손에 든 평범한 사물로 휘거나 금 갈 수 있는 것. `false`면 `""` |
| `endurer` | 참는 쪽 `{"id", "action"}`. `action`은 영어 3단어 이상으로, 무엇을 얼마나 참아 왔는지 |
| `unaware` | 모르는 쪽 `{"id", "action"}`. `action`은 영어 3단어 이상으로, 태연히 계속하는 사소한 버릇. `endurer`와 다른 `id` |
| `setting` | 어디인지 영어 한 구절. 의미 없으면 `""`(흰 종이만) |

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/gag_prompt.py build deadpan-output/<작업명>/01_<id>.json -o deadpan-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치와 illust-wash와 같은 영어·금지 낱말 검사를 본다.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/gag_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 만든다. 명령은 illust-wash의 4단계와 같고, 폴더만 `deadpan-output/<작업명>`이다.

여러 장이면 결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다.

- 참는 쪽 얼굴이 무표정이고(땀방울 하나 정도), 몸 동작만 과장돼 있다.
- 모르는 쪽이 참는 쪽을 보지 않는다(`mutual-hold`는 둘이 마주 보되 숨긴 사물을 보지 않는다).
- 아무도 맞거나 다치지 않았다(`white-knuckle`의 쥔 사물이 휘거나 금 간 것은 된다).
- 흰 종이 여백이 넓고, 글자·개·고양이·흰 털 뭉치 동물·사람이 없으며, 알려진 캐릭터와 닮지 않았다.

## 결과 보고

그림마다 제목, spec 파일, 프롬프트 파일, 채점 점수, 고른 개그 유형·팔레트·캐릭터를 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다.

## 하지 말 것

- 제목을 그림 안에 쓰거나, 제목에서 반전을 미리 말하는 것.
- 실제로 때리거나 다치는 순간, 피·무기를 그리는 것.
- 프롬프트 문장을 손으로 고치는 것. 바꿀 것이 있으면 jsonl을 고친다.
