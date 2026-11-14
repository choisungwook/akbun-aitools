---
name: akbun-draw-sena
description: 바랜 35mm 필름 입자와 무른 초점, 들뜬 갈색·남색 그림자, 해 질 녘·블루아워·나트륨 가로등 같은 실제 광원, 아날로그 시대 사물로 사람 없는 조용한 한 장면을 사진처럼 그리는 이미지 생성 프롬프트 스타일 sena. 모델은 장면 spec(JSON)만 쓰고, 스크립트가 references의 스타일·팔레트 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-sena

## 목적

아무 장면을 sena 스타일로 담는 16:9 영어 이미지 생성 프롬프트를 만든다. 이 skill이 고정하는 것은 필름 입자·초점·톤·빛·아날로그 시대 사물과 사람이 막 떠난 듯한 분위기이고, 무엇을 찍을지(장소·사물)는 입력에 맞춰 정한다.

모델은 프롬프트 문장을 직접 쓰지 않는다. spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다. 그래서 몇 장을 만들어도 같은 사진체가 나온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 사진체(입자·초점·톤·빛·시대·분위기) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 장면이 이 규칙(특히 아날로그 시대 사물, 사람 없음)과 어긋나지 않게만 한다 |
| 색 보정 | [references/palettes.jsonl](references/palettes.jsonl) | 기본 `golden-hour`. 장면의 시간·장소가 다른 줄의 `use`와 맞을 때만 그 `id`. 두 줄이 다 맞으면 화면 대부분을 비추는 빛(실내 전구인지 바깥 가로등·하늘인지)으로 고른다 |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 소재를 그대로 쓰지 않는다 |

라이브러리에 없는 팔레트가 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. 장면 정하기

입력에서 장면 하나를 정한다(여러 장이면 장면마다). 글만 있으면 가장 일상적인 한 순간을 고르고, 지어낸 장면임을 결과에 밝힌다. 장면마다 `<id>`(영어 소문자·하이픈 짧은 이름, 예: `closed-bakery`)를 붙인다.

### 2. spec 쓰기

출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `film-output/<작업명>/`이고, build 전에 폴더를 먼저 만든다. 사람이 나오는 요청(손님·승객)은 사람 대신 그 사람이 남긴 흔적(식은 찻잔, 벗어 둔 코트)을 `props`에 둔다.

| 키 | 값 |
|---|---|
| `palette` | palettes.jsonl의 `id` |
| `scene` | 어떤 순간인지 영어 6~40단어(공백으로 나눈 수, 경계 포함) |
| `setting` | 어디인지 영어 한 구절, 빈칸 불가 |
| `props` | 화면에서 알아봐야 할 사물 영어 구절 1~6개(경계 포함), 중복 없이 |

### 3. 프롬프트 조립

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 채점이 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

spec을 채점하고 프롬프트 파일을 쓰는 명령이다.

```bash
uv run --python 3.12 python -I <skill>/scripts/film_prompt.py build film-output/<작업명>/01_<id>.json -o film-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 모델이 쓴 글이 영어(ASCII)인지, 금지 낱말(human·person·people·man·woman·boy·girl·child·face·portrait·customer·passenger·crowd·pedestrian·couple·driver·hand·silhouette, 3d·cgi·render·illustration·cartoon·anime·vector·neon·hdr·4k·8k·ultra·sharp·smartphone·cyberpunk)이 없는지 본다. 낱말은 대소문자를 가리지 않고 단어 경계로 센다.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다. 예시 spec을 고쳤으면 예시 txt도 `build`로 다시 쓴다.

```bash
uv run --python 3.12 python -I <skill>/scripts/film_prompt.py --selftest
```

### 4. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 프롬프트 파일 전문을 그대로 넣어 만든다.

사용자가 쓰는 이미지 생성 도구와 기본 모델로 `film-output/<작업명>/01_<id>.txt`를 16:9 가로로 만들어 같은 폴더에 `01_<id>.png`로 저장한다. 여러 장은 장마다 따로, 동시에 만들어도 된다.

여러 장이면 결과를 한 장으로 붙여 한 번만 보고 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다.

- 디지털처럼 또렷하지 않고 필름 입자·무른 초점·광원 번짐이 보인다.
- 순검정·쨍한 색이 없고 팔레트 색 기운이 화면 전체를 덮는다.
- 사람·얼굴·손이 없고, 스마트폰·LED 화면·최신 차량 같은 요즘 사물이 없다.
- 그림 안에 읽히는 글자·로고·워터마크가 없다.
- 알려진 영화·사진·앨범 표지 장면과 닮지 않았다. 닮았으면 setting·props를 바꿔 build부터 다시 한다.

## 결과 보고

장면마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 팔레트를 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다. 프롬프트는 한 개의 `text` 코드블록으로도 보여 준다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 사람·얼굴·손을 장면에 넣는 것, 알려진 영화·사진·앨범 표지 장면을 따라 하는 것.
- 그림 안에 글자(제목·자막·간판 문구)를 넣는 것.
