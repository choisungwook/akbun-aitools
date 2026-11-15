---
name: akbun-youtube-storyboard-dami-detail
description: akbun-youtube-storyboard-dami(summary 모드)가 만든 스토리보드를 detail 모드로 바꾸는 skill. 구성·컷 길이·대본은 그대로 두고 컷마다 초 단위 비트(화면에서 일어나는 일과 자막·소리), 실제 명령·화면 문구, 녹화 방법, AI 영상 생성 프롬프트를 spec에 더하면 스크립트가 검사하고 컷 하나당 한 장인 detail.pptx를 만든다. 원리·컷 나누기·대본·스케치 규칙은 summary skill 문서에 링크로 따른다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-youtube-storyboard-dami-detail

## 목적

summary 모드의 스토리보드는 무엇을 왜 보여 줄지 정한다. detail 모드는 그 결정을 바꾸지 않고, 컷마다 몇 초에 화면에서 무엇이 일어나는지를 촘촘히 적어 사람이 바로 녹화하거나 AI로 영상을 만들 수 있게 한다.

이 skill은 summary skill([akbun-youtube-storyboard-dami](../akbun-youtube-storyboard-dami/SKILL.md))의 spec·검사·스케치를 그대로 쓰고, detail 키와 detail.pptx만 맡는다. summary 규칙을 이 문서에 옮겨 적지 않는다.

| | summary (기본) | detail |
|---|---|---|
| skill | akbun-youtube-storyboard-dami | 이 skill |
| 산출물 | `storyboard.pptx`(개요·타임라인·사운드·한 장에 컷 3개), `script.md` | `detail.pptx`(공통 규칙 한 장 + 컷 하나당 한 장) |
| 컷마다 적는 것 | 샷·움직임·화면 한 줄·의도·대본 | 위에 더해 비트 표, 녹화 방법 또는 AI 영상 프롬프트 |
| 쓸 때 | 구성과 대본을 먼저 검토할 때 | 구성이 정해져 녹화·제작을 시작할 때 |

## 무엇을 정할 때 어느 파일

`<summary>`는 `../akbun-youtube-storyboard-dami/`, `<skill>`은 이 `SKILL.md`가 있는 디렉터리다.

| 정할 것 | 파일 |
|---|---|
| 판단이 갈릴 때 돌아갈 생각, 컷 나누기, 대본 | [`<summary>`/references/philosophy.md](../akbun-youtube-storyboard-dami/references/philosophy.md), [story.md](../akbun-youtube-storyboard-dami/references/story.md) |
| summary spec 키와 검사 | [`<summary>`/references/spec.md](../akbun-youtube-storyboard-dami/references/spec.md) |
| 스케치 프롬프트와 검수 | [`<summary>`/references/sketch.md](../akbun-youtube-storyboard-dami/references/sketch.md) |
| detail 키, 비트·녹화·AI 프롬프트 쓰는 법, 검사 규칙 | [references/detail.md](references/detail.md) |
| 형식 예시와 실제 결과 | [examples/README.md](examples/README.md) |

## 작업 흐름

### 1. summary 결과 확인

출력 폴더에 `storyboard.json`이 있고 summary `check`를 통과해야 한다. 없으면 summary skill의 작업 흐름 1~5를 먼저 한다(스케치는 이미지까지 요청했을 때만).

### 2. 입력 다시 읽기

원문과 예시 코드에서 실제 명령, 출력 줄, UI 이름, URL, 수치를 모은다. 비트와 녹화 방법은 이 값으로 쓴다. 입력에서 찾지 못한 값은 지어내지 않고 `확인 필요`로 적는다. 공개 자료(공지, 공식 문서)로 확인할 수 있으면 찾아서 채우고 출처 URL을 `record`에 적는다.

### 3. detail 키 쓰기

같은 `storyboard.json`에 컷마다 `beats`와 `record` 또는 `ai_prompt`를, 최상위에 `motion_style`(모션그래픽 컷이 있을 때)과 `production`(선택)을 더한다. 쓰는 법은 detail.md다. 컷 `dur`·순서·`narration`은 바꾸지 않는다. 바꿔야 하면 summary 규칙으로 고치고 summary `build`도 다시 한다.

### 4. 검사

summary 검사와 detail 키 검사를 한 번에 돌리는 명령이다. 실패 이유를 전부 보여 주므로 한 번에 고친다.

```bash
uv run --python 3.12 <skill>/scripts/dami_detail.py check storyboard-output/<작업명>/storyboard.json
```

### 5. 스케치

summary에서 만든 `sketches/cut_NN.png`가 있으면 그대로 쓰고, 없으면 그림 자리 없이 만든다. 3단계에서 장면 자체를 바꾼 컷만 `sketch` 문장을 고치고 summary의 `prompts`와 sketch.md 순서로 다시 그린다.

### 6. detail.pptx 만들기

spec 옆에 `detail.pptx`를 만드는 명령이다. `sketches/`에 그림이 있으면 장마다 들어간다.

```bash
uv run --python 3.12 <skill>/scripts/dami_detail.py build storyboard-output/<작업명>/storyboard.json
```

스크립트나 detail.md의 수치를 고쳤으면 자체 검사가 `selftest ok`를 내는지 먼저 본다.

```bash
uv run --python 3.12 <skill>/scripts/dami_detail.py --selftest
```

### 7. 결과 보고

보고에는 컷 수와 총 길이, 녹화 컷 수와 AI 프롬프트 컷 수, `확인 필요`로 남긴 값과 공개 자료로 채운 값(출처 URL), 다시 그린 스케치 수, 출력 폴더 경로를 적는다.

## 하지 말 것

- summary 규칙(철학, 컷 나누기, 대본, 스케치)을 이 skill 문서에 복사하는 것. 링크로 따른다.
- 특정 이미지·영상 생성 도구, 모델, CLI 명령, 음원 서비스, 폰트 이름을 spec이나 프롬프트에 쓰는 것.
- `ai_prompt`에 화면 글자·라벨·얼굴을 넣는 것. 라벨은 `overlay`와 비트의 자막·소리 칸에 쓰고 편집에서 얹는다.
- 입력에 없는 명령 출력이나 화면 문구를 지어내는 것.
- agent가 `detail.pptx`를 직접 고치는 것. spec을 고쳐 다시 만든다.
