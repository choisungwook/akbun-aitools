---
name: akbun-draw-dotori
description: 따뜻한 갈색 붓펜 선, 콩 눈과 사선 볼터치를 단 2.5등신 캐릭터, 그늘 없는 차분한 단색, 색 면 없이 미색 종이 그대로인 배경으로 소소한 일상의 한 순간을 그리는 이미지 생성 프롬프트 스타일 dotori. 일상툰·인스타툰 그림체로 akbun-draw-template-cartoon-maru에 넣어 쓸 수 있다. 모델은 spec(JSON)만 쓰고, 스크립트가 references의 스타일·팔레트·캔버스 라이브러리로 영어 프롬프트를 조립하고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-dotori

## 목적

아무 소재를 dotori 그림체로 그리는 영어 이미지 생성 프롬프트를 만든다. 이 skill이 고정하는 것은 선·캐릭터 비율·채색·강조색 쓰는 법·배경이고, 무엇을 그릴지(소재·행동·소품)는 입력에 맞춰 정한다. 만화(말풍선·여러 컷)로 쓰려면 이 skill 이름을 [akbun-draw-template-cartoon-maru](../akbun-draw-template-cartoon-maru/SKILL.md)나 [akbun-draw-template-cartoon](../akbun-draw-template-cartoon/SKILL.md)의 `style`에 넣는다. 그때는 이 skill의 스크립트를 돌리지 않는다.

모델은 프롬프트 문장을 직접 쓰지 않는다. spec만 쓰고, 스타일 문장은 스크립트가 라이브러리에서 가져온다.

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 그림체(선·캐릭터·채색·배경·효과·질감·분위기) | [references/style.jsonl](references/style.jsonl) | 고르지 않는다. 스크립트가 전부 넣는다. 읽고 spec이 이 규칙과 어긋나지 않게만 한다 |
| 색 | [references/palettes.jsonl](references/palettes.jsonl) | 사용자가 정하지 않으면 `dotori`. 입력에 `soda`·`peach` 줄의 `topics` 낱말 하나가 글자 그대로 들어 있으면(부분 문자열, 영어는 대소문자 무시) 그 `id`, 둘 다 들어 있으면 `dotori` |
| 캔버스 | [references/canvases.jsonl](references/canvases.jsonl) | 사용자가 비율이나 쓰임을 말하면 그 `id`, 아무 말이 없으면 `portrait` |
| spec 형식 예시 | [references/example/](references/example/) | 형식만 본다. 소재를 그대로 쓰지 않는다 |

라이브러리에 없는 팔레트·캔버스가 필요하면 spec에 지어내지 말고, jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

### 1. spec 쓰기

입력에서 한 순간을 정한다(여러 장이면 장마다). 출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `dotori-output/<작업명>/`, 파일 이름은 `01_<id>.json`(`<id>`는 영어 소문자·하이픈).

| 키 | 값 |
|---|---|
| `palette`, `canvas` | jsonl의 `id` |
| `moment` | 어떤 순간인지 영어 6~30단어(공백으로 나눈 단어 수, a·the도 세고, 하이픈으로 이은 말은 한 단어, 경계 포함). 그림에 글자가 없으므로 시각·소리는 그림으로 쓴다 |
| `characters` | 1~3명(경계 포함). `[{"what": 누구인지 영어 2단어 이상, "doing": 무엇을 하는지 영어 2단어 이상}]`. 사람·동물 모두 된다. 옷·머리 모양은 캐릭터마다 다르게 정하고, 배치·위치는 쓰지 않는다 |
| `props` | 소품 영어 구절 0~2개, 중복 없이 |
| `accent_on` | 강조색을 칠할 것. `characters`의 `what`이나 `props` 한 항목 안에 낱말 단위로 들어 있는 말(대소문자 무시) |

### 2. 프롬프트 조립

spec을 채점하고 프롬프트 파일을 쓰는 명령이다. `<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 100점이 아니면 프롬프트를 쓰지 않고 FAIL 항목을 보여 준다. 고쳐서 다시 돌린다.

```bash
uv run --python 3.12 python -I <skill>/scripts/dotori_prompt.py build dotori-output/<작업명>/01_<id>.json -o dotori-output/<작업명>/01_<id>.txt
```

채점표만 보려면 `build` 대신 `check`를 쓴다. 채점은 위 표의 수치 외에 이것도 본다: 모델이 쓴 글은 영어(ASCII)만, 스타일을 깨는 낱말(3d·photorealistic·realistic·anime·gradient·neon·shading·glossy·watercolor·font·typeface) 없음.

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 python -I <skill>/scripts/dotori_prompt.py --selftest
```

### 3. 이미지 생성과 확인

사용자가 이미지까지 요청했을 때만 만든다. 쓸 수 있는 이미지 생성 도구에 프롬프트 파일 전문을 그대로 넣고, 비율은 캔버스대로(`portrait` 4:5, `square` 1:1, `wide` 16:9) 적는다. 모델은 사용자 설정의 기본값을 쓴다. 결과는 프롬프트 파일 옆에 같은 이름의 `.png`로 저장한다.

결과마다(여러 장이면 한 장으로 붙여 한 번만 보고) 아래를 확인한다. 어긋난 장은 같은 프롬프트로 다시 생성한다.

- 선이 따뜻한 갈색 붓펜 선이고 순검정이 아니다.
- 캐릭터가 약 2.5등신이고, 눈이 세로 콩 모양, 볼이 짧은 사선 세 개이며 코가 없다.
- 면에 그늘·그라데이션이 없고, 강조색이 `accent_on` 하나에만 있다.
- 캐릭터 뒤에 색 조각·색 면·배경 묘사가 없고 미색 종이 그대로다.
- 글자·말풍선이 없고, 알려진 캐릭터와 닮지 않았다. 닮았으면 `characters`의 생김새를 바꿔 build부터 다시 하고, 무엇을 바꿨는지 결과 보고에 적는다.

## 결과 보고

장마다 spec 파일, 프롬프트 파일, 채점 점수, 고른 팔레트·캔버스를 적는다. 이미지를 만들었으면 경로와 위 확인 결과를, 만들지 않았으면 "이미지 생성하지 않음"을 적는다.

## 하지 말 것

- 프롬프트 문장을 손으로 고치거나 라이브러리 밖 스타일 문구를 덧붙이는 것. 바꿀 것이 있으면 jsonl을 고친다.
- 사실적인 얼굴·비율로 그리는 것, 알려진 캐릭터를 따라 하는 것.
- 캐릭터 뒤에 색 면을 깔거나 배경을 자세히 그리는 것.
