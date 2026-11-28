---
name: akbun-draw-camera
description: >
  만화·일러스트 그림의 샷 크기와 카메라 높이를 정하는 camera 값의 단일 기준. 다른 akbun-draw
  skill이 장면의 camera를 고르거나 프롬프트에 넣을 때 참조한다.
---

# akbun-draw camera

## 이 skill이 하는 일

장면의 카메라 값을 한 곳에서 정의한다. 그림체나 페이지 형식은 정하지 않고, 쓰는 skill이 값을 골라 자기 spec에 넣는다.

## camera 값

| 값 | 뜻 | 이럴 때 |
|---|---|---|
| `wide` | 장소 소개 | 장소와 인물의 관계를 처음 보여 줄 때 |
| `full` | 상황 | 전신 동작으로 상황을 설명할 때 |
| `medium` | 대화 | 인물끼리 말을 주고받을 때 |
| `close` | 감정 | 표정과 감정을 보여 줄 때 |
| `extreme-close` | 결정적 표정·사물 | 한 표정이나 사물로 결정적 순간을 찍을 때 |
| `low` | 압도 | 인물이나 사물이 크고 위협적으로 보여야 할 때 |
| `high` | 초라함 | 인물이 작고 초라해 보여야 할 때 |
| `top` | 전체 배치 | 공간과 인물 배치를 한눈에 보여 줄 때 |
| `tilt` | 대치·긴장 | 두 인물이 맞서는 긴장을 보여 줄 때. 인물 2명 이상 |

전신이 보이는 값은 `full`, `low`, `high`, `top`이다.

## 값을 바꾸는 법

프롬프트 문장과 조건은 `references/cameras.jsonl`만 고치고 위 표를 맞춘다. 쓰는 skill은 `scripts/camera_prompt.py`로 읽으므로 따로 고치지 않는다.

고친 뒤 아래 명령으로 검사한다.

```bash
uv run --python 3.12 python -I <skill>/scripts/camera_prompt.py --selftest
```
