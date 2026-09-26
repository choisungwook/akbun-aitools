---
name: akbun-davinciresolve-sky
description: DaVinci Resolve 21.1 스크립팅 API로 하늘(파란 색상 범위) 픽셀만 채도·밝기를 바꾸는 DCTL을 만들어 새 `SKY` 라벨 노드에 걸고, 스틸 위쪽 절반의 하늘 픽셀 비율·채도·밝기로 검증한다. Qualifier·Power Window API가 없어 색상 가중치 DCTL로 대신한다. 하늘이 3% 미만인 클립은 건드리지 않는다. "하늘 진하게", "하늘 날아갔어", "하늘 부분 보정" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-sky

하늘만 골라 채도를 올리고 밝기를 살짝 내린다. 실행 수단은 [`scripts/sky.py`](scripts/sky.py)다. 측정·세션·노드 규칙은 `akbun-davinciresolve-exposure`의 `exposure_scope.py`를 가져다 쓴다.

색 작업 순서에서 이 skill은 마지막(`SAT` 다음)이다.

## 방식

Qualifier와 Power Window는 스크립팅 API가 없다. 대신 픽셀의 색상(hue)과 채도로 가중치 `w`를 만드는 DCTL을 생성해 `Graph.SetLUT`로 노드에 건다.

- 색상 창: 중심 `--hue`(기본 215°, 파랑) ± `--hue-width`/2(기본 40°). 창 안은 1, 창 밖으로 갈수록 0
- 채도 창: 채도 12% 미만은 0(회색 하늘·흰 구름은 제외), 24% 이상은 1
- 조정: 채도 `1 + (sat_gain − 1) × w`, 밝기 `1 + (lum_gain − 1) × w`. 기본 `--sat-gain 1.25`, `--lum-gain 0.9`
- DCTL 파일: Resolve LUT 폴더 `akbun/akbun_sky_h<hue>_w<width>_s<sat>_l<lum>.dctl`. 파라미터가 파일명이라 같은 값이면 재사용

위쪽 절반에 하늘 후보 픽셀이 3% 미만이면 하늘이 없는 것으로 보고 건너뛴다. 조명·건물 유리 같은 파란 물체도 잡힐 수 있으므로 결과 스틸을 사용자가 확인한다.

## 노드 규칙

Color 페이지에서 `SAT` 뒤에 새 노드를 만들고 라벨 `SKY`(또는 `06_Sky`)를 단다. 스크립트는 라벨에 `sky`가 들어간 노드만 쓴다. 절차는 `akbun-davinciresolve-exposure`의 노드 규칙과 같다. 노드에 LUT 자리 하나를 쓰므로 그 노드에는 다른 LUT를 두지 않는다.

## 실행 순서

1. `--dry-run`으로 클립별 하늘 비율·채도·밝기를 본다. 하늘이 없는 클립은 "건너뜀"이다.
2. 하늘이 있는 클립에 `SKY` 노드를 준비한다.
3. 적용한다. 스크립트가 DCTL을 쓰고 `RefreshLUTList` 뒤 노드에 걸고, 재측정해 채도가 의도한 방향으로 움직였는지 확인한다.

적용 명령이다.

```bash
python3 scripts/sky.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --sat-gain 1.25 --lum-gain 0.9
```

되돌리기 명령이다. `SKY` 노드의 LUT를 뗀다.

```bash
python3 scripts/sky.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --reset
```

## 작업 로그

`<출력 폴더>/sky_<YYYYMMDD_HHMM>.md`를 작업 로그 `4e. 하늘` 절에 넣는다.

```markdown
| 파일명 | 시작 TC | 하늘% | 채도 전→후 | 밝기 전→후 | 조정 | 판정 |
|---|---|---|---|---|---|---|
| VID_20260926_181622_062.mp4 | 01:01:58:21 | 31.2 | 180→221 | 760→700 | 노드5 akbun/akbun_sky_h215_w40_s125_l90.dctl | 통과 |
```

## 하지 않는 것

- 하늘이 3% 미만인 클립 조정
- 색상 창 밖(피부·초록) 변경
- 라벨 없는 노드·기존 그레이드 노드에 쓰기
- 사용자 확인 없이 스틸 검토 생략
