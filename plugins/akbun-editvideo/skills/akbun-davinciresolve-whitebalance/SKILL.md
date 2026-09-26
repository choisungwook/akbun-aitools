---
name: akbun-davinciresolve-whitebalance
description: DaVinci Resolve 21.1 스크립팅 API로 클립마다 중립(무채색) 픽셀의 R·G·B를 재고, 촬영 시간대별 허용 색온도(오후는 따뜻하게, 저녁은 차갑게 남김) 안에서 Color 페이지의 새 `WB` 라벨 노드에 채널별 CDL로 화이트밸런스를 맞춘다. iPhone Apple Log·Insta360 I-Log는 변환 앞 노드에서 채널 Offset, Rec.709는 채널 Slope. "화이트밸런스 맞춰줘", "클립마다 색온도 달라" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-whitebalance

인접 클립 사이에 색온도가 튀지 않게 화이트밸런스를 맞춘다. 판단 근거는 눈이 아니라 중립 픽셀의 R·G·B 수치다. 밝기는 `akbun-davinciresolve-exposure`가 맡고 이 skill은 색만 다룬다.

`davinciresolve-video-editor`의 기본 원칙과 `akbun-davinciresolve-exposure`의 노드 규칙(새 노드 + 라벨, 라벨 없는 노드에는 쓰지 않음)을 그대로 따른다. 실행 수단은 [`scripts/whitebalance.py`](scripts/whitebalance.py)다. 측정·세션 코드는 exposure skill의 `exposure_scope.py`를 가져다 쓴다.

## 용어

- 중립 픽셀: Resolve 출력 스틸을 320px 폭으로 줄인 뒤 최대 채널이 25~85% 밝기이고 채도((max−min)/max)가 20% 이하인 픽셀. 화면의 0.5% 미만이면 기준 없음
- R/G/B: 중립 픽셀의 채널 평균, 10비트 스케일
- 목표 R−B: 시간대별로 남길 색온도. 양수면 따뜻하게(R>B), 음수면 차갑게

## 노드 규칙

Color 페이지에서 새 노드를 만들고 라벨 `WB`(또는 `02_WB`, `white`)를 단다. 스크립트는 라벨에 `wb`나 `white`가 들어간 노드만 쓰고, 라벨 없는 노드·기존 그레이드 노드에는 쓰지 않는다. 노드 추가·라벨 절차는 `akbun-davinciresolve-exposure`의 노드 규칙과 같다(`Append a Node` → `Label Selected Node`).

- iPhone Apple Log, Insta360 I-Log: 변환(LUT·CST) 노드 **앞**에 `WB`를 둔다(`Add Serial Before Current`). 로그 공간의 채널 Offset은 선형 게인과 같아 카메라 화이트밸런스를 바꾸는 것과 같은 효과다.
- Rec.709 소스나 변환 뒤에 둔 노드: 채널 Slope(게인).
- G는 고정하고 R·B만 움직인다. Saturation은 1.0으로 둔다.

## 시간대별 목표

시간대 구분은 `akbun-davinciresolve-exposure`와 같다(`--sunrise`, `--sunset`).

| 시간대 | 목표 R−B | 뜻 |
|---|---|---|
| 아침 | +10 | 살짝 따뜻하게 |
| 낮 | 0 | 중립 |
| 오후(골든아워) | +30 | 노을의 주황빛을 남긴다 |
| 저녁(블루아워) | −20 | 푸른 기를 남긴다 |
| 밤·미상 | 0 | 인공조명은 중립 기준 |

통과 기준: R−G가 목표/2, B−G가 −목표/2에서 각각 ±20 이내. 이미 통과한 클립은 손대지 않는다.

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
python3 scripts/whitebalance.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --sunrise 06:20 --sunset 18:20 --dry-run
```

적용 명령이다. `--skip-missing`을 주면 `WB` 노드가 없는 클립은 건너뛰고 로그에만 남긴다.

```bash
python3 scripts/whitebalance.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --sunrise 06:20 --sunset 18:20
```

되돌리기 명령이다.

```bash
python3 scripts/whitebalance.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --reset
```

## 작업 로그

`<출력 폴더>/whitebalance_<YYYYMMDD_HHMM>.md`를 작업 로그 `4b. 화이트밸런스` 절에 넣는다.

```markdown
| 파일명 | 시작 TC | 촬영 시각 | 시간대 | 목표 R-B | 기준 픽셀% | R/G/B 전 | R/G/B 후 | 조정 | 판정 |
|---|---|---|---|---|---|---|---|---|---|
| VID_20260926_180716_060.mp4 | 01:01:37:08 | 18:07 | 오후 | +30 | 47.73 | 623/597/585 | 612/597/582 | 노드2 Slope R 0.9823 B 0.9949 | 통과 |
```

## 하지 않는 것

- 라벨 없는 노드·LUT·CST·기존 그레이드 노드에 쓰기
- 중립 기준 없이 눈으로 조정
- 노을·블루아워의 의도된 색온도를 중립으로 되돌리기
- 밝기·채도 조정(CDL Saturation 1.0, G 고정)
