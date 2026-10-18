# Fusion 창 카드 공용 참조

`akbun-edit-page-tour-lilac`, `akbun-edit-quote-cards-lilac`, `akbun-edit-terminal-callout-amber`가 같이 쓴다. 장면은 [scripts/resolve_cards.py](../scripts/resolve_cards.py)가 Resolve 외부 스크립팅 API로 만든다. 실행 전에 Resolve Studio가 켜져 있고 Preferences → System → General → External scripting using이 `Local`이어야 한다.

## 장면 하나 = 클립 하나

장면 하나는 작업 타임라인의 새 비디오 트랙(본편보다 위)에 놓인 단색 캔버스 클립 하나와 그 클립의 Fusion comp다.

1. 원본 타임라인은 고치지 않는다. `work_timeline` 이름의 복제본을 만들거나 이미 있으면 그것을 쓴다.
2. `track_name` 이름의 트랙 중 그 구간이 빈 것을 쓰고, 없으면 맨 위에 새 트랙을 만든다. 기존 본편 트랙의 빈 구간은 쓰지 않는다.
3. 캔버스 클립을 `AppendToTimeline`의 `trackIndex`·`recordFrame`·`startFrame`·`endFrame`으로 놓는다. 놓은 뒤 다른 트랙의 클립·마커가 그대로인지 스크립트가 대조하고, 다르면 멈춘다.
4. 클립에 `AddFusionComp()`로 comp를 붙이고 아래 노드를 만든다.

## plan.json

모든 좌표는 1920×1080 캔버스 픽셀(왼쪽 위 원점, 카메라 zoom 1 기준)이고 시간은 클립 시작 기준 초다.

창 카드 하나에 형광펜·외곽 상자·주석 하나씩을 두고 카메라가 두 곳을 짚는 plan 예시다.

```json
{
  "fps": 30,
  "source_timeline": "main",
  "work_timeline": "main_tour_1018",
  "track_name": "PAGE_TOUR",
  "at": 12.0,
  "duration": 8.0,
  "canvas_clip": "/abs/edit-assets/canvas_30fps.mp4",
  "canvas_color": "#EAEAEA",
  "cards": [
    {"id": "01", "frame": "/abs/edit-assets/card01_frame.png", "content": [240, 115, 1440, 914],
     "shot": "/abs/edit-assets/repo@2x.png", "crop": [0, 120, 2880, 0], "fade": [0, 0.25]}
  ],
  "marks": [
    {"id": "01", "card": "01", "kind": "highlight", "rect": [355, 671, 890, 38], "color": "#C9BCFF", "start": 2.0, "len": 0.5},
    {"id": "02", "card": "01", "kind": "box", "rect": [1279, 431, 187, 46], "color": "#8B78F0", "border": 4, "start": 4.4, "len": 0.2}
  ],
  "callouts": [
    {"id": "01", "card": "01", "arrow": "/abs/edit-assets/callout01_arrow.png", "label": "여기", "pos": [1500, 380],
     "size": 46, "font": "Gaegu", "style": "Bold", "color": "#FFD84D", "start": 5.0}
  ],
  "camera": [{"at": 0, "zoom": 1}, {"at": 1.3}, {"at": 2.0, "zoom": 1.6, "x": 800, "y": 690},
             {"at": 3.6}, {"at": 4.3, "zoom": 1.8, "x": 1372, "y": 454}, {"at": 8.0, "zoom": 1.84, "ease": "linear"}]
}
```

| 키 | 뜻 |
|---|---|
| `cards[].frame`, `content` | `frame` 명령이 만든 창 틀 PNG와 그 출력의 content 사각형 |
| `cards[].crop` | 스크린샷에서 보일 부분 `[x, y, w, h]`(스크린샷 픽셀). `h`가 0이면 content 높이에 맞춘다. 배율 = content 폭 ÷ crop 폭 |
| `cards[].trim_in` | 화면 녹화를 몇 초부터 쓸지(영상일 때) |
| `marks[].kind` | `highlight`(밝은 화면, Multiply 형광펜), `fill`(어두운 화면, 반투명 채움, `alpha`), `box`(외곽 상자, `border` px) |
| `marks[].sweep` | 왼쪽→오른쪽으로 쓸어 나타남. 기본은 `highlight`만 true. false면 `len` 동안 페이드 |
| `callouts[]` | `arrow` 명령으로 만든 화살표 PNG + Text+ 라벨(`pos`는 라벨 가운데). 화살표가 `start`에, 라벨이 0.25초 뒤 나타난다 |
| `camera[]` | `at`, `zoom`, `x`·`y`(가운데에 올 캔버스 점). 빠진 값은 앞 키 값. 키 사이는 ease-in-out, `"ease": "linear"`이면 그 키로 가는 구간이 등속 |

표시·주석 좌표는 눈대중으로 정하지 않는다. 스크린샷에서 대상의 픽셀 사각형을 재고 `where` 명령으로 캔버스 좌표로 바꾼다.

## 노드 구성과 사용자가 고칠 곳

사용자는 **Fusion 페이지**에서 아래 노드를 골라 Inspector 값을 바꾼다. 클립을 선택한 뒤 Fusion 페이지로 가면 노드가 보인다.

| 노드 라벨 | 종류 | 사용자가 바꿀 값 |
|---|---|---|
| `CANVAS` | Background | 배경색 |
| `FRAME_01` | Loader | 창 틀 PNG(틀을 다시 만들면 Clip 경로) |
| `CARD_01_SPACE`, `FRAME_01_PLACE` | Background, Merge | 카드를 화면 크기 투명 바탕에 올린다. 고치지 않는다 |
| `SHOT_01` | Loader | 스크린샷·화면 녹화 파일 |
| `SHOT_01_CROP` | Crop | 보일 부분(X/Y Offset, X/Y Size. Y Offset은 아래 기준) |
| `CONTENT_01` | Merge | 창 안 스크린샷 위치(Center)·배율(Size) |
| `MARK_01_SHAPE` | RectangleMask | 표시 위치(Center X/Y)·폭·높이·모서리, 상자면 Border Width |
| `MARK_01_COLOR` | Background | 표시 색(색상 피커) |
| `MARK_01` | Merge | 표시 하나 숨기기(Blend 0). 형광펜은 Apply Mode Multiply |
| `MARK_01_REVEAL` | RectangleMask | 쓸어 나타남 진행(표현식). 직접 고치지 않는다 |
| `CALLOUT_01_ARROW` | Loader | 화살표 PNG |
| `CALLOUT_01_LABEL` | Text+ | 라벨 글자·글꼴·크기·색·위치 |
| `CARD_01_LAYOUT` | Merge | 카드 전체 위치(Center)·크기(Size). Blend에는 등장 표현식이 있다 |
| `CAMERA` | Transform | 카메라 키프레임(Size, Center). Spline 창에서 고친다 |

- 위치·색·크기 입력에는 표현식·키프레임을 걸지 않는다. 시각은 `CARD_*_LAYOUT`·`MARK_*`·`CALLOUT_*`의 Blend 표현식, `MARK_*_REVEAL`의 Center 표현식, `CAMERA` 키프레임에만 있다.
- 인계할 때 "트랙 이름 → 클립 → Fusion 페이지 → 노드 라벨 → Inspector 항목"으로 적는다. 예: `PAGE_TOUR / 01:00:12:00 클립 → Fusion → MARK_01_COLOR → Color`.

## Edit Inspector 모드 (title)

사용자가 Fusion 페이지로 가지 않고 Edit 페이지 Inspector에서 바로 고치고 싶을 때 쓴다. plan에 `"mode": "title"`을 넣으면 `build`가 캔버스 클립 대신 Fusion 타이틀을 만든다. 노드 구성(위 표)은 같다.

| 키 | 뜻 |
|---|---|
| `mode` | `"title"`이면 이 모드. 없으면 캔버스 클립 모드 |
| `title_timeline` | 장면을 붙일 장면 전용 타임라인 이름. 없으면 `<work_timeline>_titles`. 없으면 새로 만든다 |

`build`가 하는 일:

1. 장면 전용 타임라인의 V1 끝 프레임으로 재생 헤드를 옮긴다. 이미 plan 파일 이름(확장자 뺀 것)과 같은 클립이 있으면 멈춘다.
2. 환경설정을 프리셋으로 저장·내보내고(`<plan 폴더>/prefs/`, 원래 값은 `restore.json`), `GeneratorDurationType=DURATION_IN_FRAMES`, `GeneratorDurationFrames=장면 프레임 수`만 바꾼 임시 프리셋을 적용한 뒤 `InsertFusionTitleIntoTimeline("Text+")`로 넣는다. 끝나면 원래 프리셋을 다시 적용하고, 실제 값이 원래와 같은지 다시 내보내 대조한 뒤 자기가 만든 임시 프리셋만 지운다. 다르면 멈추고 복원할 프리셋 이름·파일을 알려 준다.
3. 클립 시작 = 이전 끝, 길이 = 장면 프레임 수, 마커가 그대로인지 확인하고 클립 이름을 plan 파일 이름으로 바꾼다.
4. 노드를 만든 뒤 `.comp`로 내보내, Loader를 뺀 모든 노드를 `Template` MacroOperator로 감싼 `.template.comp`를 만들어 다시 들인다. 생성기(Background, Text+)의 GlobalIn/GlobalOut은 지운다.

Edit 페이지에서 장면 타임라인의 클립을 고르면 Inspector → Video → Title 탭에 아래 컨트롤이 나온다. 되돌리기 값은 plan 값이다.

| 컨트롤 | 연결된 노드 입력 |
|---|---|
| `Mark 01 Color` (Red·Green·Blue·Alpha) | `MARK_01_COLOR` TopLeft 색 |
| `Mark 01 Position` X/Y | `MARK_01_SHAPE` Center |
| `Mark 01 Width`, `Mark 01 Height` | `MARK_01_SHAPE` Width, Height |
| `Card 01 Position`, `Card 01 Size` | `CARD_01_LAYOUT` Center, Size |
| `Callout 01 Text`, `Callout 01 Position` | `CALLOUT_01_LABEL` StyledText, Center |

- 대가: 장면이 본편 위 트랙이 아니라 장면 전용 타임라인에 있다. 본편에 쓰려면 사용자가 그 클립을 복사해 본편 타임라인의 빈 위 트랙에 붙인다(붙인 뒤 컨트롤 유지는 확인하지 않음). 본편 타임라인에는 타이틀을 넣지 않는다(본편을 민다).
- `retime`은 이 모드를 지원하지 않는다. 시각·길이가 바뀌면 장면 타임라인의 그 클립을 지우고 plan을 고쳐 `build`를 다시 부른다. Inspector에서 고친 값은 그때 plan 값으로 돌아간다.
- `grab`은 `mode`를 보고 장면 타임라인에서 plan 이름의 클립 구간을 렌더한다.
- 카메라 키프레임·등장 표현식은 Inspector에 나오지 않는다. 고치려면 Fusion 페이지에서 `Template`을 펼친다.

## 21.1.1 실측

| 사실 | 대응 |
|---|---|
| PNG를 `AppendToTimeline`하면 요청 길이를 무시하고 5초로 들어간다 | 타임라인 fps의 단색 H.264(`canvas` 명령)를 놓는다 |
| `AppendToTimeline`의 `endFrame`은 끝을 포함하지 않는다(0~239 → 239프레임) | N프레임이면 `endFrame = N` |
| 클립 comp의 0프레임 = 클립 첫 프레임(`startFrame` 0으로 놓았을 때) | 표현식은 `time - 시작프레임`으로 쓴다 |
| `comp.RenderStart`를 쓴 표현식은 한 프레임씩 렌더할 때 그 프레임이 RenderStart가 되어 0이 된다(카드가 끝까지 안 보임) | `comp.RenderStart`를 표현식에 쓰지 않는다 |
| `comp.Render({"Start": 0, "End": N})` 범위 렌더는 첫 프레임만 쓰고 False | 노드 출력을 꼭 봐야 할 때만 `grab --tool`(Saver를 잠시 붙이고 한 프레임씩 렌더한 뒤 RenderStart/End를 되돌림)을 쓴다 |
| `SetCurrentTimecode`, `ExportCurrentFrameAsStill`이 None을 돌려줬다. Deliver 렌더 잡(`AddRenderJob`·`StartRendering`, MarkIn/MarkOut 구간, 960×540 H.264)은 240프레임을 2.7초에 정확히 렌더했고 창을 남기지 않았다 | `grab` 기본값은 Deliver 렌더 잡이다. Deliver 형식·코덱은 끝나면 되돌리고 자기 잡은 지운다(렌더 범위·폴더 설정은 남는다) |
| `comp.Render`는 렌더마다 "Render completed!" 창(제목 = comp 이름)을 남긴다. 창이 여러 개면 하나를 닫을 때마다 다음 창이 뜬다. 이 창이 열려 있는 동안 `AppendToTimeline`·`CreateEmptyTimeline`이 None을, `GetCurrentPage`가 None을 돌려준다. `Fusion.SetBatch(True)`로도 창이 뜬다 | `comp.Render`를 쓰지 않는 Deliver `grab`을 기본으로 쓴다. `grab --tool`을 썼다면 창을 모두 닫는다(computer-use 권한이 있으면 그 창들의 OK 버튼을 누르고, 없으면 사용자에게 OK를 눌러 달라고 한다). `place`가 None으로 멈추면 이 창부터 확인한다 |
| Loader는 이름이 숫자로 끝나는 정지 이미지(`q_frame01.png`~`03.png`)를 한 시퀀스로 읽어, 카드마다 다른 카드의 틀이 시간에 따라 바뀌어 나왔다 | 정지 이미지 이름은 숫자로 끝나지 않게 짓는다(`card01_frame.png`). `build`가 숫자로 끝나는 이름을 막는다 |
| 카메라 zoom을 올린 채 가운데를 캔버스 가장자리 가까이 두면 캔버스 밖(빈 영역)이 보인다 | 키마다 가운데 x를 960/zoom ~ 1920 − 960/zoom, y를 540/zoom ~ 1080 − 540/zoom 안에 둔다 |
| 창 틀 PNG(틀 밖 투명)를 Loader로 읽어 바탕으로 쓰면 그 위에 합친 라벨이 창 끝에서 잘렸다(투명 영역이 DoD에서 빠짐) | 카드마다 화면 크기 투명 Background(`CARD_*_SPACE`) 위에 틀을 올린다 |
| RectangleMask Width는 이미지 폭, Height는 이미지 높이에 대한 비율이다 | `rect` 픽셀을 각각 1920, 1080으로 나눈다 |
| Merge 전경은 원래 픽셀 크기로 놓이고 Size가 배율이다 | 2배 스크린샷은 Size 0.5 |
| 키프레임 손잡이(`LH`·`RH`)는 키 기준 상대 좌표이고, 값만 주면 등속 손잡이가 붙는다 | ease-in-out은 손잡이 y를 0으로 준다 |
| `InsertFusionTitleIntoTimeline`은 재생 헤드의 V1에 끼워 넣어 본편 클립과 마커를 타이틀 길이(90프레임)만큼 밀었다 | 본편 타임라인에는 쓰지 않는다. title 모드는 장면 전용 타임라인 V1 끝에만 붙인다 |
| 클립 comp 안에 컨트롤을 공개한 매크로(MacroOperator)를 넣어도 Edit 페이지 Inspector에는 나타나지 않았다 | 캔버스 클립 모드는 Fusion 페이지 Inspector에서 고친다. Edit Inspector가 필요하면 title 모드를 쓴다 |
| Fusion 타이틀 comp를 `Template` 매크로로 감싸 `ImportFusionComp`하면 Edit Inspector → Video → Title 탭에 InstanceInput 컨트롤이 나왔고, Position X를 바꾸자 뷰어의 표시가 옮겨 갔다 | title 모드의 근거 |
| 타이틀 길이는 환경설정 Standard generator duration으로만 정해진다. `DURATION_IN_FRAMES` + `GeneratorDurationFrames`로 180·240프레임이 정확히 들어갔다(초 단위는 소수 초를 못 담는다). 원래 값(초 단위 3초)으로 돌아온 것을 내보낸 프리셋으로 대조했다 | `build`가 프레임 단위로 바꿨다가 되돌리고 대조한다 |
| `SetCurrentTimecode`가 True를 돌려줬고, 두 번째 장면이 첫 장면 끝(108180)에 정확히 붙었다 | `build`가 붙은 위치를 대조하고 다르면 멈춘다 |
| 화면 녹화(mp4) Loader를 매크로 안에 넣으면 Deliver 렌더가 "Fusion composition could not be processed"로 실패했고, MediaOut1 입력 연결도 사라졌다. PNG Loader는 매크로 안에서도 됐다 | Loader는 모두 매크로 밖(comp 최상위)에 둔다. 이렇게 만든 장면은 캔버스 클립 모드와 픽셀이 같았다(평균 차 0.00) |
| API로 만든 comp는 Fusion에서는 맞게 보여도 Edit 합성·Deliver 렌더에는 빈 캔버스로 나왔다(만든 직후 Deliver 렌더 6프레임 모두 카드 0%) | `build`·`retime`이 마지막에 comp를 `.comp`로 내보냈다가 다시 들인다(들인 뒤 카드 39~75%) |
| 클립 길이를 바꾸는 API가 없다 | `retime`이 comp를 `ExportFusionComp`로 백업하고 클립을 새 길이로 다시 놓은 뒤 `ImportFusionComp`한다 |

## 녹음 후 다시 맞추기

녹음 후에는 단어 시각에서 신호 단어의 시작을 찾아 plan의 `at`·`duration`·각 `start`·`camera[].at`를 고치고 `retime`을 부른다. `--old-at`은 지금 클립이 놓인 초(바꾸기 전 `at`)다.

plan의 시각만 바꾼 뒤 클립을 다시 맞추는 명령이다.

```bash
uv run --python 3.12 <page-tour>/scripts/resolve_cards.py retime edit-assets/plan_01.json --old-at 12.0
```

- `retime`은 위치·색·크기 입력을 건드리지 않는다. 사용자가 Fusion에서 옮긴 표시·카드는 그대로 남는다.
- 위치나 길이가 바뀌면 comp를 `plan_01.<시작프레임>.comp`로 백업한 뒤 클립을 다시 놓는다. 백업에 실패하면 클립을 지우지 않는다.

## 검증

`grab`으로 클립 구간을 Deliver 렌더해 대표 프레임을 뽑고 숫자로 먼저 본다. 프레임 번호는 클립 시작 기준(0부터)이다.

장면의 시작·등장 중·첫 짚기·두 번째 짚기·끝 프레임을 뽑아 시트를 만드는 명령이다.

```bash
uv run --python 3.12 <page-tour>/scripts/resolve_cards.py grab edit-assets/plan_01.json --frames 0,4,66,135,239 --out edit-assets/grab_01
```

- 0프레임은 캔버스만(카드 등장 전), 등장 뒤 프레임은 캔버스 아닌 픽셀이 생겨야 한다. 노드 하나의 출력만 비어 있으면 `grab --tool 노드라벨`로 그 노드를 보고, 표현식에 `RenderStart`가 들어갔는지 본다.
- 시트(`sheet_TIMELINE.jpg`)를 한 번 보고 표시가 대상에 정확히 얹혔는지 확인한다.
- `place`가 다른 트랙 클립·마커 대조를 통과했는지 출력으로 확인한다.

## 스크린샷 찍기

웹 페이지는 Chrome headless로 2배 해상도로 찍는다. 카메라 zoom 2까지 글자가 흐려지지 않는다. 사용자의 Chrome 프로필을 건드리지 않게 임시 프로필을 쓰고, 다 뜰 때까지 기다리고, 찍은 뒤 그 프로필의 Chrome 프로세스를 끝낸다.

폭 1440px 페이지를 2배(2880px)로 찍는 명령이다.

```bash
P=$(mktemp -d)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$P" --force-device-scale-factor=2 --window-size=1440,2400 --virtual-time-budget=20000 --screenshot=edit-assets/page@2x.png "https://example.com"
pkill -f "user-data-dir=$P"
```

- 로그인이 필요한 페이지, 개인 정보가 보이는 페이지는 찍지 않고 사용자에게 받는다.
- 화면 녹화·터미널은 사용자가 녹화한 실제 파일만 쓴다.
