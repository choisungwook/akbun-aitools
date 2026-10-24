---
name: akbun-draw-slate-marker
description: 순검정 캔버스 위 어두운 슬레이트 카드와 손글씨 마커 캡션, 의미마다 하나씩 정한 선명한 강조색(청록 정상·코랄 위험·노랑 지금 보는 곳·라벤더 참조·초록 성공)으로 시스템 동작 원리를 설명하는 모션그래픽을 만든다. 스타일(색·글꼴·선·부품 모양·모션)만 고정하고 배치는 내용에 맞춰 자유롭게 정한다. 모델은 장면 SVG와 시간 속성만 쓰고 akbun-draw-motion-doodle의 render_doodle.py가 MP4·투명 MOV를 만든다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-slate-marker

## 언제 쓰나

요청·메모리·프로세스·권한처럼 눈에 보이지 않는 시스템 동작을 "상자와 상태 변화"로 보여 줄 때 쓴다. 이 skill이 고정하는 것은 그림체다. 무엇을 어디에 몇 개 놓을지는 설명할 내용이 정한다. 같은 영상 안에서도 장면마다 배치가 달라도 된다.

- 코드를 한 줄씩 짚는 장면은 [akbun-draw-code-window-lilac](../akbun-draw-code-window-lilac/SKILL.md), 손그림 비유 장면은 [akbun-draw-night-gouache](../akbun-draw-night-gouache/SKILL.md), 같은 스타일을 Resolve에서 글자·시점을 고칠 수 있는 타임라인으로 만드는 일은 [akbun-davinciresolve-explainer-slate-marker](../../../akbun-editvideo/skills/akbun-davinciresolve-explainer-slate-marker/SKILL.md)의 범위다.
- 실제 제품 로고·마스코트를 그리지 않는다. 제품은 이름 글자와 일반 선 아이콘(톱니, 사람, 문서, 원통)으로 나타낸다.

## 캔버스

| 용도 | size | 기준 |
|---|---|---|
| 일반 영상 (기본) | `[1920, 1080]` | 아래 px 값 그대로 |
| 쇼츠·릴스 | `[1080, 1920]` | 아래 px 값 그대로(짧은 변이 1080으로 같다) |

그 밖의 크기는 짧은 변 ÷ 1080을 곱하고 0.5px 단위로 반올림한다.

## 스타일

### 색

색은 의미 하나에 하나다. 영상 전체에서 같은 의미는 같은 색, 다른 의미는 다른 색이다.

| 이름 | 값 | 의미·쓰임 |
|---|---|---|
| INK | `#060606` | 캔버스. spec `background`, `"grain": 0`. SVG에 배경 사각형을 그리지 않는다 |
| SLATE | `#181818` | 카드 채움 |
| SLATE_EDGE | `#262626` | 카드 테두리 |
| CELL | `#101010` | 카드 안 칸(슬롯) 채움 |
| CELL_EDGE | `#2C2C2C` | 칸 테두리 |
| CHALK | `#EDEDED` | 제목·캡션·아이콘 기본 |
| MUTED | `#7A7A7A` | 작은 라벨, 번호, 창 제목 |
| DIM | `#333333` | 꺼진 눈금 칸, 비활성 선 |
| CYAN | `#42B4D2` | 정상 데이터·정상 상태(선에는 쓰지 않는다. 흐름 선은 CHALK) |
| CORAL | `#FC6666` | 위험·공격자·실패·한도 초과 |
| AMBER | `#F2B84B` | 지금 보는 곳(초점 점선) |
| LAVENDER | `#8288CC` | 참조·포인터·연결 관계 |
| GREEN | `#42DE84` | 성공·실행 결과·셸 |
| PILL_TEXT | `#0A0A0A` | 강조색으로 채운 알약·칩 위 글자 |

- 한 포즈의 강조색(CYAN·CORAL·AMBER·LAVENDER·GREEN)은 3가지까지다. 세는 법: 그 포즈 SVG에 나오는 강조색 값의 종류 수(늦게 페이드되는 요소 포함).
- 강조색은 채움 면적보다 선·알약·칩에 쓴다. 카드 전체를 강조색으로 채우지 않는다.
- 창 제목줄의 점 세 개만 예외로 CORAL·AMBER·GREEN을 함께 쓰고, 강조색 개수에 세지 않는다.

### 글꼴

모두 SIL OFL 글꼴이다.

| 대상 | 글꼴 | 크기·모양 |
|---|---|---|
| 제목·캡션·카드 이름·알약 글자 | `'Gaegu', cursive` 700 | 제목 52px, 카드 이름 28px, 캡션 32px, 알약 20px. 영어로만 된 줄은 `letter-spacing="1"`, 한국어가 한 글자라도 있으면 0 |
| 칸 번호·값·태그·창 제목·한도 표시 | `'D2Coding', monospace` | 14~18px |
| 작은 구역 라벨 | `'Gaegu', cursive` 700 | 18px, MUTED |

- 영어 손글씨의 대소문자는 영상마다 하나를 골라 끝까지 지킨다: 원래 대소문자 또는 전부 대문자. 장면마다 바꾸지 않는다. 한 줄 안에서 한국어·영어를 섞어도 된다.
- 제목은 캡션으로 세지 않는다. 제목 밑에는 CHALK 2.5px 직선 밑줄 하나를 baseline 아래 10px에 긋는다. 밑줄 길이 = Pillow `ImageFont.truetype(<Gaegu-Bold.ttf>, 크기).getlength(제목)` + letter-spacing × (글자 수 − 1), 0.5px 단위로 반올림. 글꼴 파일 경로는 `fc-match -f '%{file}' 'Gaegu:bold'`.
- 렌더 전에 `uv run --python 3.12 <doodle>/scripts/render_doodle.py --fonts "Gaegu,D2Coding"`가 둘 다 `ok`인지 본다. `missing`이면 렌더하지 말고 사용자에게 설치를 묻는다. 받는다면 Gaegu는 Google Fonts, D2Coding은 github.com/naver/d2codingfont 릴리스에서 받는다.

### 선과 모양

| 요소 | 모양 |
|---|---|
| 카드 | SLATE 채움 + SLATE_EDGE 1.5px, 모서리 14px, 안쪽 여백 32px. 카드 이름 앞에 선 아이콘(아이콘과 이름 사이 12px). 카드·칸 크기는 내용이 정한다. 그림자·그라데이션 없음 |
| 칸(슬롯) | CELL 채움 + CELL_EDGE 1.5px, 모서리 10px, 크기가 같은 칸끼리 간격 12px. 칸의 순서가 설명에 필요할 때만 칸 아래에 D2Coding MUTED 번호 |
| 칩 | 칸 안에 들어가는 데이터 조각. 강조색 채움, 모서리 6px, PILL_TEXT D2Coding 14px, 칸 가운데. 아직 의미가 없는 값은 칩 대신 MUTED D2Coding 글자로 둔다 |
| 알약 | 높이 30px, 모서리 = 높이의 절반, 강조색 채움, PILL_TEXT Gaegu 20px. 요청·파일·주체의 이름표 |
| 태그 | 값이나 주소를 가리키는 작은 상자. 채움 없음, 그 의미의 강조색 2px 테두리, 모서리 6px, 같은 색 D2Coding 15px |
| 초점 점선 | 대상 바깥 6px에 AMBER 2.5px `stroke-dasharray="7 6"`, 모서리 = 대상 모서리 + 4px |
| 경계 점선 | 묶음, 또는 방금 비워졌다는 사실이 설명의 요점인 구역. CHALK 2px `stroke-dasharray="8 8"`, 불투명도 0.8. 그냥 빈 칸은 CELL 그대로 둔다 |
| 흐름 선 | 무언가가 실제로 오가는 것(요청·응답·데이터 이동). CHALK 2px 실선, 끝에 CHALK 채운 삼각형(밑변 12px, 높이 12px). 선은 삼각형 밑변에서 끝나고 꼭짓점이 대상에 닿는다. 직선 또는 꺾임 한 번. 쓰이지 않게 된 흐름은 DIM 2px 실선, 삼각형 없음 |
| 연결 화살표 | 오가는 것 없이 A가 B를 가리키는 관계(참조·포인터·소속). 그 의미의 강조색 2.5px `stroke-dasharray="6 6"`, 끝 삼각형은 흐름 선과 같은 모양·같은 색 |
| 선 아이콘 | 외곽선만, 2.5px, `stroke-linecap="round"` `stroke-linejoin="round"`, 24~40px. `rect`·`circle`·직선 6개 이하로 만든다. CHALK, 주체가 위험하면 CORAL |
| 눈금 막대 | 정사각형 칸 12×12px, 간격 4px. 찬 칸 CYAN, 빈 칸 DIM, 한도를 넘은 칸 CORAL. 한도는 CHALK 2px 세로선 + D2Coding 라벨 |
| 창 틀 | 카드와 같은 모양 + 위쪽 제목줄(높이 36px): 왼쪽 반지름 5px 점 세 개(CORAL·AMBER·GREEN, 중심 간격 16px), 오른쪽 MUTED D2Coding 제목 |

- 카드·창의 상태(고장, 성공)를 알릴 때만 그 테두리를 그 의미의 강조색 2px으로 바꾼다. 선 아이콘 색도 같은 색으로 바꿔도 된다.
- 캡션 색은 캡션이 가리키는 요소의 강조색이고, 가리키는 요소가 강조색이 아니면 CHALK다. 한 포즈에 캡션은 하나다.
- 화면에 넣는 주소·도메인·키 값이 예시라면 문서용 값(`example.com`, `203.0.113.0/24`, `192.0.2.0/24`)을 쓴다.
- 글자는 짧게 쓴다. 캡션은 영어 6단어, 한국어 16글자 이하. 세는 법: 영어로만 된 캡션은 공백으로 나눈 단어 수, 한국어가 섞이면 공백을 뺀 글자 수(영어·숫자 글자 포함).
- 모든 글자는 `<text>`로 남긴다. `<path>`나 이미지로 바꾸지 않는다.

### 모션

매끄러운 UI 움직임이다. spec의 `drawings_per_second`는 `fps`와 같게 한다(예: 30, 30).

| 움직임 | 방식 | 길이 |
|---|---|---|
| 제목 | 밑줄과 한 `<g data-fade>` | 0.2초 |
| 카드·칸·창 등장 | 한 묶음을 `<g data-fade>`로 감싼다 | 0.25초 |
| 알약·칩·태그 등장 | `data-fade` | 0.15초 |
| 캡션 | `data-fade` | 0.2초 |
| 흐름 선·연결 화살표 | 선은 `data-draw`, 끝 삼각형은 선이 끝날 때 `data-show` | 선 길이(px, 삼각형 제외) ÷ 900초를 0.05초 단위로 올림, 최소 0.3초 |
| 초점 점선 | `data-fade` | 0.15초 |
| 눈금 막대 차오름 | 칸마다 `data-show`, 칸 사이 0.04초 | 칸 수 × 0.04초 |
| 상태 변화(칩 색 바뀜, 칸 비워짐, 창 테두리 색) | 포즈 교체. 바뀐 요소는 새 포즈에 시간 속성 없이 두어 빈 틈 없이 바로 보인다 | 즉시 |
| 사라짐 | 그 요소가 없는 포즈로 교체 | 즉시 |
| 카메라(선택) | 지금 설명하는 묶음으로 다가가기. ease-in-out | 이동 0.6~0.8초, zoom ≤ 1.4, 장면당 2번까지 |

- 빌드(`data-fade`·`data-draw`·눈금 막대 차오름)는 동시에 둘까지 진행한다. 포즈와 상관없이 장면 시각으로 센다. `data-show`와 포즈 교체는 빌드로 세지 않는다.
- 마지막 빌드는 장면 끝 1.0초 전에 끝낸다. 대본 마지막 단어에 묶인 요소 때문에 지킬 수 없으면 0.5초 전까지 허용한다. 장면 전환은 하드 컷, 장면 하나는 25초 이하.
- 카메라 키마다 보이는 영역(가운데 ± 가로/2/zoom, ± 세로/2/zoom)이 캔버스 안에 있어야 한다.
- 시각은 대본의 신호 단어에 묶는다. 신호 단어는 그 요소의 이름이나 그 상태 변화를 말하는 첫 단어다. 이 skill의 수치(선 속도, 빌드 수, 끝 여유)가 링크한 다른 skill과 다르면 이 skill을 따른다. 음절 세는 법과 녹음 후 다시 맞추는 법은 [code-window-lilac의 녹음 전후 시각 맞추기](../akbun-draw-code-window-lilac/SKILL.md#녹음-전후-시각-맞추기)를 따른다.

## 작업 흐름

`<skill>`은 이 `SKILL.md`가 있는 디렉터리, `<doodle>`은 [akbun-draw-motion-doodle](../akbun-draw-motion-doodle/SKILL.md) 디렉터리다. 출력 폴더는 사용자가 정한 곳, 없으면 `slate-marker-output/<작업명>/`.

1. **장면 표**: 장면마다 id, 길이, 보여 줄 상태 변화, 쓰는 부품과 강조색(3가지 이하), 요소별 신호 단어와 시각을 적는다.
2. **SVG 포즈**: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 W H">`로 시작하고 `width`·`height`·배경 사각형·`filter`·`<image>`를 넣지 않는다. 포즈가 여러 장이면 공통 부분을 한 번만 정의하는 작은 생성 스크립트(출력 폴더)로 만들어 포즈 사이 좌표를 똑같이 맞춘다. 점선을 그려지게 하려면 `stroke-dasharray`를 그 `<path>`에 직접 둔다.
3. **spec.json**: `"background": "#060606"`, `"grain": 0`, `fps`와 `drawings_per_second`는 놓을 타임라인 fps(정수). 23.976·29.97처럼 정수가 아니면 렌더하지 말고 사용자에게 알린다. 형식은 render_doodle.py 머리 주석을 따른다.
4. **렌더**: 기본은 `uv run --python 3.12 <doodle>/scripts/render_doodle.py <출력>/spec.json <출력>/out.mp4 --stills <출력>/stills`. 배경을 따로 작업한다는 신호가 있으면 렌더 전에 [motion-doodle의 출력 형식](../akbun-draw-motion-doodle/SKILL.md#2-출력-형식)대로 "MOV(투명 배경)"와 "MP4(검정 배경)" 두 선택지로 묻고, MOV를 고르면 `out.mov`로 렌더한다.
5. **검수**: 아래 숫자 검사를 먼저 하고, 스틸을 한 장으로 붙여 한 번만 본다.

예시: [references/example/](references/example/)는 로드밸런서 헬스체크를 두 포즈로 설명한 장면이다. 스타일 확인용이며 배치·문구를 그대로 쓰지 않는다.

### 검수

SVG에 색 표 밖의 색이 없는지 보는 명령이다. 아무것도 출력하지 않아야 한다.

```bash
grep -ohiE '#[0-9a-f]{6}' <출력>/*.svg | tr a-f A-F | sort -u | grep -vE '^#(060606|181818|262626|101010|2C2C2C|EDEDED|7A7A7A|333333|42B4D2|FC6666|F2B84B|8288CC|42DE84|0A0A0A)$'
```

- 렌더 프레임 수 = 장면 길이 합 × fps.
- `--fonts "Gaegu,D2Coding"`가 모두 `ok`.
- 포즈마다 강조색 종류 ≤ 3(창 제목줄 점 제외), 캡션 ≤ 1개(제목 제외), 캡션 길이 규칙을 지켰는가.
- 동시 빌드 ≤ 2, 마지막 빌드가 장면 끝 1.0초 전에 끝나는가. 카메라 zoom ≤ 1.4, 보이는 영역이 캔버스 안인가.
- 시트에서: 글자가 잘리거나 겹치지 않는가, 실제 로고·알려진 캐릭터와 닮은 그림이 없는가, 같은 의미가 장면마다 같은 색인가.

## 완료 보고

출력 경로, 출력 형식(MP4·MOV)과 고른 이유, 장면 표(신호 단어·녹음 전 시각·녹음 후 시각), 렌더 프레임 수, 글꼴 검사, 색 검사 출력, 검수 결과를 적는다. 확인하지 않은 항목은 "확인하지 않음"으로 적는다. Resolve에 놓아 달라고 하면 [motion-doodle의 Resolve 배치](../akbun-draw-motion-doodle/SKILL.md#resolve-배치)를 따른다.

## 하지 말 것

- 특정 배치를 기본값처럼 반복하지 않는다. 장면의 배치는 그 장면이 설명하는 관계가 정한다.
- 후광(glow)·그라데이션·그림자·3D 기울기를 쓰지 않는다. 깊이는 SLATE와 CELL의 밝기 차이로만 낸다.
- 강조색을 장식으로 쓰지 않는다. 의미가 없는 요소는 CHALK·MUTED·DIM이다.
