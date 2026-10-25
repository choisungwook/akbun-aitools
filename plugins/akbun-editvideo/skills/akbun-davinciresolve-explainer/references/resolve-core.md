# Explainer 스타일 공통 Resolve 구현

explainer 스타일 스킬(dark-diagram, ember-grid, scribble-black, slate-marker, live-ink)이 장면 클립 구조의 기준으로 쓰는 문서다. 이 스킬(akbun-davinciresolve-explainer) 자체는 `scene.py comp`가 같은 구조를 만들므로 [resolve.md](resolve.md)를 따른다.

- 타임라인: 1920×1080 새 타임라인 하나. 기존 타임라인을 덮어쓰지 않고 새 이름(예: `<주제> v2`)으로 만든다. fps는 사용자 지정값 또는 대상 프로젝트 값, 기준이 없으면 24fps. 기존 프로젝트의 전역 설정을 덮어쓰지 않는다.
- 마지막 프레임 스틸(`ExportCurrentFrameAsStill`)을 장면마다 뽑아 한 장으로 붙여 한 번에 본다. API 성공 반환만으로 화면 적용을 완료 처리하지 않는다.

## 사실 확인

입력을 읽고 기술 내용을 사실 확인한다. 제공 자료와 공식 문서 등 확인한 출처를 기록한다. 틀린 내용은 고치고, 무엇을 고쳤는지 목록으로 남긴다. 확인할 수 없는 숫자나 설정값은 추측해서 화면에 넣지 말고 사용자에게 묻는다.

## 민감 정보 규칙

- 회사명, 고객사명, 협력사명, 특정 산업명, 사람 이름, 내부 시스템 이름, 실제 공인 IP, 계정 ID는 화면·내레이션·파일명·노드 이름 어디에도 쓰지 않는다.
- "파트너사", "고객사"처럼 관계를 드러내는 말도 쓰지 않는다. 필요하면 "외부 네트워크", "다른 IP 대역", "Site A / Site B", "조직 내부 / 외부"처럼 기술적으로만 표현한다.
- 예시 IP는 RFC 5737 문서용 대역(192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24)과 사설 대역을 쓴다.
- 경험담 투의 내레이션은 괜찮다. 다만 조직이나 규제 주체를 특정하지 않는다(예: "규제 등의 이유로").

## 내레이션 규칙

- 존댓말, 1인칭 경험담 또는 팟캐스트 말투. 문장은 짧게.
- 장면 길이(초) = ceil(음절 수 / 5.5 + 2.0). 최소 5초. 음절은 한글·숫자 1자 = 1음절, 영문 단어 = 모음 글자 묶음 수(최소 1)이고, 식별자는 `.`·`_`·`-`로 나눠 단어마다 센다. 영문을 글자 수로 세면 `spring.datasource.hikari.maximum-pool-size` 같은 식별자가 많은 장면이 실제 낭독의 몇 배로 길어진다.
- 질문 장면은 한두 문장(5~9초).
- 요소 등장 시점은 내레이션에서 그 요소를 말하는 위치(앞 음절 수 / 5.5)로 잡는다. 장면 길이와 같은 세기 함수를 쓴다.
- 전체 길이는 사용자가 요청한 범위(예: 5~15분) 안으로 맞춘다.

## Resolve 구현

DaVinci Resolve 스크립팅 API(Python)를 쓴다. 파일 읽기·쓰기가 필요한 단계는 파일 접근이 되는 실행 환경을 쓴다.

### 장면 클립 = Fusion 타이틀 + Template 매크로

- `timeline.InsertFusionTitleIntoTimeline("Text+")`로 타이틀 클립을 넣는다. 삽입된 comp의 실제 노드 구조를 읽고, Edit 페이지 Inspector가 `Template` 매크로의 컨트롤을 표시하도록 구성한다.
- 장면을 API로 빌드한 뒤 comp를 내보내고(`ExportFusionComp`), 텍스트를 고쳐서 모든 노드를 `Template = MacroOperator { Inputs = ordered() { InstanceInput ... }, Outputs = { MainOutput1 = InstanceOutput {...} }, Tools = ordered() {...} }`로 감싼 뒤 `ImportFusionComp`로 다시 넣는다.
- 바깥 MediaOut 연결은 매크로 이름이 아니라 매크로 안쪽 최종 노드를 가리켜야 한다(`SourceOp = "레이어_목록", Source = "Output"`).
- 매크로 안 생성기 노드의 `GlobalIn`/`GlobalOut` 입력은 지운다. 남기면 클립 길이를 바꿀 때 잘린다.
- 스크립트로 수정한 클립 comp를 내보내기 → 가져오기 한 뒤 Edit 출력에서 확인한다. 화면이 안 바뀌면 이 단계와 클립·트랙 활성 상태, 출력 연결을 확인한다.
- `.setting` 템플릿을 Effects 라이브러리 폴더에 넣는 방식은 Resolve를 재시작해야 인식되므로 쓰지 않는다.

### 클립 길이 맞추기

- 타이틀·Fusion Composition 클립은 환경설정의 "Standard generator duration" 길이로만 삽입된다.
- 현재 환경설정을 프리셋으로 저장해 파일로 내보내고, `GeneratorDurationType=DURATION_IN_FRAMES`와 `GeneratorDurationFrames=<프레임>`만 바꾼 임시 프리셋(초 단위보다 프레임이 정확하다)을 가져와 적용한 뒤 삽입하고, 끝나면 원래 프리셋을 다시 적용한다. 변경 전 원래 값과 복원용 프리셋 경로를 파일로 기록하고 고유한 임시 이름을 쓴다. API: `SaveUserPreferencesPreset`, `ExportUserPreferencesPreset`, `ImportUserPreferencesPreset`, `LoadUserPreferencesPreset`, `DeleteUserPreferencesPreset`.
- 복원은 finally에서 하되, 스크립트가 시간 제한으로 강제 종료되면 finally가 돌지 않는다. 종료 후 원래 값으로 돌아왔는지 꼭 확인한다. 복원을 확인한 뒤 자신이 만든 임시 프리셋만 삭제한다. 복원이 안 되면 다음 삽입을 중단하고 복원 경로·절차를 전달한다.
- 삽입은 타임라인 끝(마지막 클립 바로 뒤)에서만 안정적으로 성공한다. 장면을 순서대로 끝에 붙인다.
- 장면 내용만 바꿀 때는 클립을 다시 넣지 말고 같은 클립의 comp를 다시 빌드한다. 길이가 바뀌면 그 장면 뒤를 다시 배치해야 한다.

### 장면 내부 구조 (Fusion 페이지용, 입문자 기준)

- 배경: Background 노드 하나(색은 스타일 스킬이 정한다).
- 화면의 모든 요소는 MultiMerge 노드 하나(`레이어_목록`)의 레이어로 쌓는다. `ConnectInput("Layer{n}.Foreground", node)`로 연결하면 다음 슬롯이 자동으로 생기고, `LayerName{n}`에 레이어 이름을 넣는다. 번호가 클수록 위에 그려진다.
- 노드 이름은 한글로 종류를 붙인다: 글자_, 박스_, 영역_, 화살표_, 표시_(✕), 단계*_원, 범위_, 표_, 채움_, 선_. 공백은 자동으로 빠지니 밑줄을 쓴다. 표현식에서 참조할 노드만 ASCII 이름(`Timing`)을 쓴다.
- 도형 하나 = 도형 노드(들) → sMerge → sRender → MultiMerge 레이어 1개.
- API로 만든 노드는 위치가 저장되지 않는다. 내보낸 .comp 텍스트에 `ViewInfo = OperatorInfo { Pos = { x, y } }`를 써 넣는다(격자 1칸 = x 110, y 33). 구역 묶음은 Underlay(`ViewInfo = UnderlayInfo { Pos = 좌상단, Size = { w, h } }`)로, 편집 안내는 Note(`StickyNoteInfo`)로 남긴다.
- 마지막 툴 블록은 쉼표 없이 `}`로 끝난다. 텍스트를 고칠 때 주의한다.

### Edit 페이지 Inspector 설계

- 그룹 = 화면에 함께 나타나는 요소 묶음(빌드 단계). 순서는 화면에 나오는 순서다.
- 그룹마다 컨트롤:
  - 접기 라벨: LabelControl, `LBLC_DropDownButton = true`, `LBLC_NumInputs` = 그룹에 속한 컨트롤 수, `INP_External = false`
  - 글자마다 "보이기 · (글자)" 체크박스: CheckboxControl, 기본 1
  - 글자 칸: Text+의 `StyledText`를 공개. Text+ 블록에 `UserControls = { StyledText = { INPID_InputControl = "TextEditControl", LINKID_DataType = "Text", TEC_Lines = 2, LINKS_Name = "글자: …" } }`를 덮어써서 2줄 높이와 이름표를 준다
  - "등장 시점(초)": SliderControl, 기본값 = 그 단계 시각
  - "위치 이동": OffsetControl(Point), 기본 0.5, 0.5
- 시점·위치·체크박스 값은 `Timing`이라는 보조 노드(화면에 연결하지 않는 Background)의 UserControls에 두고, 매크로 InstanceInput으로 공개한다. UserControls 정의와 기본값 Input은 .comp 텍스트에 직접 써 넣는다.
- 모든 애니메이션은 키프레임 대신 표현식으로 `Timing`을 참조한다.
  - 시각 기준: `comp.RenderStart + Timing.At{k} * fps`. 이렇게 해야 Edit 페이지에서 클립 앞을 잘라도 모션이 새 시작점부터 다시 나온다(실행 시 시험 클립으로 확인할 것). 끝을 줄이면 늦은 단계가 잘리고, 끝은 원래 길이보다 길게 늘려도 마지막 화면이 유지된다(실행 시 시험 클립으로 확인할 것).
  - 레이어 페이드: `Layer{n}.Blend = Timing.On{n} * min(1, max(0, (time - 시각) / (0.4*fps)))` (체크박스는 글자 레이어에만 곱한다)
  - 레이어 위치: `Layer{n}.Center = Timing.Pos{k}`
  - 실선 화살표 그리기: 선 sRectangle의 Width와 Translate.X/Y를 같은 진행률 p(0~1, 0.5초)로 시작점에서 늘린다. 화살촉 Opacity = `iif(time < 끝 시각, 0, 1)`
  - 점선 화살표 그리기: sDuplicate의 `Copies = floor((개수-1) * p)`
  - 강조 색 전환: 도형 Red/Green/Blue = `iif(time < 시각, 원래값, 강조값)`
- `AddModifier(…, "BezierSpline")`는 0프레임에 값 1인 키를 몰래 만든다. 키프레임을 꼭 써야 하면 `SetKeyFrames({...}, True)`로 0프레임 값까지 지정한다.

### 좌표와 단위

- Fusion 도형(sRectangle, sEllipse, sNGon) 좌표: 원점은 화면 가운데, y는 위쪽, 단위는 화면 가로 기준. X = (px - 960) / 1920, Y = (540 - py) / 1920, 크기 = px / 1920. BorderWidth도 같은 단위.
- 삼각형: sNGon Sides=3, Angle 0이면 오른쪽을 향한다. 20×20 화살촉은 Width 24px 정도.
- Text+: Size = px / 1920. HorizontalLeftCenterRight(-1/0/1), VerticalTopCenterBottom(-1 위 / 0 가운데). 위 정렬이면 Center.y가 글자 윗선에 맞는다.
- 마스크로 그릴 경우 EllipseMask의 Height는 화면 가로 기준, RectangleMask의 Height는 세로 기준이다.

### 성능과 안정성

- 입력 객체는 `tool["Layer3.Blend"]`처럼 직접 꺼낸다. MultiMerge는 입력이 수백 개이므로 매번 `GetInputList()`를 순회하지 않는다. 최초 ID 확인 뒤 직접 접근한다.
- 스크립트 한 번의 실행 시간 제한에 맞춰 장면을 나눠서 빌드한다. Resolve MCP `run_script`는 샌드박스라 `import os`·`open`을 못 쓰고 호출당 약 10초에서 끊긴다. 파일 읽기·쓰기는 Bash에서 하고 Resolve 호출은 4~5개씩 나눈다.
- 화면이 잠겼거나 대화상자가 떠 있으면 `OpenPage`·`SetCurrentTimecode`·`ImportFusionComp`가 None/False를 돌려준다. 이때는 사용자에게 화면을 깨우고 대화상자를 닫아 달라고 한다.
- `GetItemListInTrack`은 트랜지션도 돌려준다. `GetType() != "transition"`으로 거른다.
- 장면 배치 기준은 첫 클립의 `GetStart()`로 기록한다. 타임라인 시작 프레임과 첫 클립 시작은 구분한다. `GetStartFrame()`은 트랙을 비우고 다시 배치하는 중에 값이 달라질 수 있으므로 배치 전후 실제 값을 대조한다.
- 크로스 디졸브: 마지막 장면을 제외한 각 클립 끝에 `AddTransition({"type": "Cross Dissolve", "category": "simple", "position": "end", "alignment": "center", "duration": transition_frames})`.
- 마커: 첫 클립 시작이 타임라인 시작과 일치하는지 확인하고 `timeline.AddMarker(타임라인 시작 기준 프레임 오프셋, "Blue", 장면 이름, 내레이션, 1)`로 추가한다. 다르면 그 차이를 포함해 보정한다. 실제 장면 시작·마커 위치를 다시 읽는다.
