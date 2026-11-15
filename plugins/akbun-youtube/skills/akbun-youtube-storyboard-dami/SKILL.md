---
name: akbun-youtube-storyboard-dami
description: 사용자가 준 아이디어나 글귀를 분석해 YouTube에 올릴 영상의 스토리보드와 대본을 만드는 skill. 얼굴을 드러내지 않는 채널을 전제로 핵심 메시지 한 문장, 파트, 컷(길이·샷·집중을 만드는 움직임·연출 의도·대본)을 spec(JSON)에 쓰면 스크립트가 검사하고, 편집 가능한 storyboard.pptx(개요, DaVinci Resolve식 타임라인, BGM·후시녹음·효과음 계획, 컷마다 스케치 틀)와 script.md를 만든다. 스케치는 글자·얼굴 없는 흑백 연필 그림이고 이미지까지 요청했을 때만 쓸 수 있는 이미지 생성 도구로 그린다. IT 실습, IT 핵심 메시지 설명, 얼굴 없는 말하기 브이로그, 일상 기록, 여행 브이로그 다섯 장르를 다룬다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-youtube-storyboard-dami

## 목적

아이디어나 글귀를 영상 제작용 스토리보드와 대본으로 바꾼다. 독자가 더 쉽고 재밌게 이해하는 것이 목표다. 사용자는 얼굴을 드러내지 않고, 편집은 DaVinci Resolve에서 하며, 화면 녹화는 별도 도구로 하고, 후시녹음(영상을 보며 마이크로 녹음)이 가능하다. 모션그래픽과 사운드트랙은 AI로 만들 수도 있다. 이 skill은 무엇을 어떻게 보여 주고 어디서 말할지를 정하고, 영상 편집과 업로드는 하지 않는다.

모델은 `storyboard.json`(spec)만 쓴다. 검사·프롬프트 조립·pptx·대본은 스크립트가 만든다. 이유는 [references/decisions.md](references/decisions.md).

## 무엇을 정할 때 어느 파일

| 정할 것 | 파일 | 고르는 법 |
|---|---|---|
| 판단이 갈릴 때 돌아갈 생각 | [references/philosophy.md](references/philosophy.md) | 가장 먼저 읽는다. 도입부는 궁금증 먼저, 중반은 답을 향해 곧장, 반응할 거리 하나 |
| 핵심 메시지·파트·컷 나누기, 대본 쓰기 | [references/story.md](references/story.md) | 입력 분석 순서를 따른다 |
| 장르·기본 파트·훅 길이 | [references/genres.jsonl](references/genres.jsonl) | 소재에 맞는 `id` 하나 |
| 컷마다 샷 | [references/shots.jsonl](references/shots.jsonl) | 컷이 보여 줄 것에 맞는 `id`. `genres`는 어울리는 장르 안내이고 검사하지 않는다. 제작자 얼굴 대신 손·뒷모습·1인칭·화면·사물 |
| 컷마다 집중을 만드는 움직임 | [references/moves.jsonl](references/moves.jsonl) | 목적이 있을 때만. 없으면 `hold` |
| BGM·효과음·후시녹음 구간 | [references/sound.md](references/sound.md) | 서술로 쓴다. 서비스 이름을 쓰지 않는다 |
| 스케치 프롬프트와 검수 | [references/sketch.md](references/sketch.md) | `sketch` 문장 쓰는 법, 얼굴·글자 금지 |
| spec 키와 검사 규칙 | [references/spec.md](references/spec.md) | 키 표와 수치 |
| pptx 장 구성과 타임라인 읽는 법 | [references/deck.md](references/deck.md) | 결과를 사용자에게 설명할 때 |
| spec 형식 예시 | [references/example/storyboard.json](references/example/storyboard.json) | 형식만 본다. 주제·대본을 그대로 쓰지 않는다 |
| 실제 결과물과 전·후 비교 | [examples/README.md](examples/README.md) | 결과가 어떻게 생겼는지 볼 때. skill을 고쳤으면 같은 변경에서 예시 PNG를 다시 만들어 덮어쓴다 |

라이브러리에 없는 장르·샷·움직임이 필요하면 spec에 지어내지 말고 jsonl에 한 줄을 더하는 변경으로 사용자에게 제안한다.

## 작업 흐름

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 출력 폴더는 사용자가 정한 곳, 없으면 작업 디렉터리 아래 `storyboard-output/<작업명>/`이고 아래 파일이 그 안에 생긴다.

```text
storyboard.json  prompts/cut_01.txt…  sketches/cut_01.png…  storyboard.pptx  script.md
```

### 1. 입력 분석

philosophy.md를 먼저 읽고, story.md의 순서로 대상·행동·장르·핵심 메시지 한 문장을 정한다. 글만 받았으면 모르는 부분은 가정으로 정하고 결과에 밝힌다.

### 2. spec 쓰기

출력 폴더에 `storyboard.json`을 쓴다. 키와 값은 spec.md, 컷 나누기와 대본은 story.md, 사운드는 sound.md를 따른다. 컷마다 `source`로 화면 녹화·촬영·모션그래픽·사진·자료를 정하고, 말이 필요한 구간이 후시녹음이면 `voice`와 `adr_reason`을 적는다.

### 3. 검사

실패 이유를 전부 보여 주므로 한 번에 고친다. 통과할 때까지 2단계로 돌아간다. 실행은 `uv run`이 스크립트 맨 위 inline metadata의 의존성을 읽는 이 형태다. `python -I`로 부르면 의존성을 못 읽어 `build`가 실패한다.

spec만 검사하는 명령이다.

```bash
uv run --python 3.12 <skill>/scripts/dami_storyboard.py check storyboard-output/<작업명>/storyboard.json
```

### 4. 스케치 생성 (요청 시)

사용자가 이미지까지 요청했을 때만 한다. 프롬프트 파일을 만든 뒤 쓸 수 있는 이미지 생성 도구에 파일 전문을 그대로 넣어 `sketches/cut_NN.png`로 저장한다. 순서와 일관성 맞추기는 sketch.md를 따른다. 요청하지 않았으면 건너뛴다. pptx에 회색 자리표시가 들어간다.

컷마다 `prompts/cut_NN.txt`를 쓰는 명령이다.

```bash
uv run --python 3.12 <skill>/scripts/dami_storyboard.py prompts storyboard-output/<작업명>/storyboard.json
```

### 5. pptx·대본 만들기

`storyboard.pptx`와 `script.md`를 만드는 명령이다. `sketches/`에 그림이 있으면 틀 안에 들어간다.

```bash
uv run --python 3.12 <skill>/scripts/dami_storyboard.py build storyboard-output/<작업명>/storyboard.json
```

스크립트나 jsonl을 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 <skill>/scripts/dami_storyboard.py --selftest
```

### 6. 검수와 결과 보고

스케치를 만들었으면 sketch.md의 검수 다섯을 본다. 보고에는 핵심 메시지, 장르, 답이 나오는 컷과 반응 요소, 총 길이와 컷 수, 후시녹음 구간 수, 생성한 스케치 수와 다시 그린 횟수, 가정한 것, 출력 폴더 경로를 적는다. 스케치를 만들지 않았으면 "스케치 생성하지 않음"을 적는다.

## 하지 말 것

- 제작자 얼굴을 그리는 것. 스케치에 글자를 그리는 것.
- 특정 이미지 생성 도구·모델·CLI 명령, 특정 음원 서비스, 폰트 이름을 프롬프트나 spec에 쓰는 것.
- 시각을 spec에 직접 쓰는 것. 컷 `dur`만 쓰고 시각은 스크립트가 센다.
- agent가 프롬프트 파일이나 pptx를 직접 고치는 것. 바꿀 것이 있으면 spec이나 jsonl을 고쳐 다시 만든다. pptx를 손으로 고치는 것은 사용자의 몫이다.
- pptx를 저장소에 올리는 것. 대표 예시는 examples/에 PNG로만 둔다.
