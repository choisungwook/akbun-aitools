---
name: davinciresolve-subtitle-devtalk
description: 말하는 개발자 브이로그의 오버레이 자막을 만드는 devtalk 스타일. 편집 스타일(essay·project·reflection)의 글자 표에 따라 대사 자막(Resolve CreateSubtitlesFromAudio), 키워드 강조·장면 코멘트·목록 자막(Text+)을 넣고 전사와 대조해 용어를 고친다. 글꼴은 Windows·macOS 어디서나 쓸 수 있는 SIL OFL 한글 글꼴(Pretendard, 없으면 Noto Sans KR)만 쓰고, 자막 글자 높이는 화면 높이의 5% 이상으로 스틸로 재서 지킨다. "대사 자막 넣어줘", "키워드 강조 자막", "장면 코멘트 자막" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-subtitle-devtalk

자막 스타일 중 하나다. 이름의 devtalk은 "화자가 말한 것만 글자로 얹는다"는 뜻이다. 장소·시간을 적는 여행 자막은 `davinciresolve-subtitle-travelnote`가 맡는다.

`davinciresolve-video-editor`의 기본 원칙(대표 자막 1개 선적용, 작업 로그)을 따른다. 어떤 자막을 어디에 넣는지는 `davinciresolve-story-devtalk`이 정한 style skill의 글자 표가 원본이다. 스타일이 없으면 그 skill의 스타일 선택 표로 먼저 정한다. 글꼴과 최소 크기는 style skill보다 이 문서가 우선한다.

## 글꼴

Windows와 macOS 어디서 편집하든 같은 결과가 나오고 저작권 문제가 없어야 하므로 SIL Open Font License 한글 글꼴만 쓴다. 상업 사용은 되지만 재배포 조건이 붙는 글꼴(Gmarket Sans 등)은 이 스타일에서 쓰지 않는다.

| 순서 | 글꼴 | 대사 자막 | 제목·키워드 | 확인 |
|---|---|---|---|---|
| 기본 | Pretendard(SIL OFL) | Medium(500) | Bold(700) | macOS `fc-list \| grep -i pretendard`, Windows `설정 → 글꼴`에서 Pretendard |
| 대체 | Noto Sans KR(SIL OFL) | Medium | Bold | 같은 방법으로 `noto sans kr` |

둘 다 없으면 멈추고 설치 경로(Pretendard GitHub 릴리스 또는 Google Fonts의 Noto Sans KR)를 안내한다. 다른 글꼴로 대체하지 않는다. 대사 자막은 자막 트랙에서, Text+는 `Font` 입력에서 같은 글꼴 이름을 쓴다.

## 최소 크기

자막은 스마트폰 화면에서도 읽혀야 한다. 픽셀 값은 글꼴마다 다르므로 대표 자막 1개를 스틸로 찍어 한글 한 글자 높이를 잰다.

| 요소 | 글자 높이 최소값(화면 높이 대비) | 4K 기준 |
|---|---|---|
| 대사 자막, 장면 코멘트, 목록 자막 | 5% | 108px 이상 |
| 키워드 강조, 비트 제목, 오프닝 부제 | 6% | 130px 이상 |
| 번호 제목, 오프닝 제목 | 8% | 173px 이상 |

style skill 글자 표의 값이 이보다 작으면 최소값으로 올리고 로그에 적는다. 크기를 줄여 문장을 넣지 않는다. 안 들어가면 글자 수를 줄이거나 2줄로 나눈다(대사 자막은 style skill이 한 줄로 정했으면 글자 수를 줄인다).

## 대사 자막

style skill이 대사 자막을 쓰는 경우에만 만든다. 화자가 화면에 없으므로 대사 자막은 누가 말하는지 보여 주는 유일한 글자다. 음성 문장마다 하나씩 있어야 한다.

- `Timeline.CreateSubtitlesFromAudio`로 만든다. `language` 한국어, `charsPerLine`·`lineBreak`·`gap`은 style skill 글자 표의 값.
- 만든 뒤 전사와 대조해 고유명사·영문 용어(예: `kubectl`, `namespace`)를 원문 표기로 고친다. 필러는 뺀다. 화자가 말하지 않은 내용을 넣지 않는다.
- 자막 트랙 스타일(글꼴 Pretendard Medium, 글자 높이, 위치, 그림자)은 API가 없으므로 Inspector 트랙 스타일에서 한 번 설정한다. 화면 조작이 안 되면 값 표를 절차서로 남긴다.
- 문장 부호는 쉼표·물음표만 쓴다.

## Text+ 오버레이

키워드 강조, 번호 제목, 장면 코멘트, 목록 자막, 비트 제목, 오프닝 타이틀은 Text+로 만든다.

- `InsertFusionTitleIntoTimeline("Text+")` 뒤 `GetFusionCompByIndex(1)`로 `StyledText`·`Font`·`Style`·`Size`를 설정한다. 트랙은 V3(`davinciresolve-story-devtalk` 트랙 배치). 삽입 위치가 다른 트랙이면 V3로 옮긴다.
- 크기는 대표 자막 1개를 스틸로 찍어 글자 높이를 재고 style skill 글자 표의 비율(화면 높이의 N%)에 맞춘다. 위 최소 크기 표보다 작으면 최소값으로 올린다. 한 줄 최대 글자 수도 같은 스틸로 정해 로그에 적는다. 측정 방식은 `davinciresolve-subtitle-travelnote`와 같다.
- 텍스트는 전사에서만 가져온다. 키워드 강조는 화자가 그 단어를 말하는 프레임에 등장한다.
- 안전 영역: 글자 전체가 화면 폭의 90%, 높이의 90% 안에 있어야 한다. 대표 자막 스틸로 확인한다.
- 등장·퇴장은 8프레임 페이드. 화면 녹화의 코드·터미널 글자 위에 겹치지 않게 놓는다.

## 컷 변경 반영

`davinciresolve-cut-devtalk`이 넘긴 바뀐 구간 목록을 받으면 Text+는 새 위치에 다시 삽입하고 옛것을 삭제한다(이동 API 없음). 대사 자막은 `CreateSubtitlesFromAudio`를 다시 돌리고 전사 대조를 다시 한다. 결과를 `자막·챕터` 표에 "재타이밍" 비고로 적는다.

## 작업 로그

`자막·챕터` 절에 채운다.

```markdown
확정값: 글꼴 Pretendard / 대사 자막 글자 높이 119px(화면 높이 5.5%), charsPerLine 18 / 키워드 Text+ Size 0.12, 글자 높이 130px(6.0%)

| 시작 TC | 종료 TC | 종류 | 텍스트 | 위치 | 비고 |
|---|---|---|---|---|---|
| 00:00:00:12 | 00:00:02:20 | 대사 | 컨테이너는 왜 이렇게 빨리 뜰까 | 하단 가운데 | |
| 00:01:05:00 | 00:01:06:15 | 키워드 | namespace | 우상단 | |

챕터 목록
00:00 훅
00:15 왜 이 얘기를 하나
```

## 하지 않는 것

- Pretendard·Noto Sans KR 외 글꼴, 최소 크기 표보다 작은 글자, style skill 글자 표 밖의 위치
- 전사에 없는 문장·수치
- style skill이 쓰지 않는 자막 종류 추가
- 컷 변경 뒤 자막 타이밍을 그대로 두는 것
