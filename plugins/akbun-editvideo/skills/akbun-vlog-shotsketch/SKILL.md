---
name: akbun-vlog-shotsketch
description: 얼굴 없이 찍는 브이로그의 한 샷을 영화 스토리보드 한 컷처럼 스케치한다. 카메라를 어디에 어떤 높이·각도로 두고, 화자는 어디에 어떻게 앉아 무엇을 하며, 프레임 안에 무엇이 들어오고 얼굴은 어디서 잘리는지를 한 장의 그림과 표로 만든다. 이미지 생성 도구가 있으면 그림 파일을, 없으면 이미지 생성 모델에 그대로 넣을 영어 프롬프트를 낸다. "이 장면 카메라 구도 그려줘", "어떻게 앉아서 찍어야 해", "샷 스케치" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-vlog-shotsketch

촬영 직전에 보는 한 컷짜리 스토리보드다. 사용자는 이 그림을 보고 카메라를 놓고 자리에 앉는다. 여러 샷이 필요하면 `akbun-vlog-storyboard`가 이 skill을 컷마다 쓴다.

전제: 화자는 얼굴을 드러내지 않는다. 촬영은 대부분 집 안 책상이다. 장비는 종류로만 부른다(카메라, 마이크).

## 입력

샷 설명 한 줄(예: "터미널 보면서 kubectl 설명하는 장면")과, 있으면 방·책상 배치(카메라 놓을 수 있는 자리, 창 위치, 모니터 수). 배치를 모르면 책상 정면에 모니터 1대, 왼쪽에 창이 있다고 가정하고 그림에 `가정`이라고 적는다.

## 샷 유형

`akbun-vlog-shootplan`의 얼굴이 나오지 않는 프레이밍 표와 같은 다섯 가지다. 샷 설명에서 하나를 고르고 표에 이유를 적는다.

| 유형 | 카메라 위치·높이 | 화자 | 프레임 상단이 끊는 곳 |
|---|---|---|---|
| 탑다운 | 책상 위 60~80 cm, 수직 아래 | 의자에 앉아 손을 책상 위에 | 손목 위 팔뚝 중간 |
| 오버 숄더 | 화자 뒤 1 m, 어깨 높이 + 10 cm, 모니터 향해 15° 아래 | 등을 카메라에, 모니터를 본다 | 뒷머리 윗부분(머리카락만) 또는 머리 밖 |
| 가슴 아래 | 책상 정면 1 m, 가슴 높이, 수평 | 정면으로 앉아 손을 움직인다 | 쇄골 아래 |
| 물건·공간 | 물건에서 30~50 cm, 물건 높이 | 프레임 밖 | 사람 없음 |
| 측면 손 | 책상 옆 50 cm, 책상 높이 + 20 cm, 손 향해 | 옆모습으로 앉아 키보드·노트 | 팔꿈치 |

## 출력

그림 한 장과 표 하나다. 그림은 이미지 생성 도구가 있으면 만들어 `<출력 폴더>/storyboard/<샷 이름>.png`로 저장하고, 없으면 아래 프롬프트를 그대로 낸다. 어느 경우든 표는 항상 낸다.

### 그림 규칙

- 한 프레임, 16:9, 회색 연필 선 스토리보드. 색은 쓰지 않고 카메라와 시선 화살표만 빨간 선.
- 그림 안에 세 가지가 보여야 한다. 카메라(삼각대 위 상자와 렌즈 방향 화살표), 화자(얼굴 없이 뒷모습·손·어깨), 프레임 안에 들어오는 것(모니터·키보드·노트)을 점선 사각형으로 표시.
- 그림 아래 여백에 카메라 높이·거리 치수를 손글씨 숫자로 적는다.
- 화자의 얼굴이 그림에 나오지 않는다. 점선 사각형(프레임) 안에도 나오지 않는다.

### 이미지 생성 프롬프트 형식

프롬프트는 영어로 쓰고 샷 유형·치수·소품을 채운다.

```text
Storyboard frame, 16:9, gray pencil sketch on white paper, no color except thin red lines for the camera axis and eye line.
Scene: a home desk. <소품: one monitor, keyboard, notebook, mug>.
Camera: <유형별 위치. 예: on a tripod 1 m behind the chair, lens at shoulder height plus 10 cm, tilted 15 degrees down toward the monitor>, drawn as a small box on a tripod with a red arrow showing where it points.
Person: seen <from behind / only hands and forearms / from the collarbone down>, sitting at the desk, <동작: typing, pointing at the terminal, writing in a notebook>. The face is never visible.
A dashed rectangle marks the camera frame; inside it: <프레임 안 요소>. The top edge of the dashed frame cuts at <끊는 곳>.
Handwritten dimension notes below the sketch: "camera height <n> cm", "distance <n> cm".
Clean, minimal, film storyboard style, no text other than the dimension notes.
```

### 샷 표

그림과 함께 내는 샷 표 예시다.

```markdown
| 항목 | 값 |
|---|---|
| 샷 이름 | 03-terminal-overshoulder |
| 유형 | 오버 숄더(이유: 모니터의 터미널이 화면의 주인공) |
| 카메라 | 화자 뒤 1 m, 어깨 높이 + 10 cm, 15° 아래, 4K 30fps |
| 화자 | 등을 카메라에, 모니터 정면, 오른손으로 터미널 가리키며 말한다 |
| 프레임 안 | 모니터(터미널 글꼴 16pt 이상), 키보드 상단, 오른손 |
| 프레임 상단 | 뒷머리 밖. 앉은키가 크면 카메라를 5 cm 올린다 |
| 마이크 | 책상 위 카메라 반대편, 입에서 20 cm, 프레임 밖 |
| 조명 | 창을 화자 옆(왼쪽)에. 모니터 빛만으로 어두우면 책상 램프를 카메라 뒤에 |
| 확인 | 녹화 10초 뒤 재생해 얼굴·반사(모니터·창)에 얼굴이 없는지 본다 |
```

## 하지 않는 것

- 얼굴이 보이는 구도, 얼굴이 모니터나 창에 비치는 구도
- 장비 제품명
- 치수 없는 그림. 카메라 높이와 거리는 항상 숫자로 적는다
- 표 없이 그림만 내는 것
