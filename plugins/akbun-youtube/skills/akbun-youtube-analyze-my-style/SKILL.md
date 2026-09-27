---
name: akbun-youtube-analyze-my-style
description: 내 YouTube 영상에서 지금의 스타일을 뽑아 YAML 스타일 프로필로 만드는 skill. 내 영상 3~5개의 프레임, 컷 간격, 자막, 설명의 배경음악 목록을 근거로 시각(색·촬영 공간·옷·글꼴·효과), 리듬(음악·효과음·속도), 전달(말하는 방식·카메라·성격) 세 요소를 관찰하고, 영상끼리 일관된 것과 흔들리는 것을 구분한다. 분위기·역할·가치로 이루어진 아키타입과 관찰한 스타일이 맞는지 대조하고 다음 영상에서 시험할 작은 변화 하나를 제안한다. 얼굴이 나오지 않는 영상은 해당 없는 항목을 표시한다. 화면은 조작하지 않는다. "내 유튜브 스타일 분석해줘", "내 영상 스타일 정리해줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-youtube-analyze-my-style

내 영상이 지금 어떤 스타일인지 관찰해서 적는다. 새 스타일을 지어내지 않고 영상에 실제로 있는 것만 적는다. 결과는 YAML 스타일 프로필 하나다. 조회수와 지표는 [`akbun-youtube-analyze-my-videos`](../akbun-youtube-analyze-my-videos/SKILL.md)가 맡는다.

## 규칙

아래는 이 skill이 지키는 규칙이다.

```yaml
rules:
  operates_screen: false
  observe_only: 영상에 실제로 있는 것만 적는다. 근거가 없는 항목은 "관찰 못함"으로 적는다
  evidence_required: 항목마다 영상 ID와 시각 또는 파일 이름을 근거로 단다
  not_applicable: 얼굴이나 몸이 나오지 않는 영상의 wardrobe처럼 해당 없는 항목은 not_applicable로 적는다
  style_not_copy: 다른 채널의 스타일을 그대로 가져오라고 권하지 않는다
  judge_by: 아키타입과 맞는지. 좋고 나쁨이나 유행으로 판단하지 않는다
  change_size: 제안은 영상 하나에서 시험할 작은 변화 하나로 한다
  revisit: 스타일은 바뀐다. 1년에 한 번쯤 다시 한다
```

## 스타일의 구조

아래는 스타일을 이루는 요소다. 아키타입이 목표이고 세 요소가 그것을 만든다.

```yaml
archetype:
  description: 시청자가 내 영상에서 겪기를 바라는 경험. 스타일을 판단하는 기준이다
  parts:
    vibe: 영상 전체의 느낌
    role: 시청자에게 내가 맡는 역할
    value: 시청자가 보고 나서 얻는 것
  example: {vibe: 조용한, role: 옆에서 같이 걷는 사람, value: 직접 간 듯한 시간}

elements:
  visual:                                 # 영상이 어떻게 보이는가
    color_palette:
      slots: [주 색 1, 주 강조색 1, 보조 강조색 3, 글자색 1]
      look_at: [색보정, 썸네일, 자막, 그래픽]
    set_design:
      meaning: 촬영하는 공간. 방이 아니라 바깥 장소일 수도 있다
    wardrobe:
      meaning: 반복되는 옷, 머리 모양, 소품
    typography:
      look_at: [글꼴 수, 제목·본문·강조의 글꼴, 대소문자, 글자를 쓰는 용도]
    visual_effects:
      look_at: [전환, 오버레이, 글자가 나타나고 사라지는 방식, 그래픽]
      production_level: [매끈하고 공들인, 손으로 그린 듯한, 과장되고 어수선한, 깔끔하고 최소한의]

  rhythmic:                               # 영상이 어떻게 느껴지는가
    mood:
      music: [장르, 시대, 반복해 쓰는 곡, 장면에 따라 바뀌는지]
      sound_effects: [종류, 빈도, 과장된지 절제됐는지]
    momentum:
      pacing:
        fast: 짧은 컷, 잦은 구도 변화, 쉼과 숨소리 제거. 신나고 예측하기 어려운 느낌
        medium: 중간 길이와 짧은 컷의 혼합, 약한 줌과 전환, 강조를 위한 쉼. 대화하는 느낌
        slow: 적은 컷, 길게 이어지는 장면. 차분하고 빠져드는 느낌

  delivery:                               # 내가 어떻게 드러나는가
    speech:
      scripting: [한 글자씩 쓴 대본, 요점만 적은 메모, 대본 없음]
      word_choice: [전문 용어, 일상어, 표현이 강한 말]
      signature: 반복하는 말, 시청자를 부르는 이름, 되풀이되는 농담
    camera:
      tripod: 안정되고 정돈된 느낌
      handheld: 개인적이고 날것의 느낌
      gimbal_or_drone: 공들인 영화 같은 느낌
    personality:
      look_at: [에너지의 높낮이, 유머, 버릇, 장면에 따라 달라지는 모습]
      note: 에너지가 높을수록 좋은 것이 아니다. 원래 가진 것을 드러내는 쪽을 본다
```

## 입력

아래는 시작 전에 확인할 입력이다.

```yaml
inputs:
  - id: videos
    description: 분석할 내 영상 3~5개. 주소나 파일 경로
    when_missing: ask
    pick: 최근 영상과 오래된 영상을 섞는다. 같은 종류의 영상끼리 묶는다
  - id: archetype
    description: 내가 의도한 vibe, role, value
    when_missing: 관찰을 끝낸 뒤 후보 3개를 내고 사용자가 고르게 한다
  - id: has_face
    description: 얼굴이나 몸이 나오는지
    when_missing: 프레임에서 확인한다
  - id: has_speech
    description: 말소리가 있는지
    when_missing: 자막에서 확인한다. 없으면 speech는 화면 글자의 말투로 본다
  - id: work_dir
    description: 영상과 프레임을 받을 폴더
    when_missing: ask
```

## 근거 모으기

아래 명령은 영상과 자막을 720p 이하로 받는다.

```bash
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --merge-output-format mp4 --write-auto-subs --sub-langs "ko" -o "%(id)s.%(ext)s" "https://youtu.be/영상ID"
```

아래 명령은 10초마다 한 프레임을 뽑아 12장씩 한 장의 표로 만든다. 색, 공간, 글꼴, 효과를 이 표에서 본다.

```bash
ffmpeg -loglevel error -y -i 영상ID.mp4 -vf "fps=1/10,scale=480:-1,tile=4x3" 영상ID_sheet_%02d.jpg
```

아래 명령은 영상에서 많이 쓰인 색 8개를 16진수로 출력한다. 프레임 표와 대조해 색의 역할을 정한다.

```bash
ffmpeg -loglevel error -y -i 영상ID.mp4 -vf "fps=1/10,scale=160:-1,palettegen=max_colors=8:reserve_transparent=0" 영상ID_palette.png
ffmpeg -loglevel error -i 영상ID_palette.png -f rawvideo -pix_fmt rgb24 - | xxd -p -c 3 | sort -u
```

아래 명령은 영상 길이(초)와 컷 수를 출력한다. 평균 컷 길이는 길이 ÷ (컷 수 + 1)이다.

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 영상ID.mp4
ffmpeg -hide_banner -i 영상ID.mp4 -vf "select='gt(scene,0.3)',showinfo" -an -f null - 2>&1 | grep -c "pts_time"
```

아래는 요소마다 쓰는 근거다.

```yaml
evidence_sources:
  color_palette: [프레임 표, 색 8개, 썸네일]
  set_design: [프레임 표]
  wardrobe: [프레임 표]
  typography: [글자가 나온 프레임]
  visual_effects: [컷 앞뒤의 프레임]
  music: [영상 설명의 배경음악 목록, 편집 프로젝트의 작업 로그]
  sound_effects: [편집 프로젝트의 작업 로그, 사용자가 알려 준 것]
  pacing: [평균 컷 길이, 프레임 표]
  speech: [자막]
  camera: [프레임 표에서 이어지는 프레임의 흔들림과 움직임]
  personality: [자막, 프레임 표]
limits:
  - 소리를 직접 듣지 못하면 music과 sound_effects는 목록과 로그에 있는 것만 적는다
  - 평균 컷 길이는 장면 변화로 센 근사값이다. 영상끼리 비교하는 데만 쓴다
```

## 절차

아래는 실행 순서다.

```yaml
procedure:
  - step: 1
    name: 근거 모으기
    do:
      - 영상마다 프레임 표, 색 8개, 컷 수, 자막을 만든다
      - 영상 설명에서 배경음악 목록을 읽는다
  - step: 2
    name: 영상마다 관찰하기
    do:
      - elements의 항목마다 관찰한 것과 근거를 적는다
      - 해당 없는 항목은 not_applicable, 근거가 없는 항목은 "관찰 못함"으로 적는다
  - step: 3
    name: 영상끼리 비교하기
    do:
      - 항목마다 모든 영상에서 같으면 consistent, 영상마다 다르면 varies로 적는다
      - varies인 항목은 의도한 변화인지 사용자에게 묻는다
  - step: 4
    name: 아키타입과 대조하기
    do:
      - 아키타입이 없으면 관찰에서 후보 3개를 만들어 고르게 한다
      - 항목마다 아키타입과 맞으면 fit, 어긋나면 mismatch와 이유를 적는다
  - step: 5
    name: 시험할 변화 하나 정하기
    do:
      - mismatch나 varies 중 하나를 고른다
      - 다음 영상 하나에서 바꿀 것 한 가지를 적는다
      - 바꾼 뒤 무엇을 보고 남길지 버릴지 정할지 적는다
```

## 산출물

아래는 스타일 프로필의 형식이다. 출력 폴더에 `youtube-style-profile-{YYYYMMDD}.yaml`로 저장하고 대화에도 요약을 보여 준다.

```yaml
channel: 채널 이름
created: 2026-09-27
videos: [AbCdEfGhIjK, BcDeFgHiJkL, CdEfGhIjKlM]
has_face: false
has_speech: false
archetype:
  vibe: 조용한
  role: 옆에서 같이 걷는 사람
  value: 직접 간 듯한 시간
  chosen_by: user                         # user | proposed
style:
  visual:
    color_palette:
      observed:
        dominant: "#2f3b3a"
        primary_accent: "#d9a441"
        secondary_accents: ["#7a8f86", "#c9c2b4", "#51606b"]
        text: "#ffffff"
      consistency: consistent             # consistent | varies
      fit: fit                            # fit | mismatch
      evidence: [AbCdEfGhIjK_sheet_01.jpg, BcDeFgHiJkL_palette.png]
    wardrobe:
      observed: not_applicable
    typography:
      observed: Gmarket Sans 한 가지, 장소와 시간을 한 줄로 표시
      consistency: consistent
      fit: fit
      evidence: [AbCdEfGhIjK 00:42]
  rhythmic:
    pacing:
      observed: slow
      average_shot_sec: {AbCdEfGhIjK: 7.8, BcDeFgHiJkL: 8.4, CdEfGhIjKlM: 3.1}
      consistency: varies
      fit: mismatch
      reason: CdEfGhIjKlM만 컷이 짧아 조용한 느낌과 어긋남
      evidence: [컷 수 계산]
    music:
      observed: 관찰 못함
      reason: 영상 설명에 배경음악 목록이 없음
  delivery:
    speech:
      observed: 화면 글자만 사용, 짧은 평서문
      consistency: consistent
      fit: fit
      evidence: [AbCdEfGhIjK 자막]
summary:
  consistent: [color_palette, typography, speech]
  varies: [pacing]
  mismatch: [pacing]
  not_observed: [music, sound_effects]
next_experiment:
  target: pacing
  change: 다음 영상에서 평균 컷 길이를 7초 이상으로 유지한다
  keep_or_discard_by: 다시 봤을 때 조용한 느낌이 드는지와 평균 조회율
```

## 완료 확인

아래를 모두 만족해야 끝난다.

```yaml
done_when:
  - elements의 모든 항목이 프로필에 있다
  - 관찰마다 근거가 있다
  - 관찰하지 못한 항목과 해당 없는 항목이 구분돼 있다
  - 아키타입을 사용자가 골랐거나 확인했다
  - next_experiment에서 바꾸는 것이 하나다
  - 저장한 YAML 파일이 파싱된다
```
