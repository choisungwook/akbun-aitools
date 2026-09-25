---
name: davinciresolve-beats-devtalk
description: 말하는 개발자 브이로그의 클립을 전사해 소재 인벤토리를 만들고, 선택한 편집 스타일(essay·project·reflection)의 구조 표에 맞춰 스토리 비트 시트를 제안하고, 사용자가 확정하면 비트 순서대로 클립 구간을 DaVinci Resolve 작업 타임라인에 나열한다. "이 클립들로 스토리 잡아줘", "비트 순서로 타임라인 만들어줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-beats-devtalk

스토리를 정하고 그 순서로 클립을 놓는 단계다. 전사가 근거이고, 비트 시트는 사용자가 확정한다. `davinciresolve-video-editor`의 기본 원칙(작업 타임라인, 클립은 파일명 + 시작 타임코드, 작업 로그)과 마커 등록표를 따르고, 구조 표는 `davinciresolve-story-devtalk`이 정한 style skill의 `SKILL.md`에서 읽는다. 스타일이 정해지지 않은 채 단독 호출되면 그 skill의 스타일 선택 표로 먼저 정하고 로그에 이유를 적는다.

## 용어

- 비트(beat): 스토리의 한 단락. 메시지 1개, 클립 구간, 목표 길이를 가진다. YouTube 챕터와 1:1
- 전사(transcript): 말소리를 문장·단어 단위 타임코드로 적은 것. `(...)`는 침묵
- 음성 클립: 화자의 말소리가 담긴 클립. 소리만 쓴다. 화자 얼굴이 찍혀 있어도 그 영상은 화면에 내지 않는다
- 화면 클립(B-roll): 화면에 내는 클립. 종류를 제한하지 않는다. 화면 녹화 파일은 `화면 녹화`로 따로 표시한다
- 얼굴 있음(`face`): 화자 얼굴이 식별되는 클립. 소리는 써도 화면에는 쓰지 않는다

## 전사 수단

| 순서 | 수단 | 조건 |
|---|---|---|
| 1 | `MediaPoolItem.TranscribeAudio()` 뒤 `GetTranscription()` | Resolve Studio 20 이상. 프로젝트 설정 `transcriptionLanguage`를 `ko`로 맞춘 뒤 실행 |
| 2 | 아래 whisper 명령 | Resolve 전사가 없을 때 |
| 3 | 사용자 대본 | 둘 다 없을 때. 대본 없이 스토리를 만들지 않는다 |

whisper 대체 명령이다. 결과 JSON의 `segments[].start/end/text`를 전사로 쓴다.

```bash
python3 -m venv .venv && .venv/bin/pip install -q mlx-whisper
.venv/bin/python -c "import mlx_whisper,json,sys; r=mlx_whisper.transcribe(sys.argv[1], path_or_hf_repo='mlx-community/whisper-large-v3-turbo', language='ko', word_timestamps=True); json.dump(r, open(sys.argv[1]+'.json','w'), ensure_ascii=False)" "<클립 경로>"
```

## 1. 소재 인벤토리

- 클립 메타데이터(파일명, 촬영 시간, 카메라, 길이, 해상도, 프레임레이트)를 읽는다. 카메라 판별과 시계 오프셋은 `davinciresolve-video-editor` 1단계 규칙을 따른다.
- 말소리가 클립 길이의 절반 이상이면 음성 클립, 아니면 화면 클립, 화면 녹화 파일(모니터 비율, 카메라 메타데이터 없음)은 `화면 녹화`. 한 클립이 음성이면서 화면으로도 쓸 수 있다(손·화면을 찍으며 말한 클립).
- 클립마다 시작·중간·끝 프레임과 1초 간격 프레임을 `ffmpeg`로 뽑아 얼굴 탐지기(`davinciresolve-video-editor` `references/agent-api.md`의 대체 방법)에 넣는다. 화자 얼굴이 한 프레임이라도 식별되면 `face`로 표시하고 화면 클립 후보에서 뺀다. 파일명이 `_face`로 끝나는 클립은 탐지 없이 `face`다. 탐지기가 없으면 전 클립을 `face 확인 필요`로 두고 사용자에게 얼굴 없는 클립을 지정받는다.
- 음성 클립 전부를 전사하고 문장마다 시작·끝 타임코드와 텍스트를 붙인다.
- 재녹음(`retake`)은 문장 앞 10글자가 같고 시작 시각이 60초 이내인 세그먼트 묶음으로 찾아 표시한다.

인벤토리 표 형식이다.

```markdown
| 파일명 | 카메라 | 종류 | 얼굴 | 길이 | 문장 수 | 핵심 문장(전사 요약 1줄) | 비고 |
|---|---|---|---|---|---|---|---|
| IMG_2001.MOV | 카메라 | 음성 | face | 04:12 | 38 | 왜 컨테이너는 VM보다 빨리 뜨나 | retake 2묶음, 소리만 사용 |
| IMG_2002.MOV | 카메라 | 음성·화면 | 없음 | 03:05 | 21 | 터미널 보면서 설명 | 손·키보드 탑다운 |
| C0012.MP4 | 보조 카메라 | 화면 | 없음 | 00:48 | 0 | 책상 정리(손) | |
| screen_k8s.mov | - | 화면 녹화 | 없음 | 02:30 | 0 | 터미널 kubectl | |
```

## 2. 스토리 비트 제안

- style skill의 구조 표를 뼈대로 하고 인벤토리의 핵심 문장을 비트에 배정한다. 비트마다 메시지 1개, 음성 구간(파일명 + 소스 타임코드 범위), 그 위에 나갈 화면(화면 클립·화면 녹화·카드), 목표 길이를 적는다. 화면 칸이 비는 비트가 없어야 한다. 채울 화면이 없으면 `화면 없음`으로 적고 사용자에게 알린다.
- 첫 비트(훅)는 영상 시작 10초 안에 "시청자가 왜 봐야 하는가"를 한 문장으로 말하는 구간이어야 한다. 없으면 뒤 비트에서 가장 강한 주장 문장을 앞으로 끌어와 쓰고 로그에 적는다.
- 어느 비트에도 들어가지 않는 음성 문장은 `미사용` 목록에 남긴다. 버리는 것이 기본이고 남길 이유가 있으면 사용자에게 묻는다.
- `akbun-vlog-shootplan`이 만든 촬영 계획서가 있으면 그 비트 시트를 초안으로 쓴다.
- 비트 시트를 사용자에게 보이고 확정을 받는다. 확정 전에는 3단계로 가지 않는다.

비트 시트 형식이다.

```markdown
스타일: essay(이유: 기술 원리 설명), 목표 길이 7분

| # | 비트 | 메시지 | 음성 구간 | 화면 | 길이 |
|---|---|---|---|---|---|
| 1 | 훅 | 컨테이너가 VM보다 빨리 뜨는 건 가상화가 아니라 격리라서다 | IMG_2001.MOV 00:03:10–00:03:25 | 키워드 Text+ 위 IMG_2002.MOV 손·키보드 | 0:15 |
| 2 | 왜 이 얘기를 하나 | 면접에서 이 질문을 받고 답을 못 했다 | IMG_2001.MOV 00:00:05–00:00:50 | 카드: 챕터 제목 → C0012.MP4 | 0:45 |
| 3 | 원리 1 namespace | ... | IMG_2001.MOV 00:01:00–00:01:40 | 번호 제목 Text+ → screen_k8s.mov | 0:40 |
```

## 3. 비트 순서로 클립 나열

- 새 작업 타임라인 `<프로젝트 이름>_story_<YYYYMMDD_HHMM>`을 만든다. 복제본이 아니라 미디어 풀에서 새로 만드는 타임라인이라 `davinciresolve-video-editor`의 `_edit_` 이름과 구분한다. 사용자가 만든 타임라인이 있으면 그 skill대로 복제해서 쓴다.
- 트림·이동 API가 없으므로 `MediaPool.CreateTimelineFromClips` 또는 `AppendToTimeline`에 `mediaPoolItem`, `startFrame`, `endFrame`을 준 구간 목록으로 만든다. 비트 시트의 클립 구간 하나가 목록 항목 하나다. 소스 프레임은 전사 타임코드를 클립 프레임레이트로 환산한다.
- 트랙은 `davinciresolve-story-devtalk`의 트랙 배치대로 음성 구간은 A1에 소리만(`mediaType: 2`), 화면 클립은 V1에 영상만(`mediaType: 1`). 같은 `recordFrame`으로 넣어 음성 문장과 화면이 맞물리게 한다. 화면 클립의 현장음이 필요하면(타자 소리, 물건 소리) 같은 구간을 A2에 한 번 더 넣는다.
- `face` 클립은 A1에만 들어간다. V1에 넣지 않는다.
- 비트 시작 프레임마다 Blue 타임라인 마커 `CHAPTER <비트 이름>`. 첫 마커는 frameId 0.
- 카드가 있는 위치에는 Cyan 타임라인 마커 `GFX <카드 종류> <제목>`. 카드 자리를 비워 두지 않는다(`davinciresolve-gfx-hyperframes`가 V2에 `recordFrame`으로 넣고, 그동안 A1 소리는 그대로 흐른다).

## 작업 로그

`인벤토리`, `비트 시트(확정본)`(미사용 문장 목록 포함) 절을 채우고, 구간 목록(`트랙 | 파일명 | 소스 시작 TC | 소스 끝 TC | 타임라인 시작 TC | 비트`)을 `컷` 절 첫 표로 남긴다. 이 목록이 `davinciresolve-cut-devtalk`의 입력이다.

## 하지 않는 것

- 전사·대본 없이 스토리 만들기, 화자가 말하지 않은 문장을 비트에 넣기
- 사용자 확정 없이 나열 시작
- 클립 원본 트림·삭제
- `face` 클립이나 얼굴 판정이 안 된 클립을 V1에 넣는 것
