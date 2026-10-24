---
name: akbun-davinciresolve-explainer-ember-grid
description: 따뜻한 검정 격자 캔버스 위 굵은 흰 숫자·단어, 흐름을 따라 드러나는 얇은 흰 선, 납작한 벡터 사물, 작은 라임·코발트 라벨로 개념을 차분하게 설명하는 다큐멘터리 설명 영상 스타일 ember-grid를 DaVinci Resolve 타임라인으로 만든다. 끝난 요소는 회색으로 흐려지고, 요소가 작아지며 옮겨 가 다음 설명의 라벨이 된다. 색·글꼴·선·사물·모션 길이는 akbun-draw-ember-grid를 그대로 쓰고, 글자는 Text+로 Inspector에서 고치며, 선·사물은 draw skill이 만든 투명 레이어 PNG를 Fusion으로 움직인다. 클립 구조는 akbun-davinciresolve-explainer를 따르고 배치는 내용에 맞춰 자유롭게 정한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-explainer-ember-grid

## 목적

추상적인 개념을 숫자·선·사물 몇 개로 차분하게 풀어 주는 얼굴 없는 설명 영상을 만든다. 결과물은 Resolve에서 고칠 수 있는 타임라인이다. 장면마다 Fusion 클립 하나이고, 글자·등장 시점·보이기를 Edit 페이지 Inspector에서 바꾼다.

## 범위

- 사용자가 직접 호출할 때 실행한다.
- **스타일 원본**: 색·글꼴·선·사물·바탕·모션 길이·시각 맞추기는 [akbun-draw-ember-grid의 "스타일"](../../../akbun-draw/skills/akbun-draw-ember-grid/SKILL.md#스타일)이 원본이다. 이 문서는 Resolve로 옮기는 데 필요한 값만 옮겨 적고, 어긋나면 draw skill을 따른다. Resolve 때문에 일부러 다르게 하는 것은 하나다: 선은 경로를 따라 그려지지 않고 흐름의 시작 쪽 변에서 끝 쪽 변으로 드러난다.
- **클립 구조**: [akbun-davinciresolve-explainer의 "Resolve 구현"](../akbun-davinciresolve-explainer/SKILL.md#resolve-구현)을 따른다(Fusion 타이틀 + Template 매크로, `Timing` 노드, 표현식 애니메이션, 제너레이터 길이 조정, Inspector 설계, 마커 API, 성능 규칙). 그 스킬의 사실 확인과 "민감 정보 규칙"도 그대로 적용한다.
- **대신하는 것**: 기본 explainer의 "스타일"(고정 위치 포함), "내레이션 규칙", 장면 전환 규칙. 무엇을 어디에 몇 개 둘지는 장면이 설명하는 관계가 정하고, 배치 고르는 기준은 draw skill의 "하지 말 것" 첫 줄을 따른다(흐름을 기본으로 왼쪽→오른쪽에 두지 않는다).
- **그림 레이어**: 선·사물·바탕은 draw skill로 만든 투명 PNG를 쓰고 Fusion 도형으로 다시 그리지 않는다. 글자·숫자·라벨은 PNG로 굽지 않고 Text+로 둔다.
- 사람 얼굴·실사 인물 컷을 넣지 않는다. 렌더된 MP4로 장면을 대신하지 않는다.
- 녹음 정리는 [akbun-davinciresolve-narration-cleanup](../akbun-davinciresolve-narration-cleanup/SKILL.md)을 부른다.

## 캔버스

- 1920×1080이 기본, 쇼츠는 1080×1920 타임라인이다. fps는 대상 타임라인 값(기준이 없으면 30)이고 표현식의 `fps`에는 소수까지 그대로 넣는다(예: 29.97).
- Text+ 좌표·크기는 기본 explainer의 "좌표와 단위"를 화면 폭 W(가로 1920, 세로 1080)로 쓴다: Size = px ÷ W, Center = (px ÷ W, 1 − py ÷ H).
- 모든 장면의 맨 아래는 Background 노드 EMBER(`#181212`) 위 `바탕` Loader(`ground.png`)다. 장면이 바뀌어도 같다.

## 그림 레이어 만들기

draw skill의 SVG 규칙대로 장면을 그린 뒤, 레이어마다 그 부품 하나만 남긴 SVG(바탕 `ground`·글자·시간 속성 없음, 화면 전체 viewBox)를 만든다. 바탕은 `ground` 묶음만 남긴 SVG 하나다. 흐려지는 그림은 같은 도형을 DIMMED 한 색으로 칠한 실루엣 SVG도 하나 더 만든다.

레이어 SVG마다 장면 하나(길이 1프레임)를 둔 spec을 MOV로 렌더하면 `--stills`가 레이어별 투명 PNG를 만든다.

```bash
uv run --python 3.12 <doodle>/scripts/render_doodle.py <출력>/layers_spec.json <출력>/layers.mov --stills <출력>/layers
```

- `<doodle>`은 [akbun-draw-motion-doodle](../../../akbun-draw/skills/akbun-draw-motion-doodle/SKILL.md) 디렉터리다. spec의 장면 `id`가 PNG 이름이 된다(`NN_<id>_1.png`). `layers.mov`는 쓰지 않으니 지워도 된다.
- 레이어마다 그림 영역(bbox, px)과 중심을 장면 표에 적는다. Fusion에서 위치는 PNG 안에 있으므로 Loader·Transform에 위치를 넣지 않고 크기 변화의 중심만 Pivot으로 준다.

## Fusion 구성

| 노드 | 이름 | 연결 |
|---|---|---|
| Background | `배경` | EMBER 단색 → MultiMerge Background |
| Loader | `바탕` | `ground.png` → 첫 레이어 |
| Loader + Transform | `그림_<레이어>` / `이동_<레이어>` | 레이어 PNG → Transform → MultiMerge 레이어. Pivot = 레이어 중심 |
| RectangleMask | `드러남_<선>` | 선 레이어의 Transform에 마스크로. 흐름이 시작하는 쪽 bbox 변(왼·오른·위·아래 중 하나)에 고정하고 그 반대쪽으로 크기를 늘린다 |
| Text+ | `글자_<이름>` | Font `Pretendard`, Style `ExtraBold`(숫자·단어)·`Bold`(라벨)·`SemiBold`(설명). 색은 draw skill 색 표 |
| MultiMerge | `레이어_목록` | 레이어 순서 = 바탕 → 선 → 사물 → 글자 |
| Background | `Timing` | 화면에 연결하지 않는다. `At{k}`, `On{k}`, `MoveAt{k}`, `MoveX{k}`, `MoveY{k}`, `MoveS{k}`, `DimAt{k}` 컨트롤 |

- 색은 hex를 0~1로 바꿔(각 값 ÷ 255, 소수 넷째 자리 반올림) Text+ `Red1`·`Green1`·`Blue1`에 넣는다.
- 그림자·Glow·그라디언트 노드를 넣지 않는다(비네트와 선 끝 흐림은 PNG 안에 이미 있다).

## 모션

길이는 draw skill의 모션 표를 따른다. `fps`는 숫자로 넣고 `^`는 곱셈으로 풀어 쓴다.

- `A(t0)` = `time - (comp.RenderStart + t0 * fps)`, `q(t0, d)` = `min(1, max(0, A(t0) / (d * fps)))`
- `e(u)` = `u * u * (3 - 2 * u)` (ease-in-out)

| 움직임 | 입력 | 식 |
|---|---|---|
| 등장(숫자·단어·사물 0.3초, 라벨·설명 0.2초) | `Layer{n}.Blend` | `q(Timing.At{k}, d)`. 글자 레이어에만 `Timing.On{k}`를 곱한다 |
| 선 드러나기 | `드러남_<선>`의 Width(가로로 드러남) 또는 Height(세로로 드러남)와 Center | 진행률 p = `q(Timing.At{k}, d)`, d = 선 길이(px) ÷ 800을 0.05초 단위로 올림(최소 0.4). 크기 = bbox 크기 × p, Center = 시작 변 + 크기 ÷ 2(Fusion 좌표). 가로·세로는 bbox의 긴 쪽 |
| 흐려지기 | 글자 `Red1`·`Green1`·`Blue1` / 그림은 DIMMED 실루엣 레이어의 `Layer{n}.Blend` | 글자: `원래값 + (DIMMED값 - 원래값) * q(Timing.DimAt{k}, 0.4)`. 그림: 같은 도형을 DIMMED 한 색으로 칠한 실루엣 PNG(그림 레이어 바로 위)의 Blend = `q(Timing.DimAt{k}, 0.4)` |
| 바뀌어 이어지기 | `이동_*`(그림) 또는 Text+의 Size·Center | u = `e(q(Timing.MoveAt{k}, 0.6))`. Size = `원래 Size * (1 + (Timing.MoveS{k} - 1) * u)`. Center = `Point(원래 X + Timing.MoveX{k} * u, 원래 Y + Timing.MoveY{k} * u)`. 원래 값은 그림 Transform이면 Size 1·Center (0.5, 0.5), Text+면 "캔버스"의 Size·Center 값. MoveX·MoveY는 옮길 거리 ÷ W, ÷ H(위가 +) |
| 늘어나기 | 같은 레이어 사본의 `Layer{n}.Blend` | `iif(A(Timing.At{k} + i * 0.08) < 0, 0, 1)`, i = 사본 번호(0부터) |
| 사라짐 | `Layer{n}.Blend` | 등장 식 × `iif(A(사라짐 시점) < 0, 1, 0)` |

- 동시에 진행하는 빌드는 둘까지다. 마지막 빌드는 장면 끝 1.0초 전까지 끝낸다(대본 마지막 단어 때문이면 0.5초까지). 장면 하나는 25초 이하다.
- 카메라는 쓰지 않는다. 장면 전환은 하드 컷이다. 앞 장면 마지막 요소가 다음 장면에서 이어지면 그 요소를 옮긴 자리·크기로 새 장면 0초부터 다 그려진 채로 보이게(`Timing.At` = `-100`) 둔다.
- 시점·이동 값은 `Timing` 컨트롤로만 바꾼다. 키프레임을 쓰지 않는다.

## 작업 흐름

1. **장면 표**: 장면마다 보여 줄 변화, 큰 숫자·단어, 선·사물 레이어(bbox·중심), 라벨 색, 요소별 신호 단어와 시각, 길이를 적는다. 시각은 draw skill의 신호 단어 규칙(녹음 전 초당 6.5음절, 0.1초 앞당김, 장면 끝 + 0.4초)을 따른다. 사용자에게 먼저 보여 주고 확인받는다.
2. **레이어 PNG**: "그림 레이어 만들기"대로 `ground.png`와 선·사물 레이어를 만든다.
3. **Resolve 준비**: 다른 작업이 열어 둔 프로젝트·타임라인을 확인 없이 바꾸지 않는다. 새 타임라인(V1 장면, A1 내레이션, A2 BGM, A3 효과음)을 만든다. `fc-list : family`로 Pretendard 설치를 본다.
4. **대표 장면 하나**로 삽입·매크로·길이·Inspector·선 드러나기·이동을 확인한 뒤 나머지를 만든다.
5. **장면 삽입과 빌드**: 기본 explainer의 "클립 길이 맞추기"로 장면을 끝에 차례로 붙이고, "Fusion 구성"대로 노드를 만들어 표현식을 건다. Template 매크로로 감싸 기본 explainer의 Inspector 설계에 그룹별 "흐려지는 시점"·"옮겨 가는 시점"을 더해 공개한다.
6. **마커**: 장면 시작마다 대본 메모 마커를 단다.
7. **녹음 뒤**: 음성 인식 단어 시각에서 신호 단어를 찾아 `Timing` 시점과 장면 길이를 다시 맞춘다. 못 찾은 신호 단어는 추측하지 말고 목록으로 보고한다.
8. **검수**: 아래 표로 채점한다.

## 검수

장면마다 첫 등장 직후·흐려지기 직후·이어지기 직후·마지막 프레임을 `ExportCurrentFrameAsStill`로 뽑아 한 장으로 붙여 한 번만 본다. 항목마다 0·5·10점, 80점 미만 장면은 고친다.

| # | 항목 | 10점 기준 |
|---|---|---|
| 1 | 바탕 | 모든 장면이 같은 EMBER·격자·비네트 |
| 2 | 색 | 글자 색이 draw skill 색 표 안, 라벨은 LIME·COBALT만 |
| 3 | 글꼴 | Pretendard, 대체 글꼴 없음, 큰 숫자·단어 화면당 2개 이하 |
| 4 | 선 | 흰 선, 흐름의 시작에서 끝으로 드러남, 긴 선은 끝이 흐림 |
| 5 | 사물 | 레이어 PNG 그대로(번짐·잘림 없음), 화면당 2개 이하 |
| 6 | 흐려지기 | 끝난 요소가 0.4초에 걸쳐 회색으로 바뀜 |
| 7 | 이어지기 | 요소가 0.6초에 작아지며 옮겨 가고, 다음 장면에서 같은 자리·크기 |
| 8 | 등장 | 신호 단어 순서대로, 동시 빌드 2개 이하, 마지막 빌드 뒤 1.0초(예외 0.5초) 이상 정지 |
| 9 | 배치 | 글자가 잘리거나 겹치지 않음, 장면마다 같은 배치를 기계적으로 반복하지 않음 |
| 10 | 전환 | 하드 컷, 카메라 움직임 없음, 사람 얼굴·실사 컷 없음 |

- 클립·마커 개수와 끝 프레임을 장면 표와 대조한다.
- Inspector에서 등장 시점 하나를 바꿔 움직임이 옮겨지는지 확인하고 되돌린다. 프로젝트를 저장한다.
- 실제 로고·알려진 캐릭터·영상 장면과 닮아 보이는 화면이 없는지 본다. 닮았으면 사물 모양이나 배치를 바꾼다.

## 완료 보고

타임라인 이름·fps·길이, 장면 표, 레이어 폴더 경로, 장면별 채점 점수, 글꼴 확인, 환경설정 복원 확인 결과를 적는다. 화면으로 보지 않고 스틸로만 확인한 것은 그렇게 적는다.

## 하지 말 것

- 렌더된 MP4로 장면을 대신하거나, 글자를 PNG로 굽지 않는다.
- 기본 explainer의 고정 위치, 크로스 디졸브, 기본 5색을 섞어 쓰지 않는다.
- 카메라 확대·이동, Glow·그림자, 키프레임 애니메이션을 쓰지 않는다.
- 사람 얼굴·실사 인물 컷을 넣지 않는다.
- 다른 작업이 열어 둔 Resolve 프로젝트를 확인 없이 바꾸지 않는다.
