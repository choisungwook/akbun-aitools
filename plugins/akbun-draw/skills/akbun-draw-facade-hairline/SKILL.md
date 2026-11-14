---
name: akbun-draw-facade-hairline
description: 따뜻한 미색 종이 위 굵기 하나인 가는 펜 선, 원근 없이 정면으로 그린 세부 많은 건물, 얼굴 없이 팔다리를 두 줄로 연 길쭉한 작은 인물, 좁은 곳에만 칠한 강조색 1~2개, 밤이면 남색 종이에 옅은 선으로 뒤집히는 라인 드로잉 이미지 생성 프롬프트 스타일 facade-hairline. 모델은 spec(JSON)만 쓰고, 스크립트가 references의 스타일·시간대·강조색·캔버스·펜 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-facade-hairline

## 목적

아무 장소·장면을 facade-hairline 그림체로 그리는 영어 이미지 생성 프롬프트를 만든다. 이 skill이 고정하는 것은 선 굵기·채움·건물 그리는 법·인물과 동물 그리는 법·여백·색 쓰는 법·밤 반전이고, 무엇을 그릴지(장소·구조물·사람·소품)와 구도는 입력에 맞춰 정한다.

모델은 프롬프트 문장을 직접 쓰지 않는다. spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다. 그래서 몇 장을 만들어도 같은 그림체가 나온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체(매체·선·채움·구조물·인물·동물·여백·색) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 spec이 이 규칙과 어긋나지 않게만 한다 |
| 시간대 | [references/times.jsonl](references/times.jsonl) | 입력에 저녁·밤·새벽·야경·불 켜진 같은 말이 있으면 `night`, 그 밖(아침·한낮·오후·해질녘·노을)은 `day` |
| 날씨 | [references/weathers.jsonl](references/weathers.jsonl) | 입력에 비·눈이 있으면 `rain`·`snow`, 아니면 `clear` |
| 강조색 | [references/accents.jsonl](references/accents.jsonl) | 1~2개. 사용자가 색을 말하면 가장 가까운 `id`, 아니면 장면에서 눈이 갈 물건 1~2개를 고른다. 물건 이름이 어떤 `use`에 있으면 그 `id`(여럿이면 파일에서 위의 줄), 없으면 그 물건의 실제 색에 가장 가까운 `id`. `night`에서는 `indigo`를 쓰지 않는다 |
| 캔버스 | [references/canvases.jsonl](references/canvases.jsonl) | 사용자가 비율이나 쓰임(SNS·포스터·파노라마)을 말하면 그 `id`, 아니면 장면 내용과 상관없이 `wide` |
| 펜 | [references/pens.jsonl](references/pens.jsonl) | 사용자가 손맛·떨림·잉크 느낌을 말하면 `wobble`, 아니면 `steady` |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 장소·인물을 그대로 쓰지 않는다 |

라이브러리에 없는 색·캔버스가 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. spec 쓰기

입력에서 장면 하나를 정한다(여러 장이면 장마다). 출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `hairline-output/<작업명>/`, 파일 이름은 `01_<id>.json`. `<작업명>`과 `<id>`는 장면을 줄인 영어 소문자·하이픈 말이다.

배치(어디에 무엇을 두는지)는 쓰지 않는다. 구도는 이미지 모델이 정한다. 단어 수는 공백으로 나눈 덩어리 수다. a·the도 세고, 하이픈으로 이은 말은 한 단어다. 범위는 모두 경계를 포함한다.

| 키 | 값 |
|---|---|
| `time`, `weather`, `canvas`, `pen` | jsonl의 `id` |
| `scene` | 어떤 장소의 어떤 순간인지 영어 6~30단어 |
| `structures` | 1~4개. `[{"what": 무엇인지 영어 2단어 이상, "details": 그 구조물의 세부 영어 구절 2~6개}]`. 건물이 없는 장면이면 부두·다리·정자·기차처럼 세부를 붙일 구조물을 고른다 |
| `figures` | 0~5명. `[{"who": 관사를 붙인 역할 2단어 이상(a driver, an old man), "head": 머리 모양이나 모자 2단어 이상, "garment": 옷 2단어 이상, "doing": 하는 일 2단어 이상}]`. 나이는 `who`로 드러내고(girl·old woman), 나이 낱말이 없으면 어른이다. 인물마다 머리·모자를 다르게 해서 얼굴 없이 구분되게 한다. 우산처럼 든 물건은 `doing`에 쓴다(holds a paper umbrella) |
| `animals` | 0~3개. `[{"what": 영어 2단어 이상, "doing": 영어 2단어 이상}]`. 무리는 한 항목에 수를 쓴다(three gulls) |
| `props` | 영어 구절 0~6개, 대소문자 무시하고 중복 없이 |
| `lights` | `night`면 빛나는 것 영어 구절 2~5개(창·가로등·자전거 등), `day`면 빈 목록. 낮 장면의 등은 `structures`·`props`에 그냥 두면 켜지지 않은 채 그려진다 |
| `accents` | 1~2개, 색 중복 없이. `[{"color": accents.jsonl id, "on": 칠할 것}]`. `on`은 `structures`의 what·details, `figures`의 head·garment·doing, `animals`의 what, `props` 중 정확히 한 항목 안에 낱말 단위로 들어 있는 말(대소문자 무시, 관사만은 안 됨). 두 항목에 같은 낱말(coat 등)이 있으면 더 긴 말(long buttoned coat)을 쓴다 |

### 2. 프롬프트 조립

spec을 채점하고 프롬프트 파일을 쓰는 명령이다. `<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

```bash
uv run --python 3.12 python -I <skill>/scripts/hairline_prompt.py build hairline-output/<작업명>/01_<id>.json -o hairline-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 이것도 본다: 모델이 쓴 글은 영어(ASCII)만, 얼굴을 뜻하는 낱말(face·eyes·nose·mouth·smile·expression 등), 스타일을 깨는 낱말(3d·photo·realistic·anime·cartoon·gradient·neon·shading·shadow·glossy·watercolor·bold·thick·hatch·perspective·isometric), 글자를 부르는 낱말(text·letters·words·logo·number·label·caption)과 따옴표, 배치 낱말(left·right·foreground·background·center·middle·corner·top·bottom)이 없을 것. 낱말은 모두 낱말 단위로 찾는다(signal은 걸리지 않는다). 간판·포스터는 글자 없이 비워 둔다.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/hairline_prompt.py --selftest
```

### 3. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 프롬프트 파일 전문을 그대로 넣어 만든다.

codex CLI를 쓸 때, 프롬프트 파일이 있는 폴더에서 내장 이미지 생성으로 PNG를 만드는 명령이다. 모델은 사용자 설정의 기본값을 쓴다. `<비율>`은 캔버스의 `aspect`다.

```bash
cd hairline-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read 01_<id>.txt. Use your built-in image generation tool with that file's full text as the prompt, exactly, aspect <비율>. Save the result as 01_<id>.png here. Reply with the path only." < /dev/null
```

`< /dev/null`이 없으면 codex가 입력을 기다리며 멈춘다. 여러 장은 장마다 따로 돌린다.

결과마다(여러 장이면 한 장으로 붙여 한 번만 보고) 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다.

- 선이 굵기 하나로 가늘고, 굵은 외곽선·빗금 그늘이 없다.
- 건물이 원근 없이 정면이고, 세부가 촘촘하다.
- 인물에 얼굴이 없고, 팔다리가 열린 두 줄이다.
- 강조색이 `accents`의 `on`에만 있다.
- `night`면 건물 벽까지 남색이고 선이 옅은 색이다. 건물이 미색으로 칠해졌으면 반전이 안 된 것이다.
- 글자가 없다.
- 알려진 작품·캐릭터·실제 거리 사진과 닮지 않았다. 닮았으면 `structures`·`figures`를 바꿔 build부터 다시 하고, 무엇을 바꿨는지 결과 보고에 적는다.

## 결과 보고

장마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 시간대·날씨·강조색·캔버스·펜을 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다. 프롬프트는 한 개의 `text` 코드블록으로도 보여 준다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 인물에 얼굴을 그리는 것, 간판에 글자를 넣는 것.
- 강조색을 셋 이상 쓰거나 넓은 면에 칠하는 것.
