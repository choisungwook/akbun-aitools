---
name: akbun-draw-title-nib
description: 이미 있는 그림 위에 옛 그림책 표지처럼 손으로 그린 제목·부제를 넣는 이미지 편집 스타일 nib. 획 대비가 큰 세리프(한글은 붓 명조 같은 획), 한 가지 잉크색, 테두리·그림자·박스 없이 그림 질감 위에 칠한 글자. 폰트를 쓰지 않고 이미지 생성 모델이 글자를 그림의 일부로 그린다. 모델은 spec(JSON)만 쓰고, 스크립트가 references 라이브러리로 영어 편집 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-title-nib

## 목적

그림 한 장과 제목(부제는 선택)을 받아, 그 그림 위에 nib 스타일 title을 그려 넣은 새 그림을 만든다. 이 skill이 고정하는 것은 글자의 획 모양·크기 비율·잉크·마감이고, 글자를 어디에 둘지는 그림마다 이미지 모델이 비어 있는 곳으로 정한다.

글자는 폰트로 얹지 않는다. 이미지 생성 모델이 그림의 붓질과 같은 결로 그린다. 그래서 철자가 틀리면 글자를 덮어 고치지 않고 다시 생성한다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 글자 스타일(획·부제·마감·자리·보존) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다 |
| 잉크색 | [references/inks.jsonl](references/inks.jsonl) | 기본 `navy`. 그림이 어두우면 `cream`, 밝고 주황·갈색 기운이면 `sepia`. 채점의 명도 대비가 3:1 미만이면 다른 줄로 바꾼다 |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 문구를 그대로 쓰지 않는다 |

## 작업 흐름

### 1. 문구 정하기

제목은 그림의 내용을 한눈에 부르는 짧은 말로, 부제는 필요할 때만 한 줄로 쓴다. 사용자가 문구를 주면 그대로 쓰고, 없으면 지어낸 뒤 결과에 밝힌다. 기존 책·영화·노래·브랜드의 제목이나 문구를 쓰지 않는다. 그림마다 `<id>`(영어 소문자·하이픈 짧은 이름)를 붙인다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `title-output/<작업명>/`이고, 먼저 만든다. 원본 그림을 그 폴더에 `01_<id>.jpg`(또는 png)로 복사하고 spec은 `01_<id>.json`이다.

| 키 | 값 |
|---|---|
| `image` | 원본 그림 경로, spec 파일이 있는 폴더 기준 |
| `ink` | inks.jsonl의 `id` |
| `title` | 제목 한 줄, 1~20자(공백 포함, 앞뒤 공백 제외, 경계 포함) |
| `subtitle` | 부제 한 줄, 0~40자(같은 방식), 없으면 `""` |

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 --with pillow python -I <skill>/scripts/title_prompt.py build title-output/<작업명>/01_<id>.json -o title-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 줄바꿈·큰따옴표가 없는지, 폰트·브랜드를 가리키는 말(font·typeface·폰트·글꼴·서체, 폰트 이름 일부(예: garamond·helvetica·nanum), logo·로고, ™·®·©)이 없는지, 잉크와 그림 평균색의 명도 대비(WCAG 상대 휘도)가 3:1 이상인지 본다. 평균색은 그림 전체를 한 화소로 줄인 값이라 대략값이다.

스크립트나 jsonl을 고쳤으면 예시 txt를 `build`로 다시 쓰고 자체 검사가 `selftest ok`를 내는지 본다.

```bash
uv run --python 3.12 --with pillow python -I <skill>/scripts/title_prompt.py --selftest
```

### 4. 그림에 그리기

codex CLI로 원본 그림에 title을 그리는 명령이다. 모델은 사용자 설정의 기본값을 쓴다. 프롬프트를 `-i` 앞에 둔다. `-i`는 값을 여러 개 받아서, 뒤에 두면 프롬프트까지 이미지 경로로 먹고 "No prompt provided"로 끝난다.

```bash
cd title-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read 01_<id>.txt. Edit the attached image 01_<id>.jpg with your built-in image generation tool: use that file's full text as the edit prompt, exactly, keep the original aspect ratio. Save the result as 01_<id>-after.png here. Reply with the path only." -i 01_<id>.jpg < /dev/null
```

`< /dev/null`이 없으면 codex가 입력을 기다리며 멈춘다. 여러 장은 장마다 따로, 동시에 돌려도 된다.

결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성하되 장마다 2번까지만 하고, 그래도 어긋나면 그 항목을 결과 보고에 적는다.

- 제목·부제가 spec과 한 글자도 다르지 않고, 다른 글자가 없다.
- 글자가 주 소재를 가리지 않는다.
- 제목이 획 대비가 큰 세리프이고, 한글이면 고딕이 아니라 붓 명조 같은 획이다. 부제가 제목보다 확실히 작고 자간이 넓다.
- 테두리·그림자·박스 없이 그림 질감 위에 칠한 잉크로 보인다.
- 그림 자체의 구도·색·화풍이 원본과 크게 다르지 않다. 편집은 그림 전체를 다시 그리므로 작은 차이는 생긴다.
- 알려진 책 표지·로고·포스터의 글자 모양과 닮지 않았다.

## 결과 보고

장마다 spec 파일, 프롬프트 파일, 채점 점수(명도 대비 값 포함), 고른 잉크, 결과 그림 경로, 몇 번째 생성에서 맞았는지와 위 확인 결과를 적는다. 그림을 만들지 않았으면 "이미지 생성하지 않음"을 적는다.

## 하지 말 것

- 폰트 파일을 받거나 Pillow·SVG로 글자를 얹는 것. 철자가 틀린 글자를 덮어 고치는 것.
- 프롬프트에 폰트 이름·브랜드·특정 책이나 작품을 쓰는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 프롬프트 문장을 손으로 고치는 것.
