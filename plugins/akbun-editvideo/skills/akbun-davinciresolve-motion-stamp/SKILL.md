---
name: akbun-davinciresolve-motion-stamp
description: 내레이션(투어 해설·브이로그 음성)이 있는 DaVinci Resolve 타임라인에 레퍼런스 영상의 스타일을 분석해 카드·칩·숫자 타일·도장·막대그래프 모션그래픽(MG)을 만들어 넣는다. 레이아웃은 고정하지 않고 장면마다 내레이션 내용을 보고 정한다. PIL로 그린 프레임을 ProRes 4444 알파 MOV로 렌더하고, 기존 사진·영상 컷을 줄이거나 지워 MG로 대체한 뒤 전환·효과음까지 배치한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-motion-stamp

## 결과물

- 작업 타임라인(마지막 작업 타임라인의 복제본)에 MG 클립·전환·효과음이 놓인 상태
- `<프로젝트>/mg/scenes.json`: 장면 spec. 레이아웃은 이 파일에 장면마다 따로 적는다
- `<프로젝트>/mg/out/*.mov`: 장면별 MG 클립(1920×1080, ProRes 4444 알파)
- `<프로젝트>/mg/out/events.json`: 장면별 효과음 큐
- 완료 보고: 장면 타이밍 대조표, 미삽입 SFX, 짧게 들어간 전환 목록

출력 형식은 항상 ProRes 4444 알파 MOV다. 오버레이 장면은 사진·영상 위에 겹치므로 알파가 필요하고, 전체 화면 장면도 같은 형식으로 맞춰 import·교체 절차를 하나로 유지한다. H.264(MP4)는 알파를 담지 못한다. 완료 보고에 이 이유를 한 줄로 적는다.

## 레이아웃 원칙

레이아웃은 고정하지 않는다. 장면마다 그 장면의 내레이션이 전하는 정보를 보고 AI가 부품·개수·위치·등장 순서를 정한다. 스크립트는 좌표를 받아 그릴 뿐이고 장면 템플릿이 없다. 고정하는 것은 아래 "스타일"(색·글꼴·크기·모션)과 "배치 제약"뿐이다.

### 정보 종류별 부품

| 내레이션이 전하는 것 | 쓰기 좋은 부품 |
|---|---|
| 주제가 바뀜(새 장소·새 이야기) | `chapter` |
| 숫자 1~3개(거리·연도·개수·가격) | `tile` |
| 여러 값의 비교·순위 | `bar` |
| 이름·키워드 한두 개 | `chip`, `text` |
| 설명이 붙는 정보 묶음 | `card` |
| 평가·결론·인증 같은 한 단어 | `stamp` |
| 사진 속 특정 대상 | `box` + `arrow` + `chip` (오버레이) |
| 순서·위치 표시 | `dot` |

### 배치를 정하는 순서

1. 장면에서 화면에 남길 정보를 키워드·숫자로 1~4개 고른다. 한 화면에 동시에 보이는 부품은 5개 이하로 둔다.
2. 정보 사이의 관계(나열·비교·원인과 결과·주인공 하나)를 정하고, 관계에 맞게 배치한다. 나열이면 같은 크기를 한 줄 또는 한 열로, 비교면 나란히, 주인공 하나면 크게 두고 나머지는 작게 둔다.
3. 내레이션에서 그 정보가 나오는 순서대로 `at`을 정한다. 말보다 먼저 나오지 않게 단어 시각 0.1초 전을 기준으로 한다.
4. 사진 배경 장면은 강조 대상의 위치를 먼저 정하고, 칩·카드는 대상을 가리지 않는 빈 쪽에 둔다.
5. 이어지는 두 장면이 같은 배치가 되지 않게 한다. 직전 장면과 정렬(가운데·왼쪽·오른쪽)이나 부품 배열 방향 중 하나 이상을 바꾼다.

### 배치 제약

| 항목 | 값 |
|---|---|
| 좌우 안전 여백 | 96px. `x ± 폭/2`가 96~1824 안 |
| 자막 영역 | y 880px 아래는 비운다. 사진 위 오버레이만 있는 장면도 같다. 자막이 없는 장면은 `captions: false` |
| 부품 간격 | 동시에 보이는 부품끼리 24px 이상 |
| 좌표 기준 | `x`, `y`는 부품의 가운데. `box`·`arrow`는 화면 절대 좌표 |

렌더 스크립트는 안전 여백 침범, 자막 영역 침범, 24px 안쪽 겹침, 글자가 부품 폭을 넘는 경우를 `경고:`로 출력하고 종료 코드 1을 낸다. 경고가 남으면 배치를 고쳐 다시 렌더한다. `bar`·`arrow`는 자라는 부품이라 겹침 검사에서 빠지므로 스틸로 확인한다.

## 스타일

1920×1080, 타임라인 fps 기준이다. spec의 `theme`으로 색을 바꿀 수 있다. 레퍼런스 분석에서 다른 팔레트가 나오면 `theme`에 hex로 적는다.

### 색과 글꼴

| 역할 | theme 키 | 기본값 |
|---|---|---|
| 배경 | `bg` | `#F4EFE6` |
| 줄무늬 배경의 줄 | `stripe` | `#EAE2D3` (폭 40px, 간격 80px, 45°) |
| 별 배경 | `night` | `#14213D` (흰 점 160개, 반지름 1~3px) |
| 카드·타일 | `card` | `#FFFFFF` |
| 본문 글자 | `ink` | `#1F1F1F` |
| 보조 글자·보조 막대 | `sub` | `#6B6B6B` |
| 강조(칩·박스·화살표·숫자) | `accent` | `#FFC93C` |
| 도장 | `stamp` | `#D64541` |
| 그림자 | `shadow` | `#00000040`, 아래 8px, blur 16px |

글꼴은 Gmarket Sans. 제목·숫자는 Bold, 본문·라벨은 Medium이다.

### 부품 크기

| 부품 | 기본 크기 |
|---|---|
| `chapter` | 번호 Bold 150px(accent), 제목 Bold 88px, 아래 강조 막대 120×12px |
| `card` | 720×360px, 모서리 28px, 제목 Bold 64px, 본문 Medium 40px, 안쪽 여백 40px |
| `chip` | 글자 Medium 44px, 높이 64px 이상, 좌우 여백 28px, 알약 모양 |
| `tile` | 240×240px, 모서리 32px, 위쪽 accent 띠 16px, 숫자 Bold 42%, 라벨 Medium 15% |
| `stamp` | 지름 260px, 바깥 원 8px + 안쪽 원 3px, -12° 기울임, 글자 Bold 20% |
| `bar` | 폭 1100px, 행 96px, 막대 두께 48px, 라벨 Medium 38px, 값 Bold 40px. 강조 행만 accent |
| `box` | 테두리 8px accent, 채움 accent 20%, 모서리 12px |
| `arrow` | 선 10px, 머리 34px, accent |

### 모션

| anim | 동작 |
|---|---|
| `rise` (기본) | 0.4초 동안 40px 아래에서 올라오며 투명도 0→1, ease-out(3차) |
| `fade` | 0.3초 동안 투명도 0→1 |
| `pop` | 0.3초 동안 크기 0.6 → 1.06(0.18초) → 1.0, 투명도 0.1초에 1 |
| `none` | 바로 나타남 |
| 퇴장 | `out`이 있으면 끝 0.25초 동안 투명도 1→0 |
| `bar` | 막대가 0.8초 동안 자라고 행마다 0.12초씩 늦게 시작 |
| `arrow` | 0.4초 동안 시작점에서 끝점으로 그려짐 |
| 사진 배경 | `zoom` [시작, 끝] 배율과 `pan` [[시작 x,y],[끝 x,y]](0~1 비율)로 장면 내내 등속 이동. 둘 다 생략하면 고정 크롭 |

## 장면 spec

장면 spec은 `{"theme": {...}, "scenes": [...]}` JSON이다. 예시는 [scripts/example_scenes.json](scripts/example_scenes.json)이고, 이 예시의 배치는 형식을 보여 주는 한 가지 선택일 뿐이다. 새 장면은 위 "배치를 정하는 순서"로 정한다.

| 키 | 위치 | 뜻 |
|---|---|---|
| `id` | 장면 | 장면 ID. 출력 파일 이름 |
| `duration` | 장면 | 초. 내레이션 끝까지 덮는 길이 |
| `version` | 장면 | 있으면 `<id>_<version>.mov`로 출력(예: `v2`) |
| `bg` | 장면 | `{"type": "none"}`이면 투명 오버레이. `color`(`color`), `stripe`, `star`, `photo`(`file`, `crop` [x,y,w,h] 원본 픽셀, `zoom`, `pan`) |
| `captions` | 장면 | 기본 `true`. 자막 영역 검사 여부 |
| `type` | 요소 | `card`, `chip`, `tile`, `stamp`, `dot`, `chapter`, `bar`, `box`, `arrow`, `text` |
| `name` | 요소 | 경고·효과음 큐에 쓰는 이름 |
| `at`, `out` | 요소 | 등장·퇴장 초(장면 시작 기준). `out` 생략 시 장면 끝까지 |
| `anim` | 요소 | `rise`, `fade`, `pop`, `none` |
| `sfx` | 요소 | 효과음 종류 또는 `none`. 생략하면 `stamp`→stamp, `chapter`→whoosh, `bar`→rise, `anim: pop`→pop, 나머지는 없음 |
| `x`, `y` | 요소 | 부품 가운데 좌표 |
| `title`, `body`, `w`, `h`, `fill`, `title_size`, `body_size` | `card` | `body`는 `\n`으로 줄을 나눔 |
| `text`, `size`, `fill`, `ink` | `chip` | |
| `value`, `label`, `size`, `fill` | `tile` | |
| `text`, `size`, `color`, `angle`, `text_size` | `stamp` | |
| `r`, `color` | `dot` | |
| `number`, `title`, `title_size`, `ink` | `chapter` | |
| `items` [{`label`, `value`, `text`, `hi`}], `w`, `row`, `label_w`, `max` | `bar` | `text`는 값 대신 표시할 글자, `hi`는 강조 행 |
| `rect` [x,y,w,h], `color` | `box` | |
| `from` [x,y], `to` [x,y], `color` | `arrow` | |
| `text`, `size`, `weight`(`bold`/`medium`), `color` | `text` | |

## 작업 흐름

### 1. 레퍼런스 분석

레퍼런스 영상을 내려받고 0.5초 간격으로 프레임을 뽑는다.

```bash
mkdir -p "$HOME/Downloads/ref_<영상ID>/frames"
yt-dlp -f "bv*[height<=1080]+ba/b" -o "$HOME/Downloads/ref_<영상ID>/ref.%(ext)s" "<URL>"
ffmpeg -i "$HOME/Downloads/ref_<영상ID>/ref.mp4" -vf fps=2 "$HOME/Downloads/ref_<영상ID>/frames/%05d.jpg"
```

- 프레임을 contact sheet로 묶어 직접 열어 본다. 기록할 것: 배경색, 카드·칩·숫자 타일·도장·그래프의 모양과 hex, 등장 애니메이션 종류와 길이, 장면 길이, 스토리라인(훅 → 챕터 → 정보 → 마무리), 효과음이 들리는 시점.
- 기록은 `ref_<영상ID>/notes.md`에 스타일 규칙(hex, px, 초)으로 남긴다. 레퍼런스의 문구·장면 구성·배치는 옮기지 않는다. 배치는 우리 내레이션을 보고 새로 정한다.
- 분석이 끝나면 `ref.mp4`는 지우고 `notes.md`와 contact sheet만 남긴다. 디스크가 부족했던 적이 있다.
- 산출물(spec, MG, 보고)에 레퍼런스 URL·영상 ID·채널 이름을 넣지 않는다.

### 2. 타임라인 준비

- 마지막 작업 타임라인을 `DuplicateTimeline`으로 복제해 복제본에서만 작업한다. 원본은 고치지 않는다.
- 복제본의 fps를 읽는다(`GetSetting("timelineFrameRate")`). 렌더 `--fps`에 같은 값을 넣는다. 23.976·29.97·59.94는 지원하며 `--fps 23.976`처럼 넘긴다. 렌더 결과 fps와 타임라인 fps가 다르면 배치하지 않고 멈춘다.
- 내레이션 전사(cues json)를 기준으로 장면을 나눈다. 장면 하나 = 내레이션 주제 하나. 장면 표(장면ID, 시작 TC, 끝 TC, 내레이션 요약)를 먼저 만든다.
- 장면마다 기존 사진·영상 컷을 줄일지, 지울지, 오버레이 배경으로 남길지 표에 적는다.

### 3. MG 문구 작성

- MG에는 키워드·숫자만 쓴다. 자막과 같은 문장을 화면에 또 쓰지 않는다. 같은 시각에 MG 문구와 자막이 같은 말을 하면 고친다.
- 문구는 `/akbun-writing:akbun-writing-naturalize` 기준으로 다듬어 AI 말투를 뺀다.
- 확인되지 않은 이야기(투어 해설의 일화)는 "~라는", "전해지는"으로 쓴다. 단정하지 않는다.

### 4. 렌더

먼저 글꼴을 확인한다. Gmarket Sans Bold·Medium이 없으면 렌더하지 않고 설치를 안내한 뒤 멈춘다. 스크립트는 `~/Library/Fonts`, `/Library/Fonts`, `~/.local/share/fonts`, `/usr/share/fonts`에서 찾고, 띄어쓰기가 네모로 그려지는 웹용 woff는 거부한다(종료 코드 2).

배치 확인용 contact sheet(장면마다 시작·중간·끝)를 먼저 만든다.

```bash
uv run -q --python 3.12 scripts/render_mg.py --spec <프로젝트>/mg/scenes.json --fps 24 --out <프로젝트>/mg/out --pic <프로젝트>/photos --stills S01 S02
```

`<프로젝트>/mg/out/stills/contact.jpg` 한 장을 열어 보고 경고와 함께 배치를 고친 뒤 MOV를 렌더한다.

```bash
uv run -q --python 3.12 scripts/render_mg.py --spec <프로젝트>/mg/scenes.json --fps 24 --out <프로젝트>/mg/out --pic <프로젝트>/photos S01 S02
```

- 장면 ID를 비우면 전체 장면을 렌더한다. 같은 이름 MOV가 있으면 건너뛰고, 덮어쓰려면 `--force`.
- 스크립트는 렌더 뒤 ffprobe로 프레임 수(= `round(duration × fps)`)와 ProRes 4444 알파 여부를 확인하고, 다르면 실패한다. `events.json`은 렌더한 장면만 갱신한다.
- 전체 화면 장면(`bg`가 있음)과 오버레이 장면(`bg.type: none`, 사진 위에 칩·화살표)을 구분한다.
- 사진 배경 장면은 `crop`으로 고정 크롭하고 강조 대상을 `box` + `arrow` + `chip`으로 가리킨다. 강조할 대상의 위치가 모호하면 추측하지 말고 사진 캡처를 보여 주며 사용자에게 먼저 확인한다. 오른쪽 담장을 잘못 강조했다가 가운데 마루로 고친 사례가 있다.
- 재렌더로 길이가 바뀌면 `version`을 올려(`v2`) 새 이름으로 렌더하고 다시 import한다. `ReplaceClip`은 캐시 때문에 바뀐 길이가 반영되지 않는다.

### 5. 배치

- 전체 화면 MG는 메인 트랙(V2)에, 오버레이는 그 위 `MG_OVERLAY` 트랙에 놓는다. 트랙이 없으면 새로 만들고, 다른 클립을 덮어쓰지 않는다.
- 오버레이 클립의 Composite/Alpha mode는 Straight로 둔다.
- MG 장면은 해당 내레이션이 끝날 때까지 유지한다. 내레이션보다 먼저 장면이 바뀌면 `duration`을 늘려 다시 렌더한다(3초 늘린 사례가 있다).
- 훅(앞 약 50초)에도 MG 오버레이를 넣는다.
- 놓은 뒤 클립마다 시작 프레임과 트랙별 클립 수를 다시 읽어 장면 표와 대조한다.

### 6. 전환

- 훅 끝: Fusion 전환(예: mJourney Transition 09). duration 24, alignment right로 넣어야 제 길이로 들어간다.
- 장면 사이: Cross Dissolve 0.3초(24fps면 7프레임).
- API: `TimelineItem.AddTransition({"type": <이름>, "category": "simple"|"fusion", "position": "end", "alignment": <정렬>, "duration": <프레임>})`.
- 넣은 뒤 전환 길이를 다시 읽는다. 소스 여유가 없어 1~2프레임만 들어간 전환은 목록으로 보고한다.

### 7. 효과음

- Epidemic Sound MCP의 `SearchSoundEffects` → `DownloadSoundEffect`로 pop·whoosh·stamp·rise를 받아 `<프로젝트>/audio-assets/sfx/`에 저장한다. 연결·검색·라이선스 확인 절차는 [akbun-davinciresolve-caption-template의 효과음 절](../akbun-davinciresolve-caption-template/SKILL.md#효과음)을 따른다.
- `events.json`의 장면별 `frame`(장면 시작 기준) + 그 장면 클립의 타임라인 시작 프레임 위치에 A4 `SFX` 트랙으로 놓는다.
- 내레이션을 가리지 않게 gain을 내린다. 내레이션 구간과 겹치는 효과음은 내레이션보다 작게 들리는지 들어 보고 조절한다.

### 8. 정리

- 새 버전 MG·영상을 만들면 이전 버전 파일은 지운다. 사용자가 용량 부족을 말한 적이 있다.
- 지우기 전에 미디어 풀에서 그 파일을 쓰는 클립이 없는지 확인한다. 쓰는 타임라인이 있으면 지우지 않고 보고한다.

## Resolve 21.1 주의사항

| 상황 | 동작과 대응 |
|---|---|
| `AppendToTimeline`으로 스틸 넣기 | 요청 길이와 무관하게 120프레임으로 들어간다. 긴 스틸은 중첩 타임라인으로 감싸 길이를 맞춘다 |
| `InsertFusionTitleIntoTimeline` | V1 재생헤드에 리플 삽입한다. 타임라인 중간에서 쓰지 않는다 |
| 긴 Text+가 필요함 | Preferences `GeneratorDurationType`을 프레임 단위로 바꿔 넣고, 반드시 원래 값(초, 3초)으로 되돌린 뒤 다시 읽어 확인한다 |
| `DeleteClips` | 현재 타임라인에서만 동작한다. `SetCurrentTimeline` 먼저. 지우기 직전에 다시 읽은 핸들만 쓴다 |
| DRT import로 타임라인 교체 | Resolve가 세그폴트로 종료된다. 시도하지 않는다 |
| 백그라운드 raw 키 입력 | Resolve 단축키로 처리될 수 있다. UI 조작은 AX 기반 `app_*` 도구로 한다 |
| 자막 겹침·이중 표시 | [akbun-davinciresolve-caption-template](../akbun-davinciresolve-caption-template/SKILL.md)의 자막 트랙 배치 규칙을 따른다 |

## 완료 검증

- 장면마다 시작·중간·끝 스틸을 뽑아 한 장의 contact sheet로 확인한다. 렌더 단계는 `--stills`, 배치 후에는 `ExportCurrentFrameAsStill`로 뽑아 붙인다. 볼 것: 글자 잘림, 자막과 겹침, 알파 합성(오버레이 가장자리 검은 테두리), 이어지는 장면의 배치 반복.
- 렌더 출력의 프레임 수 = 장면 `duration` × fps인지 스크립트 출력으로 확인한다.
- 닮음 확인: MG가 레퍼런스 영상의 장면 구성·문구·배치를 그대로 옮기지 않았는지 `notes.md`와 대조한다. 닮은 장면은 부품 배열이나 정렬을 바꾼다.
- 보고에 넣을 것:
  - 타이밍 대조표 `| 장면ID | 시작TC | 끝TC | 내레이션 요약 |`
  - 렌더 스크립트 경고 중 고치지 않은 것과 이유
  - 미삽입 SFX, 1~2프레임만 들어간 전환
  - 출력 형식(ProRes 4444 알파 MOV)과 고른 이유

## 스크립트

| 명령 | 하는 일 |
|---|---|
| `render_mg.py --selftest` | easing·pop 곡선, 등장·퇴장, fps 파싱, 효과음 큐, 자막 영역·겹침 경고, 공백 글리프 검사, 12프레임 MOV 인코딩·ffprobe 확인 |
| `render_mg.py --spec ... --fps ... --out ... [--pic ...] [--stills] [--force] [ID...]` | 장면 렌더 또는 contact sheet. 종료 코드 0 정상, 1 레이아웃 경고 있음, 2 글꼴·인자 오류 |
