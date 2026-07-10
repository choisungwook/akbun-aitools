# HyperFrames composition 작성 규칙

HyperFrames는 HTML/CSS/JS를 headless Chrome에서 프레임 단위로 seek하며 캡처하고 FFmpeg로 MP4를 만드는 오픈소스다.
같은 입력이면 항상 같은 프레임이 나오는 결정적(deterministic) 렌더링이 전제다.

## composition 구조

composition은 data attribute로 타임라인을 정의한 평범한 HTML 파일이다.

- 루트 요소: `data-composition-id`, `data-start`, `data-duration`, `data-width`, `data-height`
- 각 요소(clip): `class="clip"` + `data-start`(등장 시각, 초) + `data-duration`(표시 시간, 초) + `data-track-index`
- 오디오: `<audio data-start data-duration data-track-index data-volume src>`
- `<html>`, `<body>`는 캔버스 크기로 고정하고 `overflow: hidden`을 준다.

## track 규칙 (lint 오류 1순위)

같은 `data-track-index`에서 시간이 겹치는 clip은 렌더링 충돌을 일으켜 lint 오류가 된다.
**동시에 화면에 보이는 clip은 반드시 서로 다른 track에 배치한다.**
같은 track은 "앞 clip이 끝난 뒤 다음 clip이 시작"하는 순차 배치에만 쓴다.
장면 안에서 역할별로 track을 나누면 안전하다: 제목 1, 도형 2, 화살표 3, 수식 4 처럼.

## 애니메이션: paused GSAP timeline

렌더러는 실시간 재생이 아니라 프레임 위치로 seek한다. 모든 모션은 seek 가능해야 한다.

- GSAP timeline을 `paused: true`로 만들고 `window.__timelines[<composition-id>]`에 등록한다.
- timeline의 시각은 composition 초 단위와 그대로 대응한다. `tl.from("#el", {...}, 2.0)`은 2초 시점에 시작한다.
- `setInterval`, `requestAnimationFrame`, autoplay CSS animation, `<video autoplay>` 등 wall-clock 의존 코드 금지.
- GSAP는 CDN(`https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js`)으로 로드한다.

## gold example

아래는 "이진 탐색" 주제의 단일 장면 composition 전체 예시다. 스타일 토큰과 track 분리, 선 그리기 애니메이션 패턴을 보여준다.

```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1920px; height: 1080px; overflow: hidden; background: #0d1117; }
      body { font-family: "Inter", sans-serif; color: #e6edf3; }
      .clip { position: absolute; }
      #title { top: 90px; width: 1920px; text-align: center; font-size: 68px; font-weight: 700; color: #79c0ff; }
      .cell {
        top: 460px; width: 150px; height: 110px; border-radius: 14px;
        border: 3px solid #8b949e; background: rgba(139, 148, 158, 0.10);
        display: flex; align-items: center; justify-content: center; font-size: 42px;
      }
      .cell.active { border-color: #58a6ff; background: rgba(88, 166, 255, 0.12); }
      .cell.hit { border-color: #7ee787; background: rgba(126, 231, 135, 0.12); }
      #caption { top: 700px; width: 1920px; text-align: center; font-size: 40px;
                 font-family: "JetBrains Mono", monospace; color: #ffa657; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="8"
         data-width="1920" data-height="1080">
      <div id="title" class="clip" data-start="0" data-duration="8" data-track-index="1">
        이진 탐색은 범위를 절반씩 줄인다
      </div>

      <div id="cell-1" class="clip cell"        style="left: 360px"  data-start="1"   data-duration="7" data-track-index="2">3</div>
      <div id="cell-2" class="clip cell"        style="left: 560px"  data-start="1.2" data-duration="6.8" data-track-index="3">8</div>
      <div id="cell-3" class="clip cell active" style="left: 760px"  data-start="1.4" data-duration="6.6" data-track-index="4">15</div>
      <div id="cell-4" class="clip cell hit"    style="left: 960px"  data-start="1.6" data-duration="6.4" data-track-index="5">21</div>
      <div id="cell-5" class="clip cell"        style="left: 1160px" data-start="1.8" data-duration="6.2" data-track-index="6">40</div>

      <svg id="probe" class="clip" data-start="3" data-duration="5" data-track-index="7"
           width="1920" height="1080" viewBox="0 0 1920 1080" fill="none" style="top: 0; left: 0">
        <path id="arc" d="M 835 440 Q 935 330 1035 440" stroke="#f778ba" stroke-width="6" fill="none"/>
      </svg>

      <div id="caption" class="clip" data-start="4.5" data-duration="3.5" data-track-index="8">
        검색 횟수 = log₂(n)
      </div>
    </div>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });

      tl.from("#title", { opacity: 0, y: -40, duration: 0.8 }, 0);
      gsap.utils.toArray(".cell").forEach((el, i) => {
        tl.from(el, { opacity: 0, scale: 0.6, duration: 0.5 }, 1 + i * 0.2);
      });

      const arc = document.querySelector("#arc");
      const len = arc.getTotalLength();
      arc.style.strokeDasharray = String(len);
      arc.style.strokeDashoffset = String(len);
      tl.to("#arc", { strokeDashoffset: 0, duration: 1.0, ease: "power2.out" }, 3);

      tl.from("#caption", { opacity: 0, y: 30, duration: 0.8 }, 4.5);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
```

## 여러 장면 구성

장면은 별도 기능이 아니라 시간 구간이다. 장면별 요소 묶음에 서로 다른 시간대의 `data-start`/`data-duration`을 주고,
timeline에서 장면 시작 시각에 등장 모션을, 장면 끝 0.4초 전에 fade out을 건다.
30초를 넘는 영상은 5~15초짜리 장면 3~5개로 나눈다.

## CLI 요약

프로젝트 생성부터 렌더링까지 순서대로 쓰는 명령이다.

```bash
npx hyperframes init <name> --example blank --non-interactive  # 스캐폴드
npx hyperframes lint                                           # 정적 검증(track 겹침 등)
npx hyperframes validate                                       # headless Chrome 런타임 검증(JS 오류, 누락 asset)
npx hyperframes snapshot --at 2.0,5.5,9.0                      # 지정 시각 프레임 PNG + contact-sheet
npx hyperframes render                                         # renders/*.mp4 생성
npx hyperframes preview                                        # (로컬 사용자용) 브라우저 라이브 프리뷰
```

## 트러블슈팅

- `render`가 Chrome을 못 찾으면: `npx hyperframes browser ensure`
- FFmpeg 없음: OS 패키지 매니저로 설치 후 `npx hyperframes doctor`로 재확인
- npm 설치가 onnxruntime 등 postinstall 다운로드에서 실패: `npm install hyperframes --ignore-scripts`
  (whisper 전사만 비활성화되고 렌더링은 정상 동작)
- lint의 `overlapping_clips_same_track`: 겹치는 clip 중 하나의 `data-track-index`를 바꾼다
