---
name: akbun-draw-template-cartoon
description: 기존 akbun-draw 그림체를 그대로 쓰면서 짧은 이야기를 만화 템플릿(4컷 세로 4koma, 2·4·6컷 격자, 인스타툰 4:5, 유튜브 커뮤니티 1:1)으로 만드는 이미지 생성 프롬프트를 조립한다. 대사·효과음·컷 번호는 폰트로 얹지 않고 이미지 생성 모델이 그림의 일부로 직접 쓴다. 모델은 spec(JSON)만 쓰고 스크립트가 스타일 skill의 그림체 문장을 읽어 프롬프트를 조립·검사한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-template-cartoon

## 목적

짧은 이야기를 만화로 만든다. 그림체는 새로 정하지 않고 사용자가 고른 akbun-draw 스타일 skill(예: [akbun-draw-wash](../akbun-draw-wash/SKILL.md), [akbun-draw-moss](../akbun-draw-moss/SKILL.md), [akbun-draw-storybook-vintage](../akbun-draw-storybook-vintage/SKILL.md))의 것을 그대로 쓴다. 이 skill이 정하는 것은 만화 템플릿(컷 수·비율·배치·컷 역할)과 글자 규칙이다.

글자는 [.claude/rules/image-lettering.md](../../../../.claude/rules/image-lettering.md)를 따른다. 대사·효과음·컷 번호는 이미지 생성 모델이 그림과 같은 펜으로 직접 쓰고, 폰트 파일·Pillow·SVG `<text>`로 얹지 않는다.

## 템플릿

| `template` | 컷 수 | 결과 이미지 | 쓰는 곳 |
|---|---|---|---|
| `4koma` | 4 | 한 장, 세로 2:3, 컷 4개를 위 → 아래 한 줄 | 4컷 만화, 블로그 |
| `grid` | 2·4·6 | 한 장. 2컷 가로 16:9(1×2), 4컷 가로 3:2(2×2), 6컷 세로 2:3(3×2) | 블로그·문서 한 장 |
| `instagram` | 2~10 | 컷마다 1장, 세로 4:5 | 인스타툰 캐러셀 |
| `youtube` | 2~10 | 컷마다 1장, 정사각 1:1 | 유튜브 커뮤니티 게시물 |

- 사용자가 템플릿이나 게시처를 말했으면 그것을 쓴다(4컷 만화 → `4koma`, 인스타툰 → `instagram`, 유튜브 커뮤니티 → `youtube`, 블로그 한 장 → `grid`). 말하지 않았으면 spec을 쓰기 전에 선택지 질문 도구로 묻는다. 그림체(스타일 skill)가 정해지지 않았으면 같은 질문에서 묻는다. 한 만화에 그림체는 하나다.
- 한 장 템플릿은 모든 컷을 한 번에 생성해 캐릭터가 컷마다 같게 나온다. 1장씩 템플릿은 2번 컷부터 1번 컷 결과를 참고 이미지로 붙여 같은 캐릭터를 유지한다(4단계).

## 컷 역할

| 컷 수 | 역할(순서대로) |
|---|---|
| 2 | 상황 → 반전 |
| 4 | 상황(기) → 전개(승) → 뜻밖의 일(전) → 마무리(결). 기본값 |
| 6 | 상황 → 시도 → 문제 → 다시 시도 → 뜻밖의 일 → 마무리 |
| 7~10(1장씩 템플릿만) | 4컷 역할에서 전개를 늘린다. 마지막 컷이 결말인 것은 같다 |

첫 컷에서 인물과 장소를 보여 주고, 마지막 컷이 결말(웃음·깨달음)이다. 웃음의 결은 스타일 skill을 따른다. 무표정 그림체면 담담한 얼굴과 어이없는 상황의 차이로 웃긴다. 4컷 이상이면 한 컷은 한 캐릭터의 머리와 어깨만 크게 보여 줘 같은 구도가 반복되지 않게 한다.

## 작업 흐름

### 1. 템플릿·그림체·컷 표

템플릿과 스타일 skill을 정하고, 컷마다 역할·장면·대사를 표로 적는다. 글만 받았으면 이야기를 지어내고 그 사실을 결과에 밝힌다. 캐릭터는 스타일 skill의 캐릭터 규칙(라이브러리가 있으면 그 안에서)으로 고른다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `cartoon-output/<작업명>/`. spec은 그 폴더의 `cartoon.json`이다.

| 키 | 값 |
|---|---|
| `template` | 템플릿 표의 이름 |
| `style` | 스타일 skill 이름(`akbun-draw-…`). 스크립트가 그 skill의 `references/style.jsonl`을 그림체 문장으로 넣는다 |
| `palette` | 스타일 skill `palettes.jsonl`의 `id`. 빼면 첫 줄(기본 팔레트) |
| `fill` | 팔레트가 채우지 못한 `{자리표시자}` 값. 검사가 "fill에 값 필요"로 알려 줄 때만 쓴다(예: bori의 `season`, `line`) |
| `style_text` | 스타일 skill에 `references/style.jsonl`이 없을 때만. 그 skill의 그림체·선·색·질감 규칙을 영어 문장으로 옮긴다 |
| `cast` | `[{"name", "look"}]` 1~3명, `name` 중복 없이 영어 한 단어. `look`은 종·색·옷을 담은 영어 4단어 이상. 모든 컷에 글자 그대로 들어간다 |
| `panels` | 읽는 순서대로 |
| `panels[].scene` | 이 컷에서 일어나는 일, 영어 6~40단어(공백으로 나눈 수, 경계 포함). 캐릭터는 `name`으로 부른다 |
| `panels[].lines` | `[{"who", "text"}]` 0~2개, 말하는 순서대로. `who`는 `cast`의 `name`. `text`는 한국어, `\n`으로 나눈 2줄 이하, 줄마다 1~12자(공백·문장부호 포함) |
| `panels[].sfx` | 효과음, 한 줄 6자 이하. 없으면 뺀다 |

이미지 모델이 한글을 정확히 쓰도록 대사는 짧게 한다. 영어 문장에 폰트 이름·`font`·`typeface`를 쓰지 않는다. 글씨 모양은 스크립트의 LETTERING 문장이 획으로 묘사한다.

4koma로 wash 그림체를 쓰는 spec 예시다. 형식만 보고 이야기를 그대로 쓰지 않는다.

```json
{
  "template": "4koma",
  "style": "akbun-draw-wash",
  "cast": [{"name": "otter", "look": "a small brown otter in a mustard knit vest"}],
  "panels": [
    {"scene": "The otter stands at a bus stop holding a paper cup, looking down the empty road.", "lines": [{"who": "otter", "text": "버스 언제 와"}]},
    {"scene": "Close-up of the otter checking a wristwatch with a blank face.", "lines": [{"who": "otter", "text": "5분 남았네"}]},
    {"scene": "A bus passes behind the otter, who is still staring at the wristwatch.", "sfx": "부웅"},
    {"scene": "The otter sits on the bench alone, sipping from the paper cup calmly.", "lines": [{"who": "otter", "text": "다음 거 타지"}]}
  ]
}
```

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 검사에 걸리면 프롬프트를 쓰지 않고 FAIL 이유를 보여 준다. spec을 고쳐 다시 돌린다.

spec을 검사하고 `cartoon.json` 옆에 `cartoon.txt`(한 장 템플릿) 또는 `cartoon_01.txt` …(1장씩 템플릿)를 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/cartoon_prompt.py build cartoon-output/<작업명>/cartoon.json
```

검사만 하려면 `build` 대신 `check`를 쓴다. 스크립트를 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/cartoon_prompt.py --selftest
```

### 4. 이미지 생성

사용자가 이미지까지 요청했을 때만 만든다. 프롬프트 파일 전문을 그대로 넣고, 비율은 템플릿 표대로 적는다. 도구와 모델은 사용자의 기본값을 쓴다.

`cartoon-output/<작업명>/cartoon.txt`로 만들어 같은 폴더에 `cartoon.png`로 저장한다. 1장씩 템플릿은 `cartoon_01.txt`부터 파일마다 만들고, 2번 컷부터는 `cartoon_01.png`를 참고 이미지로 붙여 인물을 그 그림과 똑같이 그리게 한다.

### 5. 검수

결과를 한 장만 열어 본다. 1장씩 템플릿은 결과를 가로로 붙여서 본다.

1장씩 템플릿의 결과를 한 장으로 붙이는 명령이다. `tile=Nx1`의 N은 컷 수다.

```bash
ffmpeg -v error -y -pattern_type glob -i 'cartoon-output/<작업명>/cartoon_*.png' -vf "scale=360:-1,tile=4x1:color=white" -frames:v 1 cartoon-output/<작업명>/sheet.jpg
```

어긋난 장은 같은 프롬프트로 다시 생성하고, 몇 번 만에 맞았는지 결과 보고에 적는다. 대사 글자가 계속 틀리면 그 대사를 더 짧게 고쳐 3단계부터 다시 한다.

- 컷 수·배치·읽는 순서 번호가 템플릿과 같은가.
- 대사·효과음이 spec의 글자 그대로이고, 그 밖의 글자가 없는가.
- 말풍선 꼬리가 말하는 캐릭터를 가리키고, 말풍선이 얼굴을 가리지 않는가.
- 같은 캐릭터가 모든 컷에서 같은 종·색·옷·비율이고, 모든 컷이 고른 스타일 skill의 그림체인가.
- 마지막 컷이 결말이고, 캐릭터·장면이 이미 알려진 캐릭터·만화 장면과 닮아 보이지 않는가.

## 결과 보고

템플릿과 고른 이유, 스타일 skill·팔레트, 컷 표(번호·역할·대사), 프롬프트 파일, 결과 이미지 경로, 검수 결과와 다시 생성한 횟수를 적는다. 이미지를 만들지 않았으면 "이미지 생성하지 않음"과 프롬프트 파일 경로를 적는다.

## 하지 말 것

- 대사·번호를 폰트로 얹거나, 폰트를 받거나 설치하는 것.
- 이 skill에서 그림체·색 규칙을 새로 만드는 것. 바꿀 것이 있으면 스타일 skill의 jsonl을 고친다.
- 프롬프트 문장을 손으로 고치는 것. 바꿀 것이 있으면 spec이나 이 스크립트를 고친다.
- 한 만화에 그림체 두 개, 1장씩 템플릿에서 비율 두 개를 섞는 것.
