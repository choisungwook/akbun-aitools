---
name: akbun-davinciresolve-whitebalance
description: DaVinci Resolve 21.1 스크립팅 API로 중립 후보 픽셀의 R·G·B를 측정해 기본은 중립 기준(`R-B 0`)으로 맞추고, 요청하면 따뜻하거나 차가운 기준을 적용한다. `WB` 노드가 있는 LUT-to-Rec.709 경로의 클립 색편차를 정리한다. "화이트밸런스 맞춰줘", "중립 기준으로 맞춰줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-whitebalance

인접 컷과 카메라 사이의 색편차를 정리한다. 판단 근거는 중립 후보 픽셀의 R·G·B 수치와 장면 맥락이다. 인물이나 피부톤은 필요하지 않다. 하얀 건물·회색 포장·구름도 주변광이나 반사색을 받았을 수 있으므로, 장면에서 실제 중립이라고 판단할 근거가 있을 때만 표본으로 쓴다. 확실한 기준이 없으면 억지로 중립화하지 않고 `WB_CHECK`로 남긴다. 기본 목표는 중립(`R-B 0`)이며 촬영 시간만으로 따뜻하거나 차가운 cast를 자동으로 덧붙이지 않는다. 따뜻하거나 차가운 분위기와 split tone은 요청된 새 `LOOK` 노드에서 만든다. 필요하면 `--target-rb`로 사용자가 명시한 색 편향을 보존한다.

참고 영상은 중립적이고 자연스러운 보정과 창작 look을 분리하며, DWG/Intermediate 노드 경로의 HDR Global X/Y 컨트롤로 WB를 맞춘다. 이 스크립트는 현재의 카메라 Log→Rec.709 LUT 경로에서 CDL 채널 보정만 지원하므로 HDR wheel과 동일한 연산이라고 설명하지 않는다. 밝기는 `akbun-davinciresolve-exposure`가 맡는다.

Resolve 21.1과 2026년 9월 공개된 DaVinci Resolve AI Assistant를 대상으로 한다. AI Assistant가 WB 표본이나 변환 위치를 제안해도 색관리 경로와 표본이 실제 중립인지 먼저 확인한다.

`akbun-davinciresolve-workflow`의 기본 원칙과 `akbun-davinciresolve-exposure`의 노드 규칙(새 노드 + 라벨, 라벨 없는 노드에는 쓰지 않음)을 그대로 따른다. 실행 수단은 [`scripts/whitebalance.py`](scripts/whitebalance.py)다. 측정·세션 코드는 exposure skill의 `exposure_scope.py`를 가져다 쓴다.

## 용어

- 중립 픽셀: Resolve 출력 스틸을 320px 폭으로 줄인 뒤 최대 채널이 25~85% 밝기이고 채도((max−min)/max)가 20% 이하인 픽셀. 화면의 0.5% 미만이면 기준 없음
- R/G/B: 중립 픽셀의 채널 평균, 10비트 스케일
- 목표 R−B: 중립 기준은 0. 사용자가 의도적으로 남기려는 색온도 편향을 명시하면 양수는 따뜻하게(R>B), 음수는 차갑게

## 노드 규칙

Color 페이지에서 새 노드를 만들고 라벨 `WB`(또는 `02_WB`, `white`)를 단다. 스크립트는 라벨에 `wb`나 `white`가 들어간 노드만 쓰고, 라벨 없는 노드·기존 그레이드 노드에는 쓰지 않는다. 노드 추가·라벨 절차는 `akbun-davinciresolve-exposure`의 노드 규칙과 같다(`Append a Node` → `Label Selected Node`).

- iPhone Apple Log, Insta360 I-Log: 이 자동 스크립트에서만 변환(LUT·CST) 노드 **앞**에 `WB`를 둔다(`Add Serial Before Current`).
- Rec.709 소스나 변환 뒤에 둔 노드: 채널 Slope(게인).
- G는 고정하고 R·B만 움직인다. Saturation은 1.0으로 둔다.
- 프로젝트 색관리가 DWG/Intermediate이거나 Input CST와 Output CST가 함께 있으면 이 스크립트를 실행하지 않는다. 아래 `workflow`의 DWG/Intermediate 노드 경로를 따라 Resolve UI/AI Assistant에서 HDR Global의 X(따뜻함/차가움)와 Y(녹색/마젠타)를 조정한다. 이 경우 카메라 Log와 CST 사이의 CDL Offset을 임의로 사용하지 않는다.

## 목표 색편향

| 선택 | 목표 R−B | 뜻 |
|---|---|---|
| 기본 | 0 | 중립 후보가 신뢰 가능할 때 중립화 |
| 사용자 지정 예: `--target-rb 30` | +30 | 확인된 따뜻한 cast를 약하게 보존 |
| 사용자 지정 예: `--target-rb -20` | −20 | 확인된 차가운 cast를 약하게 보존 |

`--target-rb`는 해당 실행의 모든 클립에 같은 값을 적용한다. 클립마다 다른 따뜻함·차가움을 자동 추정하지 않는다. `--sunrise`·`--sunset`은 로그의 시간대 표시만 바꾸고 보정 기준에는 영향을 주지 않는다. 통과 기준은 R−G가 목표/2, B−G가 −목표/2에서 각각 ±20 이내다. 이미 통과한 클립은 손대지 않는다.

## 한계값

| 항목 | 값 |
|---|---|
| 채널당 최대 변화 | Offset ±0.10, Slope 1±0.20 |
| secant 반복 | 최대 3회, 매회 스틸 재측정 |
| 중립 픽셀 최소 비율 | 0.5% |

캐스트가 20%를 넘으면 중립 픽셀이 후보에서 빠져 `기준 없음`이 된다. 그때는 조정하지 않고 `WB_CHECK` 클립 마커(Sky, +6)와 `확인 필요`로 남긴다. 사용자가 회색 피사체가 있는 프레임을 알려주면 그 프레임을 기준으로 다시 잰다.

## 실행 순서

1. `--dry-run`으로 클립별 R/G/B와 기준 픽셀 비율을 본다.
2. 노드 규칙대로 `WB` 노드를 준비한다.
3. 적용한다. 스크립트가 클립마다 측정 → 채널 CDL → 재측정으로 맞추고 로그를 쓴다.
4. `확인 필요`와 `WB_CHECK` 마커를 사용자에게 보고한다.

dry-run 명령이다.

```bash
python3 scripts/whitebalance.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --target-rb 0 --dry-run
```

적용 명령이다. `--skip-missing`을 주면 `WB` 노드가 없는 클립은 건너뛰고 로그에만 남긴다.

```bash
python3 scripts/whitebalance.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --target-rb 0
```

되돌리기 명령이다.

```bash
python3 scripts/whitebalance.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --reset
```

## 작업 로그

`<출력 폴더>/whitebalance_<YYYYMMDD_HHMM>.md`를 작업 로그 `4b. 화이트밸런스` 절에 넣는다.

```markdown
| 파일명 | 시작 TC | 촬영 시각 | 시간대(기록용) | 목표 R-B | 기준 픽셀% | R/G/B 전 | R/G/B 후 | 조정 | 판정 |
|---|---|---|---|---|---|---|---|---|---|
| VID_20260926_180716_060.mp4 | 01:01:37:08 | 18:07 | 오후 | +30(사용자 지정) | 47.73 | 623/597/585 | 612/597/582 | 노드2 Slope R 0.9823 B 0.9949 | 통과 |
```

## 하지 않는 것

- 라벨 없는 노드·LUT·CST·기존 그레이드 노드에 쓰기
- 중립 기준 없이 눈으로 조정
- 노을·블루아워의 의도된 색온도를 사용자 확인 없이 중립으로 되돌리기
- 밝기·채도 조정(CDL Saturation 1.0, G 고정)
