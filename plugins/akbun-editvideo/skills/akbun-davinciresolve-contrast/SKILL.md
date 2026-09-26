---
name: akbun-davinciresolve-contrast
description: DaVinci Resolve 21.1 스크립팅 API로 Log 변환 뒤의 새 `CONTRAST` 라벨 노드에 피벗 기준 대비(Contrast + Pivot)를 CDL(Slope·Offset)로 걸고, 스틸의 p10~p90 폭과 클리핑을 재서 하이라이트·섀도가 날아가면 대비를 줄인다. "대비 올려줘", "밋밋해", "콘트라스트" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-contrast

변환 뒤 밋밋한 영상에 피벗 기준 대비를 준다. 실행 수단은 [`scripts/contrast.py`](scripts/contrast.py)다. 측정·세션·노드 규칙은 `akbun-davinciresolve-exposure`의 `exposure_scope.py`를 가져다 쓴다.

색 작업 순서에서 이 skill은 `CST`(변환) 다음, `SAT`·`SKY` 앞이다.

## 방식

CDL로 피벗 대비를 표현한다. `out = (in − pivot) × c + pivot` → `Slope = c`, `Offset = pivot × (1 − c)`, R=G=B 같은 값. 피벗 기본값은 Rec.709 18% 회색의 부호화값 0.435라 중간 회색은 그대로 두고 위아래만 벌어진다.

S 커브는 CDL로 만들 수 없어 하지 않는다. S 커브가 필요하면 Color 페이지 Curves에서 사용자가 직접 넣는다.

| 항목 | 값 |
|---|---|
| 기본 대비 | 1.15 (`--contrast`, 0.5~1.5) |
| 피벗 | 0.435 (`--pivot`) |
| 클리핑 판정 | p1 < 16 또는 p99 > 1008 또는 클리핑 0.5% 초과 |
| 클리핑 시 | 대비를 낮춰 최대 3회 재측정, 1.0까지 내려가면 적용 안 함 |

## 노드 규칙

Color 페이지에서 변환(LUT·CST) **뒤**에 새 노드를 만들고 라벨 `CONTRAST`(또는 `04_Contrast`)를 단다. 스크립트는 라벨에 `contrast`가 들어간 노드만 쓴다. 노드가 변환 앞(Log 공간)에 있으면 적용하지 않고 `확인 필요`로 남긴다. 절차는 `akbun-davinciresolve-exposure`의 노드 규칙과 같다.

## 실행 순서

1. `--dry-run`으로 클립별 p10~p90 폭을 본다.
2. `CONTRAST` 노드를 준비한다.
3. 적용한다. 필요하면 `--contrast`를 바꿔 다시 돌린다. 같은 노드를 덮어쓴다.

적용 명령이다.

```bash
python3 scripts/contrast.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --contrast 1.15
```

되돌리기 명령이다.

```bash
python3 scripts/contrast.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --reset
```

## 작업 로그

`<출력 폴더>/contrast_<YYYYMMDD_HHMM>.md`를 작업 로그 `4c. 대비` 절에 넣는다.

```markdown
| 파일명 | 시작 TC | p10~p90 전→후 | p1/p99 후 | 클리핑% 후 | 조정 | 판정 |
|---|---|---|---|---|---|---|
| VID_20260926_181622_062.mp4 | 01:01:58:21 | 420→480 | 60/900 | 0.0 | 노드3 Slope 1.150 Offset -0.0653 | 통과 |
```

## 하지 않는 것

- 변환 앞 노드에 대비 적용
- 클리핑을 만들면서 대비 유지
- 라벨 없는 노드·기존 그레이드 노드에 쓰기
- 색·채도 변경(R=G=B, Saturation 1.0)
