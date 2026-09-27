---
name: akbun-davinciresolve-workflow
description: 말소리 없는 여행 브이로그를 DaVinci Resolve 21.1에서 처음부터 끝까지 편집하는 workflow 오케스트레이터. 미디어 풀 영상 전부를 촬영 시간순 타임라인으로 만드는 것(akbun-davinciresolve-timeline-chrono)이 항상 첫 단계이고, 그 복제본에서 컷·안정화(davinciresolve-cut-travelflow) → 라벨 노드(EXPOSURE→WB→CST→CONTRAST→SAT) 기본 색보정(logconvert → exposure → whitebalance → contrast → saturation) → 요청된 look skill과 새 LOOK 노드 → 얼굴 모자이크(davinciresolve-face-privacy) → 한글 자막·챕터(davinciresolve-subtitle-travelnote) → 오디오 믹싱·4K 출력(davinciresolve-audio-delivery) 순서로 각 skill의 SKILL.md를 읽어 직접 수행하고 마커 등록표·단계별 완료 조건·검증·작업 로그를 관리한다. "이 프로젝트 편집 계획 세워서 끝까지 해줘", "영상 전부 시간순으로 놓고 색보정까지 해줘", "타임라인 정리부터 렌더까지" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-workflow

말소리 없는 여행 브이로그(iPhone + Insta360 Luna Ultra 촬영)를 DaVinci Resolve에서 편집하는 전체 흐름을 잡는다. 이 skill은 순서·노드 준비·검증·기록을 책임지고, 각 단계의 세부 규칙은 해당 skill의 `SKILL.md`가 원본이다.

하위 skill은 모두 사용자 직접 호출 전용(`disable-model-invocation: true`)이라 Skill 도구로 부를 수 없다. 이 skill은 각 단계에서 해당 `SKILL.md`를 읽고 그 절차와 스크립트를 직접 수행한다. 하위 skill 경로는 이 파일과 같은 `skills/` 아래다.

## 용어

- 타임라인 A: `akbun-davinciresolve-timeline-chrono`가 미디어 풀 영상 전부를 촬영 시간순으로 넣어 만든 타임라인. 이 skill이 손대지 않는 되돌리기 기준점이다
- 원본 타임라인: 사용자가 미리 만들어 둔 타임라인. 있어도 손대지 않는다
- 작업 타임라인(B): A를 복제해 이번 편집을 적용하는 타임라인. 이름은 `<A 이름>_edit_<YYYYMMDD_HHMM>`. 같은 이름이 있으면 분 단위가 다르므로 겹치지 않는다
- 클립 식별자: 클립 번호가 아니라 `파일명 + 작업 타임라인 시작 타임코드`. 클립 번호는 컷이 바뀌면 밀리므로 쓰지 않는다
- 출력 폴더: 사용자가 시작 시 지정한 폴더. 지정이 없으면 미디어가 있는 폴더 옆의 `<프로젝트 이름>_edit/`. Resolve 프로젝트는 데이터베이스에 저장되므로 "프로젝트 폴더"라는 경로는 없다
- 작업 로그: 이번 편집에서 바꾼 모든 것을 기록한 Markdown 파일. `<출력 폴더>/edit-log_<YYYYMMDD_HHMM>.md`. 실행마다 새 파일이고 덮어쓰지 않는다
- 타임라인 마커: 타임라인 자체에 찍는 마커. 클립을 옮겨도 따라가지 않는다. 챕터에만 쓴다
- 클립 마커: 클립(TimelineItem)에 찍는 마커. 클립과 함께 이동한다. 컷·모자이크 표시에 쓴다

## 마커 등록표

Resolve는 한 프레임에 마커 1개만 허용한다. 종류마다 색·대상·프레임 오프셋을 여기서 고정하고 하위 skill은 이 표를 따른다. 오프셋은 클립 마커면 클립 첫 프레임 기준, 타임라인 마커면 해당 지점 기준이다.

| 색 | 이름 | 대상 | 오프셋 | 찍는 skill |
|---|---|---|---|---|
| Blue | `CHAPTER <장소명·행사명 또는 비트 이름>` | 타임라인 마커 | 장면·비트 시작 프레임 | `davinciresolve-subtitle-travelnote`, `davinciresolve-beats-devtalk` |
| Purple | `PRIVACY_MOSAIC <파일명> <창 개수>개` | 클립 마커 | +0 | `davinciresolve-face-privacy` |
| Pink | `PRIVACY_CHECK <파일명> <사유>` | 클립 마커 | +1 | `davinciresolve-face-privacy` |
| Red | `CUT_DONE <사유>` | 클립 마커 | +2 | `davinciresolve-cut-travelflow` |
| Yellow | `CUT_REVIEW <사유>` | 클립 마커 | +3 | `davinciresolve-cut-travelflow` |
| Green | `TALK_REVIEW <사유>` | 클립 마커 | +4 | `davinciresolve-cut-devtalk` |
| Cyan | `GFX <카드 종류> <제목>` | 타임라인 마커 | 카드 시작 프레임 | `davinciresolve-beats-devtalk` |
| Lemon | `EXPOSURE_CHECK <파일명> <사유>` | 클립 마커 | +5 | `akbun-davinciresolve-exposure` |
| Sky | `WB_CHECK <파일명> <사유>` | 클립 마커 | +6 | `akbun-davinciresolve-whitebalance` |

클립 길이가 오프셋보다 짧으면 오프셋을 줄이지 않고 그 클립의 마커를 작업 로그 `확인 필요`에만 적는다.

## 기본 원칙

1. 편집은 항상 촬영 시간순 타임라인 A를 만드는 것으로 시작하고, A를 복제한 작업 타임라인에서만 편집한다.
2. 타임라인 A, 원본 타임라인, 미디어 파일은 수정하지 않는다. 미디어 풀의 파일 이동·이름 변경도 하지 않는다.
3. 클립을 가리킬 때 클립 번호 대신 고유 ID, 파일명, 시작 타임코드를 쓴다.
4. 일괄 작업 전 대표 클립 1개에 먼저 적용하고 결과를 확인한 뒤 나머지에 적용한다. 스크립트가 있는 단계는 `--dry-run` → 사용자 확인 → 적용이 이를 대신한다.
5. 모든 변경을 작업 로그에 기록한다. 기록 없는 변경은 없다.
6. 렌더링 전 컷 → 색상 → 모자이크 → 자막 → 오디오 순서로 검사한다.
7. 되돌릴 수 없는 작업(삭제, 렌더 파일 덮어쓰기, YouTube 업로드)은 실행 전에 무엇을 할지 한 줄로 알리고 사용자 확인을 받는다.

## 실행 환경 확인

시작할 때 무엇으로 Resolve를 조작할 수 있는지 확인하고 작업 로그 `환경` 절에 적는다. 색보정 스크립트는 `uv run --python 3.12 --with pillow python`으로 실행한다. AI Assistant 연동은 [공식 21.1 발표](https://www.blackmagicdesign.com/media/partial/release/20260908-03)를 기준으로 하되, 실제 설치 버전과 노출된 API·UI 기능을 확인한다. 자연어 요청만으로 특정 색 컨트롤·노드 생성 기능이 보장된다고 가정하지 않는다.

| 수단 | 확인 방법 | 가능한 작업 |
|---|---|---|
| 외부 스크립팅 API(Python `DaVinciResolveScript`) | 아래 명령이 프로젝트 이름을 출력 | 타임라인 복제·생성, 클립 목록·메타데이터, 클립·타임라인 마커, CDL·LUT, Fusion Text+ 속성, 렌더 설정·실행 |
| 화면 조작(computer use) | Resolve 창이 보임 | Color 페이지 노드 추가·라벨, Power Window·Stabilizer 파라미터, 내부 Console에 스크립트 입력 |
| API만 있음(headless) | API 성공, 화면 없음 | 컷·마커·CDL·LUT·자막·렌더는 실행하고, 노드 추가·모자이크·안정화 파라미터는 사람이 따라 할 절차서로 작성 |
| 둘 다 없음 | 위 둘 다 실패 | 사람이 따라 할 수 있는 단계별 절차와 체크리스트만 작성 |

외부 스크립팅은 Resolve Studio 전용이고 Preferences → System → General → External scripting using이 `Local`이어야 한다. 무료판은 Resolve 안의 Console(Workspace → Console)에서만 스크립트가 돈다. 아래 명령이 실패하면 순서대로 확인한다. Resolve 실행 여부 → Studio 여부 → External scripting 설정 → 환경변수(`RESOLVE_SCRIPT_API`, `RESOLVE_SCRIPT_LIB`, `PYTHONPATH`). 무료판이면 화면 조작으로 Console에 같은 스크립트를 붙여 넣는다.

```bash
python3 -c "import DaVinciResolveScript as dvr; r = dvr.scriptapp('Resolve'); print(r.GetProjectManager().GetCurrentProject().GetName())"
```

API가 있어도 없는 기능이 있다. 기능별 API 유무·버전 조건·대체 방법은 [`references/agent-api.md`](references/agent-api.md)를 따른다. 대체 방법으로도 판정할 수 없으면 추측하지 않고 마커를 찍고 작업 로그에 `확인 필요`로 남긴다.

## 색관리 방식 선택

색보정 노드를 준비하기 전에 **활성 타임라인**의 Color Science, Timeline Color Space, Output Color Space와 실제 노드 변환을 확인해 작업 경로를 고른다. Project Settings 화면의 Color Management 값만 보지 않는다. 참고 영상에서도 해당 창에 현재 타임라인 설정이 프로젝트 설정을 덮어쓴다는 경고가 표시된다.

| 경로 | 식별 기준 | 실행 |
|---|---|---|
| 현재 저장소의 LUT 자동 경로 | 클립별 Log→Rec.709 LUT 한 개. 별도 DWG/Intermediate 작업·출력 CST 쌍 없음 | 아래 `EXPOSURE → WB → CST → CONTRAST → SAT` 노드와 스크립트를 사용 |
| DWG/Intermediate 노드 경로 | 원본별 Input CST가 DWG/Intermediate로 변환하고, 기술 보정 뒤 Output CST가 있음 | 현재 exposure·whitebalance·contrast 스크립트를 실행하지 않는다. 이중 CST가 단일 LUT 변환으로 오인될 수 있다. Resolve UI 또는 2026.9 AI Assistant로 노드를 확인해 수동 절차를 따른다 |
| Project/Timeline Color Managed 자동 변환 | 색공간 변환이 Project/Timeline 설정에서 자동 적용되고 같은 노드 안에 명시적 CST 쌍이 없음 | 현재 스크립트가 지원하지 않는다. 입력·타임라인·출력 색공간을 먼저 확인하고, 자동 보정 스크립트는 사용하지 않는다 |

참고 영상([I Made Color Grading QUICK and SIMPLE](https://youtu.be/RPDqklqWGSs))의 수동 노드 예시는 **Input CST(1) → HDR Global Exposure(2) → HDR Global WB(3) → Contrast/Pivot(4) → Color Slice 채도(5) → 필요한 선택 보정(6) → Output CST(7) → 창작 LOOK/LUT(8)** 순서다. 노드 연결과 조정 순서는 다르다. 설명자는 4번 Contrast/Pivot을 먼저 조정해 화면을 살핀 뒤 2번 Exposure와 3번 WB로 돌아간다. WB의 X는 따뜻함/차가움, Y는 녹색/마젠타 조정이다. 영상은 Contrast 1.3과 Pivot 0.336을 시작 예로 들지만 고정값으로 복사하지 않는다. `0.336`은 그 Contrast 노드 입력이 DaVinci Intermediate일 때만 맞는 기준이고, 대비·노출량은 샷과 카메라별로 판단한다. 휴대전화·360 카메라는 이미 대비와 채도가 강할 수 있으므로 더 약한 보정이 필요할 수 있다. 인물 없이도 가능하며, WB는 실제로 중립이라고 판단할 수 있는 풍경 표본만 기준으로 삼는다. 여러 카메라를 같은 장면에 썼다면 중립 표본과 Waveform의 흰 점·블랙 여유를 비교해 카메라 간 차이를 확인한다.

이 수동 경로에서 LUT를 쓸 때는 Project Settings의 3D LUT interpolation을 확인한다. [Blackmagic의 Resolve 20 Colorist Guide](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-20-Colorist-Guide.pdf)는 낮은 bit-depth LUT를 고 bit-depth 소스에 적용할 때 생길 수 있는 banding을 줄이는 방법으로 Tetrahedral을 권한다. 기존 프로젝트나 다른 앱에서 만든 LUT의 호환성·기존 결과를 유지해야 하면 설정을 바꾸기 전에 대표 샷을 비교한다. LUT interpolation이나 출력 감마를 앱 기본값으로 저장하지 않는다. 튜토리얼의 Mac `Rec.709 Scene` 출력도 개인 모니터링 선택이므로 YouTube 납품 설정으로 그대로 복사하지 말고 활성 타임라인과 납품 대상을 확인한다.

## 기본 작업 순서

각 단계는 "읽는 skill → 완료 조건"이다. 완료 조건을 못 채우면 다음 단계로 넘어가지 않고 사용자에게 알린다. 1단계(촬영 시간순 타임라인)는 건너뛰지 않는다. 스크립팅 API에는 클립 이동 함수가 없어 순서는 타임라인을 만드는 시점에만 정할 수 있기 때문이다.

| 순서 | 작업 | 읽는 skill | 완료 조건 |
|---|---|---|---|
| 0 | 실행 환경 확인 | 이 skill의 실행 환경 확인 절 | 로그 `환경` 절 기록 |
| 1 | 미디어 풀 영상 전부를 촬영 시간순 타임라인 A로. dry-run 표로 메타데이터(파일명, 촬영 시간, 카메라, 해상도, 프레임레이트, 색공간·감마)를 정리하고 카메라별 시계 오프셋과 타임라인 프레임레이트를 정한 뒤 만든다 | `akbun-davinciresolve-timeline-chrono` | 클립 전부가 표로 정리, V1 순서 검증 일치. 촬영 시간 없음·시계 오프셋 미확인은 `확인 필요` |
| 2 | A를 복제해 작업 타임라인 B | `scripts/workflow.py duplicate` | B가 현재 타임라인, A는 그대로 |
| 3 | 컷 편집과 흔들림 보정 | `davinciresolve-cut-travelflow` | 불량 구간 제거·안정화 결과가 작업 로그에 클립별로 기록 |
| 4 | Log 판정 dry-run으로 클립별 `Log`·`비Log`·`미확인` 확정. `미확인`은 사용자에게 물어 `--profile`로 | `akbun-davinciresolve-logconvert --dry-run` | 판정 표 |
| 5 | 클립마다 라벨 노드 준비 | 아래 "노드 준비" | `scripts/workflow.py nodes`가 빠진 라벨 0개 |
| 6 | LUT 적용 | `akbun-davinciresolve-logconvert` | Log 클립 전부 `적용` |
| 7 | 밝기 | `akbun-davinciresolve-exposure` | 전환 표에서 `확인 필요`·`EXPOSURE_CHECK` 사용자 보고 |
| 8 | 화이트밸런스 | `akbun-davinciresolve-whitebalance` | `WB_CHECK` 사용자 보고 |
| 9 | 대비 | `akbun-davinciresolve-contrast` | 클리핑 없음 |
| 10 | 채도 | `akbun-davinciresolve-saturation` | 대역 미달 없음 |
| 11 | 창작 look | 사용자가 고른 `akbun-davinciresolve-look-*` skill | 기본 보정이 끝난 뒤 해당 style skill을 읽는다. Color 페이지에서 새 Serial 노드를 추가해 `LOOK`으로 라벨하고 이 노드에만 창작 조정을 한다. 룩 LUT를 지정하지 않아도 노드는 새로 만든다. Look을 요청하지 않았으면 적용하지 않는다 |
| 12 | 얼굴과 개인정보 모자이크 | `davinciresolve-face-privacy` | 모자이크 클립마다 `PRIVACY_MOSAIC` 클립 마커와 노드 존재 |
| 13 | Gmarket Sans 한글 자막과 챕터 마커 | `davinciresolve-subtitle-travelnote` | 자막이 안전 영역 안에 있고 챕터 마커가 장소 변경 지점마다 존재 |
| 14 | 현장음·효과음·BGM 믹싱 | `davinciresolve-audio-delivery` (믹싱 절) | 라우드니스·피크 기준 통과, 사용한 곡 목록 기록 |
| 15 | YouTube 챕터 마커 최종 정리 | 이 skill | 마커 이름이 장소명·행사명이고 첫 마커가 `timeline.GetStartFrame()`에 있고 `00:00`부터 시간과 장소명이 표시되며 3개 이상 |
| 16 | 썸네일 후보·YouTube 설정·4K 렌더와 검증 | `davinciresolve-audio-delivery` (YouTube 업로드·출력 절) | 요청된 썸네일·제목·설명·카테고리·공개 상태 적용, 렌더 파일의 해상도·프레임레이트·길이·오디오 스트림이 타임라인과 일치 |

1단계 세부 규칙이다.

- 타임라인 프레임레이트는 클립 수가 가장 많은 프레임레이트로 하고, 사용자가 지정하면 그 값을 쓴다. 혼합(예: iPhone 60fps + Insta360 30fps)이면 정한 값과 이유를 로그에 적는다.
- 카메라별 시계 오프셋은 두 카메라로 같은 장면을 찍은 클립 1쌍(사용자가 알려주거나 추출 프레임이 같은 장소인 쌍)의 촬영 시간 차이로 구하고 `--offset 접두어=초`로 넘긴다. 쌍이 없으면 오프셋 0으로 두고 `확인 필요`로 남긴다. Insta360 촬영 시간이 2000년대 초 같은 기본값이면 시계 미설정으로 보고 파일 생성 시간을 대신 쓴다.
- 사용자가 원본 타임라인의 순서를 의도했다고 하면 A를 만들지 않고 원본 타임라인을 A로 쓴다. 로그에 "사용자 지정 순서"라고 적는다.
- 색공간·감마가 클립마다 다르면(예: iPhone Apple Log, Insta360 I-Log) 4단계의 `akbun-davinciresolve-logconvert`가 Log 판정과 LUT를 맡는다. 판정 표를 로그에 적는다.

4~10단계(색보정)는 한 단계의 `확인 필요`가 다음 단계를 막지 않지만 마지막 보고에 모두 모은다. 되돌리기는 각 skill의 `--reset`이고, 전체 되돌리기는 B를 버리고 A를 다시 복제하는 것이다.

컷이 바뀌면(3단계 이후 재편집 포함) 자막·효과음·전환·챕터 타임라인 마커 위치를 다시 맞춘다. 클립 마커는 클립과 함께 움직이므로 다시 찍지 않는다. 순서를 건너뛰거나 바꾸려면 이유를 작업 로그에 적는다.

## 색보정 노드 순서와 실행 순서

다음 노드 표와 순서는 **현재 저장소의 단일 Log→Rec.709 LUT 자동 경로**에만 적용한다. 노드는 신호 흐름 순서, 실행은 측정이 가능한 순서다. LUT를 먼저 걸어야 그 뒤 스코프값이 Rec.709 기준이 되고, 밝기·화이트밸런스 노드는 LUT **앞**에 있어도 측정은 LUT를 거친 출력으로 한다. DWG/Intermediate 경로는 위 수동 경로를 따른다.

색보정 순서는 look 취향만으로 정하지 않는다. 입력 Log를 어떤 작업 색공간으로 변환하는지에 따라 노출·대비·화이트밸런스의 적절한 위치가 달라질 수 있다. 다른 참고 영상 [Create Your Film Grade](https://youtu.be/1-5mXPEsm3k)는 노출→대비→WB의 조정 순서를 설명하고, [Only 3 Nodes](https://youtu.be/eMxGU2IRoko)는 수동 곡선과 색 관계 탐색을 보여준다. 어느 예시도 모든 소스에 같은 순서·값을 강제하는 근거가 아니다. 수동 곡선으로 대비를 넓히는 것은 검증된 카메라 Log 색공간 변환의 대체가 아니다.

pivot 참고 영상(RPDqklqWGSs)은 DaVinci YRGB, DWG/Intermediate 타임라인, 입력·출력 CST와 중간 보정 노드를 사용한다. 여기의 자동 경로는 카메라별 Log→Rec.709 LUT를 쓰므로 노드 순서를 그대로 섞지 않는다. 두 경로를 연결하는 자동화는 입력·출력 transform과 HDR wheel 처리를 별도로 구현하기 전까지 지원되지 않는다.

| 노드 순서 | 라벨 | skill | 실행 순서(작업 단계) | 위치 |
|---|---|---|---|---|
| 1 | `EXPOSURE` | `akbun-davinciresolve-exposure` | 2 (7단계) | 변환 앞(Log는 Offset) |
| 2 | `WB` | `akbun-davinciresolve-whitebalance` | 3 (8단계) | 변환 앞(Log는 채널 Offset) |
| 3 | `CST` | `akbun-davinciresolve-logconvert` | **1** (6단계) | Log 클립만. LUT를 건다 |
| 4 | `CONTRAST` | `akbun-davinciresolve-contrast` | 4 (9단계) | 변환 뒤 |
| 5 | `SAT` | `akbun-davinciresolve-saturation` | 5 (10단계) | 변환 뒤 |
| 6 (선택) | `LOOK` | 사용자가 고른 look skill | 6 (11단계) | 보정 노드 뒤 새 Serial 노드 |

비Log 클립은 `CST`가 없고 나머지는 같다. 이 순서는 실무 튜토리얼 세 편(Declan Jenkinson "Colour Grading For BEGINNERS", Dunna Did It "My Davinci Resolve Color Grading Process", KC ian "The Highest Level of Color Grading")의 공통점에서 왔다.

| 공통점 | 이 workflow의 대응 |
|---|---|
| 기본 보정과 창작 look을 별도 노드에 둠 | 기본 보정 라벨 5개, 요청 시 창작용 `LOOK` 노드 1개를 추가 |
| 화이트밸런스·노출은 Log 상태(변환 앞)에서, 대비·채도는 변환 뒤에서 | `EXPOSURE`·`WB`는 `CST` 앞, `CONTRAST`·`SAT`은 뒤 |
| 스코프로 판단: Waveform으로 노출·클리핑, Vectorscope·피커로 WB, 대비 피벗은 CONTRAST 입력 공간 기준 | 스틸 기반 스코프값, 중립 픽셀 R/G/B, [로컬 pivot reference](../akbun-davinciresolve-contrast/references/pivot-reference.md), workflow 기본 시작값 `--pivot 0.435` |
| 밤 장면은 어두운 게 맞다("context is important") | 시간대별 목표 대역 |
| 채도는 조금만, 섀도·하이라이트는 채도를 빼서 필름처럼 | 채도 상한 1.25, `--rolloff` |
| 창작 룩은 기본 보정과 분리된 새 노드에서 한다 | 요청된 style skill을 읽고 마지막 `LOOK` 노드에서 조정 |

기술 보정과 creative look을 구분한다. 기술 보정은 소스 변환, 노출, 화이트밸런스, 대비·채도를 장면 의도에 맞게 정돈한다. 따뜻하거나 차가운 분위기, 분할 색조, 필름 질감 같은 스타일 선택은 기본 보정에 섞지 말고 요청된 경우 새 `LOOK` 노드에서 한다. 참고 튜토리얼 중 인물·피부톤 예시가 있더라도 이 사용자의 풍경 중심 영상에서는 인물이나 피부톤을 필수 기준으로 삼지 않는다. 풍경의 중립 물체도 조명·반사색을 받을 수 있으므로 확실한 기준일 때만 화이트밸런스 표본으로 쓴다.

이 skill은 2026년 9월에 공개된 DaVinci Resolve AI Assistant를 포함한 Resolve 작업을 대상으로 한다. AI Assistant가 색관리 설정이나 노드 연결을 제안해도 현재 프로젝트의 실제 입력·출력 색공간과 스코프로 확인한 뒤 적용한다.

## Look 측정

네 look은 [공통 스코프 측정 규약](references/look-scopes.md)을 공유한다. 측정 영역·신호·색 ROI를 고정하고 룩별 허용 폭을 사용한다. 고휘도 픽셀과 채널 클리핑을 구분하며 자동 노출 스크립트의 밝기 근사치를 Look IRE로 대신 쓰지 않는다.

## 노드 준비

스크립팅 API에는 노드 추가·라벨 함수가 없다. Color 페이지 메뉴로 한다. 실측(21.1)으로 확인된 절차다.

1. 작업 타임라인 B를 열고 Color 페이지, `Clips` 스트립을 켠다.
2. 클립마다: API `Timeline.SetCurrentTimecode(클립 중간)`으로 현재 클립을 옮긴다 → 기본 빈 노드가 있어도 `Color → Nodes → Append a Node`로 새 노드를 만들고 `Label Selected Node`로 `EXPOSURE` → 이어서 필요한 라벨마다 `Color → Nodes → Append a Node` → `Label Selected Node` → 라벨 입력 → Return.
3. 기존 그레이드(LUT·CST·휠)가 있는 클립은 그 노드를 두고 뒤에 붙인다. 이미 기술 변환 LUT가 있으면 입력·출력 공간을 확인하고 보존한다. 그 클립은 logconvert 재적용을 건너뛰며, `EXPOSURE`·`WB`는 `Add Serial Before Current`로 변환 앞에 새로 넣는다. 기존 변환의 검사 라벨 정리 외에 기존 그레이드 값을 덮어쓰지 않는다. 같은 용도의 새 노드를 뒤와 앞에 중복 생성하지 않는다.
4. `scripts/workflow.py nodes`로 클립별 필요 라벨·현재 라벨·빠진 라벨·순서를 표로 확인한다. 빠진 것이 0개일 때 6단계로 간다.

주의(실측): 클립 전체 선택 뒤 Alt+S·메뉴는 현재 클립 하나에만 적용된다. `Add Serial Node`는 선택된 노드 뒤에 끼워 마지막이 아닐 수 있으므로 `Append a Node`를 쓴다. 백그라운드 키 입력(Alt+S)은 전달되지 않으므로 메뉴로 한다. `Next Node`·`Previous Node`로 선택 노드를 옮길 수 있고, 라벨은 선택된 노드에 붙는다. `Label Selected Node` 뒤 Cmd+A → Backspace → Return으로 라벨을 지운다.

화면 조작 권한이 없으면 위 절차를 사용자에게 요청하고 `workflow.py nodes`로만 확인한다.

## 명령

작업 타임라인 복제다.

```bash
python3 scripts/workflow.py duplicate --src "<타임라인 A>" --name "<A>_edit_<YYYYMMDD_HHMM>"
```

노드 준비 상태 점검이다. 빠진 라벨이 있으면 종료 코드 1이다.

```bash
python3 scripts/workflow.py nodes --timeline "<작업 타임라인>" --profile "VID_=Insta360 I-Log" --out "<출력 폴더>"
```

`ORDER`·`required()` 같은 라벨 규칙을 고치면 `python3 scripts/workflow.py selftest`로 확인한다.

각 단계 명령은 해당 skill의 `SKILL.md`에 있다. `--out`·`--timeline`·`--sunrise`·`--sunset`은 모든 단계에 같은 값을 준다.

## 검증

렌더 전 아래를 순서대로 확인하고 결과를 작업 로그의 `검증` 절에 표로 남긴다. 하나라도 실패면 렌더하지 않는다.

| 항목 | 확인 방법 | 통과 기준 |
|---|---|---|
| 타임라인 해상도·프레임레이트 | 타임라인 설정 | 3840×2160, 1단계에서 정한 프레임레이트 |
| 오프라인 미디어·검은 프레임 | 미디어 풀 오프라인 표시, 타임라인 빈 구간 | 0개 |
| 음량 급변·피크 | 라우드니스 미터, 클립 경계 전후 비교 | True Peak -1 dBTP 이하, 같은 장면 안 인접 클립 차이 6 dB 이내. 장면 전환(장소·행사 변경)은 예외로 두고 로그에 적는다 |
| 밝기·색 급변 | 인접 컷 tail→head 스코프값·중립 R/G/B 비교 | `akbun-davinciresolve-exposure`의 전환 피로 기준, `akbun-davinciresolve-whitebalance`의 채널 차이 20 |
| 얼굴 모자이크 누락 | `PRIVACY_MOSAIC` 클립 마커 목록과 얼굴 탐지 결과 대조 | 얼굴이 식별되는 클립 전부에 마커·노드 존재. 탐지 실패 클립은 `PRIVACY_CHECK` 존재 |
| 자막 화면 밖 잘림 | 자막 클립마다 시작·끝 프레임 스틸 | 텍스트 전체가 안전 영역 안 |
| 렌더 파일 재생·길이 | `ffprobe` 또는 Resolve 미디어 풀 재가져오기 | 재생되고 길이가 타임라인과 1프레임 이내 |

## 작업 로그 형식

`<출력 폴더>/edit-log_<YYYYMMDD_HHMM>.md`에 아래 구조로 쓴다. 각 skill과 스크립트가 자기 절을 채우고, 스크립트가 낸 `.md`는 그 자리에 이어 붙인다. 절 번호는 스크립트가 내는 제목을 그대로 둔다.

```markdown
# 편집 작업 로그 <YYYYMMDD_HHMM>

## 환경
- 조작 수단: 외부 API / 화면 조작 / API만 / 절차만
- Resolve 에디션·버전:
- 타임라인 A: <이름>
- 작업 타임라인: <이름>
- 색관리 경로: 단일 Log→Rec.709 LUT 자동 / DWG·Intermediate 수동 / Color Managed 미지원
- 활성 타임라인 입력·출력 변환과 LUT interpolation: <설정>
- 타임라인 프레임레이트: <값>(이유)
- 카메라 시계 오프셋: <카메라> <초>(근거)

## 2. 작업 타임라인(촬영 시간순)      ← timeline-chrono(클립 목록 표 포함)
## 3. 컷·안정화                       ← cut-travelflow
## 노드 준비 상태                     ← workflow.py nodes
## 5. LUT(Log 변환)                   ← logconvert
## 4. 노출(밝기)                      ← exposure
## 4b. 화이트밸런스                   ← whitebalance
## 4c. 대비                           ← contrast
## 4d. 채도                           ← saturation
## LOOK

사용자가 look을 요청한 경우 선택한 skill 이름과 새 `LOOK` Serial 노드에서 조정한 목적을 기록한다. 요청한 룩 노드가 없거나 기존 노드에 창작 조정이 섞여 있으면 다음 단계로 넘어가지 않는다. 사용자가 요청하지 않았다면 `LOOK 없음`으로 남긴다.
## 모자이크                           ← face-privacy
## 자막·챕터                          ← subtitle-travelnote
## 오디오                             ← audio-delivery
## 검증
## 확인 필요                          ← 각 표의 확인 필요 행과 마커(EXPOSURE_CHECK, WB_CHECK, PRIVACY_CHECK, CUT_REVIEW) 모음
```

## 하지 않는 것

- 촬영 시간순 타임라인 A를 건너뛰고 원본 타임라인에서 바로 편집(사용자가 원본 순서를 의도한 경우만 예외)
- 타임라인 A·원본 타임라인·미디어 파일 수정
- 클립 번호로 클립 지정
- 라벨 없는 노드·기존 그레이드 노드에 쓰기
- `미확인` 클립에 LUT 적용
- 사용자 확인 없이 dry-run 건너뛰기
- 사용자 확인 없는 삭제, 렌더 파일 덮어쓰기, YouTube 업로드(업로드 시 기본 공개 상태는 비공개)
- 스코프·얼굴 탐지 결과 없이 "문제없음" 판정. 판정 근거가 없으면 `확인 필요`로 남긴다
- 사용자가 지정하지 않은 LUT·스타일 적용
- 마커 등록표 밖의 색·이름·오프셋 사용
