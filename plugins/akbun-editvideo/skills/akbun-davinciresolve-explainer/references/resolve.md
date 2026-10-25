# Resolve 타임라인 만들기

`scene.py build`·`check`를 통과한 장면만 Resolve에 넣는다. 노드 구성·표현식·Inspector 컨트롤은 `scene.py comp`가 만든다. 손으로 노드를 짜지 않는다.

## comp가 만드는 것

| 노드 | 이름 | 하는 일 |
|---|---|---|
| Loader | `배경`, `그림_<레이어>` | `background.png`, 레이어 PNG(화면 전체 크기) |
| Transform | `등장_<레이어>` | 팝·자라기 크기 표현식. Pivot = layers.json `pivot`(Center는 건드리지 않는다) |
| MultiMerge | `레이어_합성` | 레이어 순서 = spec 순서. Blend에 등장·페이드 표현식 |
| Transform | `레이어_목록` | 펀치 인(0.2초, 3차 감속) |
| Background | `Timing` | `On{n}`·`At{n}`·`PunchAt`·`PunchZoom` 컨트롤. Template 매크로로 Edit 페이지 Inspector에 공개 |

모션은 shapes.jsonl의 `motion`이 정한다. 팝 = 0.3초 0.6 → 1.04 → 1.0, 자라기 = 0.25초 0.85 → 1.0, 페이드 = 0.25초. 키프레임은 쓰지 않는다.

## 순서

1. 새 타임라인을 만든다(기존 타임라인을 덮어쓰지 않고 새 이름, 예: `<주제> v2`). 타임라인 fps(`GetSetting("timelineFrameRate")`)를 읽어 `comp --fps <값>`으로 넘긴다. 정수가 아니면(23.976, 29.97) 멈추고 사용자에게 알린다. 장면 프레임 수 = round(dur × fps)다. 다른 작업이 열어 둔 프로젝트는 확인 없이 바꾸지 않는다.
2. 자막 srt(타임라인 시작 기준 시각)를 미디어 풀에 가져와 빈 타임라인에 먼저 `AppendToTimeline`으로 넣는다. 클립이 있는 타임라인에 넣으면 마지막 클립 뒤에 붙는다. 자막 트랙을 잠그고 `GetIsTrackLocked("subtitle", 1)`이 True인지 본다.
3. 제너레이터 기본 길이: `SaveUserPreferencesPreset`·`ExportUserPreferencesPreset`으로 현재 값을 저장한다. 내보낸 파일에서 `GeneratorDurationType`을 `DURATION_IN_FRAMES`, `GeneratorDurationFrames`를 장면 프레임 수로 바꾼 임시 프리셋을 `ImportUserPreferencesPreset`·`LoadUserPreferencesPreset`으로 적용한다.
4. 장면마다 플레이헤드를 장면 시작에 두고 `InsertFusionCompositionIntoTimeline()`. 자막 트랙은 잠근 채 둔다(풀려 있으면 자막이 밀린다). 넣은 뒤 자막 시작 프레임이 그대로인지 본다.
5. 저장한 프리셋을 다시 적용하고, 현재 설정을 새 프리셋으로 내보내 `GeneratorDuration*` 값이 작업 전과 같은지 대조한다. 같으면 임시 프리셋을 지운다.
6. 클립마다 `ImportFusionComp(<id>.comp)`. 한글 노드 이름은 comp 텍스트에서 `["배경"]`처럼 대괄호 키여야 한다. 아니면 오류 없이 빈 comp가 된다(21.1.1 실측).
7. 자막 트랙 잠금을 풀고 `GetIsTrackLocked`가 False인지 본다. `SetTrackLock`은 이미 같은 상태면 False를 돌려주므로 반환값으로 판단하지 않는다.
8. 자막 트랙 스타일(Inspector → Track): Font `Pretendard`, Face `Medium`, Size `42`, Color = 팔레트 `SUB`, Stroke Size `0`, Position Y `85`. API로는 못 바꾼다. 화면 조작이 허용되면 Size·Stroke·Y는 값 더블클릭 → cmd+a → 입력 → return, Font·Face 콤보는 클릭해 포커스를 준 뒤 이름 입력 → return. 확대 캡처로 값을 확인한다. 못 하면 값을 사용자에게 넘긴다. 같은 스타일 타임라인을 `DuplicateTimeline`으로 복제해도 스타일이 남는다.
9. 장면 시작마다 파란 마커(장면 이름, 자막 문장). 전환은 하드 컷, 디졸브 없음.

## 확인

- 펀치 인 직전 프레임(`ExportCurrentFrameAsStill`)과 `<id>_still.png`의 자막 위(y < 880) 평균 픽셀 차이가 1 이하. 크면 Pivot·Center를 의심한다. 첫 캡처가 검게 나오면 1초 기다려 다시 뽑는다.
- `등장_<레이어>.Size`를 등장 뒤 10프레임 읽어 최댓값 1.03~1.05, `레이어_목록.Size`가 `PunchAt` + 0.2초에 `PunchZoom`에 닿는지.
- `Timing.At{n}`을 바꾸면 `GetInput("Size", 프레임)` 값이 옮겨지는지 보고 되돌린다.
- 클립·자막·마커 개수와 시작 프레임을 spec과 대조하고, 타임라인 끝 프레임 = 장면 프레임 수 합인지 보고, 프로젝트를 저장한다.
