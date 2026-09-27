---
name: davinciresolve-story-devtalk
description: 개발자의 얼굴 비노출 말하기 영상(기술 설명·프로젝트·일상·주차 diary·회고)을 DaVinci Resolve에서 편집하는 workflow. story arc와 5–7분 기본 길이를 적용하고 전사·비트·컷·화면·자막·그래픽·오디오 단계를 관리한다. 촬영 전 기획은 akbun-vlog-prepared-devtalk으로 연결한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-story-devtalk

말소리가 있는 개발자 브이로그 편집의 순서·완료 조건·검증·기록을 선언한다. 화자는 얼굴을 드러내지 않는다. 화면에는 얼굴 없는 화면 클립·화면 녹화·필요한 그래픽만 나가고 말소리는 그 위에 흐른다. 개인 경험은 시청자 맥락과 실제 사건을 잇는 이야기의 중심을 이루며, 하루·주차의 작업 목록만 나열하지 않는다. 기본 길이는 5–7분, 최대 10분 미만이다. 화면 클립은 이야기 역할을 기록한다. 각 단계 규칙의 원본은 그 단계 `SKILL.md`이며, 이 skill은 그것을 순서대로 읽는다. 모든 단계 skill이 직접 호출 전용이므로 Skill 도구로 부르지 않고 문서를 읽어 수행한다. 사용자는 단계 skill을 단독으로 부를 수 있다.

`akbun-davinciresolve-workflow`의 기본 원칙(작업 타임라인에서만 편집, 클립은 파일명 + 시작 타임코드, 대표 1개 선적용, 작업 로그, 되돌릴 수 없는 작업은 확인)과 마커 등록표를 그대로 따른다. 말소리 없는 여행 영상은 그 skill이 맡는다.

## 시작 조건

미디어 풀 또는 사용자가 준 폴더에 영상 클립이 1개 이상 있어야 한다. 클립이 없거나 사용자가 "촬영 전"이라고 하면 편집은 시작하지 않는다. 이야기·스토리보드·스케치·촬영 계획을 만들려면 `akbun-vlog-prepared-devtalk`을, 이야기가 정해져 있고 촬영 logistics만 필요하면 `akbun-vlog-shootplan`을 안내한다.

## 스타일 선택

사용자가 지정하면 그것을 쓴다. 지정이 없으면 주제 유형으로 정하고 로그에 이유를 적는다. 고른 style skill의 `SKILL.md`(구조 표, 컷 리듬 표, 글자 표)를 아래 모든 단계가 읽는다.

| 주제 유형 | 스타일 skill |
|---|---|
| 기술 원리·개념·트레이드오프 설명(모션 그래픽으로 원리를 보여 주는 영상) | `davinciresolve-style-essay` |
| 내가 무엇을 만드는 과정, 개발자 일상·주차 diary의 구체적 변화 | `davinciresolve-style-project` |
| 회고, 개인 생각, 위 둘이 아닌 것 | `davinciresolve-style-reflection` |

day-in-the-life와 주차 diary에서 진행·장애·결과가 중심이면 `project`, 사건 뒤 생각의 변화가 중심이면 `reflection`을 고른다. 두 유형이 섞이면 큰 틀은 `reflection`, 근거가 필요한 설명 구간만 `essay`의 규칙을 쓰고 로그에 적는다. 기본 목표는 5–7분, 최대 10분 미만이다. 사용자가 더 긴 길이를 지정하면 범위를 확인한다.

## 트랙 배치

새 devtalk 타임라인의 기본 배치다. 기존 타임라인의 오디오 역할·인덱스는 사운드 공통 스킬에서 확인하며, 겹치는 음악·스템은 빈 트랙을 추가한다.

| 트랙 | 내용 | 놓는 skill |
|---|---|---|
| V1 | 화면 클립(얼굴 없는 클립, 화면 녹화), 영상만 | `davinciresolve-beats-devtalk`, `davinciresolve-cut-devtalk` |
| V2 | 필요한 그래픽 | 선택한 제작 도구. HyperFrames 선택 시 `davinciresolve-gfx-hyperframes` |
| V3 | Text+ 오버레이 | `davinciresolve-subtitle-devtalk` |
| 자막 트랙 | 대사 자막 | `davinciresolve-subtitle-devtalk` |
| A1 `VOICE` | 음성 클립의 소리만(`mediaType: 2`) | `davinciresolve-beats-devtalk`, `davinciresolve-cut-devtalk` |
| A2 `LOCATION` | 화면 클립의 현장음(쓸 때만) | `davinciresolve-beats-devtalk` |
| A3 `SFX` | Epidemic Sound 효과음 | `davinciresolve-sfx-epidemicsound` |
| A4 `MUSIC` | Epidemic Sound 배경음악 | `davinciresolve-bgm-epidemicsound` |

효과음·음악·레벨·덕킹·검토 마커는 [davinciresolve-sfx-epidemicsound](../davinciresolve-sfx-epidemicsound/SKILL.md)의 공통 기준을 따른다. 오디오 편집 직전에 복제한 작업본 ID를 이후 모든 단계가 이어받는다. 출력 계측은 `davinciresolve-audio-delivery`가 맡는다.

## 실행 환경 확인

시작할 때 확인하고 작업 로그 `환경` 절에 적는다. Resolve 조작 수단은 `akbun-davinciresolve-workflow`의 표를 따르되, Resolve MCP(`get_resolve_status`, `run_script`)가 있으면 그것을 1순위로 쓴다. 전사 수단은 `davinciresolve-beats-devtalk`을 따른다. 그래픽 제작은 필요성과 도구 선택을 먼저 확인한다. 준비 문서의 도구가 미정이면 비용·편집 가능성·출력 형식에 맞춰 제안하고, 선택 전에는 특정 도구를 설치·구매·호출하지 않는다. HyperFrames를 선택한 경우만 `davinciresolve-gfx-hyperframes`를 읽는다. 글꼴은 `davinciresolve-subtitle-devtalk`, Epidemic Sound Workflow Integration 또는 MCP는 사운드 공통 스킬의 확인 방법을 따른다.

## 작업 순서

각 단계는 "읽는 skill → 완료 조건"이다. 필수 입력이나 안전한 실행 조건을 못 채우면 해당 작업을 보류하고 알린다. 그래픽 도구 미정처럼 독립적인 보류 사항은 기록한 뒤 나머지 작업을 진행할 수 있지만, 필요한 결과가 미완성인 상태를 최종 완료로 보고하지 않는다.

| 순서 | 작업 | 읽는 skill | 완료 조건 |
|---|---|---|---|
| 1 | 전사·소재 인벤토리 | `davinciresolve-beats-devtalk` 1절 | 클립 전부가 인벤토리 표에 있고 얼굴 판정과 음성 전사가 붙어 있다 |
| 2 | 스토리 비트 제안 | `davinciresolve-beats-devtalk` 2절 | 비트 시트를 사용자가 확정했다. 이 workflow에서 사용자 확인을 받는 유일한 필수 지점 |
| 3 | 비트 순서로 나열 | `davinciresolve-beats-devtalk` 3절 | 작업 타임라인에 구간이 비트 순서로 놓였고 비트마다 `CHAPTER`, 카드 자리마다 `GFX` 마커가 있다 |
| 4 | 문장 단위 컷 | `davinciresolve-cut-devtalk` | 불필요한 침묵·재녹음·필러 제거, 의도된 pause 보존, 리듬 조정 이유 기록 |
| 5 | 오버레이 자막 | `davinciresolve-subtitle-devtalk` | style skill 글자 표대로 들어갔고 안전 영역 안이며 최소 글자 크기를 지킨다 |
| 6 | 필요한 그래픽 제작 | 선택한 도구의 절차; HyperFrames 선택 시 `davinciresolve-gfx-hyperframes` | 확정한 `GFX` 위치에 타임라인 해상도·fps와 맞는 결과가 있다. 그래픽 불필요이면 건너뜀, 도구 미정이면 아이디어와 위치를 유지하고 다른 작업 진행 |
| 7 | 사운드 디자인·음악 계획 | `davinciresolve-sfx-epidemicsound` | 복제본에 원음·환경음·동작/창작 SFX·필요한 음악 cue가 배치되고 말 가림·싱크와 검토 마커 확인 |
| 8 | 필요한 BGM 보완 | `davinciresolve-bgm-epidemicsound` | 7단계에 미완성인 음악 cue만 보완. 이미 배치된 음악은 반복 삽입하지 않고 선택 이유·구간 기록 |
| 9 | 노출·색, 타인 얼굴 모자이크, 최종 믹스 계측·렌더 | `akbun-davinciresolve-workflow` 5~11·13·17단계 | 그 skill의 완료 조건 |

5단계 뒤에 컷을 다시 고치면 `davinciresolve-cut-devtalk`이 바뀐 구간 목록을 넘기고 5~8단계 skill이 위치를 다시 맞춘다. 단계를 건너뛰거나 바꾸면 이유를 로그에 적는다.

## 검증

9단계 렌더 전 확인하고 작업 로그 `검증` 절에 표로 남긴다. 하나라도 실패면 렌더하지 않는다.

| 항목 | 확인 방법 | 통과 기준 |
|---|---|---|
| 훅 위치 | 첫 음성 문장 시작 시각 | 10초 이내 |
| 비트 순서 | `CHAPTER` 마커 순서와 확정 비트 시트 대조 | 일치 |
| 침묵 | `davinciresolve-cut-devtalk`의 silencedetect 명령 | 의도하지 않은 0.7초 초과 침묵 0개. `TALK_REVIEW pause`와 로그로 남긴 여운·현장음 구간은 보존 |
| 리듬 | 평균 샷 길이, 첫 60초 컷 수 | style skill의 시작 범위와 비교하고, 벗어난 구간은 이야기·가독성 근거를 기록 |
| 자막 | 대사 자막 수와 음성 문장 수, 대표 자막 스틸 | style skill이 대사 자막을 쓰면 문장마다 존재, `davinciresolve-subtitle-devtalk`의 최소 크기·안전 영역 안 |
| 그래픽 | 확정한 `GFX` 위치와 V2 결과 대조 | 필요한 그래픽은 존재하고 해상도·fps 일치. 도구 미정으로 미완성이면 완료·최종 렌더로 보고하지 않음 |
| 화자 얼굴 | 타임라인 렌더 프리뷰 또는 V1 구간 원본을 1초 간격 프레임으로 뽑아 얼굴 탐지(`akbun-davinciresolve-workflow` `references/agent-api.md`의 대체 방법) | 화자 얼굴이 식별되는 프레임 0개. 탐지기가 없으면 `확인 필요`로 남기고 렌더하지 않는다 |
| 챕터 | `CHAPTER` 마커 | 3개 이상, 간격 10초 이상 |
| 사운드 | 공통 스킬의 큐시트·검청·마커 | 말 가림·싱크·의도하지 않은 무음/클릭 확인, 미확인 항목은 `AUDIO_REVIEW`와 TC 목록에 존재 |
| 배경음악 | 작업 로그 `오디오` 절 | 사용 곡·스템·구간·전환 이유 기록. 무음 선택도 허용하며 추가 음악 미필요를 실패로 보지 않음 |

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
