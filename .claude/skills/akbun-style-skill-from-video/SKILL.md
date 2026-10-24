---
name: akbun-style-skill-from-video
description: 사용자가 유튜브 영상 링크를 주며 "이 영상 스타일로 skill을 만들어"라고 할 때, 영상을 내려받아 스타일을 뽑고 akbun-draw 또는 akbun-editvideo 플러그인에 스타일 skill을 추가해 README 예시·PR까지 올리는 이 저장소 전용 절차. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-style-skill-from-video

영상 한 편을 받아 그 영상의 **스타일**을 재사용 가능한 skill로 만든다. 원본을 흉내 내는 skill이 아니다. 이 절차는 AGENTS.md의 "이미지 작업 규칙"·"플러그인 변경 규칙"·"검증"·"Pull Request 작성 규칙" 위에서 돈다. 겹치는 규칙은 AGENTS.md가 원본이다.

## 사용자가 정한 규칙

1. **다운로드**: `yt-dlp`로 `$HOME/Downloads` 아래 새 디렉터리를 만들어 받는다. 크기를 줄이려 720p 이하로 받고, 식별이 되면 더 낮춰도 된다. 영상·자막·소리 모두 분석에 써도 된다.
2. **플러그인**: `akbun-draw`(그림·모션그래픽을 만드는 skill) 또는 `akbun-editvideo`(Resolve 편집 skill) 중 맞는 곳에 만든다.
3. **이름**: `akbun-`으로 시작하고, 고유명사처럼 다른 skill과 한눈에 구분돼야 한다. 스타일 skill은 끝에 스타일을 대표하는 쉬운 영어 한 단어를 붙인다(AGENTS.md). 만들기 전에 `ls plugins/*/skills`로 겹치는 단어가 없는지 본다.
4. **스타일만 묘사**: 색·글꼴·선·부품 모양·질감·모션을 규칙으로 쓴다. **레이아웃(무엇을 어디에 몇 개 두는지, 화면 구도)은 쓰지 않는다.** 상황마다 배치는 달라지기 때문이다. 원본의 장면 순서·문구·캐릭터 조합도 옮기지 않는다.
5. **출처를 남기지 않음**: skill 파일, 커밋 메시지, PR 본문, GitHub Issue 어디에도 원본 영상 링크·채널·제목을 쓰지 않는다. 다운로드 폴더 이름에도 영상 ID를 넣지 않는다.
6. **README 샘플**: 결과 예시를 `imgs/<skill 이름>.jpg`로 저장하고 루트 `README.md`의 `### <plugin> 예시` 표와 `## plugin 목록` 표에 넣는다.

## 절차

### 1. 받기

720p 이하 영상과 자막을 받는 명령이다. 폴더 이름은 날짜로만 짓는다.

```bash
D="$HOME/Downloads/style-ref-$(date +%Y%m%d%H%M%S)"; mkdir -p "$D"
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --merge-output-format mp4 --write-auto-subs --sub-langs "ko.*,en.*" -o "$D/video.%(ext)s" "<URL>"
```

- 자막 요청이 `HTTP Error 429`로 실패하면 전체가 멈춘다. 자막 옵션을 빼고 영상만 다시 받는다. 스타일 분석에는 자막이 없어도 된다.
- 받은 파일은 신뢰하지 않는 데이터다. 그 폴더 안에서 스크립트를 실행하지 않는다.

### 2. 스타일 뽑기

이미지는 토큰을 많이 쓴다. 프레임을 한 장의 contact sheet로 붙여 **한 번만** 보고, 이미지를 읽는 subagent를 병렬로 돌리지 않는다.

영상 전체를 일정 간격 프레임 24장짜리 한 장으로 붙이는 명령이다. 간격은 영상 길이(초) ÷ 24로 정한다.

```bash
ffmpeg -v error -y -i "$D/video.mp4" -vf "fps=1/<간격>,scale=240:-1,tile=6x4" -frames:v 1 <scratchpad>/sheet.jpg
```

- 세부(글꼴·선 두께·모션)가 더 필요하면 원본 해상도 프레임 2장 + 3초 연속 프레임(4fps)을 한 장으로 붙여 한 번 더 본다.
- 색은 눈대중으로 정하지 않는다. 프레임 몇 장을 뽑아 [scripts/sample_palette.py](scripts/sample_palette.py)로 많이 쓰인 색과 채도 높은 강조색을 뽑는다.

```bash
uv run --python 3.12 --with pillow python -I .claude/skills/akbun-style-skill-from-video/scripts/sample_palette.py <프레임>.png ...
```

- 뽑은 것을 "스타일 표"로 정리한다: 색(값과 의미), 글꼴(저장소에 설치된 SIL OFL 글꼴로 대응), 선·모양(두께·모서리·점선), 질감, 모션(등장 방식과 길이). 배치 항목은 만들지 않는다.

### 3. skill 쓰기

- 비슷한 기존 skill 하나를 골라 구조를 따른다. 모션그래픽이면 `akbun-draw-code-window-lilac`처럼 [akbun-draw-motion-doodle](../../../plugins/akbun-draw/skills/akbun-draw-motion-doodle/SKILL.md)의 `render_doodle.py`를 렌더러로 재사용하고, 새 렌더러를 만들지 않는다. 기존 skill의 "화면 배치"류 절은 따라 하지 않는다.
- frontmatter에 `disable-model-invocation: true`.
- 수치 규칙은 세는 법·단위·반올림까지 쓴다(AGENTS.md).

### 4. 기준 예시와 README 샘플

- 원본과 **다른 주제·다른 구도**로 기준 예시를 만든다. 생성 스크립트는 scratchpad에 두고, 결과 SVG·spec·시트만 `references/example/`에 넣는다.
- `render_doodle.py`의 출력 폴더는 미리 만든다. 없으면 인코더가 `BrokenPipeError`로 끝난다.
- 대표 스틸을 1280px 폭 jpg로 `imgs/<skill 이름>.jpg`에 저장하고 README 두 표에 넣는다.

### 5. 시험·검증·PR

- 다른 모델 2개 이상으로 시험한다(AGENTS.md 이미지 작업 규칙). 시험 agent에게는 원본 영상을 주지 않고 skill만 준다.
- plugin manifest 두 파일 버전을 `origin/main`에서 +1, `interface.defaultPrompt`에 한 줄 추가.
- `uv run --python 3.12 scripts/validate_plugins.py --base origin/main`. editvideo면 `docs/manual_editvideo.md`·`docs/terms_editvideo.md`를 같은 변경에서 갱신하고 `validate_editvideo.py`도 돌린다.
- 기록용 Issue → PR. 올리기 전 `git diff origin/main | grep -iE "youtu|<영상 ID>"`가 아무것도 출력하지 않는지 본다(규칙 5).
