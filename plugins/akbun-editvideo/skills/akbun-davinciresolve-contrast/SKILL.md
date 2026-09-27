---
name: akbun-davinciresolve-contrast
description: 단일 Log→Rec.709 LUT 경로에서 DaVinci Resolve 21.1 스크립팅 API로 새 `CONTRAST` 라벨 노드에 pivot 기준 대비를 적용하고 입력 공간의 기준값과 클리핑을 확인한다. DWG 이중 CST 경로는 자동 스크립트 미지원이다. "대비 올려줘", "pivot 맞춰줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-contrast

변환 뒤 밋밋한 영상에 피벗 기준 대비를 준다. 실행 수단은 [`scripts/contrast.py`](scripts/contrast.py)다. 측정·세션·노드 규칙은 `akbun-davinciresolve-exposure`의 `exposure_scope.py`를 가져다 쓴다.

색 작업 순서에서 이 skill은 `CST`(변환) 다음, `SAT` 앞이다.

## 피벗 이해와 기준값

Contrast는 어두운 값과 밝은 값의 간격을 pivot을 중심으로 넓히거나 좁힌다. Pivot은 대비 조정에서 중심으로 삼을 톤이다. 중간 회색을 anchor로 삼으면 그 값은 고정점으로 남고, 어두운 영역과 밝은 영역이 그 주위에서 반대 방향으로 움직인다. Pivot을 바꾸면 대비의 양쪽에 주는 비중도 바뀌므로, 노출을 대신 맞추는 숫자가 아니라 대비의 기준점을 정하는 값으로 설명하고 화면과 스코프로 판단한다.

피벗 기준값은 카메라 원본의 Log 감마가 아니라 **`CONTRAST` 노드 입력 신호의 작업 색공간/감마**에 맞춘다. 튜토리얼의 `0.336`은 S-Log3 입력을 DaVinci Wide Gamut / DaVinci Intermediate로 CST 변환한 뒤, 출력 CST보다 앞에 둔 대비 노드의 기준이다. 현재 workflow의 Log→Rec.709 LUT 뒤 노드에 그대로 복사하지 않는다.

자주 쓰는 기준값은 [pivot reference](references/pivot-reference.md)에 정리돼 있다. 표에 맞는 색공간이면 그 값을 시작점으로 쓰고, 카메라별 LUT처럼 변환 특성이 다르거나 입력 색공간이 불명확하면 LUT 뒤의 확실한 중립 회색 표본을 스코프로 측정한다. 근거가 없으면 값이 정확히 맞는다고 단정하지 말고, 현재 프로젝트 기본값 `0.435`를 비교 시작점으로 유지한다.

이 스크립트는 Resolve native Contrast/Pivot 연산 자체를 호출하지 않는다. CDL로 `out = (in − pivot) × c + pivot`을 구성한다 → `Slope = c`, `Offset = pivot × (1 − c)`, R=G=B. 이는 같은 기준점 개념을 쓰는 선형 근사이므로 native contrast와 픽셀별 결과가 완전히 같다고 설명하지 않는다.

S 커브는 CDL로 만들 수 없어 하지 않는다. S 커브가 필요하면 Color 페이지 Curves에서 사용자가 직접 넣는다.

| 항목 | 값 |
|---|---|
| 기본 대비 | 1.15 (`--contrast`, 0.5~1.5) |
| workflow 시작 피벗 | 0.435 (`--pivot`, 기본값. universal middle-gray 값이라고 가정하지 않음) |
| 클리핑 판정 | p1 < 16 또는 p99 > 1008 또는 클리핑 0.5% 초과 |
| 클리핑 시 | 대비를 낮춰 최대 3회 재측정, 1.0까지 내려가면 적용 안 함 |

## 노드 규칙

Color 페이지에서 변환(LUT·CST) **뒤**에 새 노드를 만들고 라벨 `CONTRAST`(또는 `04_Contrast`)를 단다. 스크립트는 라벨에 `contrast`가 들어간 노드만 쓴다. 노드가 변환 앞(Log 공간)에 있으면 적용하지 않고 `확인 필요`로 남긴다. 절차는 `akbun-davinciresolve-exposure`의 노드 규칙과 같다.

현재 자동 경로에서는 단일 카메라 LUT 뒤 Rec.709 신호를 처리한다. DWG/Intermediate에서 보정한 뒤 Output CST로 나가는 구조는 이 스크립트가 Output CST를 변환 앞 노드로 오인해 건너뛸 수 있으므로 실행하지 않는다. 해당 경로에서는 Resolve native Contrast/Pivot을 사용하고 workflow의 로컬 pivot reference와 신호 공간을 확인한다.

## 실행 순서

1. `--dry-run`으로 클립별 p10~p90 폭을 본다.
2. `CONTRAST` 노드를 준비한다.
3. 적용한다. 기본 피벗을 바꾸려면 로컬 pivot reference에서 노드 입력 공간의 값을 확인해 `--pivot`에 준다. 대표 클립 한 개에서 결과를 확인하고 필요하면 `--contrast`도 조절한다. 같은 노드를 덮어쓴다.

적용 명령이다.

```bash
python3 scripts/contrast.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --contrast 1.15 --pivot 0.435
```

예: `CONTRAST` 노드 입력이 DaVinci Intermediate면 스크립트를 실행하지 않고 Resolve native Contrast/Pivot에서 `0.336`을 비교 시작점으로 쓴다. 자동 경로용 `--pivot` 예시와 혼동하지 않는다.

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
