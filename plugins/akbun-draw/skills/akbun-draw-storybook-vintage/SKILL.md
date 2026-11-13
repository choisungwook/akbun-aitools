---
name: akbun-draw-storybook-vintage
description: 20세기 초중반 그림책 컬러 삽화처럼 가는 갈색 연필 윤곽, 겹쳐 칠한 투명 수채와 과슈 하이라이트, 고르게 얼룩진 한 색 바탕, 바랜 인쇄 종이결로 사람 없는 다정한 한 장면을 그리는 이미지 생성 프롬프트 스타일 vintage. 모델은 장면 spec(JSON)만 쓰고, 스크립트가 references의 스타일·팔레트 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-storybook-vintage

## 목적

아무 장면을 vintage 그림책 삽화 스타일로 담는 16:9 영어 이미지 생성 프롬프트를 만든다. 이 skill이 고정하는 것은 선·칠·바탕·빛·인쇄 질감과 옛이야기 같은 분위기이고, 무엇을 그릴지(사물·동물·장소)는 입력에 맞춰 정한다.

모델은 프롬프트 문장을 직접 쓰지 않는다. spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다. 그래서 몇 장을 만들어도 같은 그림체가 나온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체(선·칠·바탕·빛·인쇄 질감·분위기) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 장면이 이 규칙(사람 없음, 옷 입은 동물 없음)과 어긋나지 않게만 한다 |
| 색 | [references/palettes.jsonl](references/palettes.jsonl) | 기본 `periwinkle`. 장면이 다른 줄의 `use`와 맞을 때만 그 `id`. 두 줄이 다 맞으면 화면 넓이를 더 차지하는 쪽(식물인지 실내 불빛인지)으로 고른다 |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 소재를 그대로 쓰지 않는다 |

라이브러리에 없는 팔레트가 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. 장면 정하기

입력에서 장면 하나를 정한다(여러 장이면 장면마다). 글만 있으면 가장 조용한 한 순간을 고르고, 지어낸 장면임을 결과에 밝힌다. 장면마다 `<id>`(영어 소문자·하이픈 짧은 이름, 예: `card-catalog`)를 붙인다. 개념(예: 캐시, 인덱스)을 그려 달라는 요청이면 그 개념을 옛 사물·자연물 하나로 비유한다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `storybook-output/<작업명>/`이고, build 전에 폴더를 먼저 만든다. 사람이 나오는 요청은 사람 대신 그 사람이 남긴 사물(놓고 간 바구니, 켜 둔 촛불)을 `subjects`에 둔다. 동물은 옷·모자·장갑 없이 동물 그대로 둔다.

| 키 | 값 |
|---|---|
| `palette` | palettes.jsonl의 `id` |
| `scene` | 어떤 순간인지 영어 6~40단어(공백으로 나눈 수, 경계 포함) |
| `setting` | 어디인지 영어 한 구절, 빈칸 불가, 마침표로 끝내지 않음 |
| `subjects` | 화면에서 알아봐야 할 사물·동물 영어 구절 1~5개(경계 포함), 대소문자·앞뒤 공백을 무시하고 중복 없이 |

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/storybook_prompt.py build storybook-output/<작업명>/01_<id>.json -o storybook-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 모델이 쓴 글이 영어(ASCII)인지, 금지 낱말 네 묶음이 없는지 본다. 사람(human·person·people·man·woman·boy·girl·child·kid·face·portrait·princess·prince·king·queen·hand·silhouette), 옷(coat·jacket·waistcoat·vest·dress·hat·glove·shoe·clothes·clothing·wearing), 스타일을 깨는 말(photo·photorealistic·realistic·3d·cgi·render·anime·vector·neon·hdr·4k·8k·ultra·glossy·cyberpunk), 그림 안 글자(text·letter·lettering·word·title·caption·sign·signboard·label·logo·book cover). 낱말은 대소문자를 가리지 않고 단어 경계로 세며, 복수형도 센다.

스크립트나 jsonl을 고쳤으면 예시 txt를 `build`로 다시 쓰고 자체 검사가 `selftest ok`를 내는지 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/storybook_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 프롬프트 파일 전문을 그대로 넣어 만든다.

codex CLI를 쓸 때, 프롬프트 파일이 있는 폴더에서 내장 이미지 생성으로 PNG를 만드는 명령이다. 모델은 사용자 설정의 기본값을 쓴다. 이미지 도구가 품질(quality)·복잡도(complexity)를 받으면 둘 다 low로 요청해 빨리 만든다.

```bash
cd storybook-output/<작업명> && codex exec --skip-git-repo-check -s workspace-write "Read 01_<id>.txt. Use your built-in image generation tool with that file's full text as the prompt, exactly, landscape 16:9, low quality and low complexity for speed. Save the result as 01_<id>.png here. Reply with the path only." < /dev/null
```

`< /dev/null`이 없으면 codex가 입력을 기다리며 멈춘다. 여러 장은 장마다 이 명령을 따로 돌리고, 동시에 돌려도 된다.

여러 장이면 결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다.

- 사진·3D·매끈한 디지털 칠이 아니라 갈색 연필 윤곽과 겹친 수채 칠이 보인다. 검은 굵은 외곽선이 없다.
- 바탕이 팔레트 바탕색 한 가지로 고르게 얼룩져 있고, 화면 전체에 바랜 종이결이 보인다.
- 사람·얼굴·손이 없고, 동물이 옷을 입지 않았다.
- 그림 안에 읽히는 글자·제목·로고·워터마크가 없다.
- 알려진 그림책·동화 삽화의 캐릭터나 장면과 닮지 않았다. 닮았으면 setting·subjects를 바꿔 build부터 다시 한다.

## 결과 보고

장면마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 팔레트를 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다. 프롬프트는 한 개의 `text` 코드블록으로도 보여 준다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 사람·얼굴·손, 옷 입은 동물을 장면에 넣는 것, 알려진 그림책·동화의 캐릭터·장면을 따라 하는 것.
- 그림 안에 글자(제목·책 표지 문구·간판)를 넣는 것.
