---
name: davinciresolve-story-devtalk
description: 개발자가 얼굴 없이 목소리로 말하는 브이로그(기술 원리·트레이드오프 설명, 내 프로젝트 과정, 회고·개인 생각)를 DaVinci Resolve에서 편집하는 workflow 선언. 편집 스타일(davinciresolve-style-essay·project·reflection)을 고른 뒤 davinciresolve-beats-devtalk(전사·비트·나열) → davinciresolve-cut-devtalk(문장 단위 컷) → davinciresolve-subtitle-devtalk(자막) → davinciresolve-gfx-hyperframes(그래픽 카드) → davinciresolve-sfx-epidemicsound(효과음) → davinciresolve-bgm-epidemicsound(배경음악 후보·선택 보고) 순서로 각 SKILL.md를 읽어 수행하고 단계별 완료 조건·검증·작업 로그를 관리한다. 영상 클립이 없으면 중단하고 akbun-vlog-shootplan을 안내한다. "이 영상 스토리 잡아서 끝까지 편집해줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-story-devtalk

말소리가 있는 개발자 브이로그 편집의 순서·완료 조건·검증·기록을 선언한다. 화자는 얼굴을 드러내지 않는다. 화면에는 얼굴이 없는 화면 클립·화면 녹화·그래픽 카드만 나가고 말소리는 그 위에 흐른다. 화면 클립의 종류는 제한하지 않는다. 이 전제는 모든 단계 skill에 적용된다. 각 단계의 규칙은 그 단계 skill의 `SKILL.md`가 원본이고, 이 skill은 그것을 순서대로 읽어 수행할 뿐 규칙을 다시 적지 않는다. 단계 skill은 모두 사용자 직접 호출 전용(`disable-model-invocation: true`)이므로 Skill 도구로 부르지 않고 `SKILL.md`를 읽어 직접 수행한다. 경로는 이 파일과 같은 `skills/` 아래다. 사용자는 어느 단계 skill이든 단독으로 부를 수 있다.

`davinciresolve-video-editor`의 기본 원칙(작업 타임라인에서만 편집, 클립은 파일명 + 시작 타임코드, 대표 1개 선적용, 작업 로그, 되돌릴 수 없는 작업은 확인)과 마커 등록표를 그대로 따른다. 말소리 없는 여행 영상은 그 skill이 맡는다.

## 시작 조건

미디어 풀 또는 사용자가 준 폴더에 영상 클립이 1개 이상 있어야 한다. 클립이 없거나 사용자가 "촬영 전"이라고 하면 여기서 중단하고, 촬영 방향은 `akbun-vlog-shootplan`이 맡는다고 한 줄로 안내한다. 클립 없이 스토리·촬영 계획을 만들지 않는다.

## 스타일 선택

사용자가 지정하면 그것을 쓴다. 지정이 없으면 주제 유형으로 정하고 로그에 이유를 적는다. 고른 style skill의 `SKILL.md`(구조 표, 컷 리듬 표, 글자 표)를 아래 모든 단계가 읽는다.

| 주제 유형 | 스타일 skill |
|---|---|
| 기술 원리·개념·트레이드오프 설명(모션 그래픽으로 원리를 보여 주는 영상) | `davinciresolve-style-essay` |
| 내가 무엇을 만드는 과정, 시행착오 | `davinciresolve-style-project` |
| 회고, 개인 생각, 위 둘이 아닌 것 | `davinciresolve-style-reflection` |

두 유형이 섞이면 큰 틀은 `reflection`, 설명 구간만 `essay`의 규칙을 쓰고 섞은 구간을 로그에 적는다. 총길이는 스타일과 무관하게 10분 미만이다.

## 트랙 배치

단계 skill이 같은 트랙에 겹쳐 놓지 않도록 여기서 고정한다.

| 트랙 | 내용 | 놓는 skill |
|---|---|---|
| V1 | 화면 클립(얼굴 없는 클립, 화면 녹화), 영상만 | `davinciresolve-beats-devtalk`, `davinciresolve-cut-devtalk` |
| V2 | 그래픽 카드 | `davinciresolve-gfx-hyperframes` |
| V3 | Text+ 오버레이 | `davinciresolve-subtitle-devtalk` |
| 자막 트랙 | 대사 자막 | `davinciresolve-subtitle-devtalk` |
| A1 `VOICE` | 음성 클립의 소리만(`mediaType: 2`) | `davinciresolve-beats-devtalk`, `davinciresolve-cut-devtalk` |
| A2 `LOCATION` | 화면 클립의 현장음(쓸 때만) | `davinciresolve-beats-devtalk` |
| A3 `SFX` | Epidemic Sound 효과음 | `davinciresolve-sfx-epidemicsound` |
| A4 `MUSIC` | Epidemic Sound 배경음악 | `davinciresolve-bgm-epidemicsound` |

레벨·덕킹·마스터는 `davinciresolve-audio-delivery`가 맞춘다. 그 skill의 트랙 표는 여행용이므로 A1 `LOCATION`을 `VOICE`, A2 `AMBIENCE`를 `LOCATION`(같은 -12 dB)으로 읽고 A3·A4는 그대로다.

## 실행 환경 확인

시작할 때 확인하고 작업 로그 `환경` 절에 적는다. Resolve 조작 수단은 `davinciresolve-video-editor`의 표를 따르되, Resolve MCP(`get_resolve_status`, `run_script`)가 있으면 그것을 1순위로 쓴다. 전사 수단은 `davinciresolve-beats-devtalk`, HyperFrames는 `davinciresolve-gfx-hyperframes`, 글꼴은 `davinciresolve-subtitle-devtalk`, Epidemic Sound 플러그인은 `davinciresolve-bgm-epidemicsound`의 확인 방법을 따른다.

## 작업 순서

각 단계는 "읽는 skill → 완료 조건"이다. 완료 조건을 못 채우면 다음으로 넘어가지 않고 사용자에게 알린다.

| 순서 | 작업 | 읽는 skill | 완료 조건 |
|---|---|---|---|
| 1 | 전사·소재 인벤토리 | `davinciresolve-beats-devtalk` 1절 | 클립 전부가 인벤토리 표에 있고 얼굴 판정과 음성 전사가 붙어 있다 |
| 2 | 스토리 비트 제안 | `davinciresolve-beats-devtalk` 2절 | 비트 시트를 사용자가 확정했다. 이 workflow에서 사용자 확인을 받는 유일한 필수 지점 |
| 3 | 비트 순서로 나열 | `davinciresolve-beats-devtalk` 3절 | 작업 타임라인에 구간이 비트 순서로 놓였고 비트마다 `CHAPTER`, 카드 자리마다 `GFX` 마커가 있다 |
| 4 | 문장 단위 컷 | `davinciresolve-cut-devtalk` | 침묵·재녹음·필러 제거, style skill 컷 리듬 표 범위 안 |
| 5 | 오버레이 자막 | `davinciresolve-subtitle-devtalk` | style skill 글자 표대로 들어갔고 안전 영역 안이며 최소 글자 크기를 지킨다 |
| 6 | 그래픽 카드 | `davinciresolve-gfx-hyperframes` | `GFX` 마커마다 V2에 카드 클립이 있다(style skill이 카드를 쓰는 경우) |
| 7 | 효과음 | `davinciresolve-sfx-epidemicsound` | 이벤트 표의 위치에 A3 효과음이 있고 밀도 제한 안 |
| 8 | 배경음악 | `davinciresolve-bgm-epidemicsound` | 후보 표와 선택 이유를 사용자에게 말했고 A4에 곡이 있다 |
| 9 | 노출·색, 타인 얼굴 모자이크, 오디오 믹싱, 렌더 | `davinciresolve-video-editor` 4·6·8·10단계 | 그 skill의 완료 조건 |

5단계 뒤에 컷을 다시 고치면 `davinciresolve-cut-devtalk`이 바뀐 구간 목록을 넘기고 5~8단계 skill이 위치를 다시 맞춘다. 단계를 건너뛰거나 바꾸면 이유를 로그에 적는다.

## 검증

9단계 렌더 전 확인하고 작업 로그 `검증` 절에 표로 남긴다. 하나라도 실패면 렌더하지 않는다.

| 항목 | 확인 방법 | 통과 기준 |
|---|---|---|
| 훅 위치 | 첫 음성 문장 시작 시각 | 10초 이내 |
| 비트 순서 | `CHAPTER` 마커 순서와 확정 비트 시트 대조 | 일치 |
| 침묵 | `davinciresolve-cut-devtalk`의 silencedetect 명령 | 0.7초 넘는 침묵 0개(카드 구간 제외) |
| 리듬 | 평균 샷 길이, 첫 60초 컷 수 | style skill 컷 리듬 표 범위 안 |
| 자막 | 대사 자막 수와 음성 문장 수, 대표 자막 스틸 | style skill이 대사 자막을 쓰면 문장마다 존재, `davinciresolve-subtitle-devtalk`의 최소 크기·안전 영역 안 |
| 카드 | `GFX` 마커 수와 V2 카드 클립 수 | 같다, 해상도·fps가 타임라인과 같다 |
| 화자 얼굴 | 타임라인 렌더 프리뷰 또는 V1 구간 원본을 1초 간격 프레임으로 뽑아 얼굴 탐지(`davinciresolve-video-editor` `references/agent-api.md`의 대체 방법) | 화자 얼굴이 식별되는 프레임 0개. 탐지기가 없으면 `확인 필요`로 남기고 렌더하지 않는다 |
| 챕터 | `CHAPTER` 마커 | 3개 이상, 간격 10초 이상 |
| 효과음 | A3 클립 수와 위치 | 분당 6개 이하, 음성 문장 중간에 없음 |
| 배경음악 | 작업 로그 `오디오` 절 | 후보 표·선택 이유·곡명·아티스트가 있다 |

## 작업 로그

`<출력 폴더>/edit-log_<YYYYMMDD_HHMM>.md`에 아래 구조로 쓴다. 각 단계 skill이 자기 절을 채운다. 9단계에서 읽는 여행 skill들이 쓰는 절 이름은 여기서 바꿔 읽는다. `4. 색보정`·`5. LOOK`·`6. 모자이크`는 `색` 절 아래 소제목으로, `8. 오디오`는 `오디오` 절로 쓴다.

```markdown
# 편집 작업 로그 <YYYYMMDD_HHMM>
## 환경
## 스타일
## 인벤토리
## 비트 시트(확정본)
## 컷
## 자막·챕터
## 그래픽 카드
## 색
## 오디오
## 검증
## 확인 필요
```

## 하지 않는 것

- 클립 없이 시작, 사용자 확정 없이 3단계 진입
- 화자 얼굴이 보이는 프레임을 화면에 내는 것. 모자이크로 가리는 것도 하지 않고 다른 화면으로 바꾼다
- 단계 skill의 규칙을 이 파일에서 바꾸거나 덧붙이는 것
- 말소리 없는 여행 영상 편집
- 마커 등록표 밖의 색·이름·오프셋
