---
name: akbun-davinciresolve-saturation
description: DaVinci Resolve 21.1 스크립팅 API로 대비 조정 뒤의 새 `SAT` 라벨 노드에서, 스틸 평균 채도가 촬영 시간대별 대역보다 낮은 클립만 CDL Saturation으로 보충한다. 채도를 낮추지는 않는다. "채도 부족해", "색이 빠졌어", "채도 보충" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-saturation

대비를 준 뒤 부족한 채도만 보충한다. 실행 수단은 [`scripts/saturation.py`](scripts/saturation.py)다. 측정·세션·노드 규칙·시간대 구분은 `akbun-davinciresolve-exposure`의 `exposure_scope.py`를 가져다 쓴다.

색 작업 순서에서 이 skill은 `CONTRAST` 다음, `SKY` 앞이다.

## 측정과 대역

채도는 Resolve 출력 스틸을 320px로 줄여 픽셀마다 `max − min`을 구한 평균이다(10비트). 시간대별 대역보다 낮을 때만 `Saturation = 하한 / 측정값`(최대 1.25)을 건다. 채도는 덜어내는 쪽이 낫다는 것이 실무 튜토리얼의 공통 조언이라 상한을 낮게 둔다. 대역 위는 낮추지 않고 "통과(대역 위)"로 적는다.

| 시간대 | 대역 |
|---|---|
| 아침 | 50~110 |
| 낮 | 60~120 |
| 오후 | 60~130 |
| 저녁 | 45~100 |
| 밤 | 30~80 |
| 미상 | 45~130 |

대역은 경험값이다(화면 전체 평균이라 값이 낮다. 실측: Insta360 저녁 강변 클립 48). 촬영 스타일에 맞지 않으면 스크립트 상단 `BANDS`를 고친다.

## 노드 규칙

Color 페이지에서 `CONTRAST` 뒤에 새 노드를 만들고 라벨 `SAT`(또는 `05_Saturation`)를 단다. 스크립트는 라벨에 `sat`가 들어간 노드만 쓴다. 절차는 `akbun-davinciresolve-exposure`의 노드 규칙과 같다.

## 실행 순서

1. `--dry-run`으로 클립별 채도와 대역을 본다.
2. `SAT` 노드를 준비한다.
3. 적용한다. 스크립트가 적용 뒤 재측정해 하한에 못 미치면 한 번 더 올린다(상한 1.25).
4. `--rolloff`를 주면 섀도(<15%)·하이라이트(>85%)의 채도를 60%까지 줄이는 Luminosity vs Saturation DCTL을 같은 노드 LUT로 건다. 중간톤이 색을 끌고 가고 양끝은 필름처럼 롤오프된다. 양끝 채도가 줄었는지 재측정해 검증한다.

적용 명령이다.

```bash
python3 scripts/saturation.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --sunrise 06:20 --sunset 18:20 --rolloff
```

되돌리기 명령이다. CDL과 롤오프 LUT를 모두 뗀다.

```bash
python3 scripts/saturation.py --out "<출력 폴더>" --timeline "<작업 타임라인>" --reset
```

## 작업 로그

`<출력 폴더>/saturation_<YYYYMMDD_HHMM>.md`를 작업 로그 `4d. 채도` 절에 넣는다.

```markdown
| 파일명 | 시작 TC | 시간대 | 대역 | 채도 전→후 | 양끝/중간 채도 전→후 | 조정 | 판정 |
|---|---|---|---|---|---|---|---|
| VID_20260926_181622_062.mp4 | 01:01:58:21 | 오후 | 60~130 | 48→60 | 30/70→22/70 | 노드4 Saturation 1.250 + 롤오프 akbun/akbun_lumsat_lo15_hi85_f60.dctl | 통과 |
```

## 하지 않는 것

- 채도 낮추기
- 상한 1.25를 넘는 보충
- 피부색 별도 보호(필요하면 `SKY`처럼 색상 범위 DCTL로 따로 만든다)
- 라벨 없는 노드·기존 그레이드 노드에 쓰기
