---
name: akbun-draw-template-cartoon-maru
description: 사용자가 고른 akbun-draw 그림체를 그대로 쓰면서 짧은 일상 이야기를 세로 웹툰식 인스타툰(한 박자 = 세로 4:5 한 장, 2~10장 캐러셀)으로 만드는 연출 템플릿 maru. 종이색 페이지 위 테두리 없는 장면 영역, 장면 위 내레이션 손글씨, 작은 캐릭터와 넓은 말풍선 자리, 읽는 순서대로 지그재그로 쌓이고 장면 밖으로 삐져나가는 말풍선, 캐릭터마다 색이 다른(기본 흰색) 그림자 깔린 둥근 사각형 말풍선, 박자마다 고르는 샷(투샷·클로즈업·뒤통수 너머·사물·리액션·말싸움·내레이션만)을 정한다. 모델은 spec(JSON)만 쓰고 스크립트가 영어 프롬프트를 조립·검사한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-template-cartoon-maru

## 목적

짧은 이야기를 인스타툰 캐러셀로 만든다. 이 skill이 정하는 것은 연출, 즉 한 장 안의 구성(내레이션·장면 영역·말풍선 자리), 말풍선 구도(읽는 순서·지그재그·겹침·화자 구분), 박자마다 고르는 샷이다. 그림체는 새로 정하지 않고 사용자가 고른 akbun-draw 스타일 skill의 것을 그대로 쓴다. 기본으로 어울리는 그림체는 [akbun-draw-dotori](../akbun-draw-dotori/SKILL.md)다.

4컷·격자처럼 한 장에 여러 컷을 담는 만화는 [akbun-draw-template-cartoon](../akbun-draw-template-cartoon/SKILL.md)을 쓴다. 글자는 [.claude/rules/image-lettering.md](../../../../.claude/rules/image-lettering.md)를 따른다. 내레이션·대사·효과음은 이미지 생성 모델이 그림과 같은 펜으로 직접 쓴다. 글씨 모양은 스크립트의 LETTERING 문장이 획(시작과 끝, 길이·기울기의 흔들림, 글자마다 다른 크기)으로 묘사한다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체 | 스타일 skill의 `references/style.jsonl`·`palettes.jsonl` | 사용자가 말한 스타일 skill. 말하지 않았으면 spec을 쓰기 전에 선택지 질문 도구로 묻고, 첫 선택지는 `akbun-draw-dotori`. 캐릭터를 그리는 그림체만 쓴다(사진풍 sena·juno, 다이어그램·글자·모션 skill은 맞지 않는다). 한 편에 그림체는 하나 |
| 페이지 구성·말풍선 구도 | [references/page.jsonl](references/page.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 spec이 이 규칙과 어긋나지 않게만 한다 |
| 박자마다 샷 | [references/shots.jsonl](references/shots.jsonl) | 아래 2단계의 샷 고르는 법 |
| 말풍선 종류 | [references/bubbles.jsonl](references/bubbles.jsonl) | 대사마다 `kind`. 보통은 `say`라서 뺀다 |
| spec 형식 예시 | [references/example/maru.json](references/example/maru.json) | 형식만 본다. 이야기·대사를 그대로 쓰지 않는다 |

라이브러리에 없는 샷·말풍선이 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. 박자 나누기

이야기를 2~10박자로 나눈다(기본 5~7). 한 박자는 한 장이고, 한 장에는 사건 하나와 그에 대한 말 몇 마디만 둔다. 첫 박자는 누가 어디서 무엇을 하려는지, 마지막 박자는 결말(웃음·깨달음·다짐)이다. 글만 받았으면 이야기를 지어내고 그 사실을 결과에 밝힌다. 출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `maru-output/<작업명>/`. spec은 그 폴더의 `maru.json`이다.

### 2. spec 쓰기

| 키 | 값 |
|---|---|
| `style` | 스타일 skill 이름(`akbun-draw-…`) |
| `palette` | 스타일 skill `palettes.jsonl`의 `id`. 빼면 첫 줄(기본 팔레트) |
| `fill` | 팔레트가 채우지 못한 `{자리표시자}` 값. 검사가 "fill에 값 필요"로 알려 줄 때만 쓴다. 비율 자리표시자는 `"portrait 4:5"` |
| `style_text` | 스타일 skill에 `references/style.jsonl`이 없을 때만. 그 skill의 그림체 규칙을 영어 10단어 이상으로 옮긴다 |
| `cast` | `[{"name", "look", "bubble"}]` 1~3명. `name`은 영어 한 단어, 중복 없이, `narrator` 금지. `look`은 종·색·옷을 담은 영어 4단어 이상. `bubble`은 그 캐릭터 말풍선 색 `#RRGGBB`, 캐릭터마다 다른 색. 스타일 팔레트의 옅은 색에서 고르고, 빼면 흰색. 그림 밖 목소리만 나오는 인물도 여기 넣는다 |
| `beats[].shot` | shots.jsonl `id` |
| `beats[].place` | 장소 영어 구절. 같은 장소는 글자 그대로 같게 쓴다. 없으면 뺀다 |
| `beats[].scene` | 이 장에서 일어나는 일, 영어 6~40단어(공백으로 나눈 수, 경계 포함). 캐릭터는 `name`으로 부른다. 그 장 프롬프트에는 `scene`에 이름이 나오거나 그림 안에서 말하는 캐릭터만 들어간다. `caption-only`면 뺀다 |
| `beats[].caption` | 내레이션, 한국어. `\n`으로 나눈 2줄 이하, 줄마다 1~16자(공백·문장부호 포함). `caption-only`면 필수이고 그 장은 `lines`·`sfx`를 뺀다. 없으면 뺀다 |
| `beats[].lines` | `[{"who", "text", "kind"}]`, 읽는 순서대로. 0~3개, `rapid-fire`는 3~5개(경계 포함). `who`는 `cast`의 `name`(`kind`가 `box`면 `narrator`). `text`는 한국어, `\n`으로 나눈 2줄 이하, 줄마다 1~12자 |
| `beats[].sfx` | 효과음, 한 줄 1~6자(공백·문장부호 포함, 경계 포함). `reaction`이면 필수, 그 밖에는 없으면 뺀다 |

한 장의 글자 합(caption·대사·sfx, 줄바꿈 제외)은 60자 이하다. 이미지 모델이 한글을 정확히 쓰도록 짧게 한다. 영어 문장(`style_text` 포함)에 폰트 이름·`font`·`typeface`를 쓰지 않는다. 검사는 `font`·`typeface` 낱말만 잡으므로 폰트 이름은 직접 피한다.

샷 고르는 법:

- 첫 장은 `two-shot`이나 `object`로 인물과 상황을 보여 준다.
- 혼잣말·뿌듯함·당황처럼 한 사람의 마음이 중심이면 `closeup`, 두 사람이 주고받는데 한쪽 반응이 중심이면 `over-shoulder`, 말이 빠르게 오가면 `rapid-fire`, 갑자기 놀라면 `reaction`.
- 숨 고르기·속마음 한 줄·결말 한 줄은 `caption-only`. 장면 없이 내레이션만 둔다.
- 같은 샷은 3장 연달아 쓰지 않고, 4장 이상이면 3종류 이상 쓴다(검사가 본다).

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 검사에 걸리면 프롬프트를 쓰지 않고 FAIL 이유를 보여 준다. spec을 고쳐 다시 돌린다.

spec을 검사하고 `maru.json` 옆에 `maru_01.txt` …를 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/maru_prompt.py build maru-output/<작업명>/maru.json
```

검사만 하려면 `build` 대신 `check`를 쓴다. 그림체 문장은 akbun-draw-template-cartoon의 `cartoon_prompt.py`와 같은 함수로 읽는다. 스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/maru_prompt.py --selftest
```

### 4. 이미지 생성

사용자가 이미지까지 요청했을 때만 만든다. 쓸 수 있는 이미지 생성 도구에 프롬프트 파일 전문을 그대로 넣고 비율은 portrait 4:5로 적는다. 모델은 사용자 설정의 기본값을 쓰고, 결과는 프롬프트 파일 옆에 같은 이름의 `.png`로 저장한다. `maru_01`을 먼저 만들고, 2번 장부터는 `maru_01.png`를 참고 이미지로 붙여 캐릭터를 맞춘다. 첫 장이 `caption-only`면 캐릭터가 처음 나오는 장을 먼저 만들어 참고 이미지로 쓴다.

### 5. 검수

결과를 가로로 붙여 한 번만 본다(template-cartoon 5단계의 명령, `cartoon_*` 대신 `maru_*`). 어긋난 장은 같은 프롬프트로 다시 생성하고, 몇 번 만에 맞았는지 결과 보고에 적는다. 글자가 계속 틀리면 그 대사를 더 짧게 고쳐 3단계부터 다시 한다.

- 장마다 테두리와 캐릭터 뒤 색 면 없이 종이 위에 장면이 그려지고, 내레이션이 장면 위 여백에 상자 없이 있다.
- 말풍선이 모서리 둥근 사각형에 아래로 밀린 납작한 그림자와 갈고리 꼬리가 있고, 위에서 아래로 대사 순서대로 놓이며, 서로 겹치거나 얼굴을 가리지 않는다.
- 말풍선이 캐릭터마다 spec의 `bubble` 색이고, 색이 없는 캐릭터는 흰색이다.
- 글씨가 획마다 손으로 쓴 듯 크기·기울기가 조금씩 다르고, 반듯하게 고른 인쇄 글자처럼 보이지 않는다.
- 대사·내레이션·효과음이 spec의 글자 그대로이고 그 밖의 글자가 없다.
- 같은 캐릭터가 모든 장에서 같고, 모든 장이 고른 스타일 skill의 그림체이며, 알려진 캐릭터·만화와 닮지 않았다.

## 결과 보고

스타일 skill·팔레트, 박자 표(번호·샷·내레이션·대사), 프롬프트 파일, 결과 이미지 경로, 검수 결과와 다시 생성한 횟수를 적는다. 이미지를 만들지 않았으면 "이미지 생성하지 않음"과 프롬프트 파일 경로를 적는다.

## 하지 말 것

- 글자를 폰트로 얹거나, 폰트를 받거나 설치하는 것.
- 이 skill에서 그림체·색 규칙을 새로 만드는 것. 바꿀 것이 있으면 스타일 skill의 jsonl을 고친다.
- 프롬프트 문장을 손으로 고치는 것. 바꿀 것이 있으면 spec이나 jsonl을 고친다.
- 한 장에 사건을 둘 이상 넣는 것.
