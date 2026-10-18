---
name: akbun-edit-page-tour-lilac
description: 웹 페이지·GitHub 저장소 스크린샷을 연회색 캔버스 위 브라우저 창 카드에 넣고, 카메라가 요소마다 짧게 다가가 머물며 연보라 형광펜·외곽 상자로 짚는 페이지 둘러보기 장면 page-tour를 DaVinci Resolve 안에서 Fusion 노드로 만든다. 작업 타임라인을 복제해 본편을 밀지 않는 새 트랙에 놓고, 사용자가 Fusion 페이지에서 카드·표시의 위치·색·크기를 고칠 수 있게 노드에 이름을 붙인다. 녹음 후에는 단어 시각으로 시점만 다시 맞춘다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-edit-page-tour-lilac

## 언제 쓰나

레이아웃은 고정하지 않는다. 상황에 맞는 부품을 고르고, 부품의 모양·색·글꼴·모션만 아래 "스타일"대로 지킨다.

| 상황 | 화면에 나오는 것 |
|---|---|
| GitHub 저장소를 소개한다 | 저장소 첫 화면 카드 하나. 이름·설명·별 수·폴더 목록을 차례로 짚는다 |
| 저장소 → 코드 구조로 들어간다 | 저장소 카드 → (컷) 폴더·파일 목록 카드. 말하는 폴더 줄에 형광펜 |
| 문서·위키 페이지의 한 문단을 읽는다 | 문서 카드 하나. 읽는 줄을 형광펜으로 차례로 칠하며 천천히 흐름 |
| 순위·목록 페이지에서 하나를 가리킨다 | 목록 카드 하나. 대상 항목에 외곽 상자, 카메라가 그 항목으로 |
| 페이지 아래쪽으로 이어진다 | 같은 창 자리에 아래쪽을 잘라 낸 두 번째 카드가 0.25초 페이드로 바뀐다(스크롤 대신) |

- 트윗·기사·댓글처럼 여러 출처의 글을 겹쳐 보여 줄 때는 [akbun-edit-quote-cards-lilac](../akbun-edit-quote-cards-lilac/SKILL.md), 터미널·AI 도구 화면 녹화는 [akbun-edit-terminal-callout-amber](../akbun-edit-terminal-callout-amber/SKILL.md)이다. 본편이 계속 보이는 위에 발췌 패널을 띄우는 것은 [akbun-davinciresolve-article-overlay](../akbun-davinciresolve-article-overlay/SKILL.md)다. 이 스킬은 본편을 가리는 전체 화면 장면이다.
- 화면은 실제로 찍은 스크린샷만 쓴다. 페이지 내용·숫자를 지어내거나 그려 넣지 않는다. 얼굴 화면(PIP)·인물 촬영은 넣지 않는다.

## 녹음 전후 시각 맞추기

작업 흐름은 대본 → 영상 → 녹음 → 영상 수정이다. 카드 등장·표시·카메라 키·클립 길이는 모두 대본의 "신호 단어"에 묶는다. plan의 시간은 클립 시작 기준 초이고, 클립의 0초는 그 장면 첫 문장의 시작이다.

- **녹음 전**: 대본을 초당 6.5음절로 읽는다고 보고 시각을 잡는다. 한글 한 글자 = 1음절, 영어 단어 = 모음 글자 묶음 수(a·e·i·o·u, 단어 끝이 아닌 y 포함, 붙어 있는 모음은 한 묶음, 최소 1, camelCase·snake_case는 단어로 나눠 센다), 숫자·기호 = 한국어로 읽는 소리 수. 띄어쓰기는 시간을 더하지 않고, 쉼표는 0.2초, 문장 끝은 0.4초를 더한다. 요소는 신호 단어 시작 0.1초 전에 시작한다(0보다 작으면 0). 클립 길이는 그 장면 마지막 음절이 끝나는 시각 + 0.4초다(문장 끝 쉼 0.4초를 한 번만 더한다).
- **녹음 후**: 단어 시각(Resolve 전사, SRT, Whisper 단어 타임스탬프 중 있는 것)에서 신호 단어의 시작 시각을 찾아 plan의 `at`·`duration`·`start`·`camera[].at`를 고치고 `retime`으로 다시 맞춘다. 길이(형광펜 쓸기·페이드·카메라 이동 시간)는 그대로 두고 시작 시각만 옮긴다.
- SRT처럼 문장 단위 시각만 있으면 문장 시작~끝을 음절 수 비율로 나눠 단어 시각을 추정하고 장면 표에 "추정"으로 표시한다. 신호 단어를 못 찾으면 시각을 추측하지 말고 목록으로 보고한다.
- **우선순위**: 신호 단어 시각 > 아래 모션 표의 길이 > 그 밖의 간격 규칙.
- 장면 표에는 요소마다 신호 단어, 녹음 전 시각, 녹음 후 시각 열을 둔다. 녹음 전이면 녹음 후 열은 "녹음 후 갱신"으로 둔다.

## 스타일

1920×1080 기준이다.

### 색과 글꼴

| 이름 | 값 | 쓰임 |
|---|---|---|
| CANVAS | `#EAEAEA` | 배경(`canvas_color`) |
| 창 틀 | `frame` 명령 light 테마 | 흰 바탕, 신호등 점, 제목줄에 페이지 주소 |
| MARK | `#C9BCFF` | 형광펜(`highlight`, Multiply) |
| BOX | `#8B78F0` | 외곽 상자(`box`, 4px, 모서리 `corner` 0.05) |

- 강조색은 연보라 두 값뿐이다. 빨강 밑줄·노랑 형광펜·원을 쓰지 않는다.
- 창 제목줄 글자는 Pretendard(없으면 Noto Sans KR)다. 렌더 전에 `fc-list | grep -i pretendard` 또는 `~/Library/Fonts`로 설치를 확인하고, 없으면 받기 전에 사용자에게 묻는다(공식 배포처 github.com/orioncactus/pretendard 릴리스).

### 부품

| 부품 | 모양 |
|---|---|
| 창 카드 | `frame` 명령으로 만든 틀. 폭 1100~1500px, 창 안을 스크린샷이 꽉 채운다. 창 위아래 여백 60px 이상 |
| 스크린샷 | 2배 해상도(`--force-device-scale-factor=2`)로 찍은 PNG. 배율 0.5 안팎으로 들어간다 |
| 형광펜 | 대상 글자 줄을 위아래 4~6px 넉넉히 덮는 사각형. 여러 줄이면 줄마다 하나씩 |
| 외곽 상자 | 대상(버튼·숫자·항목)에서 사방 6~10px 띄운 사각형 |

- 표시 좌표는 스크린샷 픽셀을 재서 `where` 명령으로 바꾼다.
- 한 화면에 동시에 보이는 표시는 2개까지다. 형광펜 한 줄, 외곽 상자 하나를 각각 1개로 센다.

### 모션

| 움직임 | 방식 | 길이 |
|---|---|---|
| 카드 등장 | `CARD_*_LAYOUT` Blend 페이드 | 0.25초 |
| 형광펜 | 왼쪽→오른쪽으로 쓸기(`highlight`) | 0.3~0.5초 |
| 외곽 상자 | 페이드(`box`) | 0.2초 |
| 다음 카드(스크롤 대신) | 같은 자리에 새 카드 페이드 | 0.25초 |

- **짚기(기본)**: 카메라는 머물기와 짧은 이동을 번갈아 한다. 이동은 0.5~0.9초 ease-in-out, 머물기는 1.2초 이상이다. 머무는 동안 `"ease": "linear"`로 zoom을 0~0.04 더 키운다(기본 0.02).
- **확대 한도**: zoom 1.0~2.0. 2배 스크린샷일 때만 1.6을 넘긴다. 확대 중 보이는 영역(x ± 960/zoom, y ± 540/zoom)에 지금 짚는 표시가 다 들어간다.
- **읽기 흐름**: 문단을 읽는 장면은 짧은 이동 없이 장면 전체를 linear로 zoom 0.05~0.10 키우며 읽는 줄 쪽으로 천천히 옮긴다.
- 표시는 카메라가 도착한 뒤(이동 끝 시각 이후) 시작한다. 장면 전환은 하드 컷이다.
- **캔버스 밖 금지**: 카메라 키마다 보이는 영역(x ± 960/zoom, y ± 540/zoom)이 캔버스(0~1920, 0~1080) 안에 있어야 한다. 대상이 가장자리에 가까우면 가운데를 안쪽으로 옮긴다(x는 960/zoom ~ 1920 − 960/zoom, y는 540/zoom ~ 1080 − 540/zoom).

## 작업 흐름

`<skill>`은 이 `SKILL.md`가 있는 디렉터리다. 공용 사항(plan 형식, 노드 구성, 21.1.1 실측, 검증 방법)은 [references/fusion-cards.md](references/fusion-cards.md)를 먼저 읽는다.

1. **장면 표**: 장면마다 "언제 쓰나"의 행, 스크린샷 URL, 짚을 요소와 신호 단어·시각, 카메라 짚기 순서를 적는다.
2. **자산**: 출력 폴더(사용자가 정한 곳, 없으면 원본 미디어 옆 `<프로젝트명>_edit/edit-assets/`)에 스크린샷(2배)·창 틀·캔버스 영상을 만든다. 임시 폴더에 두지 않는다. Resolve가 재부팅 뒤에도 같은 경로를 읽는다.
3. **plan.json**: 표시 좌표는 `where`로, 카메라 키는 짚기 순서대로 쓴다.
4. **빌드**: `build`. 출력의 트랙·시작·길이·노드 목록을 장면 표에 적는다.
5. **검증**: `grab`(Deliver 렌더)으로 0프레임, 등장 중, 짚기마다 머무는 프레임, 끝 프레임을 뽑아 숫자로 본 뒤 시트를 한 번 본다.
6. **녹음 후**: plan 시각만 고치고 `retime`.

예시 plan과 Resolve에서 만든 결과 시트는 [references/example/](references/example/)에 있다. 스타일 확인용이며 좌표·문구를 그대로 쓰지 않는다.

자산을 만드는 명령이다. 창 틀은 (239, 70)에 1442×960, 캔버스 영상은 타임라인 fps로 60초다.

```bash
uv run --python 3.12 <skill>/scripts/resolve_cards.py frame --rect 239,70,1442,960 --theme light --title github.com/owner/repo --out edit-assets/card01_frame.png
uv run --python 3.12 <skill>/scripts/resolve_cards.py canvas --fps 30 --seconds 60 --out edit-assets/canvas_30fps.mp4
uv run --python 3.12 <skill>/scripts/resolve_cards.py where edit-assets/plan_01.json --card 01 --rect 240,1240,1760,64
```

plan대로 Resolve에 장면을 만들고 대표 프레임을 뽑는 명령이다.

```bash
uv run --python 3.12 <skill>/scripts/resolve_cards.py build edit-assets/plan_01.json
uv run --python 3.12 <skill>/scripts/resolve_cards.py grab edit-assets/plan_01.json --frames 0,4,66,135,239 --out edit-assets/grab_01
```

## 사용자가 고치는 법

Edit 페이지에서 `PAGE_TOUR` 트랙의 클립을 고르고 Fusion 페이지로 간다. 노드 라벨과 Inspector 항목은 [fusion-cards.md의 노드 표](references/fusion-cards.md#노드-구성과-사용자가-고칠-곳)를 따른다.

| 고치려는 것 | 노드 → Inspector |
|---|---|
| 형광펜·상자 위치, 폭·높이 | `MARK_01_SHAPE` → Center X/Y, Width, Height |
| 형광펜·상자 색 | `MARK_01_COLOR` → Color |
| 상자 선 두께 | `MARK_01_SHAPE` → Border Width |
| 표시 하나 숨기기 | `MARK_01` → Blend 0 |
| 카드 전체 위치·크기 | `CARD_01_LAYOUT` → Center, Size |
| 카메라 | `CAMERA` → Size·Center 키프레임(Spline) |

캔버스 클립 모드에서는 Edit 페이지 Inspector에 이 값들이 나오지 않는다(21.1.1 실측).

**Edit Inspector에서 고치고 싶을 때(title 모드)**: plan에 `"mode": "title"`을 넣고 `build`하면 장면이 장면 전용 타임라인(`title_timeline`) 끝에 Fusion 타이틀로 붙는다. 그 클립을 고르고 Inspector → Video → Title 탭에서 `Mark 01 Color`·`Mark 01 Position`·`Mark 01 Width/Height`·`Card 01 Position/Size`·`Callout 01 Text/Position`을 바로 바꾼다. 대가는 장면이 본편 위 트랙이 아니라 별도 타임라인에 있어 사용자가 본편으로 복사해 붙여야 하고, `retime`이 안 돼 녹음 후에는 클립을 지우고 다시 `build`한다는 점이다(Inspector에서 고친 값은 plan 값으로 돌아간다). 자세한 절차는 [fusion-cards.md의 Edit Inspector 모드](references/fusion-cards.md#edit-inspector-모드-title)다.

완료 보고에 어느 모드로 만들었는지와 해당 표(또는 Inspector 컨트롤 목록)를 적는다.

## 검수

- `build` 출력의 `frames` = 장면 길이 × fps이고, 다른 트랙 클립·마커 대조를 통과했다.
- `grab` 0프레임은 캔버스만(캔버스 아닌 픽셀 0%), 등장 뒤 프레임은 카드가 보인다.
- 짚기마다 머무는 프레임에서 표시가 대상 글자에 정확히 얹혔고, 보이는 영역 안에 다 들어온다(시트로 확인).
- 카메라 이동 0.5~0.9초, 머물기 1.2초 이상, zoom ≤ 2.0(1배 스크린샷이면 ≤ 1.6).
- 표시가 카메라 이동 끝 뒤에 시작하고, 동시에 보이는 표시가 2개 이하다.
- 스크린샷에 로그인 정보·개인 정보가 보이지 않는다.

## 완료 보고

작업 타임라인 이름, 트랙 이름·번호, 클립 시작 타임코드·길이, plan·자산 경로, 장면 표(신호 단어·녹음 전/후 시각), `grab` 결과, "사용자가 고치는 법" 표를 적는다. 확인하지 않은 항목은 "확인하지 않음"으로 적는다.

## 하지 말 것

- 원본 타임라인과 본편 트랙을 고치지 않는다. 본편 타임라인에 `InsertFusionTitleIntoTimeline`·`InsertFusionCompositionIntoTimeline`으로 넣지 않는다(재생 헤드 위치의 V1에 끼워 넣어 본편을 민다). title 모드는 장면 전용 타임라인 끝에만 붙인다.
- 스크린샷 위에 글자·숫자를 그려 바꾸지 않는다. 표시(형광펜·상자)만 더한다.
- 표현식에 `comp.RenderStart`를 쓰지 않는다.
