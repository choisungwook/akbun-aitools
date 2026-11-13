---
name: akbun-draw-comic-wash
description: akbun-draw-illust-wash 그림체(흰 종이 여백, 끊어 겹친 펜 선, 옅은 수채 칠, 무표정 오리지널 동물)로 2·4·6컷 만화를 만든다. 블로그용 한 장 격자(page), 인스타툰 1080×1350, 유튜브 커뮤니티 1080×1080 중 하나로 낸다. 모델은 만화 spec(JSON)만 쓰고, 스크립트가 컷마다 한글 말풍선·컷 번호까지 그리게 하는 영어 이미지 프롬프트를 조립·채점하며, 생성된 컷에 테두리를 둘러 묶는다. 글자는 폰트로 얹지 않고 이미지 모델이 그림 안에 직접 그린다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-comic-wash

## 목적

짧은 이야기를 wash 그림체의 2·4·6컷 만화로 만든다. 이미지 생성 도구가 컷마다 그림과 함께 말풍선·한글 대사·읽는 순서 번호를 같은 펜 선 손글씨로 직접 그린다. 폰트를 쓰지 않아 글자가 그림과 한 붓질로 섞인다. 대신 대사를 고치면 그 컷을 다시 생성해야 한다. 스크립트는 컷을 형식 크기로 맞추고 테두리를 둘러 묶기만 한다.

그림체·색·캐릭터는 [akbun-draw-illust-wash](../akbun-draw-illust-wash/SKILL.md)의 라이브러리를 그대로 쓴다. 이 skill이 더하는 것은 출력 형식, 컷 수와 역할, 컷 크기(shot), 말풍선 규칙이다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체 | illust-wash [style.jsonl](../akbun-draw-illust-wash/references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다 |
| 색 | illust-wash [palettes.jsonl](../akbun-draw-illust-wash/references/palettes.jsonl) | 기본 `paper-wash`. 이야기 대부분의 시간·장소가 다른 줄의 `use`와 맞을 때만 그 `id`, 맞는 줄이 없으면 `paper-wash`. 한 만화에 하나 |
| 캐릭터 | illust-wash [characters.jsonl](../akbun-draw-illust-wash/references/characters.jsonl) | 1~3종. 사람 역할도 이 동물들이 맡는다 |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 이야기를 그대로 쓰지 않는다 |

## 출력 형식

| `format` | 결과 | 쓰는 곳 |
|---|---|---|
| `page` | 16:9 컷(960×540)을 2열 격자로 놓은 `comic.png` 한 장. 읽는 순서는 왼쪽 → 오른쪽, 위 → 아래 | 블로그·문서 |
| `instagram` | 컷마다 1080×1350(4:5) `comic_01.png` … | 인스타툰 캐러셀 |
| `youtube` | 컷마다 1080×1080(1:1) `comic_01.png` … | 유튜브 커뮤니티 게시물 |

사용자가 게시처를 말했으면 그 형식(인스타툰 → `instagram`, 유튜브 커뮤니티 → `youtube`, 블로그·한 장 → `page`)을 쓴다. 말하지 않았으면 spec을 쓰기 전에 선택지 질문 도구로 셋 중 하나를 묻는다. 컷 그림의 비율이 형식마다 달라 그린 뒤에는 바꾸기 어렵다.

## 컷 수와 역할

| 컷 수 | 역할(순서대로) | 고르는 기준 |
|---|---|---|
| 2 | 상황 → 반전 | 사건 하나와 뜻밖의 결과 하나 |
| 4 | 상황 → 전개 → 뜻밖의 일 → 무표정 마무리 | 기본값 |
| 6 | 상황 → 시도 → 문제 → 다시 시도 → 뜻밖의 일 → 무표정 마무리 | 시도가 두 번 필요한 이야기 |

웃음은 큰 표정이 아니라 담담한 얼굴과 어이없는 상황의 차이에서 나온다. 마지막 컷은 캐릭터가 아무렇지 않은 얼굴로 결말을 받아들이는 장면이 좋다.

## 작업 흐름

### 1. 형식·컷 수·컷 표

형식과 컷 수를 정하고, 컷마다 역할·장면·나오는 캐릭터와 위치·대사를 표로 적는다. 글만 있으면 이야기를 지어내고 그 사실을 결과에 밝힌다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `comic-wash-output/<작업명>/`. spec은 그 폴더의 `comic.json`이다.

| 키 | 값 |
|---|---|
| `format` | `page`·`instagram`·`youtube` |
| `palette` | illust-wash palettes.jsonl의 `id` |
| `cast` | `[{"id", "outfit"}]` 1~3개, `id` 중복 없이. `outfit`은 영어 2단어 이상의 옷 하나(예: `a mustard knit vest`). 따로 생성되는 컷끼리 같은 캐릭터로 보이게 모든 컷 프롬프트에 똑같이 들어간다 |
| `panels` | 컷 2·4·6개, 읽는 순서대로 |
| `panels[].scene` | 이 컷에서 일어나는 일, 영어 6~30단어(공백으로 나눈 수, 경계 포함). 캐릭터별 동작은 `action`에 쓰고 여기서는 상황·소품 위주로 쓴다 |
| `panels[].setting` | 어디인지 영어 한 구절, 의미 없으면 `""` |
| `panels[].shot` | `wide`(전신, 장소 조금)·`medium`(무릎 위)·`close`(한 캐릭터 머리와 어깨). 4·6컷이면 `close`를 1컷 이상 넣어 같은 크기가 반복되지 않게 한다 |
| `panels[].chars` | `[{"id", "pos", "action"}]` 1~3개. `id`는 `cast` 안에서만. `pos`는 `left`·`center`·`right` 중 컷 안에서 서로 다르게. 말풍선 꼬리가 이 위치를 가리킨다. `action`은 영어 3단어 이상 |
| `panels[].lines` | `[{"who", "text"}]` 0~2개, 말하는 순서대로. `who`는 그 컷의 `chars`에 있는 `id`. `text`는 한국어, `\n`으로 나눈 2줄 이하, 줄마다 1~12자(공백·문장부호 포함) |

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

spec을 채점하고 `comic.json` 옆에 `panel_01.txt` …를 쓰는 명령이다.

```bash
uv run --python 3.12 --with pillow python -I <skill>/scripts/comic_prompt.py build comic-wash-output/<작업명>/comic.json
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치와 illust-wash와 같은 영어·금지 낱말 검사를 본다.

스크립트를 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 --with pillow python -I <skill>/scripts/comic_prompt.py --selftest
```

### 4. 컷 그림 생성

사용자가 이미지까지 요청했을 때만 만든다. 컷마다 프롬프트 파일 전문을 그대로 넣어 `panel_01.png` …로 저장한다.

codex CLI를 쓸 때, 컷 하나를 만드는 명령이다. 모델은 사용자 설정의 기본값을 쓰고, 비율은 형식 표대로(`page` 16:9, `instagram` 4:5, `youtube` 1:1) 적는다.

```bash
cd comic-wash-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read panel_01.txt. Use your built-in image generation tool with that file's full text as the prompt, exactly, portrait 4:5. Save the result as panel_01.png here. Reply with the path only." < /dev/null
```

`< /dev/null`이 없으면 codex가 입력을 기다리며 멈춘다. 컷마다 따로 돌린다.

### 5. 묶기

`panel_01.png` …에 테두리를 둘러 형식대로 묶는 명령이다.

```bash
uv run --python 3.12 --with pillow python -I <skill>/scripts/comic_prompt.py compose comic-wash-output/<작업명>/comic.json
```

결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 컷(대사 철자가 하나라도 틀린 컷 포함)은 같은 프롬프트로 다시 생성하고 compose를 다시 돌린다. 대사를 바꾸려면 spec의 `text`를 고치고 build부터 다시 해 그 컷만 새로 생성한다.

- 말풍선 안 대사가 spec의 `text`와 한 글자도 다르지 않고, 줄바꿈 위치가 같다. 말풍선·번호 밖에 다른 글자가 없다.
- 말풍선이 컷 위쪽 28% 안에 있어 그림을 가리지 않고, 왼쪽 위에 컷 번호가 있다.
- 같은 캐릭터가 모든 컷에서 같은 종·색·옷이다.
- 말풍선 꼬리가 말하는 캐릭터 쪽을 가리킨다.
- 개·고양이·흰 털 뭉치 동물·사람이 없으며, 알려진 캐릭터와 닮지 않았다.

## 결과 보고

형식, 컷 수, spec 파일, 채점 점수, 고른 팔레트·캐릭터, 결과 PNG 경로와 위 확인 결과를 적는다. 이미지를 만들지 않았으면 "이미지 생성하지 않음"과 프롬프트 파일 경로를 적는다.

## 하지 말 것

- 말풍선·대사·번호를 폰트로 그림 위에 얹는 것.
- 프롬프트 문장을 손으로 고치는 것. 바꿀 것이 있으면 illust-wash의 jsonl이나 이 스크립트를 고친다.
- 컷마다 다른 옷·다른 종으로 같은 캐릭터를 그리는 것.
