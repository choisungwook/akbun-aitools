---
name: akbun-draw-style-bori
description: 짙은 청록 잉크 손그림 외곽선, 민트·코랄 계열 평면 셀 채색, 소품이 가득한 아늑한 배경, 그 안에서 작게 지내는 동글동글한 오리지널 치비 동물들로 일상의 한 장면을 그리는 이미지 생성 프롬프트 스타일 bori. 모델은 장면 spec(JSON)만 쓰고, 스크립트가 references의 스타일·팔레트·구도·캐릭터 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-style-bori

## 목적

아무 장소·순간을 bori 그림체로 그리는 16:9 영어 이미지 생성 프롬프트를 만든다. 이미지 생성 도구에 그대로 붙여 넣는다. 이 skill이 고정하는 것은 선·채색·색감·배경 밀도·빛·캐릭터 그림체이고, 무엇을 그릴지(장소·사건·소품)는 입력에 맞춰 정한다.

모델은 프롬프트 문장을 직접 쓰지 않는다. 장면 spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다. 그래서 몇 장을 만들어도 같은 그림체가 나온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체(선·채색·질감·배경·빛·캐릭터·분위기) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 장면이 이 규칙과 어긋나지 않게만 한다 |
| 색 | [references/palettes.jsonl](references/palettes.jsonl) | 각 줄의 `use`가 장면의 시간·날씨·장소와 맞는 `id` 하나. 둘 이상 맞으면 광원이 장면을 지배하는 쪽(실내 조명이면 `lamp-interior`). 맞는 것이 없으면 가장 가까운 것을 고르고 결과 보고에 적는다 |
| 구도(카메라) | [references/compositions.jsonl](references/compositions.jsonl) | 장면이 가장 잘 읽히는 `id` 하나. 여러 장이면 같은 구도를 연달아 3장 넘게 쓰지 않는다 |
| 캐릭터 | [references/characters.jsonl](references/characters.jsonl) | 구도가 허용하는 수(`chars`, 경계 포함)만큼 `id`를 고른다. 사람이 나오는 요청(팀·손님·봉사자)도 사람 대신 이 캐릭터들이 그 역할을 맡는다. 여러 장이면 같은 캐릭터를 다시 써서 이어지게 한다 |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 소재를 그대로 쓰지 않는다 |

라이브러리에 없는 캐릭터·팔레트·구도가 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. 장면 정하기

입력에서 장면 하나를 정한다(여러 장이면 장면마다). 글만 있으면 가장 일상적인 한 순간을 고르고, 지어낸 장면임을 결과에 밝힌다. 장면마다 `<id>`(영어 소문자·하이픈 짧은 이름, 예: `rainy-bus-stop`)를 붙인다.

### 2. spec 쓰기

위 표대로 팔레트·구도·캐릭터를 고르고 spec JSON을 쓴다. 출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `bori-output/<작업명>/`.

| 키 | 값 |
|---|---|
| `palette`, `composition` | jsonl의 `id` |
| `season` | `spring`·`summer`·`autumn`·`winter` 중 하나. 입력에 없으면 날씨·옷차림 단서로 정하고, 단서도 없으면 `autumn` |
| `scene` | 어떤 상황인지 영어 6~40단어(공백으로 나눈 단어 수, 하이픈으로 이은 말은 한 단어, 경계 포함). 캐릭터별 행동은 `action`에만 쓰고 여기서 되풀이하지 않는다 |
| `setting` | 어디인지 영어 한 구절 |
| `characters` | `[{"id": 캐릭터 id, "action": 영어 3단어 이상}]`. 라이브러리의 대표 소품(안경·목도리·비니 등)은 늘 붙으므로 `action`에서 되풀이하거나 빼지 않는다. 역할에 필요한 소품(앞치마·집게·우산)은 캐릭터마다 하나까지 `action`에 더해도 된다 |
| `props` | 장면에 놓을 사물 영어 구절(전경의 노점, 서 있거나 달리는 탈것 포함), 구도의 `props_min`개 이상 16개 이하, 중복 없이. 화면·칠판·책에는 글자가 들어가지 않는다 |
| `lights` | 광원 1~4개. 램프·화면·창문·해·노을빛처럼 빛을 내는 것은 모두 센다. `props`에 있는 사물을 다시 적어도 된다 |
| `signs` | 그림 속 간판·현수막 글자 0~2개, 각 1~14자(공백·문장부호 포함), 영어 또는 한글. 장소나 행사를 알려 주는 간판·현수막이 자연스러울 때만 넣고, 없으면 `[]` |

### 3. 프롬프트 조립

프롬프트를 조립한다. `<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

장면 spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/bori_prompt.py build bori-output/<작업명>/01_<id>.json -o bori-output/<작업명>/01_<id>.txt
```

프롬프트를 쓰지 않고 채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 이것도 본다: 캐릭터 `id` 중복 없음, `signs` 밖 글은 영어(ASCII)만, 금지 낱말(dog·puppy·cat·kitten·hamster·human·person·people·man·woman·boy·girl·child, black outline·3d·photorealistic·realistic·anime·gradient·neon) 없음. 사람 역할은 `neighbors`·`volunteers`·`teammates`처럼 쓴다.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/bori_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 프롬프트 파일 전문을 그대로 넣어 만든다.

codex CLI를 쓸 때, 프롬프트 파일이 있는 폴더에서 내장 이미지 생성으로 PNG를 만드는 명령이다. 모델은 사용자 설정의 기본값을 쓴다.

```bash
cd bori-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read 01_<id>.txt. Use your built-in image generation tool with that file's full text as the prompt, exactly, landscape 16:9. Save the result as 01_<id>.png here. Reply with the path only." < /dev/null
```

`< /dev/null`이 없으면 codex가 입력을 기다리며 멈춘다. 여러 장은 장마다 이 명령을 따로 돌린다.

여러 장이면 결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다. 알려진 캐릭터·마스코트와 닮았으면 그 캐릭터 `id`를 다른 것으로 바꿔 build부터 다시 한다.

- 외곽선이 순검정이 아니라 짙은 청록 잉크이고, 배경까지 같은 선으로 둘러져 있다.
- 벽·바닥·하늘 같은 큰 면이 갈색이 아니라 팔레트 색이다.
- 배경이 흐리지 않고 소품이 자세하다.
- 개·고양이·햄스터·사람이 없고, 이미 알려진 캐릭터·마스코트와 닮지 않았다.
- `signs`에 없는 글자가 없다.

## 결과 보고

장면마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 팔레트·구도·캐릭터를 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다. 프롬프트는 한 개의 `text` 코드블록으로도 보여 준다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 개·고양이·햄스터·사람을 장면에 넣는 것, 알려진 캐릭터·영상 장면을 따라 하는 것.
- `signs` 밖 글자(제목·자막·라벨)를 그림에 넣는 것.
