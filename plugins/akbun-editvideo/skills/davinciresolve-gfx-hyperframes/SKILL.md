---
name: davinciresolve-gfx-hyperframes
description: 챕터 제목·원리·트레이드오프 구조·내 생각·전후 비교표 같은 전체 화면 모션 그래픽 카드를 HyperFrames(HTML → MP4)로 만들어 DaVinci Resolve 타임라인의 GFX 마커 위치에 V2 클립으로 넣는다. 카드 값은 편집 스타일(essay·project·reflection) skill의 글자 표, 내용은 비트 시트·전사에서만 가져온다. "챕터 카드 만들어줘", "전후 비교표 넣어줘", "모션 그래픽 카드" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-gfx-hyperframes

전체 화면을 대신하는 그래픽 카드를 만든다. 화면 클립 위에 얹는 글자는 카드가 아니라 `davinciresolve-subtitle-devtalk`의 Text+다. HTML 작성·렌더·삽입 절차의 원본은 [`references/hyperframes.md`](references/hyperframes.md)다.

`davinciresolve-video-editor`의 기본 원칙(작업 타임라인, 작업 로그)을 따른다. 카드 종류·색·크기·길이는 `davinciresolve-story-devtalk`이 정한 style skill의 글자 표가 원본이고, 카드 위치는 `davinciresolve-beats-devtalk`이 찍은 Cyan `GFX` 타임라인 마커다.

## 실행 조건

- `npx hyperframes --help`가 명령 목록을 출력해야 한다(Node 22 이상, ffmpeg). 안 되면 카드를 만들지 않고 `GFX` 마커와 카드 내용 표를 로그에 남긴다.
- style skill이 카드를 쓰지 않으면 이 skill은 할 일이 없다. 로그에 "카드 없음"이라고 적는다.

## 절차

[`references/hyperframes.md`](references/hyperframes.md)의 순서(준비 → 컴포지션 작성 → 검사·렌더 → Resolve에 넣기)를 그대로 따른다. 카드 내용(제목·항목·표 값)은 비트 시트와 전사에서만 가져오고, 카드는 V2(`davinciresolve-story-devtalk` 트랙 배치)에 놓으며 A1 음성은 카드 동안 그대로 흐른다.

## 컷 변경 반영

`davinciresolve-cut-devtalk`이 넘긴 바뀐 구간 목록을 받으면 `GFX` 마커를 새 시작 TC로 다시 찍고 카드 클립을 새 `recordFrame`에 다시 삽입한 뒤 옛것을 삭제한다.

## 작업 로그

`그래픽 카드` 절에 채운다.

```markdown
| 마커 TC | 카드 종류 | 제목·내용 | 파일 | 길이 | 확인 |
|---|---|---|---|---|---|
| 00:00:15:00 | 챕터 제목 | 왜 이 얘기를 하나 | gfx/renders/title-02.mp4 | 3.5초 | 3840×2160 30fps |
```

## 하지 않는 것

- 전사·비트 시트에 없는 내용의 카드
- 카드를 화면 클립 일부에만 겹치기(카드는 화면 전체를 대신한다)
- style skill 글자 표 밖의 색·크기·길이
- 렌더 실패를 "카드 완료"로 적는 것
