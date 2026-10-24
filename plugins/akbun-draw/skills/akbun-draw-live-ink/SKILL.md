---
name: akbun-draw-live-ink
description: 거의 검정인 판 위에 가는 펜 손글씨가 말하는 순서대로 한 글자씩 실시간으로 써지는 모션그래픽을 만든다. 흰 본문·초록 규칙·주황 이름표·분홍 비교 예시로 색 의미를 나누고, 펜은 한 자루라 한 번에 하나만 쓰며 쓴 것은 지우지 않는다. 스타일(색·글꼴·펜 선·써지는 속도와 순서)만 고정하고 배치는 내용에 맞춰 자유롭게 정한다. 모델은 장면 SVG와 시간 속성만 쓰고 akbun-draw-motion-doodle의 render_doodle.py가 MP4·투명 MOV를 만든다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-draw-live-ink

## 언제 쓰나

계산 과정, 숫자가 바뀌는 순서, 공식을 하나씩 풀어 가는 설명처럼 "지금 손으로 적으며 설명하는" 느낌이 필요할 때 쓴다. 화면은 상자·아이콘 없이 글자와 펜 선뿐이다. 이 skill이 고정하는 것은 그림체와 써지는 리듬이다. 무엇을 어디에 몇 개 쓸지는 설명할 내용이 정한다.

- 상자와 상태 변화로 시스템 구조를 보여 주는 장면은 [akbun-draw-slate-marker](../akbun-draw-slate-marker/SKILL.md), 코드를 한 줄씩 짚는 장면은 [akbun-draw-code-window-lilac](../akbun-draw-code-window-lilac/SKILL.md), 같은 스타일을 Resolve에서 글자·시점을 고칠 수 있는 타임라인으로 만드는 일은 [akbun-davinciresolve-explainer-live-ink](../../../akbun-editvideo/skills/akbun-davinciresolve-explainer-live-ink/SKILL.md)의 범위다.
- 사람 얼굴·캐릭터·로고를 그리지 않는다. 그림이 필요하면 다른 skill로 장면을 나눈다.

## 캔버스

| 용도 | size | 기준 |
|---|---|---|
| 일반 영상 (기본) | `[1920, 1080]` | 아래 px 값 그대로 |
| 쇼츠·릴스 | `[1080, 1920]` | 아래 px 값 그대로(짧은 변이 1080으로 같다) |

그 밖의 크기는 짧은 변 ÷ 1080을 곱하고 정수로 반올림한다. 글자와 선은 캔버스 네 변에서 96px 안쪽에만 둔다.

## 스타일

### 색

판 위에는 채운 면이 없다. 모든 것은 글자와 선이고, 색은 그 글이 하는 일 하나에 하나다.

| 이름 | 값 | 쓰임 |
|---|---|---|
| BOARD | `#0C0C07` | 판. spec `background`, `"grain": 0`. SVG에 배경 사각형을 그리지 않는다 |
| INK | `#F4F2EA` | 본문: 지금 설명하는 대상의 글자·식·선 |
| GREEN | `#94D05E` | 규칙: 본문을 만드는 공식·조건·옆 계산 |
| ORANGE | `#FC9E36` | 이름표: 본문의 한 부분에 이름을 붙이는 짧은 글과 그 화살표 |
| PINK | `#F87478` | 비교 예시: 본문과 나란히 두고 견주는 다른 경우 |

- 선의 색은 그 선이 속한 글의 색이다. 이름표의 화살표는 ORANGE, 본문 밑줄과 본문 값 사이 화살표는 INK, 비교 예시의 선은 PINK.
- 규칙·이름표·비교 예시가 필요 없는 장면은 그 색을 쓰지 않는다. 장식으로 색을 더하지 않는다.
- 마스크 안 경로만 `#FFFFFF`를 쓴다(아래 "써지기"). 화면에 보이는 요소에는 쓰지 않는다.

### 글꼴

`'Nanum Pen'`(Nanum Pen Script, SIL OFL) 하나만 쓴다. 굵기 속성을 주지 않는다.

| 대상 | 크기 | letter-spacing |
|---|---|---|
| 큰 글씨: 본문, 비교 예시 | 110px | 13 |
| 작은 글씨: 규칙, 이름표 | 76px | 9 |

- letter-spacing = 크기 × 0.12를 정수로 반올림한 값이다.
- 한 `<text>`는 한 번에 써지는 글자 묶음(빌드 하나)이고 줄을 넘기지 않는다. 글자는 문장이 아니라 숫자·식·낱말로 쓴다. 펜(한글 음절 0.3초)은 말(음절 약 0.15초)보다 느리므로 대본의 낱말을 다 받아 적지 않고, 대본 한 문장에 글자 빌드를 3개까지만 둔다(선·화살표는 세지 않는다). `<text>` 하나는 큰 글씨 10글자, 작은 글씨 14글자 이하다. 세는 법: 공백을 뺀 글자 수, 한글 음절·영문자·숫자·기호 각 1.
- 같은 줄에 나눠 쓰는 다음 `<text>`는 같은 `y`에서 앞 `<text>`의 `x + w`(아래 "써지기"의 w)부터 시작한다. w에 끝 글자 간격이 들어 있어서 따로 띄우지 않는다. 빈칸이 필요하면 공백 글자를 넣지 말고 `x`에 빈칸 하나 폭(`getlength(' ')` + letter-spacing)을 더한다.
- `text-anchor`를 쓰지 않는다(왼쪽 정렬). 써지기 마스크가 `x`에서 시작하기 때문이다.
- 모든 글자는 `<text>`로 남긴다. `<path>`나 이미지로 바꾸지 않는다.
- 렌더 전에 `uv run --python 3.12 <doodle>/scripts/render_doodle.py --fonts "Nanum Pen"`이 `ok`인지 본다. `missing`이면 렌더하지 말고 사용자에게 설치를 묻는다. 받는다면 Google Fonts의 Nanum Pen Script에서 받는다.

### 펜 선

모든 선은 끝이 둥근 한 획이다: `fill="none"` `stroke-linecap="round"` `stroke-linejoin="round"`. 굵기는 큰 글씨와 함께 쓰는 선 6px, 작은 글씨와 함께 쓰는 선 4px이다. 점선·채움·그림자를 쓰지 않는다.

| 선 | 모양 |
|---|---|
| 밑줄·가로줄 | `Q` 곡선 하나. 높이는 위 글자 baseline 아래 0.2 × 글자 크기, 제어점은 두 끝의 가운데에서 수직으로 4~8px 비킨다. 강조 밑줄, 분수 선 |
| 화살표 | 몸통 직선 `<path>` 하나 + 머리 꺾은선 `<path>` 하나(`M 팔1 L 끝점 L 팔2`). 팔은 끝점에서 몸통을 거슬러 가는 방향을 ±35° 돌린 쪽으로 18px. 이름표와 대상 사이, 값이 다음 값으로 넘어갈 때 |
| 동그라미 | 대상을 두르는 타원 한 획. `A` 호 두 개로 한 바퀴 돌고, 짧은 `A` 호 하나로 시작점을 10~20px 더 지나쳐 끝낸다 |

### 써지기

펜은 한 자루다. 한 번에 하나만 쓰고, 쓴 것은 장면이 끝날 때까지 그대로 남는다.

- **글자**: `<text>`마다 마스크 하나를 `<defs>`에 두고, 마스크 안의 굵은 흰 선이 `data-draw`로 왼쪽에서 오른쪽으로 그려지면서 글자가 펜이 지나간 만큼 드러난다. 글자 위치·크기가 `x`, `y`(baseline), `s`이고 그 `<text>`의 폭이 `w`일 때 아래 모양으로 쓴다. 중괄호는 계산한 숫자로 바꾸고, `id`는 장면 안에서 겹치지 않게 번호를 붙인다.

  ```xml
  <mask id="pen7" maskUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080"><path d="M{x-0.1*s} {y-0.22*s} L{x+w+0.1*s} {y-0.22*s}" stroke="#FFFFFF" stroke-width="{s}" fill="none" data-draw="t0 t1"/></mask>
  <text x="{x}" y="{y}" font-family="'Nanum Pen'" font-size="{s}" letter-spacing="{ls}" fill="#F4F2EA" mask="url(#pen7)">{글자}</text>
  ```

  - 좌표는 정수로 반올림한다. 마스크 `width`·`height`는 캔버스 크기다.
  - w = Pillow `ImageFont.truetype(<글꼴 파일>, s).getlength(글자)` + letter-spacing × 글자 수(공백 포함). 글꼴 파일 경로는 `fc-match -f '%{file}' 'Nanum Pen'`.
  - 걸리는 시간 = 한글 음절 수 × 0.3초 + 그 밖의 글자 수 × 0.2초(공백은 0). 0.05초 단위로 올리고 최소 0.2초.
- **선**: 그 `<path>`에 `data-draw`. 걸리는 시간 = 선 길이(px) ÷ 1500초를 0.05초 단위로 올림, 최소 0.15초. 화살표는 몸통을 먼저 그리고, 머리는 몸통이 끝난 시각에 바로 0.15초 동안 그린다. 선은 신호 단어를 따로 갖지 않고 바로 앞 빌드 끝 + 0.15초에 시작한다. 화살표는 그 뒤에 쓸 글자 빌드(값 사이 화살표는 끝 쪽 값, 이름표 화살표는 이름표 글자) 바로 앞 빌드이고, 밑줄·동그라미는 대상 글자 빌드 바로 다음 빌드다.
- **펜 옮기기**: 한 빌드(글자 한 줄, 선 하나, 화살표 하나)가 끝나고 다음 빌드는 0.15초 이상 뒤에 시작한다. 빌드끼리 시간이 겹치지 않는다. 화살표의 몸통과 머리는 한 빌드다.
- `data-write`·`data-fade`·`data-show`·포즈 교체·카메라를 쓰지 않는다. 장면 하나는 포즈 한 장이다. 글자가 한 번에 튀어나오거나 서서히 나타나면 손으로 쓰는 느낌이 사라진다.
- spec의 `drawings_per_second`는 `fps`와 같게 한다(예: 30, 30). 펜이 매 프레임 조금씩 나아가야 한다.
- 마지막 빌드 뒤에는 1.0초(예외 0.5초) 이상 멈춘다. 장면 길이 계산은 아래 "시각 맞추기"에 있다. 장면 하나는 90초 이하이고, 장면 전환은 빈 판으로의 하드 컷이다.

### 시각 맞추기

시각은 대본의 신호 단어에 묶는다. 신호 단어는 그 글자가 나타내는 값이나 이름을 말하는 첫 단어이고, 식은 대본에서 그 식을 읽기 시작하는 첫 단어이고, 대본에 읽는 말이 없는 식은 그 결과를 말하는 첫 단어다. 음절 세는 법, 신호 단어 0.1초 앞에서 시작하기, 장면 길이, 녹음 후 다시 맞추는 법은 [code-window-lilac의 녹음 전후 시각 맞추기](../akbun-draw-code-window-lilac/SKILL.md#녹음-전후-시각-맞추기)를 따르고, 시작 시각은 0.01초 단위로 내림한다. 요청에 적힌 대략의 길이보다 이 계산이 우선이다. 그 문서의 우선순위 중 간격 규칙과 "다른 신호 단어로 옮기기" 대신 아래 두 규칙을 쓴다.

- 앞 빌드 끝 + 0.15초가 다음 빌드의 신호 단어 시각보다 늦으면 앞 글자 빌드 전체의 글자당 시간을 한글 0.2초, 그 밖 0.15초로 줄인다(선은 줄이지 않는다). 그래도 늦으면 뒤 빌드를 앞 빌드 끝 + 0.15초로 미루고 장면 표에 적는다. 한 신호 단어에 빌드가 여럿이면 장면 표 순서대로 뒤의 것이 밀린다.
- 녹음 전 장면 길이는 (마지막 음절 끝 + 0.4초)와 (마지막 빌드 끝 + 1.0초) 중 긴 쪽을 프레임 단위로 올린 값이다. 마지막 단어에 묶인 빌드라서 1.0초를 지키면 대본과 어긋날 때만 + 0.5초로 줄인다. 녹음 후 장면 길이는 code-window-lilac대로 다음 장면 첫 문장 시작까지이고, 그 안에서 마지막 빌드 뒤 0.5초가 안 되면 글자 빌드를 최소 속도로 줄이고, 그래도 안 되면 장면 표에 적고 보고한다.

## 작업 흐름

`<skill>`은 이 `SKILL.md`가 있는 디렉터리, `<doodle>`은 [akbun-draw-motion-doodle](../akbun-draw-motion-doodle/SKILL.md) 디렉터리다. 출력 폴더는 사용자가 정한 곳, 없으면 `live-ink-output/<작업명>/`.

1. **장면 표**: 장면마다 id, 길이, 빌드 순서대로 요소(글자·선), 색, 신호 단어, 시작·끝 시각을 적는다.
2. **SVG**: 장면마다 한 장. `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 W H">`로 시작하고 `width`·`height`·배경 사각형·`filter`·`<image>`를 넣지 않는다. 마스크 폭과 시각 계산이 많으므로 출력 폴더에 작은 생성 스크립트를 두고 빌드 목록에서 SVG와 spec을 함께 만든다.
3. **spec.json**: `"background": "#0C0C07"`, `"grain": 0`, `fps`와 `drawings_per_second`는 놓을 타임라인 fps(정수). 23.976·29.97처럼 정수가 아니면 렌더하지 말고 사용자에게 알린다. 형식은 render_doodle.py 머리 주석을 따른다.
4. **렌더**: 출력 폴더와 `stills` 폴더를 먼저 만들고 `uv run --python 3.12 <doodle>/scripts/render_doodle.py <출력>/spec.json <출력>/out.mp4 --stills <출력>/stills`. 배경을 따로 작업한다는 신호가 있으면 렌더 전에 [motion-doodle의 출력 형식](../akbun-draw-motion-doodle/SKILL.md#2-출력-형식)대로 "MOV(투명 배경)"와 "MP4(검정 배경)" 두 선택지로 묻고, MOV를 고르면 `out.mov`로 렌더한다.
5. **검수**: 아래 숫자 검사를 먼저 하고, 장면마다 쓰는 도중 프레임 몇 장과 마지막 프레임을 한 장으로 붙여 한 번만 본다. `--stills`는 마지막 프레임만 저장하므로 쓰는 도중 프레임은 장면 표에서 글자 빌드 몇 개의 가운데 시각(장면 시작 기준이 아니라 영상 전체 기준 초)을 골라 `out.mp4`에서 뽑는다.

예시: [references/example/](references/example/)는 지수 백오프 재시도 간격을 한 장면으로 쓴 것이다. `sheet.jpg`는 쓰는 도중과 끝 프레임이다. 스타일 확인용이며 배치·문구를 그대로 쓰지 않는다.

### 검수

SVG에 색 표 밖의 색이 없는지 보는 명령이다. 아무것도 출력하지 않아야 한다.

```bash
grep -ohiE '#[0-9a-f]{6}' <출력>/*.svg | tr a-f A-F | sort -u | grep -vE '^#(0C0C07|F4F2EA|94D05E|FC9E36|F87478|FFFFFF)$'
```

펜 옮기기(빌드가 겹치지 않고 사이 0.15초 이상, 화살표 머리만 몸통 끝에 바로 붙음)와 글자·선이 96px 안쪽에 있는지 보는 명령이다. 장면 SVG 하나와 그 장면의 스틸을 준다. `간격 위반 없음`이 나오고 범위가 96 ~ (폭 − 96), 96 ~ (높이 − 96) 안이어야 한다.

```bash
uv run --python 3.12 --with numpy --with pillow python - <출력>/<장면>.svg <출력>/stills/<장면 스틸>.png <<'EOF'
import re, sys, numpy as np
from PIL import Image
w = []
for tag in re.findall(r'<path\b[^>]*data-draw="[^"]+"[^>]*>', open(sys.argv[1]).read()):
  a, b = map(float, re.search(r'data-draw="([^"]+)"', tag).group(1).split())
  head = re.search(r'\bd="M[^MLQA"]*L[^MLQA"]*L[^MLQA"]*"', tag) is not None  # 화살표 머리: L이 두 번인 꺾은선
  w.append((a, b, head))
bad, end = [], -1.0
for a, b, head in sorted(w):  # 머리만 몸통 끝에 바로 붙어도 된다
  if a < end - 1e-6 or (a < end + 0.15 - 1e-6 and not (head and abs(a - end) < 1e-6)): bad.append((a, b))
  end = max(end, b)
print("간격 위반", bad or "없음")
ys, xs = np.nonzero(np.asarray(Image.open(sys.argv[2]).convert("L")) > 90)
print("x", xs.min(), xs.max(), "y", ys.min(), ys.max())
EOF
```

쓰는 도중 프레임과 마지막 프레임을 한 장으로 붙이는 명령이다. `<시각들>`에 고른 초를 공백으로 나눠 넣고 장면마다 끝 프레임 시각(그 장면 끝, 영상 전체 기준 초 − 0.05)도 넣는다.

```bash
i=0; for t in <시각들>; do ffmpeg -v error -y -ss "$t" -i <출력>/out.mp4 -frames:v 1 -vf scale=640:-1 "<출력>/sheet_$i.png"; i=$((i+1)); done
ffmpeg -v error -y -i "<출력>/sheet_%d.png" -vf "tile=2x$(( (i + 1) / 2 ))" -frames:v 1 <출력>/sheet.jpg
```

- 렌더 프레임 수 = 장면 길이 합 × fps.
- `--fonts "Nanum Pen"`이 `ok`.
- `#FFFFFF`가 `<mask>` 안에만 있는가, `data-write`·`data-fade`·`data-show`가 없는가.
- 한 줄 글자 수 규칙, 마지막 빌드 뒤 1.0초(예외 0.5초) 정지를 지켰는가.
- 시트에서: 글자가 왼쪽부터 조금씩 드러나는가, 글자끼리 겹치거나 잘리지 않는가, 같은 역할이 장면마다 같은 색인가, 알려진 영상 장면·캐릭터와 닮은 화면이 없는가.

## 완료 보고

출력 경로, 출력 형식(MP4·MOV)과 고른 이유, 장면 표(신호 단어·녹음 전 시각·녹음 후 시각), 렌더 프레임 수, 글꼴 검사, 색 검사·간격 검사 출력, 검수 결과를 적는다. 확인하지 않은 항목은 "확인하지 않음"으로 적는다. Resolve에 놓아 달라고 하면 [motion-doodle의 Resolve 배치](../akbun-draw-motion-doodle/SKILL.md#resolve-배치)를 따른다.

## 하지 말 것

- 특정 배치를 기본값처럼 반복하지 않는다. 글자를 어디에 둘지는 그 장면이 설명하는 관계가 정한다.
- 상자·카드·아이콘·채운 면·그라데이션·후광을 넣지 않는다. 강조는 밑줄·동그라미·이름표 화살표로만 한다.
- 두 군데를 동시에 쓰지 않는다. 쓴 것을 지우거나 옮기지 않는다.
