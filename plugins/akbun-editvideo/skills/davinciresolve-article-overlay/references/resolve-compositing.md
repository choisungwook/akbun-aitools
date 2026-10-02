# Resolve 기사 발췌 합성

현재 연결의 Resolve API 문서와 Fusion 입력 목록을 확인한 뒤 실행한다. 아래 노드 이름은 구현 방향이며 설치 버전에 없는 입력·속성을 추측해 호출하지 않는다.

## 편집 가능한 노드 구성

타임라인 해상도의 투명 캔버스 위에 다음 순서로 합성한다. 배경 본편은 아래 비디오 트랙에서 계속 재생한다.

1. `Background`와 `Rectangle` 마스크로 종이 패널을 만든다. 프레임 전체의 alpha를 1로 채우지 않는다.
2. 원문 이미지는 미디어 풀에서 읽는 `MediaIn` 또는 영구 경로의 `Loader`로 불러와 필요한 제목·본문을 `Crop`/`Transform`으로 배치한다. 편집 가능한 재조판은 `TextPlus`를 제목·본문·출처로 나누고 원문과 대조한다. 캡처 원문의 글자는 이미지의 일부라 직접 수정할 수 없다는 점을 인계한다.
3. 형광 강조는 Text+ 뒤의 색 띠, 밑줄은 가는 선, 원 표시는 속이 빈 타원/곡선으로 만든다. 기본 도형·마스크로 정적 표시를 먼저 검증한다.
4. `Merge`로 합친 전체 패널을 공통 `Transform`에 연결하고 `MediaOut`으로 보낸다. 강조는 패널과 같은 변환 아래에 두고 소스 크롭·scale이 확정된 다음 위치를 잡는다.
5. 등장/퇴장은 공통 Transform의 위치와 합성 Blend에 키프레임을 준다. write-on은 마스크의 좌→우 reveal 또는 Paint/Polyline의 실제 노출된 쓰기 제어를 사용한다. 원을 그리는 애니메이션은 열린 곡선의 진행 길이를 제어하며, 단순 좌→우 reveal을 원의 둘레를 따라 그리는 효과라고 보고하지 않는다.

`GetInputList()`와 입력 속성으로 노드의 정확한 ID를 확인한다. UI에 보이는 라벨을 그대로 Python 속성명으로 추측하지 않는다. `BezierSpline`/키프레임 방식도 현재 Fusion API 문서를 읽고 저장 후 대표 프레임을 확인한다. 키프레임 API가 없으면 Fusion UI로 설정하고, UI도 불가하면 정적 강조까지 만든 뒤 미적용 애니메이션과 필요한 프레임을 알린다.

글자·강조 좌표는 캡처 픽셀의 좌상단 기준인지 Fusion의 정규화된 좌하단 기준인지 명시한다. 크롭·scale·이동을 반영한 뒤 변환한다. `x/W`, `1-y/H`는 같은 캔버스 위 점 좌표의 변환일 뿐이며 크롭 전 문서 좌표에 그대로 쓰면 안 된다. 다른 화면비나 줄바꿈에 이전 좌표를 재사용하지 않는다.

## 본편을 밀지 않는 배치

먼저 작업본의 클립 ID·미디어 경로·트랙·시작/끝·길이·타임라인 마커를 읽는다. `ARTICLE_OVERLAY` 역할의 실제 트랙을 찾고 대상 구간이 비어 있는지 확인한다.

- 타임라인 중간에서 `InsertFusionTitleIntoTimeline`이나 `InsertFusionCompositionIntoTimeline`을 곧바로 호출하지 않는다. 전자는 기존 Text+ 스킬의 21.1 실측에서 V1과 다른 트랙·마커를 밀었다. 후자도 트랙/구간을 지정하는 인자가 없으므로 안전한 오버레이 배치라고 가정하지 않는다.
- **원문 이미지가 있을 때:** 영구 경로의 이미지를 `MediaPool.ImportMedia`로 가져와 `AppendToTimeline`의 `mediaType: 1`, `trackIndex`, `recordFrame`, source in/out으로 지정 트랙에 놓는다. 스틸의 요청 길이가 실제로 적용됐는지 읽고 필요하면 Edit UI에서 ripple 없이 조절한다. 해당 클립의 `GetFusionCompByIndex` 또는 확인된 `AddFusionComp`로 구성하고 원문 이미지를 MediaIn으로 쓴다.
- **텍스트만 있을 때:** 기존 Fusion 템플릿을 확인한다. 없으면 타임라인 해상도의 완전 투명 PNG를 영구 `article-assets/`에 만들고 위 이미지 배치 경로로 가져온 뒤 해당 클립의 Fusion에 패널·Text+를 만든다. PNG는 빈 캔버스일 뿐 글자는 Text+로 남긴다. alpha와 실제 클립 길이·컴포지션 생성은 대표 한 개로 확인한다.
- 이미지 기반 컴포지션 경로가 지원되지 않으면 별도 연습 타임라인에서 UI로 Fusion Composition/Title 템플릿을 만들어 미디어 풀에 보관한다. 미디어 풀 항목으로 확보할 수 없으면 작업본의 빈 상위 트랙에 UI로 overwrite 배치·트림한다. 템플릿 준비의 기존 예는 [Text+ 배치](../../davinciresolve-subtitle-travelnote/SKILL.md#text-배치)에 있다. 이 링크의 `textplus.py place`는 SUBTITLE용이며 기사 트랙에 그대로 실행하지 않는다. 자막 글꼴·크기 규칙도 기사에 적용하지 않는다.
- 위 경로를 검증할 수 없고 UI도 불가하면 시각 배치를 중단하고 화면 구성·미적용 항목·SFX 큐시트를 채팅에 남긴다. Resolve 연결 자체가 제작 기능의 지원을 보장하지 않는다.
- 기존 템플릿이 있으면 내용을 수정하기 전에 작업 클립의 컴포지션을 사용한다. 공유 템플릿이나 다른 클립의 컴포지션을 변경하지 않는다.
- API 반환 성공만으로 완료하지 않는다. 실제 destination 트랙·시작·길이를 다시 읽고 다른 클립·마커가 밀리지 않았는지 대조한다. 반복 실행은 자신의 클립만 갱신한다. 지울 필요가 있으면 직전에 다시 읽은 핸들을 사용하고 ripple 삭제를 하지 않는다.

## 프레임과 효과음 배치

큐시트는 시작 포함·끝 제외 구간 `[in, out)`으로 기록한다. Resolve API가 source `endFrame`을 포함하는지 현재 문서/짧은 배치 결과로 확인하고 그 경계에서만 변환한다.

- 화면 이벤트의 경과 초 `t`는 `offset = round(t × 실제 fps)`로 프레임에 맞춘다. `recordFrame = GetStartFrame() + offset`이고 타임라인 마커의 `frameId`는 offset이다.
- 29.97/59.94의 실제 프레임레이트와 nominal TC·drop-frame 표시를 구분한다. 초를 단순히 30/60으로 곱해 TC 문자열을 만들지 않는다. API/UI가 표시한 TC와 프레임 위치를 대조한다.
- 초를 프레임으로 맞춘 뒤의 실제 경과 시간과 길이를 큐시트에 적는다. 예를 들어 30000/1001 fps의 180프레임은 6.006초이며 정확히 6.000초라고 보고하지 않는다.
- Fusion 키프레임은 컴포지션의 실제 Global/Render 시작과 클립 source in을 확인해 클립 로컬 이벤트를 매핑한다. Fusion 프레임이 항상 0부터 시작하거나 타임라인 절대 프레임과 같다고 가정하지 않는다.
- 오디오 파일의 sample rate를 영상 fps로 쓰지 않는다. import한 오디오의 source trim 단위는 현재 Resolve 문서를 확인한다. 자른 음원의 들리는 어택이 목표 프레임보다 0.08초 뒤라면 클립 시작을 그만큼 앞당기는 식으로 실제 소리의 지점을 맞춘다. 앞당길 공간이 없으면 source in·동작 타이밍을 조절한다.
- SFX는 `AppendToTimeline`에 `mediaType: 2`, 빈 오디오 `trackIndex`, 절대 `recordFrame`을 지정하고 channel mapping·라우팅·gain을 확인한다. 미리듣기만 가능하거나 import/배치 확인이 안 되면 `미삽입` 큐시트로 인계한다.

## 캡처와 검증

`SetCurrentTimecode` 후 현재 TC가 목표인지 확인하고 Viewer 갱신 뒤 `Project.ExportCurrentFrameAsStill`로 `/tmp`에 캡처한다. API export가 불가하면 Resolve Viewer 화면을 캡처한다. 원본 ffmpeg 캡처에는 Resolve 합성 결과가 없으므로 대체 검증으로 쓰지 않는다.

대표 발췌에서 등장 전/정착/강조 완성/퇴장 뒤를 확인하고, 움직임 중간 프레임도 본다. 패널 밖 본편의 투명 합성·문구 정확성·읽는 시간·획 정렬·오디오 싱크를 확인한다. 텍스트·PNG·음원 경로가 유지되는지 확인하고 프로젝트를 저장한다. 기존 클립/마커/길이가 바뀌었으면 그 작업본을 완료본으로 전달하지 않는다.
