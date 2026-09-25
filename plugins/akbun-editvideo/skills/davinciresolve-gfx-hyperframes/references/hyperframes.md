# HyperFrames 그래픽 카드

그래픽 카드는 HTML로 쓰고 HyperFrames CLI가 헤드리스 Chrome으로 렌더한다. 같은 HTML은 항상 같은 영상이 나오므로, 카드 내용을 고치면 다시 렌더만 하면 된다. 카드는 화면 전체를 대신하는 클립이므로 기본 출력은 MP4다. 화면 클립 위에 얹는 오버레이는 카드가 아니라 Text+로 한다.

## 준비

출력 폴더 아래 `gfx/`에 프로젝트를 한 번 만든다. 스캐폴드가 런타임 스크립트를 넣어 주므로 `index.html`의 `<script>` 태그 구조는 그대로 두고 컴포지션 파일만 추가한다.

```bash
cd "<출력 폴더>" && npx hyperframes init gfx && cd gfx
```

`npx hyperframes docs data-attributes`와 `npx hyperframes docs compositions`가 속성 설명의 원본이다. 이 문서는 카드에 필요한 최소만 적는다.

## 파일 배치

| 경로 | 내용 |
|---|---|
| `compositions/<카드 종류>-<번호>.html` | 카드 하나 = 컴포지션 하나. 번호는 비트 번호. 예: `title-02.html`, `diagram-03.html`, `take-04.html`, `table-05.html` |
| `fonts/` | Pretendard otf 복사본(macOS `~/Library/Fonts/Pretendard-*.otf`, Windows `%LOCALAPPDATA%\Microsoft\Windows\Fonts\Pretendard-*.otf`). SIL OFL이라 복사해 넣어도 된다. 렌더 머신에 설치돼 있어도 `@font-face`로 파일을 지정해 두 OS에서 같은 결과를 얻는다 |
| `renders/` | 렌더 결과 MP4. 파일명은 컴포지션 이름과 같게 |

## 컴포지션 규칙

- 루트 요소에 `data-composition-id`, `data-width`, `data-height`, `data-fps`를 두고 값은 타임라인 해상도·프레임레이트와 같게 한다.
- 시간이 있는 요소는 `class="clip"`, `data-start`(초), `data-duration`(초)를 준다. 카드 길이는 style skill 글자 표의 값.
- 등장·퇴장은 CSS 애니메이션으로 하고 `animation-fill-mode: both`를 준다. 렌더러가 프레임 단위로 탐색하므로 `setTimeout`·`requestAnimationFrame`으로 직접 움직이지 않는다.
- 글자·색·크기 값은 style skill(`davinciresolve-style-essay` 등)의 글자 표에서 가져온다. 실행 조건과 로그는 `SKILL.md`, HTML·렌더·삽입 절차는 이 문서가 원본이다. 비율 값(화면 높이의 14%)은 `vh` 단위로 옮긴다(14% → `14vh`).
- 카드 내용은 비트 시트·전사에서만 가져온다.

## 제목 카드 예시

essay 스타일 챕터 제목 카드다. 텍스트와 색은 변수로 두어 `--variables`로 바꾼다.

```html
<html data-composition-variables='[
  {"id":"title","type":"string","label":"Title","default":"제목"},
  {"id":"bg","type":"color","label":"Background","default":"#EFE6F7"}
]'>
<head>
<style>
  @font-face { font-family: "Pretendard"; src: url("../fonts/Pretendard-Bold.otf"); font-weight: 700; }
  html, body { margin: 0; }
  .card { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
  .title {
    font-family: "Pretendard", "Noto Sans KR", sans-serif; font-weight: 700; font-size: 14vh; color: #FFD400;
    -webkit-text-stroke: 0.84vh #1A1A1A; paint-order: stroke fill; text-align: center; line-height: 1.15;
    animation: pop 0.4s cubic-bezier(.2,.9,.3,1.2) both;
  }
  @keyframes pop { from { transform: scale(0.6); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>
</head>
<body>
<div id="root" data-composition-id="title" data-width="3840" data-height="2160" data-fps="30">
  <div class="clip card" data-start="0" data-duration="3.5">
    <div class="title"></div>
  </div>
  <script>
    const { title, bg } = window.__hyperframes.getVariables();
    document.querySelector(".card").style.background = bg;
    document.querySelector(".title").textContent = title;
  </script>
</div>
</body>
</html>
```

## 카드 종류

| 종류 | 파일 접두어 | 구성 |
|---|---|---|
| 챕터 제목 | `title-` | 파스텔 배경 + 제목 1줄(2줄까지) + 스티커 1~2개 |
| 원리·트레이드오프 | `diagram-` | 흰 배경, 상자·화살표·라벨로 구조를 그림, 말하는 요소가 강조색으로 바뀜 |
| 내 생각 | `take-` | 파스텔 배경 + 고정 문구 `내 생각` + 스티커 |
| 전후 비교표 | `table-` | 3열(항목·전·후) 표, 말하는 행에 빨간 원 등장 |

색·글자 높이·길이·강조 타이밍은 style skill 글자 표의 값을 쓴다.

## 검사와 렌더

렌더 전에 검사한다. 오류가 있으면 고치고 다시 검사한다.

```bash
npx hyperframes check
```

카드 하나를 타임라인 프레임레이트로 렌더한다. 변수로 제목을 넘긴다.

```bash
npx hyperframes render -c compositions/title-02.html -o renders/title-02.mp4 --fps 30 --quality delivery --variables '{"title":"왜 컨테이너는 빨리 뜨나"}'
```

같은 카드 종류가 여러 장이면 `--batch`에 변수 행 JSON 배열을 주어 한 번에 렌더한다.

## Resolve에 넣기

렌더 파일을 미디어 풀에 넣고 `GFX` 마커 프레임에 V2로 놓는다. Resolve MCP `run_script`에서 실행하는 예다.

```python
mp = project.GetMediaPool()
tl = project.GetCurrentTimeline()
items = mp.ImportMedia(["<출력 폴더>/gfx/renders/title-02.mp4"])
gfx = {k: v for k, v in tl.GetMarkers().items() if v["color"] == "Cyan"}
frame = next(f for f, m in gfx.items() if m["name"] == "GFX 챕터 제목 왜 이 얘기를 하나")  # 마커 이름은 GFX <카드 종류> <제목>
mp.AppendToTimeline([{"mediaPoolItem": items[0], "trackIndex": 2, "recordFrame": tl.GetStartFrame() + frame}])
```

넣은 뒤 `ffprobe`로 렌더 파일의 해상도·프레임레이트가 타임라인과 같은지 확인하고 작업 로그 `그래픽 카드` 표에 적는다.
