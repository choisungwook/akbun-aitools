---
name: akbun-davinciresolve-timeline-chrono
description: DaVinci Resolve 21.1 스크립팅 API로 미디어 풀의 영상 클립 전부를 촬영 시각(Date Recorded, 없으면 Date Created)순으로 나열한 새 타임라인을 만든다. 카메라 시계 오프셋은 파일명 접두어별 초로 보정하고, 시각이 없는 클립은 맨 뒤에 두고 확인 필요로 남긴다. 기존 타임라인은 건드리지 않는다. "촬영 순서대로 타임라인 만들어줘", "시간순으로 클립 나열" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-timeline-chrono

미디어 풀의 영상 클립을 촬영 시각순으로 넣은 새 타임라인을 만든다. 기존 타임라인·클립은 수정하지 않는다. 실행 수단은 [`scripts/chrono_timeline.py`](scripts/chrono_timeline.py) 하나다.

`davinciresolve-video-editor`의 2단계(작업 타임라인, 촬영 시간순)를 이 skill이 맡는다.

## 시각을 읽는 순서

| 순서 | 출처 | 예 | 비고 |
|---|---|---|---|
| 1 | 클립 속성 `Date Recorded` | `2026-09-26T17:52:19+0900` | Apple Log(Blackmagic Cam) 클립에 있다 |
| 2 | 클립 속성 `Date Created` | `Sat Sep 26 2026 18:01:54` | Insta360, iPhone 기본 카메라 클립. 파일 생성 시각이라 복사 방식에 따라 어긋날 수 있다 |
| 없음 | - | - | 맨 뒤에 이름순으로 붙이고 `확인 필요` |

카메라 시계가 어긋나면 `--offset 접두어=초`로 보정한다. 예: Insta360이 37초 빠르면 `--offset VID_=-37`. 오프셋 값은 `davinciresolve-video-editor` 1단계(같은 장면을 두 카메라로 찍은 쌍)에서 구한다. 접두어가 여러 개 맞으면 긴 것이 이긴다.

## 실행 순서

1. `--dry-run`으로 순서 표를 먼저 본다. 시각 출처가 `Date Created`인 클립이 섞여 있으면 순서가 맞는지 사용자와 확인한다.
2. 이름을 정하고 만든다. 같은 이름이 있으면 만들지 않고 멈춘다.
3. 스크립트가 만든 타임라인의 V1 순서를 다시 읽어 계획과 같은지 검증하고 로그에 남긴다.

dry-run 명령이다. `--folder`로 bin을 제한할 수 있다(반복 가능).

```bash
python3 scripts/chrono_timeline.py --dry-run --folder iphone_movie --folder insta360_movie
```

생성 명령이다. 이름을 주지 않으면 `chrono_<YYYYMMDD_HHMM>`이다.

```bash
python3 scripts/chrono_timeline.py --name "<원본 이름>_edit_<YYYYMMDD_HHMM>" --offset VID_=-37 --out "<출력 폴더>"
```

## 작업 로그

스크립트 출력(`--out`이 있으면 `timeline-chrono_<YYYYMMDD_HHMM>.md`)을 작업 로그 `2. 작업 타임라인` 절에 넣는다.

```markdown
| 순서 | 파일명 | 촬영 시각(보정 후) | 출처 | 보정(초) | 비고 |
|---|---|---|---|---|---|
| 1 | IVDB4951.MOV | 2026-09-26 17:52:19 | Date Recorded | +0 |  |
| 2 | VID_20260926_180154_052.mp4 | 2026-09-26 18:01:54 | Date Created | +0 |  |
```

## 하지 않는 것

- 기존 타임라인의 클립 이동·삭제
- 파일명이나 외관으로 촬영 시각 추정
- 사용자가 준 오프셋 없이 카메라 시계 보정
- 같은 이름의 타임라인 덮어쓰기
