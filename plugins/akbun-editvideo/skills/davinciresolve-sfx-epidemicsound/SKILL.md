---
name: davinciresolve-sfx-epidemicsound
description: DaVinci Resolve Studio의 Epidemic Sound 플러그인 효과음 라이브러리에서 그래픽 카드 등장, 키워드 등장, 챕터 전환, 콜드 오픈 티저 컷, 전후 비교표 강조에 맞는 효과음을 골라 A3 SFX 트랙에 프레임 단위로 놓는다. 이벤트별 효과음 종류·검색어·타이밍 표와 분당 밀도 제한을 따른다. "효과음 넣어줘", "카드 나올 때 소리", "전환 효과음" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-sfx-epidemicsound

효과음을 고르고 놓는 단계다. 화자 얼굴이 없는 영상에서는 카드·키워드·전환이 시청자의 시선을 끌어야 하므로, 그 순간에만 짧은 효과음을 붙인다. 검색과 배치는 이 skill이 하고, 레벨은 `davinciresolve-audio-delivery`가 한다.

`davinciresolve-video-editor`의 기본 원칙(작업 타임라인, 작업 로그, 되돌릴 수 없는 작업은 확인)을 따른다. 트랙은 `davinciresolve-story-devtalk`의 트랙 배치대로 A3 `SFX`이다. 실행 조건(플러그인·로그인·화면 조작)은 `davinciresolve-bgm-epidemicsound`와 같다.

## 이벤트와 효과음

효과음은 아래 이벤트에만 붙인다. 이벤트는 `GFX`·`CHAPTER` 마커와 `davinciresolve-subtitle-devtalk`의 Text+ 목록에서 찾는다.

| 이벤트 | 효과음 종류 | 검색어 예 | 길이 | 타이밍 |
|---|---|---|---|---|
| 그래픽 카드 등장(`GFX` 마커) | whoosh, soft pop | `whoosh soft short`, `pop ui` | 0.3~0.8초 | 카드 첫 프레임 2프레임 앞에서 시작 |
| 키워드·번호 제목 Text+ 등장 | click, pop, tick | `ui click subtle`, `pop small` | 0.1~0.3초 | Text+ 첫 프레임 |
| 챕터 전환(`CHAPTER` 마커, 카드 없는 경계) | swoosh, transition | `transition swoosh clean` | 0.4~0.8초 | 마커 4프레임 앞 |
| 콜드 오픈 티저 컷 사이(reflection) | short whoosh, glitch | `whoosh quick`, `glitch short` | 0.2~0.4초 | 컷 프레임 |
| 전후 비교표 강조(빨간 원 등장) | ding, chime | `ding notification soft` | 0.3~0.6초 | 원 등장 프레임 |
| 타임랩스 시작·끝(project) | riser 짧게, whoosh | `riser short`, `whoosh` | 0.5~1.0초 | 타임랩스 첫·끝 프레임 |

화면 녹화의 타이핑 소리, 물건 소리 같은 현장음은 효과음으로 만들지 않는다. 화면 클립에 현장음이 있으면 A2 `LOCATION`에 넣는 것이 `davinciresolve-beats-devtalk`의 일이다.

## 밀도 제한

| 항목 | 제한 |
|---|---|
| 분당 효과음 수 | 최대 6개. 넘으면 키워드 Text+ 효과음부터 뺀다 |
| 같은 효과음 연속 | 3회 이상 같은 파일을 연속으로 쓰지 않는다. 같은 종류 안에서 2~3개를 번갈아 쓴다 |
| 말 위 겹침 | 음성 문장 중간에 놓지 않는다. 문장 사이 또는 문장 첫 프레임에 맞춘다 |
| 종류 수 | 영상 하나에 효과음 파일 최대 8개. 카드·키워드·전환마다 하나씩 정해 재사용한다 |

## 검색과 선택

1. 플러그인의 효과음(Sound effects) 탭에서 이벤트 종류마다 검색어로 찾아 3개씩 들어 본다.
2. 종류마다 1~2개를 고른다. 기준은 짧고, 저역이 크지 않고(말소리 아래에서 울리지 않음), 꼬리(reverb tail)가 0.3초 이내다.
3. 고른 파일 목록(종류·파일명·길이)을 사용자에게 한 번 보이고, 다운로드는 사용자 확인 뒤 한다. 미리 "확인 없이 진행"이라고 했으면 목록만 남기고 넘어간다.

## 배치

- 내려받은 효과음을 A3에 놓고 트랙 이름을 `SFX`로 맞춘다(`Timeline.SetTrackName("audio", 3, "SFX")`). 플러그인이 다른 트랙에 넣으면 A3로 옮긴다.
- 위치는 이벤트 표의 타이밍대로 프레임 단위로 맞춘다. `AppendToTimeline`에 `mediaType: 2`, `trackIndex: 3`, `recordFrame`을 주어 넣을 수 있다.
- 레벨은 손대지 않는다. `davinciresolve-audio-delivery`가 `VOICE` 기준 상대 레벨을 맞춘다.

## 컷 변경 반영

`davinciresolve-cut-devtalk`이 넘긴 바뀐 구간 목록을 받으면 효과음은 마커·Text+를 따라가지 않으므로 이벤트 위치를 다시 읽어 옮긴다.

## 작업 로그

`오디오` 절에 아래 표를 남긴다.

```markdown
효과음 파일 6개(Epidemic Sound), 총 23개, 최대 분당 5개

| 타임라인 TC | 이벤트 | 파일명 | 길이 | 비고 |
|---|---|---|---|---|
| 00:00:14:28 | 카드 등장 title-02 | whoosh_soft_01.wav | 0.5초 | |
| 00:01:05:00 | 키워드 namespace | ui_click_02.wav | 0.2초 | |
```

## 하지 않는 것

- 표에 없는 이벤트에 효과음 붙이기, 음성 문장 중간에 놓기
- 분당 6개 초과, 같은 파일 3회 연속
- 현장음을 효과음으로 대체하기
- 레벨 조정(`davinciresolve-audio-delivery`의 일)
- 사용자 확인 없는 다운로드(미리 허용한 경우 제외)
