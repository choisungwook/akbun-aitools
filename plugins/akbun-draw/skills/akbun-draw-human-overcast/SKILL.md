---
name: akbun-draw-human-overcast
description: 흐린 날의 부드러운 확산광, 채도·대비를 낮춘 색, 무광의 낡은 도시 벽 앞에서 힘을 뺀 자세로 찍힌 실사 인물 스트리트 스냅 사진 스타일 overcast의 이미지 생성 프롬프트를 만든다. 모델은 인물 spec(JSON)만 쓰고, 스크립트가 references의 스타일·팔레트·프레이밍 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-human-overcast

## 목적

아무 인물을 overcast 사진 스타일로 찍은 세로 영어 이미지 생성 프롬프트를 만든다. 이미지 생성 도구에 그대로 붙여 넣는다. 이 skill이 고정하는 것은 빛·색 보정·렌즈 느낌·배경 면의 질감·담담한 분위기이고, 누구를 어디서 어떤 자세로 찍을지는 입력에 맞춰 정한다.

모델은 프롬프트 문장을 직접 쓰지 않는다. spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다. 그래서 몇 장을 만들어도 같은 사진 톤이 나온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 사진 스타일(빛·보정·렌즈·배경 면·인물 표현·분위기) | [references/style.jsonl](references/style.jsonl), 금지 문단은 스크립트의 `DONT` | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 spec이 이 규칙과 어긋나지 않게만 한다 |
| 색 | [references/palettes.jsonl](references/palettes.jsonl) | 기본 `concrete-grey`. 입력이 말한 장소·배경이 다른 줄의 `use`와 맞을 때만 그 `id`. 장소를 말하지 않았거나 맞는 줄이 둘 이상이면 기본값. 줄의 `prompt`(있을 때만)는 배경 묘사로 색 목록 앞에 들어간다 |
| 프레이밍 | [references/shots.jsonl](references/shots.jsonl) | 기본 `half-body`. 입력이 콕 집어 말한 것(옷 전체, 얼굴, 프로필 사진 등)이 다른 줄의 `use`와 맞을 때만 그 `id`. 둘 이상 맞으면 기본값 |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 인물·장소를 그대로 쓰지 않는다 |

라이브러리에 없는 팔레트·프레이밍이 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. 인물 정하기

입력에서 사진 한 장(여러 장이면 장마다)의 인물·자세·장소를 정한다. 인물은 늘 지어낸 성인이다. 사용자가 실존 인물이나 사진 속 특정인을 닮게 해 달라고 하면 그 부분은 하지 않는다고 밝히고 지어낸 인물로 만든다. 입력이 짧으면 성별·나이대·머리·옷을 정해 채우고, 직업은 소품·옷으로만 암시한다. 지어낸 설정은 결과 보고에 밝힌다. 증명사진·프로필 사진을 원해도 스튜디오로 바꾸지 않고 이 스타일의 `close-up`으로 찍는다. 장마다 `<id>`(영어 소문자·하이픈 짧은 이름, 예: `bus-stop-wait`)를 붙인다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `overcast-output/<작업명>/`. 단어 수는 공백으로 나눈 수이고 경계를 포함한다.

| 키 | 값 |
|---|---|
| `palette` | palettes.jsonl의 `id` |
| `shot` | shots.jsonl의 `id` |
| `aspect` | `4:5`(기본). 입력이 숏폼·스토리·릴스·세로 영상을 말할 때만 `9:16` |
| `subject` | 나이대·머리·옷을 담은 인물 묘사, 영어 8~40단어. 옷은 무채색 위주 |
| `pose` | 무엇을 하는 순간인지와 시선·표정, 영어 4~25단어. 일상 동작으로 쓰고 표정은 무표정이나 옅은 미소 안에서 고른다 |
| `setting` | 장소 이름과 그곳의 배경 면을 영어 한 구절로(예: `a stained concrete wall beside a bus stop`). 간판·안내판이 있을 곳이면 글자 없는 면으로 쓴다. 비우지 않는다 |
| `props` | 인물이 들거나 걸친 물건 영어 구절 0~3개, 중복 없이. `pose`에 나온 물건도 여기 다시 쓴다 |

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/overcast_prompt.py build overcast-output/<작업명>/01_<id>.json -o overcast-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치와 id 외에 모델이 쓴 글이 영어(ASCII)인지, 금지 낱말이 없는지 본다. 금지 낱말은 실존 인물 닮음(celebrity·famous·idol·lookalike·resemble·in the style of), 미성년(child·kid·teen·boy·girl·minor), 노출(nude·naked·lingerie·sexy), 스타일을 깨는 빛·매체(studio·flash·neon·hdr·golden hour·sunset·sunlight·sunny·backlit·anime·cartoon·illustration·painting·3d·render)다. 성인은 `man`·`woman`으로 쓴다.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/overcast_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 프롬프트 파일 전문을 그대로 넣어 만든다.

codex CLI를 쓸 때, 프롬프트 파일이 있는 폴더에서 내장 이미지 생성으로 PNG를 만드는 명령이다. 모델은 사용자 설정의 기본값을 쓴다. `<aspect>`는 spec의 값이다.

```bash
cd overcast-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read 01_<id>.txt. Use your built-in image generation tool with that file's full text as the prompt, exactly, portrait <aspect>. Save the result as 01_<id>.png here. Reply with the path only." < /dev/null
```

`< /dev/null`이 없으면 codex가 입력을 기다리며 멈춘다. 여러 장은 장마다 이 명령을 따로 돌린다.

여러 장이면 결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다.

- 그림자가 옅고 경계가 흐리며, 직사광·플래시·역광 테두리가 없다.
- 채도와 대비가 낮고, 피부만 자연스럽게 따뜻하다.
- 배경 면이 무광이고 질감이 보이며, 읽히는 글자·간판이 없다.
- 프레임 안에 인물 한 명뿐이고 카메라·촬영자가 없다.
- 알려진 사람과 닮지 않았다. 닮았으면 `subject`의 머리·옷·나이대를 바꿔 build부터 다시 한다.

## 결과 보고

장마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 팔레트·프레이밍, 지어낸 설정(성별·나이대·옷 등)을 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다. 프롬프트는 한 개의 `text` 코드블록으로도 보여 준다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 실존 인물·사용자가 준 사진 속 사람을 닮게 하는 것, 미성년자를 찍는 것.
- 사진 안에 글자(자막·간판 글·워터마크)를 넣는 것.
