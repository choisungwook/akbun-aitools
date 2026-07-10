---
name: akbun-make-explainer-video
description: "개념 해설 영상, 설명 영상, 강의 영상을 만들어 달라고 명시적으로 요청할 때만 사용한다. HyperFrames(오픈소스)로 HTML composition을 작성해 어두운 배경의 도형·수식 애니메이션 MP4를 렌더링한다."
---

# akbun 개념 해설 영상 생성

수학·기술 개념을 어두운 배경 위 도형·화살표·수식 애니메이션으로 풀어내는 해설 영상 스킬이다.
HyperFrames(HTML → MP4, Apache 2.0 오픈소스)로 composition을 작성하고 로컬에서 렌더링한다.
스타일(색·모션 언어)은 고정하고, 무엇을 그릴지(주제·구도)는 입력에 맞춰 자유롭게 정한다.

## 사전 준비

Node.js 22 이상과 FFmpeg가 필요하다. 아래 명령으로 의존성을 점검한다.

```bash
npx -y hyperframes doctor
```

- FFmpeg가 없으면 OS 패키지 매니저로 설치한다(예: `apt-get install -y ffmpeg`, `brew install ffmpeg`).
- 렌더링용 Chrome이 없으면 `npx hyperframes browser ensure`로 내려받는다.
- whisper, TTS(Kokoro), MusicGen 항목은 optional이다. 없어도 영상 렌더링에는 지장 없다.
- `npm install hyperframes`가 postinstall 바이너리 다운로드(onnxruntime 등)로 실패하는 환경에서는
  `npm install hyperframes --ignore-scripts`로 설치한다. 전사(transcribe) 기능만 빠지고 렌더링은 동작한다.

## workflow

1. 요구를 정리한다.
- 주제, 대상 독자, 길이(기본 30~60초), 해상도(기본 1920x1080 landscape), 언어(기본 한국어)를 정한다.
- 내레이션 오디오나 배경음악 파일을 받았는지 확인한다. 없으면 텍스트가 내레이션 역할을 한다.

2. 장면(scene)을 설계한다.
- 장면당 5~15초, 장면마다 "핵심 문장 1개 + 시각 요소 1세트(도형/화살표/수식)"로 제한한다.
- 전체 흐름은 `질문 제시 -> 시각적 직관 -> 정식 표현(수식·정의) -> 요약` 순서를 기본으로 한다.
- 장면 목록을 표(시작~끝 시간, 핵심 문장, 시각 요소)로 먼저 사용자에게 보여주고 진행한다.

3. 프로젝트를 만든다.

```bash
npx hyperframes init <프로젝트명> --example blank --non-interactive
```

4. `index.html`에 composition을 작성한다.
- 문법과 규칙은 `references/hyperframes.md`를 따른다. 특히 track 겹침 금지와 seekable timeline 규칙을 지킨다.
- 색·타이포·모션은 `references/style.md`의 스타일 토큰을 그대로 사용한다.

5. 검증한다.

```bash
npx hyperframes lint
npx hyperframes snapshot --at <장면별 대표 시각들>
```

- lint 오류를 모두 해결한다.
- snapshot PNG를 직접 읽어 `references/style.md`의 체크리스트로 확인한다. 어긋나면 수정 후 다시 snapshot.

6. 렌더링한다.

```bash
npx hyperframes render
```

- 결과는 `renders/*.mp4`에 생긴다. 절대 경로, 길이, 해상도를 사용자에게 안내한다.

## 금지 사항

- 실시간 기반 애니메이션(`setInterval`, `requestAnimationFrame`, autoplay CSS animation) 사용 금지.
  모든 모션은 paused GSAP timeline로 작성해 어느 프레임에서든 seek 가능해야 한다.
- 한 장면에 포인트 색 3개 초과 금지, 핵심 문장 2개 이상 금지.
- 입력에 없는 사실·수식을 지어내지 않는다. 개념 설명이 불확실하면 렌더링 전에 사용자에게 확인한다.
