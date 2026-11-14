---
name: akbun-draw-character-hana
description: 1990년대 TV 셀 애니메이션 한 프레임 같은 오리지널 인물 한 명을 배경 없이 흰색 또는 투명 바탕에 그리는 이미지 생성 프롬프트 스타일 hana. 가늘고 고른 짙은 잉크 선, 바탕색과 칼같은 그늘색 두 단의 셀 채색, 눈가를 가로지르는 넓은 그림자 띠, 인물마다 고르는 눈 모양, 끝이 뾰족한 머리 덩어리, 바랜 필름 색과 고운 노이즈, 장소·소품 배경 없이 흰색 또는 투명 바탕. 모델은 인물 spec(JSON)만 쓰고, 스크립트가 references 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-character-hana

## 목적

사용자가 준 인물 페르소나(직업·성격·외모 묘사)에 맞는 오리지널 인물 한 명을 hana 그림체로 그리는 영어 이미지 생성 프롬프트를 만든다. 그림에는 인물만 있고 뒤는 순백(#FFFFFF) 또는 투명이다. 장소·하늘·가구·바닥 그림자는 그리지 않아서 결과를 다른 장면에 오려 붙이기 쉽다. 이 skill이 고정하는 것은 선·채색·얼굴과 머리 그림법·색감·질감·빈 바탕이고, 누구를 어떤 차림·표정·자세로 그릴지는 입력에 맞춰 정한다.

모델은 프롬프트 문장을 직접 쓰지 않는다. 인물 spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다. 그래서 몇 장을 만들어도 같은 그림체가 나온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체(선·셀 채색·얼굴·머리·색감·질감·빈 바탕·분위기) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 spec이 이 규칙과 어긋나지 않게만 한다 |
| 색(인물이 받는 빛) | [references/palettes.jsonl](references/palettes.jsonl) | 각 줄의 `use`에서 인물의 빛·분위기와 맞는 `id` 하나. 둘 이상 맞으면 분위기가 더 맞는 쪽. 여러 장이면 같은 것을 연달아 3장 넘게 쓰지 않는다 |
| 눈 모양 | [references/eyes.jsonl](references/eyes.jsonl) | 페르소나가 눈을 묘사했으면 가장 가까운 `id`. 아니면 각 줄 `ko`의 성격·나이 단서가 페르소나와 맞는 `id`. 여러 장이면 같은 것을 연달아 2장 넘게 쓰지 않는다 |
| 화면 크기(카메라) | [references/framings.jsonl](references/framings.jsonl) | 사용자가 정하지 않으면 `full`. 사용자가 표정·얼굴을 보여 달라고 하면 `bust`, 손 동작을 크게 보여 달라고 하면 `knee` |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 인물을 그대로 쓰지 않는다 |

## 작업 흐름

### 1. 인물 정하기

입력은 사용자가 준 인물 페르소나(직업·나이·성격·외모·차림 묘사 등)다. 여러 장이면 페르소나마다 한 장이다. 사용자가 준 묘사는 빠짐없이 spec의 해당 칸(`who`·`hair`·`outfit`·`expression`·`pose`)에 영어로 옮기고 뜻을 바꾸지 않는다. 비어 있는 칸만 페르소나에 어울리게 채운다(예: 직업에 맞는 작업복, 성격에 맞는 표정). 페르소나가 하나도 없으면 인물을 무작위로 지어낸다. 채우거나 지어낸 칸은 결과 보고에 밝힌다. 인물마다 `<id>`(영어 소문자·하이픈 짧은 이름, 예: `night-kiosk-owner`)를 붙인다. 이미 있는 애니메이션·만화·게임 인물이나 실존 인물을 그리지 않는다. 사용자가 그런 인물을 요청하면 역할만 살린 오리지널 인물로 바꾸고 그렇게 했다고 밝힌다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `hana-output/<작업명>/`이고, 먼저 만든다. spec은 `NN_<id>.json`(`NN`은 01부터 두 자리)이다. 단어 수는 공백으로 나눈 수이고, 하이픈으로 이은 말은 한 단어, 범위는 경계를 포함한다.

| 키 | 값 |
|---|---|
| `palette`, `framing` | jsonl의 `id` |
| `backdrop` | `white`(순백 #FFFFFF) 또는 `transparent`(투명 PNG). 사용자가 정하지 않으면 `transparent`. 이미지 도구가 투명을 못 만들면 `white`로 바꿔 다시 build 한다 |
| `aspect` | `3:4`·`1:1`·`16:9` 중 하나. 사용자가 정하지 않으면 `3:4` |
| `character.who` | 누구인지 영어 2~10단어(나이대·성별·직업 등) |
| `character.eyes` | eyes.jsonl의 `id` |
| `character.eye_color` | 홍채 색 영어 1~4단어 |
| `character.hair` | 머리 색·길이·모양 영어 3~15단어 |
| `character.outfit` | 차림 영어 3~20단어. 손에 들거나 몸에 지닌 소품 하나까지 포함해도 된다 |
| `character.expression` | 표정 영어 2~10단어 |
| `character.pose` | 자세·손 동작 영어 3~20단어. 기대거나 앉을 가구·장소 없이 혼자 서서 하는 동작으로 쓴다 |
| `light` | 인물에 닿는 빛의 색과 방향 영어 3~15단어. 그림자 띠가 생기도록 한쪽에서 오는 빛으로 쓴다 |

배경 키(`setting`)는 없다. spec에 넣으면 채점에서 떨어진다.

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/hana_prompt.py build hana-output/<작업명>/01_<id>.json -o hana-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 이것도 본다: 모델이 쓴 글은 영어(ASCII)만, 큰따옴표 없음(그림 속 글자를 만들지 않는다), 배경·장소·가구 낱말(background·sky·street·room·wall·floor·window·counter·table·desk·chair·stool·bench·sofa·stairs·sea·city 등) 없음, 그림체를 깨는 말(3d·cgi·photorealistic·photographic·realistic·chibi·moe·gradient·neon·glossy·sparkle·watercolor) 없음, 베끼기를 부르는 말(in the style of·fan art·cosplay·parody·logo·brand) 없음.

스크립트나 jsonl을 고쳤으면 예시 txt를 `build`로 다시 쓰고 자체 검사가 `selftest ok`를 내는지 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/hana_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 프롬프트 파일 전문을 그대로 넣어 만든다. 모델은 사용자 설정의 기본값을 쓴다.

codex CLI로 프롬프트 파일이 있는 폴더에서 내장 이미지 생성으로 PNG를 만드는 명령이다. `<비율>`은 spec의 `aspect`다.

```bash
cd hana-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read 01_<id>.txt. Use your built-in image generation tool with that file's full text as the prompt, exactly, aspect ratio <비율>, transparent background if the spec backdrop is transparent. Save the result as 01_<id>.png here. Reply with the path only." < /dev/null
```

Antigravity CLI(`agy`)로 같은 일을 하는 명령이다. `-p`는 바로 뒤 값을 프롬프트로 먹으므로 다른 옵션을 `-p` 앞에 둔다.

```bash
cd hana-output/<작업명> && agy --print-timeout 600s --mode accept-edits -p "Read 01_<id>.txt. Use your image generation tool with that file's full text as the prompt, exactly, aspect ratio <비율>, transparent background if the spec backdrop is transparent. Save the result as 01_<id>.png in this folder. Reply with the path only." < /dev/null
```

`< /dev/null`이 없으면 CLI가 입력을 기다리며 멈출 수 있다. 여러 장은 장마다 따로, 동시에 돌려도 된다.

결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성하되 장마다 처음 생성을 포함해 최대 3번까지 하고, 그래도 어긋나면 그 항목을 결과 보고에 적는다.

- 인물 칠이 바탕색과 칼같은 그늘색 두 단이고, 피부·옷에 그라데이션·광택이 없다.
- 선이 가늘고 고른 짙은 잉크다.
- 인물 뒤가 `backdrop`대로(순백 한 색이면 네 모서리 화소가 모두 RGB 각 250 이상, 투명이면 네 모서리 알파가 0)이고, 장소·가구·바닥 그림자·무늬가 없다. 인물 몸이 화면 가장자리에서 잘리는 것은 `framing`대로일 때만이다.
- 눈이 spec의 `eyes` 모양이고, 큰 반짝이는 눈·치비 비율이 아니다.
- 턱 아래 목·얼굴 아래에 검거나 짙은 그림자 덩어리가 없다. 그늘은 바탕보다 한 단계 어두운 중간 톤이다.
- 인물 칠이 팔레트 쪽으로 바래 있고 고운 노이즈가 보인다. 옷의 흰 부분도 순백이 아니다. 형광색이 없다.
- 글자·로고·워터마크가 없다.
- 이미 알려진 애니메이션·만화·게임 인물과 닮지 않았다. 닮았으면 머리 모양·차림을 바꿔 build부터 다시 한다.

## 결과 보고

장마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 팔레트·화면 크기, 지어낸 인물 설정을 적는다. 이미지를 만들었으면 경로, 몇 번째 생성에서 맞았는지와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 알려진 인물·작품·작가 이름을 spec이나 프롬프트에 쓰는 것.
- 그림 속에 글자(대사·제목·간판)나 배경(장소·하늘·가구)을 넣는 것.
