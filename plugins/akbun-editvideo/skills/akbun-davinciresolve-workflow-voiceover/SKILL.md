---
name: akbun-davinciresolve-workflow-voiceover
description: 얼굴 없이 공부·경험 공유·기술 가이드·제품 소개 영상을 보이스오버로 만드는 DaVinci Resolve 편집 workflow. 대본 확정 → 가이드 음성 → 화면 조립 → 감독 연출표 → 오버레이·글자 → 최종 보이스오버 녹음·교체 → 사운드 → 점검 → 출력 순서로 스타일(explainer, product)·감독·오버레이·사운드 skill 문서를 읽어 수행한다. 보이스오버를 편집 뒤에 녹음해도 되고 촬영하면서 녹음해도 된다. "설명 영상 처음부터 끝까지 편집해줘", "제품 소개 영상 workflow", "보이스오버는 나중에 녹음할게" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-workflow-voiceover

얼굴 없는 보이스오버 영상의 편집 순서·완료 조건·기록을 선언한다. 각 단계의 규칙은 그 단계 skill의 `SKILL.md`가 원본이고, 이 skill은 순서대로 읽어 수행한다. 하위 skill은 직접 호출 전용이라 Skill 도구로 부르지 않는다.

`davinciresolve-story-devtalk`과 다른 점: devtalk은 촬영하며 말한 음성의 전사가 출발점이다. 이 workflow는 대본이 출발점이고, 화면을 먼저 맞춘 뒤 최종 보이스오버를 나중에 녹음할 수 있다. 이미 말하며 찍은 클립이 있으면 devtalk을 쓴다.

`akbun-davinciresolve-workflow`의 기본 원칙(원본 타임라인 불변, 작업 타임라인, 클립은 파일명 + 시작 타임코드, 대표 1개 선적용, 작업 로그, 되돌릴 수 없는 작업은 확인)과 마커 등록표를 따른다.

## 용어

- 대본(script): 비트별로 말할 문장. 문장마다 번호 `S<비트>-<순번>`
- 가이드 음성(scratch VO): 화면 길이를 맞추려고 먼저 넣는 임시 음성. 사용자가 대충 읽은 녹음이거나 Resolve 음성 생성 결과
- 최종 보이스오버(final VO): 마이크로 제대로 녹음한 음성. 가이드 음성을 대체한다
- 연출표: [감독 skill](../akbun-davinciresolve-director/SKILL.md)이 만드는 비트별 화면·움직임·오버레이·소리 표

## 시작 조건

- 주제와 대본 또는 대본으로 만들 메모(공부 노트, 경험, 제품 정보)
- 재료 폴더: 촬영 클립, 화면 녹화, 사진·결과물. 없으면 대본과 연출표까지만 만들고 필요한 촬영 목록을 [akbun-vlog-shootplan](../akbun-vlog-shootplan/SKILL.md) 형식으로 넘긴다
- 출력 폴더. 없으면 재료 폴더 옆 `<주제>_edit/`

## 트랙

| 트랙 | 내용 |
|---|---|
| V1 | 본편: 촬영 클립, 화면 녹화 |
| `OVERLAY` / `GFX` / `SUBTITLE` / `HOOK_TEXT` | [overlay skill](../akbun-davinciresolve-overlay/SKILL.md)의 트랙 표 |
| A1 `VOICE` | 가이드 음성, 나중에 최종 보이스오버 |
| `AMBIENCE` / `SFX` / `MUSIC` / `HOOK` | [사운드 공통 skill](../davinciresolve-sfx-epidemicsound/SKILL.md) |

작업 타임라인에서 `python3 ../akbun-davinciresolve-workflow/scripts/workflow.py tracks --timeline "<작업 타임라인>" --out "<출력 폴더>"`로 이름 있는 트랙을 만들고, A1 이름을 `VOICE`로 바꾼다. 화면 클립의 현장음은 `AMBIENCE`로 옮기거나 끈다.

## 작업 순서

| 순서 | 작업 | 읽는 skill·방법 | 완료 조건 |
|---|---|---|---|
| 1 | 스타일 선택 | 공부·경험·기술 가이드는 [explainer](../akbun-davinciresolve-style-explainer/SKILL.md), 제품 소개는 [product](../akbun-davinciresolve-style-product/SKILL.md) | 로그에 스타일과 이유 |
| 2 | 대본 | 스타일의 구조 표로 비트를 나누고 문장을 쓴다. 한국어 분당 약 250~300자로 비트 길이를 추정한다. 사실·수치는 사용자 메모에서만 | 사용자가 대본을 확정했다(필수 확인 1) |
| 3 | 연출표 | [director](../akbun-davinciresolve-director/SKILL.md) 1절 | 사용자가 연출표를 확정했다(필수 확인 2). 재료 부족 cue는 촬영 목록으로 |
| 4 | 가이드 음성 | 아래 "가이드 음성" | `VOICE` 트랙에 문장 순서대로 음성이 있고 문장 번호 마커가 있다 |
| 5 | 화면 조립 | 연출표의 본편 샷을 가이드 음성 길이에 맞춰 V1에 놓는다. 스타일의 컷 리듬 표를 따른다 | 모든 비트에 본편이 있고 `CHAPTER` 마커가 비트 순서와 같다 |
| 6 | 오버레이·글자 | [overlay](../akbun-davinciresolve-overlay/SKILL.md) | 연출표의 오버레이·글자 cue가 놓였거나 미적용 사유가 있다 |
| 7 | 그래픽 | 선택한 그래픽 도구. 미정이면 위치만 `GFX` 마커로 남기고 진행 | 필요한 그래픽이 있거나 미완성으로 기록 |
| 8 | 최종 보이스오버 | 아래 "보이스오버 교체" | `VOICE` 트랙이 최종 음성이고, 길이 차이로 생긴 어긋남이 `VO_FIT`로 표시·해결됐다 |
| 9 | 사운드 | [davinciresolve-sfx-epidemicsound](../davinciresolve-sfx-epidemicsound/SKILL.md). 연출표 cue ID를 장면 앵커로 | 사운드 복제본과 `AUDIO_REVIEW` 목록 |
| 10 | 점검 | [director](../akbun-davinciresolve-director/SKILL.md) 3절 | `DIRECT` 마커를 사용자가 확인했거나 해결했다 |
| 11 | 색·출력 | `akbun-davinciresolve-workflow`의 색 단계(필요할 때), [davinciresolve-audio-delivery](../davinciresolve-audio-delivery/SKILL.md) 출력 절 | 그 skill의 완료 조건 |

보이스오버를 촬영하면서 이미 녹음했다면 4단계에서 그 음성을 넣고 8단계를 건너뛴다. 최종 음성을 먼저 녹음해 왔다면 4단계를 최종 음성으로 하고 8단계를 건너뛴다.

## 가이드 음성

아래 중 사용자가 고른 하나. 고르지 않았으면 1을 제안한다.

1. 사용자가 휴대폰·마이크로 대본을 대충 읽은 파일. 문장 사이 1초 쉼을 둔다.
2. Resolve 음성 생성 `Project.GenerateSpeech({"TextInput": 문장, "VoiceModel": ..., "AddToTimeline": True, "AudioTrack": <VOICE 번호>})`. 한 번에 350자까지다. 21.1 API에 있지만 이 저장소에서 한국어 품질을 확인하지 않았다. 대표 문장 1개로 먼저 만들어 들어 보고 쓴다. 생성 파일은 미디어 풀에 추가된다.
3. 가이드 음성 없이 문장 길이를 추정해 화면만 먼저 맞춘다. 8단계에서 조정이 가장 많아진다.

문장마다 시작 프레임에 마커를 두지 않고, 비트 시작의 `CHAPTER` 마커 노트에 그 비트의 문장 번호 범위를 적는다.

## 보이스오버 교체

1. 교체 전에 작업 타임라인을 `<이름>_vo_<YYYYMMDD_HHMM>`로 복제하고 복제본에서 한다.
2. 녹음 조건은 [akbun-vlog-shootplan](../akbun-vlog-shootplan/SKILL.md)의 마이크 행을 따른다. 문장 번호를 말하고 녹음하면 찾기 쉽다.
3. 최종 음성을 전사(`MediaPoolItem.TranscribeAudio`, 없으면 `davinciresolve-beats-devtalk`의 whisper 명령)해 문장 번호와 맞춘다.
4. 문장마다 가이드 음성 자리에 최종 음성 구간을 놓는다. 최종 문장이 가이드보다 길거나 짧아 다음 화면 변화(컷·카드 등장)와 0.5초 넘게 어긋나면 Rose `VO_FIT <문장 번호> <차이 초>` 타임라인 마커를 찍는다.
5. `VO_FIT`마다 해결 방법을 고른다: 본편 샷 길이 조정, 문장 사이 쉼 조정, 카드 시작 이동(`overlay.py`로 지우고 다시 놓기). 옮긴 cue는 연출표에 적는다.
6. 가이드 음성 클립은 지우지 않고 뮤트한 트랙으로 옮겨 비교용으로 둔다.

## 검증

출력 전에 작업 로그 `검증` 절에 표로 남긴다.

| 항목 | 기준 |
|---|---|
| 대본 | 모든 문장 번호가 `VOICE` 트랙에 있다. 빠진 문장은 사유 |
| 화면 | 비트마다 본편이 있고 스타일의 "변화 없는 구간" 기준을 넘는 곳은 의도로 기록 |
| 오버레이 | 연출표의 cue와 대조해 놓임·미적용 |
| 보이스오버 | `VO_FIT` 마커가 모두 해결 또는 사용자 확인 |
| 얼굴 | 화자 얼굴이 식별되는 프레임 0개. 방법은 `davinciresolve-story-devtalk` 검증 표 |
| 연출 점검 | `director.py audit` 결과와 `DIRECT` 마커 상태 |
| 사운드 | `AUDIO_REVIEW` 목록과 상태 |

## 작업 로그

`<출력 폴더>/edit-log_<YYYYMMDD_HHMM>.md`:

```markdown
# 편집 작업 로그 <YYYYMMDD_HHMM>
## 환경
## 스타일
## 대본(확정본)
## 연출
## 조립
## 오버레이
## 그래픽 카드
## 보이스오버
## 오디오
## 검증
## 확인 필요
```

## 하지 않는 것

- 대본·연출표 확정 전 타임라인 편집
- 사용자가 말하지 않은 경험·수치를 대본에 넣는 것
- 보이스오버 교체를 원본 작업 타임라인에서 바로 하는 것, 가이드 음성 삭제
- 얼굴이 보이는 화면
