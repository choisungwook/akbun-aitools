---
name: akbun-davinciresolve-workflow
description: DaVinci Resolve 21.1 색보정 workflow 선언. 미디어 풀 영상 전부를 촬영 시간순 타임라인으로 만들고(akbun-davinciresolve-timeline-chrono), 그 타임라인을 복제한 작업 타임라인에서 클립마다 라벨 노드(EXPOSURE→WB→CST→CONTRAST→SAT→SKY)를 준비한 뒤 akbun-davinciresolve-logconvert → exposure → whitebalance → contrast → saturation → sky 순서로 각 skill의 SKILL.md를 읽어 수행하고 로그를 모은다. 컷·자막·오디오는 하지 않는다. "영상 전부 시간순으로 놓고 색보정까지 해줘", "컬러 그레이딩 workflow" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-workflow

촬영한 영상을 시간순 타임라인에 올리고, 복제본에서 색보정을 노드 순서대로 끝낸다. 이 skill은 순서·노드 준비·검증·로그만 맡고, 각 단계의 규칙은 해당 skill의 `SKILL.md`가 원본이다. 하위 skill은 모두 사용자 직접 호출 전용이라 이 skill이 각 `SKILL.md`를 읽고 그 스크립트를 직접 실행한다. 경로는 이 파일과 같은 `skills/` 아래다.

`davinciresolve-video-editor`의 기본 원칙(원본 타임라인 불변, 클립은 파일명 + 시작 TC, 작업 로그)을 따른다. 컷·안정화는 `davinciresolve-cut-travelflow`, 자막·오디오·렌더는 `davinciresolve-video-editor`의 몫이고 이 workflow는 색만 한다.

## 노드 순서와 실행 순서

노드는 신호 흐름 순서, 실행은 측정이 가능한 순서다. 둘이 다르다. LUT를 먼저 걸어야 그 뒤 스코프값이 Rec.709 기준이 되고, 밝기·화이트밸런스 노드는 LUT **앞**에 있어도 측정은 LUT를 거친 출력으로 한다.

| 노드 순서 | 라벨 | skill | 실행 순서 | 위치 |
|---|---|---|---|---|
| 1 | `EXPOSURE` | `akbun-davinciresolve-exposure` | 2 | 변환 앞(Log는 Offset) |
| 2 | `WB` | `akbun-davinciresolve-whitebalance` | 3 | 변환 앞(Log는 채널 Offset) |
| 3 | `CST` | `akbun-davinciresolve-logconvert` | **1** | Log 클립만. LUT를 건다 |
| 4 | `CONTRAST` | `akbun-davinciresolve-contrast` | 4 | 변환 뒤 |
| 5 | `SAT` | `akbun-davinciresolve-saturation` | 5 | 변환 뒤 |
| 6 | `SKY` | `akbun-davinciresolve-sky` | 6 | 변환 뒤, `--sky`를 준 경우만 |

비Log 클립은 `CST`가 없고 나머지는 같다. 이 순서는 실무 튜토리얼 세 편(Declan Jenkinson "Colour Grading For BEGINNERS", Dunna Did It "My Davinci Resolve Color Grading Process", KC ian "The Highest Level of Color Grading")의 공통점에서 왔다.

| 공통점 | 이 workflow의 대응 |
|---|---|
| 작업 1개 = 라벨 노드 1개(WB, Exposure, CST/LUT, Curves, Saturation, Look) | 라벨 노드 6개, 라벨 없는 노드에는 쓰지 않음 |
| 화이트밸런스·노출은 Log 상태(변환 앞)에서, 대비·채도는 변환 뒤에서 | `EXPOSURE`·`WB`는 `CST` 앞, `CONTRAST`·`SAT`은 뒤 |
| 스코프로 판단: Waveform으로 노출·클리핑, Vectorscope·피커로 WB, 피벗 0.435(Rec.709) 대비 | 스틸 기반 스코프값, 중립 픽셀 R/G/B, `--pivot 0.435` |
| 밤 장면은 어두운 게 맞다("context is important") | 시간대별 목표 대역 |
| 채도는 조금만, 섀도·하이라이트는 채도를 빼서 필름처럼 | 채도 상한 1.25, `--rolloff` |
| 크리에이티브 룩 LUT는 맨 뒤에 약하게(Key Output Gain 0.2) | 이 workflow 밖. `davinciresolve-video-editor` 5단계 `LOOK` 노드 |

## 실행 순서

| 순서 | 작업 | 수단 | 완료 조건 |
|---|---|---|---|
| 0 | 실행 환경 확인: 외부 스크립팅(`DaVinciResolveScript`), Pillow, 화면 조작 권한 | `davinciresolve-video-editor` 실행 환경 확인 절 | 로그 `환경` 절 기록 |
| 1 | 미디어 풀 영상 전부를 촬영 시간순 타임라인 A로 | `akbun-davinciresolve-timeline-chrono` | V1 순서 검증 일치 |
| 2 | A를 복제해 작업 타임라인 B | `scripts/workflow.py duplicate` | B가 현재 타임라인, A는 그대로 |
| 3 | Log 판정 dry-run으로 클립별 `Log`·`비Log`·`미확인` 확정. `미확인`은 사용자에게 물어 `--profile`로 | `akbun-davinciresolve-logconvert --dry-run` | 판정 표 |
| 4 | 클립마다 라벨 노드 준비 | 아래 "노드 준비" | `scripts/workflow.py nodes`가 빠진 라벨 0개 |
| 5 | LUT 적용 | `akbun-davinciresolve-logconvert` | Log 클립 전부 `적용` |
| 6 | 밝기 | `akbun-davinciresolve-exposure` | 전환 표에서 `확인 필요` 사용자 보고 |
| 7 | 화이트밸런스 | `akbun-davinciresolve-whitebalance` | `WB_CHECK` 사용자 보고 |
| 8 | 대비 | `akbun-davinciresolve-contrast` | 클리핑 없음 |
| 9 | 채도 | `akbun-davinciresolve-saturation` | 대역 미달 없음 |
| 10 | 하늘(`--sky`일 때만) | `akbun-davinciresolve-sky` | 결과 스틸 사용자 확인 |
| 11 | 로그 통합 | 이 skill | 각 스크립트 `.md`를 작업 로그에 순서대로 이어 붙임 |

각 단계는 `--dry-run` → 사용자 확인 → 적용이다. 한 단계의 `확인 필요`는 다음 단계를 막지 않지만 마지막 보고에 모두 모은다. 되돌리기는 각 skill의 `--reset`이고, 전체 되돌리기는 B를 버리고 A를 다시 복제하는 것이다.

## 노드 준비

스크립팅 API에는 노드 추가·라벨 함수가 없다. Color 페이지 메뉴로 한다. 실측(21.1)으로 확인된 절차다.

1. 작업 타임라인 B를 열고 Color 페이지, `Clips` 스트립을 켠다.
2. 클립마다: API `Timeline.SetCurrentTimecode(클립 중간)`으로 현재 클립을 옮긴다 → 기본 노드 1개가 비어 있으면 `Color → Nodes → Label Selected Node`로 `EXPOSURE` → 이어서 필요한 라벨마다 `Color → Nodes → Append a Node` → `Label Selected Node` → 라벨 입력 → Return.
3. 기존 그레이드(LUT·CST·휠)가 있는 클립은 그 노드를 두고 뒤에 붙인다. 이미 LUT가 1번 노드에 있으면 그 노드 라벨을 `CST`로 바꾸고, `EXPOSURE`·`WB`는 `Add Serial Before Current`로 앞에 넣는다.
4. `scripts/workflow.py nodes`로 클립별 필요 라벨·현재 라벨·빠진 라벨·순서를 표로 확인한다. 빠진 것이 0개일 때 5단계로 간다.

주의(실측): 클립 전체 선택 뒤 Alt+S·메뉴는 현재 클립 하나에만 적용된다. `Add Serial Node`는 선택된 노드 뒤에 끼워 마지막이 아닐 수 있으므로 `Append a Node`를 쓴다. 백그라운드 키 입력(Alt+S)은 전달되지 않으므로 메뉴로 한다. `Next Node`·`Previous Node`로 선택 노드를 옮길 수 있고, 라벨은 선택된 노드에 붙는다. `Label Selected Node` 뒤 Cmd+A → Backspace → Return으로 라벨을 지운다.

화면 조작 권한이 없으면 위 절차를 사용자에게 요청하고 `workflow.py nodes`로만 확인한다.

## 명령

작업 타임라인 복제다.

```bash
python3 scripts/workflow.py duplicate --src "<타임라인 A>" --name "<A>_grade_<YYYYMMDD_HHMM>"
```

노드 준비 상태 점검이다. 빠진 라벨이 있으면 종료 코드 1이다.

```bash
python3 scripts/workflow.py nodes --timeline "<작업 타임라인>" --profile "VID_=Insta360 I-Log" --sky --out "<출력 폴더>"
```

각 단계 명령은 해당 skill의 `SKILL.md`에 있다. `--out`·`--timeline`·`--sunrise`·`--sunset`은 모든 단계에 같은 값을 준다.

## 작업 로그

`<출력 폴더>/edit-log_<YYYYMMDD_HHMM>.md`에 아래 순서로 각 스크립트의 `.md`를 이어 붙인다.

```markdown
# 색보정 작업 로그 <YYYYMMDD_HHMM>

## 환경
## 2. 작업 타임라인(촬영 시간순)      ← timeline-chrono
## 노드 준비 상태                     ← workflow.py nodes
## 5. LUT(Log 변환)                   ← logconvert
## 4. 노출(밝기)                      ← exposure
## 4b. 화이트밸런스                   ← whitebalance
## 4c. 대비                           ← contrast
## 4d. 채도                           ← saturation
## 4e. 하늘                           ← sky
## 확인 필요                          ← 각 표의 확인 필요 행과 마커(EXPOSURE_CHECK, WB_CHECK) 모음
```

## 하지 않는 것

- 컷·안정화·자막·오디오·렌더
- 라벨 없는 노드·기존 그레이드 노드에 쓰기
- `미확인` 클립에 LUT 적용
- 사용자 확인 없이 dry-run 건너뛰기
- 원본 타임라인 A 수정
