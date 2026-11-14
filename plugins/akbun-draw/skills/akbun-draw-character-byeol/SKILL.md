---
name: akbun-draw-character-byeol
description: 사용자가 준 페르소나(외모 묘사·직업·나이·성격 등)를 오리지널 캐릭터로 바꿔, 배경 없는 흰 바탕(원하면 투명 PNG)에 그 인물 한 명만 가는 남보라 선·차가운 셀 그늘의 애니메이션풍으로 그리는 캐릭터 컷 프롬프트를 만든다. 페르소나가 없으면 지어낸다. 모델은 나이·체형·강조색은 라이브러리에서 고르고 머리·눈·옷·직업 소품·자세만 영어로 쓰는 캐릭터 spec(JSON)을 쓰고, 스크립트가 프롬프트를 조립·채점하고 결과 그림의 배경이 비었는지 숫자로 검사한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-character-byeol

## 목적

페르소나 한 줄을 캐릭터 한 명으로 바꾸고, 그 인물만 흰 바탕에 그린 캐릭터 컷의 영어 이미지 생성 프롬프트를 만든다. 배경·장소·빛 알갱이는 그리지 않는다. 이 skill이 고정하는 것은 그림체(선·채색·인물 문장)와 캐릭터 문장의 틀이고, 누구를 그릴지는 페르소나가 정한다. 한 번 만든 캐릭터 spec을 다시 쓰면 몇 장을 그려도 같은 인물로 보인다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 나이·성별·체형·강조색 | [references/traits.json](references/traits.json) | 페르소나에 맞는 키 하나씩. 말이 없으면 직업과 어울리는 쪽, 그래도 모르면 `young-adult`·`neutral`·`average`. 강조색은 옷의 주된 한 벌에 칠하는 따뜻한 색이다 |
| 선·채색·인물 | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다 |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 인물을 그대로 쓰지 않는다 |

## 작업 흐름

### 1. 페르소나 받기

사용자가 준 묘사·직업·나이·성격을 그대로 `persona`에 옮긴다. 페르소나가 없으면 직업 하나와 특징 하나를 지어 한 줄로 쓰고, 지어냈다고 결과에 밝힌다. 실존 인물·알려진 캐릭터를 그려 달라는 요청이면 그 인물의 이름·생김새를 쓰지 않고 직업·분위기만 받아 오리지널로 바꾼다.

### 2. 캐릭터 spec 쓰기

캐릭터마다 spec JSON 하나를 쓴다. 파일 이름은 `<name>.json`, 출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `character-output/<작업명>/`. 단어 수는 공백으로 나눈 수이고(하이픈으로 이은 말은 한 단어), 범위는 경계를 포함한다. `persona` 밖의 글은 모두 영어다.

| 키 | 값 |
|---|---|
| `name` | 영어 소문자·하이픈 2~20자. 그림에 글자로 넣지 않는다 |
| `persona` | 사용자 원문(아무 언어), 없으면 지어낸 한 줄. 프롬프트에 들어가지 않는다 |
| `age`·`gender`·`build`·`accent` | traits.json의 키 |
| `job` | 직업·역할 1~6단어 |
| `hair` | 머리 색·길이·모양 3~15단어, 관사 없이(`short wavy grey`). 프롬프트에 `hair <값>`으로 들어간다 |
| `eyes` | 눈 색 1~4단어 |
| `face` | 점·주근깨·안경·수염처럼 알아볼 표시 0~10단어. 없으면 `""` |
| `outfit` | 옷차림 5~30단어, `a`/`an`이나 복수 명사로 시작. 주된 한 벌을 맨 앞에 쓴다. 그 옷이 `accent` 색이라는 말은 스크립트가 덧붙이므로 색 이름은 써도 빼도 된다 |
| `item` | 직업이나 성격을 보여 주는 들고 다니는 물건 1~8단어, `a`/`an`으로 시작 |
| `aspect` | `portrait`(3:4)·`square`(1:1). 말이 없으면 `portrait` |
| `view` | `front`·`three-quarter`·`side`·`back`. 같은 캐릭터를 여러 장 그리면 같은 방향을 연달아 3장 넘게 쓰지 않는다 |
| `pose` | 이번 컷의 자세·표정·`item`을 다루는 동작 3~25단어, 3인칭 동사로 시작(`holds ...`) |

`pose`에 장소·배경·빛을 부르는 말(background·scenery·room·street·sky·floor·ground·forest·park·beach·city·indoor(s)·outdoor(s)·wall·window·sparkle(s)·glow(ing)·mote(s), 하이픈 낱말 안에 있어도 걸리므로 sky-blue 대신 pale blue처럼 쓴다), 외형 글과 `pose`에 스타일을 깨는 말(black outline·thick outline·3d·photorealistic·realistic·photo·chibi·watercolor·sketch·neon, `black`·`thick` 단독은 괜찮음)은 채점에서 떨어진다. `persona` 밖의 글은 ASCII만 통과하므로 굽은 따옴표·긴 대시·악센트 글자(café)를 쓰지 않는다. `pose`에 머리·주근깨처럼 외형을 바꾸는 말(hair·bangs·freckle·ponytail·braid·wig·dyed)도 떨어진다. 시선·표정의 눈(eyes)은 써도 된다. 같은 캐릭터의 다른 컷은 파일을 복사해 `view`·`pose`만 바꾼다(`<name>_02.json`).

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 100점이 아니면 FAIL 항목을 고쳐 다시 돌린다. 채점표만 보려면 `build` 대신 `check`.

캐릭터 spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/character_prompt.py build character-output/<작업명>/<name>.json -o character-output/<작업명>/<name>.txt
```

스크립트·traits.json·style.jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 --with pillow python -I <skill>/scripts/character_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만, 사용 중인 이미지 생성 도구에 프롬프트 파일 전문을 고치지 않고 넣어 만든다. 비율은 `aspect`에 따라 `portrait 3:4` 또는 `square 1:1`이고, 결과는 `<name>.png`로 프롬프트 파일 옆에 저장한다.

그림마다 배경이 비었는지 숫자로 검사한다. 테두리(짧은 변의 3%, 내림) 픽셀 중 R·G·B가 모두 243 이상인 비율이 0.95 이상이면 PASS다. FAIL이면 같은 프롬프트로 다시 생성한다.

```bash
uv run --python 3.12 --with pillow python -I <skill>/scripts/character_prompt.py bg character-output/<작업명>/<name>.png
```

사용자가 투명(무색) 배경을 원하면, `bg`를 통과한 그림의 테두리에 이어진 흰 배경만 투명으로 바꾼 PNG를 쓴다. 인물 안의 흰 면(셔츠·눈 흰자)은 테두리와 이어지지 않으므로 남는다. 흰 배경이 기본이고, 투명 PNG는 `<name>_cutout.png`로 따로 둔다.

```bash
uv run --python 3.12 --with pillow python -I <skill>/scripts/character_prompt.py cutout character-output/<작업명>/<name>.png character-output/<작업명>/<name>_cutout.png
```

여러 장이면 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다.

- 선이 가는 남보라 선이고 그늘이 경계가 딱 떨어지는 차가운 색 한 단계다.
- 머리부터 발끝까지 잘리지 않았고, 인물 말고는 그림자·바닥선·글자가 없다.
- 페르소나의 직업·나이가 옷과 `item`으로 읽히고, 주된 옷 한 벌이 `accent` 색이다.
- 같은 캐릭터의 컷끼리 같은 인물로 보이고, 실존 인물·알려진 캐릭터와 닮지 않았다.

## 결과 보고

캐릭터마다 페르소나(지어냈으면 그렇다고), spec 파일, 프롬프트 파일, 채점 점수를 적는다. 이미지를 만들었으면 경로, `bg` 결과, 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 spec 밖에서 외형을 덧붙이는 것.
- 캐릭터 컷에 배경·장소를 넣는 것.
- 실존 인물이나 알려진 애니메이션·게임 캐릭터의 이름·생김새를 spec에 쓰는 것.
