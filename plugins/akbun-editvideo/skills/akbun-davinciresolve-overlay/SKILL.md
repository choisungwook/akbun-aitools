---
name: akbun-davinciresolve-overlay
description: DaVinci Resolve 21.1 AI Assistant로 본편 위에 사진·영상·화면 캡처 카드와 주석 글자를 얹는다. 카드는 둥근 모서리로 OVERLAY 트랙에 놓고 등장·퇴장(pop, slide, fade)을 키프레임으로 넣으며, 글자는 SUBTITLE 트랙의 Text+로 놓고 타이핑 등장을 넣는다. 본편의 느린 확대·축소(push)도 넣는다. 위치·크기·타이밍 값은 편집 스타일 skill(explainer, product)과 감독 skill의 연출표에서 받는다. "결과 사진을 카드로 띄워줘", "화면 캡처를 오른쪽에 넣어줘", "주석 글자 넣어줘", "천천히 확대해줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-overlay

본편 위에 정보를 얹는 실행 skill이다. 무엇을 언제 얹을지는 편집 스타일 skill([explainer](../akbun-davinciresolve-style-explainer/SKILL.md), [product](../akbun-davinciresolve-style-product/SKILL.md))과 [감독 skill](../akbun-davinciresolve-director/SKILL.md)의 연출표가 정한다. 이 skill은 그 값을 타임라인에 옮기고 결과를 측정한다. 연출표 없이 단독으로 불리면 요청 문장에서 위치·길이를 읽고, 없는 값은 아래 기본값을 쓴 뒤 로그에 적는다.

`akbun-davinciresolve-workflow`의 기본 원칙(작업 타임라인에서만 편집, 클립은 파일명 + 시작 타임코드, 대표 1개 선적용, 작업 로그)과 마커 등록표를 따른다.

## 용어

- 카드(card): 본편 위에 얹는 사진·영상·화면 캡처 한 장. 둥근 모서리, 화면 비율 위치(x, y)와 폭으로 정한다
- 주석(annotation): 카드나 피사체 옆에 붙는 짧은 글자. 손글씨체이고 곡선 화살표와 함께 쓸 수 있다
- 키워드: 화면에 크게 한 번 나오는 단어나 짧은 구절. 세리프체
- 2단 글자: 작은 줄(맥락) 위나 아래에 큰 세리프 단어(핵심)를 붙인 묶음. 절 제목을 카드 없이 장면 위에 놓을 때 쓴다
- push: 본편 클립 하나가 끝날 때까지 천천히 확대(또는 축소)되는 움직임
- 스냅 확대: 5~8프레임 안에 끝나는 짧은 확대. 카드가 들어올 때 본편에 준다

## 트랙

| 트랙 | 놓는 것 | 명령 |
|---|---|---|
| V1 본편 | 촬영 클립, 화면 녹화 | push는 이 트랙 클립에 넣는다 |
| `OVERLAY` | 카드 | `scripts/overlay.py place` |
| `GFX` | 전체 화면 그래픽 카드 | 선택한 그래픽 도구. HyperFrames면 `davinciresolve-gfx-hyperframes` |
| `SUBTITLE` | 주석·키워드·2단 글자·목록 Text+ | `../davinciresolve-subtitle-travelnote/scripts/textplus.py place` 뒤 `scripts/overlay.py write-on` |

트랙은 이름으로 찾는다. `OVERLAY`가 `GFX`·`SUBTITLE`·`HOOK_TEXT`보다 아래에 있어야 글자를 가리지 않는다. 트랙이 없으면 `python3 ../akbun-davinciresolve-workflow/scripts/workflow.py tracks --timeline "<작업 타임라인>"`으로 먼저 만든다. 스크립트는 글자 트랙이 이미 있는데 `OVERLAY`가 없으면 맨 위에 새로 만들지 않고 멈춘다.

## 21.1에서 확인한 것

- Edit 페이지 Inspector의 Pan·Tilt·Zoom은 API로 고정값만 넣을 수 있고 키프레임 함수가 없다. 그래서 카드의 위치·크기·움직임은 클립의 Fusion 컴포지션(`AKBUN_OVERLAY`) 안에서 타임라인 해상도의 투명 캔버스 위에 정한다. x·y·폭이 화면 비율 그대로다.
- Pan·Tilt 단위는 소스와 타임라인의 화면비가 다르면 픽셀과 다르다(세로 타임라인의 가로 소스에서 Tilt 300이 95px). Inspector 값을 스크립트로 넣지 않는다.
- Transform 도구에 마스크를 걸면 마스크 밖으로 원래 그림이 보인다. 둥근 모서리는 투명 배경 위 Merge에 `RectangleMask`를 걸어 만든다.
- `TimelineItem.SetFades`는 프로젝트를 다시 열면 0이 된다. 페이드는 Merge의 Blend 키프레임으로 넣는다.
- 클립의 마지막 Fusion 컴포지션은 `DeleteFusionCompByName`으로 지워지지 않는다. `push --reset`은 컴포지션 안의 도구를 비우고 빈 `AKBUN_PUSH`를 남긴다.
- Dynamic Zoom은 켜기와 ease만 API로 정할 수 있고 시작·끝 사각형은 정할 수 없어 쓰지 않는다.

## 카드

카드 1장을 놓는 명령이다. 사진·영상 파일은 `--file`, 미디어 풀 항목은 `--clip`으로 준다.

```bash
python3 scripts/overlay.py place --timeline "<작업 타임라인>" --at 01:00:12:00 --seconds 4 --file "<결과 이미지.png>" \
  --x 0.26 --y 0.5 --width 0.4 --radius 0.08 --in fade --in-frames 6 --out fade --out-frames 6 --out-dir "<출력 폴더>"
```

| 옵션 | 뜻 | 기본값 |
|---|---|---|
| `--x`·`--y` | 카드 중심. 0~1, 왼쪽 아래가 (0, 0) | 0.5, 0.5 |
| `--width` | 카드 폭 / 화면 폭. 높이는 소스 화면비로 정해진다 | 0.3 |
| `--radius` | 모서리 둥글기 0~1 | 0.08 |
| `--in`·`--out` | `pop`, `slide-left`, `slide-right`, `slide-up`, `slide-down`, `fade`, `none` | pop, fade |
| `--in-frames`·`--out-frames` | 등장·퇴장 프레임 수 | 8, 6 |
| `--overshoot` | pop이 목표 크기를 넘는 비율. 0.06이면 106%까지 커졌다 돌아온다 | 0 |
| `--source-in` | 영상 소스에서 쓸 시작 위치(초) | 0 |

- 등장은 ease-out(빠르게 출발해 감속), 퇴장은 ease-in(천천히 출발해 가속)이다. 스크립트가 곡선을 정한다.
- 카드 전체가 화면의 가운데 90% 안에 있어야 한다. 밖으로 나가면 스크립트가 놓지 않는다.
- 같은 트랙의 같은 구간에 클립이 있으면 놓지 않는다. 다른 트랙의 클립·타임라인 마커·타임라인 길이가 전후로 같은지 비교하고, 다르면 종료 코드 1이다.
- 놓은 뒤 `--out-dir`의 `overlay-stills/`에 카드 가운데 프레임 스틸을 남긴다. 스틸에서 카드가 피사체·글자·화면 녹화의 읽을 부분을 가리지 않는지 본다.
- 카드를 지울 때는 `python3 ../davinciresolve-subtitle-travelnote/scripts/textplus.py remove --timeline "<작업 타임라인>" --at <시작 TC> --track OVERLAY`를 쓴다. 위치를 바꾸려면 지운 뒤 다시 놓는다.
- 테두리·그림자는 스크립트가 넣지 않는다. 필요하면 Fusion 페이지에서 `AKBUN_OVERLAY`의 카드 Merge 앞에 넣는다.

## 본편 push

클립 하나에 천천히 확대하는 명령이다. `--at`은 대상 클립 안의 아무 타임코드다.

```bash
python3 scripts/overlay.py push --timeline "<작업 타임라인>" --at 01:00:25:10 --from 1.0 --to 1.06 --x 0.5 --y 0.5 --out-dir "<출력 폴더>"
```

- 곡선은 ease-in-out이다. 로그의 `초당 변화(%)`를 보고 1.5%/초를 넘으면 배율을 줄이거나 클립을 짧게 쓴다. 느린 push가 눈에 띄는 순간 몰입이 깨진다.
- 1보다 작은 배율은 가장자리에 빈 곳이 보인다. 축소가 필요하면 `--from 1.08 --to 1.0`처럼 1보다 큰 값에서 1로 줄인다.
- 클립에 다른 Fusion 컴포지션이 있으면 넣지 않는다. 지우려면 `--reset`을 쓴다.
- 스냅 확대(5~8프레임)는 스크립트가 넣지 않는다. 카드 등장과 같은 프레임에서 Resolve Inspector의 Zoom 키프레임 두 개로 넣고 로그에 적는다.

## 글자

글자는 Text+ 1개가 클립 1개다. 놓는 방법·템플릿 준비·안전 영역은 [davinciresolve-subtitle-travelnote의 Text+ 배치](../davinciresolve-subtitle-travelnote/SKILL.md#text-배치)를 따르고, 글꼴은 아래 표를 쓴다. 놓은 뒤 타이핑 등장을 넣는다.

```bash
python3 ../davinciresolve-subtitle-travelnote/scripts/textplus.py place --timeline "<작업 타임라인>" --at 01:00:14:00 --seconds 3 \
  --text "처음 만든 결과" --font "Nanum Pen Script" --style Regular --size <측정값> --x 0.2 --y 0.7 --out "<출력 폴더>"
python3 scripts/overlay.py write-on --timeline "<작업 타임라인>" --at 01:00:14:00 --seconds 0.6 --out-dir "<출력 폴더>"
```

| 종류 | 글꼴(SIL OFL) | 글자 높이(화면 높이 대비) | 등장 |
|---|---|---|---|
| 주석 | Nanum Pen Script Regular, 흰색 | 4.5% 이상 | 타이핑, 글자당 약 1프레임(한 줄 0.4~0.8초) |
| 키워드 | Noto Serif KR Bold, 흰색 또는 크림색 `#F3E6C4` | 8~10% | 타이핑 0.8~1.5초 |
| 2단 글자 | 작은 줄 Pretendard Medium 4.5%, 큰 줄 Noto Serif KR Bold 8~10% | 표 값 | 작은 줄 타이핑 → 큰 줄이 0.3초 뒤 |
| 목록 | Pretendard Medium 또는 Nanum Pen Script | 5% 이상 | 말하는 순간마다 한 줄씩 |
| 짧은 단어 자막 | Pretendard Bold 흰색 | 5% 이상 | 컷, 2~6단어 묶음 |

- 참고 영상의 주석은 라틴 문자 기준 약 3%였다. 한글은 획이 많아 4.5% 아래로 내리지 않는다. 대사 자막 5% 규칙은 `davinciresolve-subtitle-devtalk`을 따른다.
- 글꼴이 Resolve 글꼴 목록에 없으면 `textplus.py`가 놓지 않고 멈춘다. 설치 경로(Google Fonts의 Nanum Pen Script, Noto Serif KR, Pretendard GitHub 릴리스)를 안내하고 다른 글꼴로 바꾸지 않는다.
- 곡선 화살표는 Text+가 아니다. 사용자가 준 투명 PNG를 카드와 같은 `place --radius 0 --in fade`로 놓거나, 없으면 연출표에 `화살표 필요`로 남긴다.
- 글자는 피사체·카드를 가리지 않는 빈 공간에 둔다. 화면 녹화의 코드·터미널 글자 위에 겹치지 않는다.

## 작업 로그

`<출력 폴더>/edit-log_<YYYYMMDD_HHMM>.md`의 `오버레이` 절에 스크립트가 출력한 표를 옮기고 아래를 더한다.

- 연출표 cue ID와 실제 시작 TC, 바꾼 값과 이유
- 스틸로 확인한 가림 여부, Resolve에서 손으로 넣은 스냅 확대·테두리·그림자
- 실패하거나 미적용한 카드와 글자

## 하지 않는 것

- 연출표나 전사에 없는 수치·문장·로고를 카드·글자로 넣는 것
- Inspector Pan·Tilt·Zoom 값을 스크립트로 넣는 것, 타임라인 중간에서 `InsertFusionTitleIntoTimeline` 호출
- 화면 90% 밖으로 나가는 카드, 4.5%보다 작은 한글 글자
- 한 화면에 카드 3장 이상을 동시에 두는 것. 비교가 필요하면 전체 화면 그래픽으로 바꾼다
- 화자 얼굴이 보이는 영상을 카드로 쓰는 것
