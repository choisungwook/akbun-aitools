---
name: davinciresolve-gfx-hyperframes
description: 챕터 제목·원리·트레이드오프 구조·내 생각·전후 비교표 같은 전체 화면 모션 그래픽 카드를 HyperFrames(HTML → MP4)로 만들어 DaVinci Resolve 타임라인의 GFX 마커 위치에 V2 클립으로 넣는다. 카드 값은 편집 스타일(essay·project·reflection) skill의 글자 표, 내용은 비트 시트·전사에서만 가져온다. "챕터 카드 만들어줘", "전후 비교표 넣어줘", "모션 그래픽 카드" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-gfx-hyperframes

`GFX` 마커마다 HyperFrames 컴포지션 HTML 한 파일을 `<출력 폴더>/gfx/compositions/<카드 종류>-<비트 번호>.html`에 쓰되, 루트의 `data-width`·`data-height`·`data-fps`는 타임라인과 같게 하고 글꼴은 `@font-face`로 Pretendard 파일을 지정하며, 색·크기·길이는 style skill의 글자 표에서, 제목·항목·표 값은 비트 시트와 전사에서만 가져온다. 아래 명령으로 검사·렌더한 뒤 `MediaPool.ImportMedia`로 가져와 `AppendToTimeline`에 `trackIndex: 2`와 `recordFrame`(마커 프레임)을 주어 V2(`davinciresolve-story-devtalk` 트랙 배치)에 놓고, `ffprobe`로 해상도·fps가 타임라인과 같은지 확인해 작업 로그 `그래픽 카드` 절에 마커 TC·종류·내용·파일·길이를 남긴다. 화면 클립 위에 얹는 번호 제목·키워드는 카드가 아니라 `davinciresolve-subtitle-devtalk`의 Text+이고, `npx hyperframes --help`가 실패하면(Node 22 이상, ffmpeg 필요) 카드를 만들지 않고 `GFX` 마커와 카드 내용 표만 로그에 남긴다.

처음 한 번 프로젝트를 만들고, 카드마다 검사 뒤 렌더하는 명령이다.

```bash
npx hyperframes init gfx
cd gfx && npx hyperframes check && npx hyperframes render -c compositions/title-02.html -o renders/title-02.mp4 --fps 30 --quality delivery
```
