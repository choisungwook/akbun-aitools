# 영상 편집 스킬 사용자 매뉴얼

이 문서는 `akbun-editvideo` 플러그인의 스킬을 어떤 상황에 고르고, 각 스킬이 어떤 문제를 해결하는지 안내한다. 실제 작업 지침과 세부 조건은 연결된 `SKILL.md`가 기준이다.

영상·Resolve 용어는 [용어사전](terms_editvideo.md)을 참고한다.

스킬은 이름을 직접 불러 사용할 수 있다. 예: `$akbun-vlog-shotsketch`. 전체 작업을 맡는 workflow 스킬은 필요한 하위 스킬 문서를 읽어 순서대로 진행하고, 각 하위 스킬은 원하는 단계만 따로 요청할 때 쓴다.

## 스킬 이름 변경

다음 두 스킬은 새 호출명으로 사용한다.

| 이전 이름 | 새 호출명 |
|---|---|
| `davinciresolve-narration-cleanup` | `$akbun-davinciresolve-narration-cleanup` |
| `explainer-dark-diagram` | `$akbun-davinciresolve-explainer-dark-diagram` |

## 어떤 흐름을 고를까

| 상황 | 시작할 스킬 | 해결하는 문제와 동작 |
|---|---|---|
| 특정 샷의 카메라 구도와 빛을 정하고 싶음 | [akbun-vlog-shotsketch](../plugins/akbun-editvideo/skills/akbun-vlog-shotsketch/SKILL.md) | 이야기 비트에 필요한 한 샷의 프레임, 카메라 위치, 동작, 조명과 얼굴 비노출 확인을 그림과 표로 만든다. |
| 말소리 없는 여행 영상 전체를 편집하고 싶음 | [akbun-davinciresolve-workflow](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/SKILL.md) | 원본 타임라인을 보존하면서 촬영 시간순 타임라인부터 컷, 색보정, 요청된 Look, 개인정보 보호, 자막, 출력까지 단계별로 진행한다. |
| 어두운 다이어그램 스타일로 설명 영상을 만들고 녹음에 맞추고 싶음 | [akbun-davinciresolve-explainer-dark-diagram](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-dark-diagram/SKILL.md) | 대본을 읽기 시간 기준으로 장면화하고 자막 트랙을 보며 녹음하게 한다. 녹음 후 테이크를 내용으로 장면에 배정해 장면 길이·등장 시점·자막을 실제 목소리에 맞춘다. |
| 보드에 손으로 써 내려가며 수식·단계·질문과 답을 설명하는 영상을 Resolve에서 고치며 만들고 싶음 | [akbun-davinciresolve-explainer-scribble-black](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-scribble-black/SKILL.md) | akbun-draw-scribble-black의 색·선·도형·글씨 규칙을 그대로 쓰고, 글씨는 Text+ 써지기로, 도형 획은 투명 레이어 PNG를 긋는 방향으로 드러낸다. 한 번에 한 획만 그려지고, 첫 시점을 옮기면 뒤 획이 같이 밀린다. |
| 검정 배경 카드와 손글씨 캡션으로 요청·메모리 같은 시스템 동작을 설명하는 영상을 Resolve에서 고치며 만들고 싶음 | [akbun-davinciresolve-explainer-slate-marker](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-slate-marker/SKILL.md) | akbun-draw-slate-marker의 색·글꼴·부품 표를 그대로 쓰고, 카드·칩·선을 Fusion 도형으로 그려 Inspector에서 글자·등장 시점을 고친다. 배치는 장면마다 내용이 정하고, 장면 전환은 하드 컷이다. |
| 계산 과정·공식을 손으로 적으며 설명하듯, 손글씨가 말하는 순서대로 한 글자씩 써지는 영상을 Resolve에서 고치며 만들고 싶음 | [akbun-davinciresolve-explainer-live-ink](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-live-ink/SKILL.md) | akbun-draw-live-ink의 색·글꼴·써지기 규칙을 그대로 쓰고, Text+에 왼쪽부터 넓어지는 사각 마스크를 걸어 글자가 펜이 지나가듯 드러나게 한다. 한 번에 하나만 쓰고 지우지 않으며, Inspector에서 글자·써지는 시점을 고친다. |
| 대본으로 그림이 자막에 맞춰 튀어나오는 설명 영상을 만들고, 색 조합·도형 스타일을 고르고 싶음 | [akbun-davinciresolve-explainer](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer/SKILL.md) | akbun-draw-night-gouache로 장면 그림을 등장 단위 레이어로 만들고, 장면마다 Fusion 클립 하나에서 팝·자라기·페이드·펀치 인으로 움직인다. 발광·후광 없이 색 대비로 강조하고, 코드는 `cat` 프롬프트가 있는 터미널 카드로 보여 준다. `#202020` 단색 배경 위 하드 컷과 Pretendard 자막 트랙(Position Y 85)을 쓴다. |
| 녹음의 숨소리와 빈 시간을 덜어 내고 싶음 | [akbun-davinciresolve-narration-cleanup](../plugins/akbun-editvideo/skills/akbun-davinciresolve-narration-cleanup/SKILL.md) | 주파수 프로필로 숨소리를 찾아 지우고 긴 쉼을 줄인 장면별 음성 파일과 지운 구간 보고서를 만든다. 애매한 구간은 남긴다. |
| 한 단계만 처리하고 싶음 | 아래의 해당 작업별 스킬 | 전체 workflow를 쓰지 않고 필요한 색보정·컷·자막·오디오·출력만 따로 요청한다. |

## 시나리오별 사용 순서

아래는 실제 요청의 시작점과 인계 순서다. 전체 workflow를 시작하면 표의 하위 스킬을 일일이 다시 호출하지 않아도 된다. 이미 완료한 단계는 작업 로그·타임라인에서 확인한 뒤 필요한 단계만 이어간다.

| 상황·준비된 입력 | 시작과 이어지는 스킬 | 받게 되는 결과·직접 확인할 부분 |
|---|---|---|
| 말 없는 여행 원본을 통째로 편집 | `akbun-davinciresolve-workflow` → 시간순 타임라인 → 트랙 준비 → 컷·색보정 → 선택 Look → 개인정보·자막 | 원본을 보존한 여행 편집본. 시간순 배열, 주요 장면과 자연음, 검토 마커 확인 |
| 도시 클립의 리듬만 다듬고 싶음 | `akbun-davinciresolve-cut-new-york` → 바뀐 구간을 자막 스킬에 전달 | 와이드·미디엄·디테일과 움직임을 잇는 몽타주. 삭제 후보와 자막·소리의 새 위치 확인 |
| 화면이 어둡고 야간 네온 분위기를 원함 | `akbun-davinciresolve-exposure` 및 필요한 WB·대비·채도 → `akbun-davinciresolve-look-tokyo-night` | 기본 밝기와 새 LOOK 노드가 분리된 결과. 실제 보기 환경에서 밝기·간판 디테일 확인. +1/+2스톱은 선택 비교 |
| 완성한 가로 영상에서 Shorts 후보 추출 | `davinciresolve-youtube-shorts` | 별도 세로 후보, 원래 오디오 처리 보존. 잘린 말·음악 tail·세로 구도 확인 |

## 말소리 있는 개발자 영상

### 촬영 후 편집 흐름

촬영 후에는 아래 스타일·자막 스킬을 필요한 작업별로 고른다.

| 편집할 문제 | 스킬이 하는 일 |
|---|---|
| 프로젝트 진행이나 개발자 일상을 기록 | [davinciresolve-style-project](../plugins/akbun-editvideo/skills/davinciresolve-style-project/SKILL.md): 목표·장애·선택·결과의 변화를 화면과 내레이션으로 보여준다. |
| 대사 자막, 키워드, 장면 설명 추가 | [davinciresolve-subtitle-devtalk](../plugins/akbun-editvideo/skills/davinciresolve-subtitle-devtalk/SKILL.md): 전사와 대조해 대사 자막과 필요한 강조·코멘트를 넣는다. 키워드·코멘트 Text+는 본편을 밀지 않고 `SUBTITLE` 트랙에 놓는다. |

## 말소리 없는 여행 영상

전체 순서를 맡길 때는 [akbun-davinciresolve-workflow](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/SKILL.md)를 쓴다. 이 workflow는 시간순 타임라인을 만들고 복제본에 비디오·오디오 트랙을 3개씩 준비한 뒤 작업을 이어간다. 일부 작업만 원하면 아래 스킬을 직접 고른다.

| 원하는 작업 | 스킬과 동작 |
|---|---|
| 클립을 촬영 시각 순서로 새 타임라인에 배치 | [akbun-davinciresolve-timeline-chrono](../plugins/akbun-editvideo/skills/akbun-davinciresolve-timeline-chrono/SKILL.md): 기존 타임라인을 수정하지 않고 촬영 시각 메타데이터로 배열한다. |
| 빈 화면·불량 구간 컷, 흔들림 보정 | [davinciresolve-cut-travelflow](../plugins/akbun-editvideo/skills/davinciresolve-cut-travelflow/SKILL.md): 여행 장면과 자연음의 흐름을 기준으로 정리하고 삭제 전 검토 표시를 남긴다. |
| 도시 장면을 와이드·미디엄·디테일로 엮어 몽타주 구성 | [akbun-davinciresolve-cut-new-york](../plugins/akbun-editvideo/skills/akbun-davinciresolve-cut-new-york/SKILL.md): 건축·교통·거리의 움직임과 음악 리듬을 활용해 컷을 제안한다. 장면 삭제는 이유를 설명하고 사용자가 확인한 뒤 진행한다. |
| 여행 자막과 장소·시간 챕터 | [davinciresolve-subtitle-travelnote](../plugins/akbun-editvideo/skills/davinciresolve-subtitle-travelnote/SKILL.md): 장소·시간·분위기를 짧은 한글 자막과 챕터로 전달한다. 자막 Text+는 본편과 마커를 밀지 않고 `SUBTITLE` 트랙에 놓는다. |

## 색보정은 무엇을 고를까

전체 여행 workflow를 사용하면 컷 편집 뒤 필요한 기본 색보정이 진행되고, 요청한 경우 창작 Look을 그 뒤에 적용한다. 개별 문제만 다룰 때는 증상에 맞는 스킬 하나를 고른다. 밝기와 화이트밸런스는 서로 다른 조정이다. 기본 보정 스킬들은 Color 페이지에 각각 새 라벨 노드를 만들어 조정이 구분되게 한다.

| 보이는 문제 또는 요청 | 스킬과 동작 |
|---|---|
| 클립마다 밝기가 달라 컷이 튐 | [akbun-davinciresolve-exposure](../plugins/akbun-editvideo/skills/akbun-davinciresolve-exposure/SKILL.md): Waveform 측정값으로 밝기를 맞춘다. 화이트밸런스는 변경하지 않는다. |
| 조명이나 카메라에 따라 색온도가 달라 보임 | [akbun-davinciresolve-whitebalance](../plugins/akbun-editvideo/skills/akbun-davinciresolve-whitebalance/SKILL.md): 중립 픽셀의 RGB를 기준으로 클립 간 색 균형을 맞춘다. |
| Log 영상이 흐릿하고 물 빠진 것처럼 보임 | [akbun-davinciresolve-logconvert](../plugins/akbun-editvideo/skills/akbun-davinciresolve-logconvert/SKILL.md): Log 촬영 여부가 확인된 클립만 Rec.709로 변환한다. 촬영 형식이 불확실하면 추측해 변환하지 않는다. |
| 화면이 밋밋하거나 대비 조정이 필요함 | [akbun-davinciresolve-contrast](../plugins/akbun-editvideo/skills/akbun-davinciresolve-contrast/SKILL.md): Pivot 기준으로 대비를 조정하고 밝고 어두운 영역의 손실을 확인한다. |
| 변환·대비 후 색이 약함 | [akbun-davinciresolve-saturation](../plugins/akbun-editvideo/skills/akbun-davinciresolve-saturation/SKILL.md): 측정값이 낮은 클립의 채도만 보충한다. 채도를 낮추는 작업은 하지 않는다. |
| 하늘만 따로 진하게 하거나 밝기 조정 | [akbun-davinciresolve-sky](../plugins/akbun-editvideo/skills/akbun-davinciresolve-sky/SKILL.md): 하늘 색상 범위에 한해 채도와 밝기를 조절하고 적용 가능 여부를 확인한다. |
| 보정한 영상에 창작 색 스타일을 더하고 싶음 | 아래 네 Look 중 장면·취향에 가까운 스킬을 선택한다. 각 스킬은 기존 보정 노드를 보존하고 새 `LOOK` Serial 노드를 만든다. 단일 LUT 경로에서는 `SAT` 뒤, DWG 경로에서는 조정·LUT의 입력 공간에 맞춰 Output CST 전후를 선택하며, 스코프 목표·허용 오차는 대표 장면에서 조정의 출발점으로 쓴다. |
| 일본 여름의 차분하고 바랜 필름 인상 | [akbun-davinciresolve-look-japan-summer](../plugins/akbun-editvideo/skills/akbun-davinciresolve-look-japan-summer/SKILL.md): 따뜻한 햇빛·절제된 녹색·부드러운 하이라이트를 다루며 인물이 드문 풍경에 맞춘다. |
| 도쿄 야간의 청록 그림자와 따뜻한 네온 | [akbun-davinciresolve-look-tokyo-night](../plugins/akbun-editvideo/skills/akbun-davinciresolve-look-tokyo-night/SKILL.md): 어두운 거리와 간판 빛을 구분하고 네온의 색·디테일을 보존한다. |
| 절제된 자연주의 단편영화 분위기 | [akbun-davinciresolve-look-still](../plugins/akbun-editvideo/skills/akbun-davinciresolve-look-still/SKILL.md): 부드러운 대비와 회녹색 도시 배경을 만들며 원본에 없는 색을 억지로 추가하지 않는다. |
| 따뜻한 뉴욕 거리 필름 인상 | [akbun-davinciresolve-look-new-york](../plugins/akbun-editvideo/skills/akbun-davinciresolve-look-new-york/SKILL.md): 햇빛 받은 거리와 차가운 하늘·그늘의 색 관계를 살린다. |

스코프 수치는 클립 간 일관성을 판단하는 근거이지, 최종 화면이 눈에 적절한 밝기라는 보장은 아니다. 사용자가 확인한 보기 환경에서는 예상보다 1–2스탑 올려야 정상 밝기로 보인 경험이 있으므로, 수치를 일괄 적용하지 말고 실제 모니터링 환경과 기준 화면에서 확인해 조정한다.

Look 수치는 참고 영상에서 프레임을 복제한 절대값이 아니라 각 스타일을 시작할 대표 앵커 프레임의 기준이다. 먼저 데이터 레벨·HDR/SDR·출력 변환·재생 환경을 확인한 뒤, 필요하면 대표 컷에서 기본 노출과 +1·+2스탑 화면을 비교하고, 선택한 밝기를 Look 단계가 되돌리지 않도록 한다. +1·+2스탑을 모든 클립에 자동 적용하지 않는다.

## 개인정보, 그래픽, 출력

| 필요 | 스킬과 동작 |
|---|---|
| 영상에서 얼굴·번호판·개인정보 가리기 | [davinciresolve-face-privacy](../plugins/akbun-editvideo/skills/davinciresolve-face-privacy/SKILL.md): Color 페이지에서 가릴 대상을 추적하고 타임라인에 확인 표시를 남긴다. |
| Fusion에서 특정 영역만 모자이크 | [davinciresolve-face-mosaic](../plugins/akbun-editvideo/skills/davinciresolve-face-mosaic/SKILL.md): 새 Mosaic Blur 노드와 마스크로 필요한 영역을 가린다. |
| 웹 페이지·GitHub 저장소를 둘러보며 요소를 짚기 | [akbun-edit-page-tour-lilac](../plugins/akbun-editvideo/skills/akbun-edit-page-tour-lilac/SKILL.md): 2배 스크린샷을 창 카드에 넣고 카메라가 요소마다 짧게 다가가 머물며 연보라 형광펜·외곽 상자로 짚는 전체 화면 장면을 만든다. 본편을 밀지 않는 새 트랙에 놓고, 노드 라벨로 Fusion 페이지에서 위치·색을 고친다. |
| 여러 글·게시물·이슈를 겹쳐 보여주며 구절 짚기 | [akbun-edit-quote-cards-lilac](../plugins/akbun-editvideo/skills/akbun-edit-quote-cards-lilac/SKILL.md): 실제 출처 스크린샷 카드 2~4장을 겹쳐 쌓고 읽는 구절에 형광펜을 쓸어 칠한다. |
| 터미널·AI 도구 화면 녹화에 주석 달기 | [akbun-edit-terminal-callout-amber](../plugins/akbun-editvideo/skills/akbun-edit-terminal-callout-amber/SKILL.md): 실제 녹화를 어두운 창 카드에 넣고 오류 줄 옆에 노란 손그림 화살표·라벨, 토큰 하이라이트를 붙인다. 출력을 지어내지 않는다. |
| 영화식 기본 자막·타이핑 자막을 재사용 템플릿으로 만들기 | [akbun-davinciresolve-caption-template](../plugins/akbun-editvideo/skills/akbun-davinciresolve-caption-template/SKILL.md): 외형 지정이 없으면 하단 중앙의 정적 Cinema를 사용하고, 요청 시 타이핑·키워드·밑줄·원을 만든다. DRFX를 Downloads에 생성하고 macOS 설치법을 안내한다. |
| YouTube Shorts 후보 만들기 | [davinciresolve-youtube-shorts](../plugins/akbun-editvideo/skills/davinciresolve-youtube-shorts/SKILL.md): 선택한 타임라인에서 세로 영상 후보를 만들고 원본과 오디오 구성을 보존한다. |

### 창 카드 장면 사용 (page-tour, quote-cards, terminal-callout)

대본과 스크린샷(또는 터미널 녹화)을 주고 스킬을 부른다. 예: “이 저장소 스크린샷으로 대본 2문장에 맞춰 이름·폴더 목록을 차례로 짚어줘.” 얼굴 화면은 넣지 않는다.

1. AI agent가 대본을 초당 6.5음절로 읽는다고 보고 신호 단어마다 등장 시각을 잡아 장면 표와 `plan.json`을 만든다.
2. 작업 타임라인을 복제하고 본편보다 위의 새 트랙에 단색 캔버스 클립을 놓은 뒤, 그 클립의 Fusion에 `FRAME_01`·`SHOT_01`·`MARK_01`·`CARD_01_LAYOUT`·`CAMERA` 같은 이름의 노드를 만든다. 다른 트랙의 클립·마커가 그대로인지 자동으로 대조한다.
3. 녹음 뒤에는 Resolve 전사·SRT·Whisper의 단어 시각으로 plan의 시각만 고치고 `retime`으로 다시 맞춘다. 직접 옮긴 표시·카드 위치와 색은 그대로 남는다.
4. 위치·색·크기는 Fusion 페이지에서 해당 노드의 Inspector로 고친다. 기본(캔버스 클립) 모드에서는 이 값들이 Edit 페이지 Inspector에 나오지 않는다(21.1.1 실측).
5. Edit 페이지 Inspector에서 바로 고치고 싶으면 “Edit Inspector에서 고칠 수 있게 만들어줘”라고 요청한다. 장면이 장면 전용 타임라인 끝에 Fusion 타이틀로 붙고, 클립을 고르면 Inspector → Video → Title 탭에 표시 색·위치·폭·높이, 카드 위치·크기, 주석 글자·위치가 나온다. 대신 장면을 본편 타임라인으로 직접 복사해 붙여야 하고, 녹음 후에는 시각만 다시 맞추는 대신 장면을 다시 만든다. 자세한 노드 표와 절차는 [fusion-cards 참조](../plugins/akbun-editvideo/skills/akbun-edit-page-tour-lilac/references/fusion-cards.md)에 있다.

검증 프레임은 `grab`이 클립 구간을 Deliver 렌더 잡으로 한 번 렌더해 뽑는다. Fusion 노드 하나를 직접 렌더하는 `grab --tool`은 프레임마다 "Render completed!" 창을 남기고, 이 창이 열려 있으면 다음 편집 API가 실패하므로 꼭 필요할 때만 쓰고 창을 닫는다.

## 측정·촬영 규칙을 읽는 법

- Look은 [공통 측정 규약](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/references/look-scopes.md)에 따라 같은 유효 영상 영역·물체 ROI를 비교한다. 99 IRE 이상 비율은 클리핑과 다르며 RGB 채널·디테일을 별도로 본다.
- 노출 스크립트의 0–1020 밝기 근사치와 스톱·IRE를 바꿔 쓰지 않는다. +1/+2스톱은 선택 비교이며 중간값·무조정도 가능하다.
- [Pivot 로컬 표](../plugins/akbun-editvideo/skills/akbun-davinciresolve-contrast/references/pivot-reference.md)는 인터넷 검색 없이 사용할 수 있다. DWG의 노드 연결은 입력 CST→노출→WB→대비→채도·선택 보정→출력 CST이며, 대비를 먼저 조정할 수 있다.
- devtalk는 주 음성(내레이션)을 화면과 구분하며 주장 문장을 두 번 녹음할 의무가 없다. 컷 수·샷 길이는 출발점이고 이야기의 pause·자료 읽기 시간을 보존한다. 그래픽 도구가 미정이면 아이디어를 유지하고 다른 편집을 진행한다.
- 1.1.0부터 도시 컷 스킬은 `davinciresolve-cut-citymontage`에서 `akbun-davinciresolve-cut-new-york`로 변경됐다. 저장한 호출문은 새 이름으로 바꾼다.

## 버전과 세부 절차

이 매뉴얼은 스킬 선택을 돕는 안내서다. DaVinci Resolve AI Assistant 2026.9 기준으로 사용하며, 특정 버전·도구·스크립트 조건, 입력 확인, 되돌리기, 검증 방법은 각 스킬의 `SKILL.md`에서 확인한다. 그래픽 제작 도구를 아직 선택하지 않았다면 기획 단계에서는 그래픽 아이디어만 정리하고, 도구를 정한 뒤 해당 제작 스킬을 사용한다.

## 재사용 자막 템플릿

`$akbun-davinciresolve-caption-template`에 문구·표시 시간을 준다. 외형 지정이 없으면 `Akbun Cinema`가 기본이다. 하단 중앙·흰 글자·검은 외곽선이며 애니메이션·효과음은 없다. Source Han Sans KR Regular, 한 줄 우선·최대 두 줄을 사용하고 대표 자막의 가독성을 확인한다. workflow의 자동 스타일 선택만으로 이 기본값을 바꾸지 않는다. 타이핑·키워드를 요청하면 참고 영상/구간을 줄 수 있다. AI가 `/tmp`에 직접 캡처해 글자 공개 순서·정렬·색을 분석한다. 문장형 `Akbun Typewriter`와 큰 세리프 키워드형 `Akbun Keyword`는 Text+·도형으로 구성해 문구와 강조를 다시 편집할 수 있다.

템플릿만 요청하면 `~/Downloads/Akbun-Caption/<내용해시>/`의 `.drfx`·setting 3개·`readme.md` 사용설명서를 받는다. Finder에서 더블클릭해 Resolve에 설치하고 Edit → Effects → Titles에서 찾아 본편 위의 별도 비디오 트랙에 드래그한다. 이 설치는 다음 프로젝트에도 유지되며 폰트는 별도다. 원본 패키지는 백업한다.

Inspector에서 문구·위치·크기와 밑줄/원의 Visibility를 조절한다. 문장형 Reveal Duration은 클립 길이에 대한 비율이며 기본 0.65다. 타이핑·키워드의 글꼴은 오뮤 다예쁨체·나눔명조를 기본으로 확인하고 OFL 대안으로 나눔손글씨 펜을 안내한다. 문구 변경 뒤 강조 위치는 다시 맞춘다. Epidemic Sound 연결이 안 되면 효과음의 분·초·길이·검색어·오디오 트랙을 채팅으로 받는다.

호출명 변경: `davinciresolve-caption-template` → `akbun-davinciresolve-caption-template`. 이전 호출명 대신 새 이름을 사용한다.

## 대본에서 설명 영상 만들기

[akbun-davinciresolve-explainer](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer/SKILL.md)은 누가 만들어도 같은 결과가 나오게 설계했다. 장면은 JSON spec(무엇을, 어느 순서로, 언제)으로만 쓰고, 모양·색·배치는 `references/`의 jsonl 라이브러리가 정한다. `scripts/scene.py`가 SVG·레이어 PNG·Fusion comp를 만들고 검사표로 채점한다. 호출할 때 색 조합(`night` 기본, `apple-orchard`, `fiery-ocean`, `akbun`)과 도형 스타일(`gouache` 기본, akbun-presentation-paper 도형 언어인 `akbun`)을 고른다. 모든 장면이 고른 팔레트의 단색 배경이고, 사람은 얼굴 없는 실루엣(큰 원 머리 + 반원 몸통)이다. 강조는 점선 상자와 펀치 인으로만 하고, 코드는 `$ cat <파일>` 프롬프트와 실제 줄만 담은 터미널 카드로 보여 준다. 장면 전환은 하드 컷이다.

예: `$akbun-davinciresolve-explainer 이 대본을 fiery-ocean 색, akbun 도형으로 장면을 나눠 Resolve 타임라인으로 움직여줘.`

1. 대본을 장면 spec(자막·레이어·등장 시점·펀치 인)으로 나누고 확인받는다. 등장 시점은 그 대상을 말하는 자막의 시작 시각이다.
2. `scene.py build`로 장면마다 SVG와 레이어 PNG를 만들고 `scene.py check`로 채점한다. 장면별·장면 사이 점수가 모두 95% 이상이어야 다음으로 간다.
3. `scene.py comp`로 만든 comp를 Fusion 클립에 넣는다. Edit 페이지 Inspector에서 레이어별 보이기·등장 시점과 펀치 인 시점·배율을 고친다.
4. 장면을 다 넣은 뒤 자막 트랙 잠금을 풀고, 자막 스타일(Pretendard Medium 42, 팔레트 SUB 색, 외곽선 0, Position Y 85)을 Inspector → Track 탭으로 맞춘다.
5. 스킬을 고치면 서로 다른 주제 5개를 새 agent로 만들어 모두 95% 이상인지 본다(`references/testing.md`).

## 검정 보드 손그림 설명 영상 (scribble-black)

[akbun-davinciresolve-explainer-scribble-black](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-scribble-black/SKILL.md)은 클립 구조를 [공통 Resolve 구현](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer/references/resolve-core.md)에서, 색·선·도형·글씨·그리는 속도를 [akbun-draw-scribble-black](../plugins/akbun-draw/skills/akbun-draw-scribble-black/SKILL.md)에서 가져온다. 검정 보드에 흰 펜으로 생각 구름·말풍선·얼굴 없는 막대 인물·상자 사물·회색 화살표·손글씨 수식을 한 획씩 써 내려가고, 하늘색(입력)·주황(결과)·노랑(주목)·빨강(문제)으로 강조한다. 그리는 손과 사람 얼굴은 넣지 않는다.

예: `$akbun-davinciresolve-explainer-scribble-black 이 대본으로 DNS 조회 과정을 보드에 써 내려가는 설명 영상으로 만들어줘.`

1. 대본을 장면 표(획 순서·색 글씨·신호 단어와 시작·끝 시각)로 나누고 획이 겹치지 않는지 확인받는다.
2. draw skill 규칙으로 그린 SVG에서 획·채움 레이어를 투명 PNG로 뽑는다.
3. 다른 작업이 연 프로젝트를 건드리지 않고 새 타임라인을 만든다. 대표 장면 하나로 획 드러나기·Text+ 써지기·시점 이어 밀기를 확인한 뒤 나머지를 만든다.
4. 녹음이 오면 첫 빌드 시점과 장면 길이만 다시 맞춘다. 뒤 빌드는 표현식으로 따라온다.
5. 첫 획 직후·중간·마지막 프레임 스틸을 10항목 채점표로 채점한다.

## 슬레이트 카드 설명 영상 (slate-marker)

[akbun-davinciresolve-explainer-slate-marker](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-slate-marker/SKILL.md)은 클립 구조를 공통 Resolve 구현에서, 색·글꼴·부품 모양을 [akbun-draw-slate-marker](../plugins/akbun-draw/skills/akbun-draw-slate-marker/SKILL.md)에서 가져온다. 순검정 배경 위 슬레이트 카드와 손글씨 캡션, 의미마다 하나씩 정한 강조색으로 상태 변화를 보여 준다. 기본 Explainer의 고정 위치를 쓰지 않고 배치는 장면마다 내용이 정한다. 렌더된 영상 대신 Fusion 도형으로 그려 Inspector에서 고친다.

예: `$akbun-davinciresolve-explainer-slate-marker 이 대본으로 로드밸런서가 죽은 서버를 빼는 과정을 설명 영상으로 만들어줘.`

1. 대본을 장면 표(상태 변화·부품·강조색·캡션·신호 단어와 등장 시점)로 나누고 확인받는다. 시각은 draw skill의 신호 단어 규칙으로 잡는다.
2. 다른 작업이 연 프로젝트를 건드리지 않고 새 타임라인을 만든다. Gaegu·D2Coding 설치를 확인한다.
3. 대표 장면 하나로 삽입·매크로·점선·선 그리기를 확인한 뒤 나머지 장면을 만든다.
4. 녹음이 오면 단어 시각으로 등장 시점과 장면 길이를 다시 맞춘다.
5. 등장 직후·상태 변화 직후·마지막 프레임 스틸을 10항목 채점표로 채점하고, 내보낸 comp의 색 값을 색 표와 대조한다.

## 손글씨 설명 영상 (live-ink)

[akbun-davinciresolve-explainer-live-ink](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-live-ink/SKILL.md)은 클립 구조를 공통 Resolve 구현에서, 색·글꼴·써지는 속도와 순서를 [akbun-draw-live-ink](../plugins/akbun-draw/skills/akbun-draw-live-ink/SKILL.md)에서 가져온다. 거의 검정인 판 위에 Nanum Pen 손글씨가 흰 본문·초록 규칙·주황 이름표·분홍 비교 예시로 써진다. 펜은 한 자루라 두 곳을 동시에 쓰지 않고, 쓴 것은 장면 끝까지 남는다. 상자·카메라·페이드 없이 글자와 밑줄·화살표뿐이다.

예: `$akbun-davinciresolve-explainer-live-ink 이 대본으로 지수 백오프 재시도 간격이 두 배씩 늘어나는 과정을 손글씨 설명 영상으로 만들어줘.`

1. 대본을 장면 표(빌드 순서·색·신호 단어·써지는 시점과 길이)로 나누고 확인받는다. 시각은 draw skill의 신호 단어 규칙으로 잡는다.
2. 다른 작업이 연 프로젝트를 건드리지 않고 새 타임라인을 만든다. Nanum Pen 설치를 확인한다.
3. 대표 장면 하나로 삽입·매크로·마스크 써지기·글자 간격을 확인한 뒤 나머지 장면을 만든다.
4. 녹음이 오면 단어 시각으로 써지는 시점과 장면 길이를 다시 맞춘다.
5. 반쯤 써진 순간·마지막 프레임 스틸을 10항목 채점표로 채점하고, 내보낸 comp의 색 값과 빌드 겹침을 확인한다.

## 설명 영상을 녹음에 맞추기 (dark-diagram)

[akbun-davinciresolve-explainer-dark-diagram](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-dark-diagram/SKILL.md)은 장면 빌드 방식을 공통 Resolve 구현에서 가져오고 스타일과 녹음 맞춤 흐름을 정한다. 배경 `#202020`에 색으로 역할을 나눈 글자와 화살표를 기본으로 그리고, 구분·포함·색 전환이 필요한 실제 대상만 둥근 박스·영역으로 감싼다. 선 아이콘·터널·패킷을 더하고, 요소는 살짝 커지며 등장하고 장면은 천천히 확대된다. 왼쪽 위에 챕터 이름·장면 부제목·주황 결론 한 줄을 두고 화면 아래는 자막 자리로 비운다.

예: `$akbun-davinciresolve-explainer-dark-diagram 이 주제로 대본과 장면을 만들고, 내가 녹음하면 녹음에 맞춰 다시 그려줘.`

1. 대본(md·srt)과 장면을 만든다. 장면 길이는 초당 5.0음절에 15% 여유다.
2. 자막 트랙 `대본`을 먼저 넣고 장면을 배치한다. 자막 글꼴·위치는 Inspector → Track 탭에서 Gmarket Sans Medium 28, Position Y 110으로 바꾼다.
3. 사용자가 A1에 녹음한다. 대본과 다르게 말해도 된다.
4. 녹음 원본 타임라인을 보존하고, 임시 타임라인에서 음성 인식을 돌려 테이크를 내용으로 장면에 배정한다. 실제 사례·특정 조직을 가리키는 문장은 기본으로 빼고 보고한다. 녹음에서 말하지 않은 장면은 빼는 쪽을 기본으로 제안한다.
5. [akbun-davinciresolve-narration-cleanup](../plugins/akbun-editvideo/skills/akbun-davinciresolve-narration-cleanup/SKILL.md)으로 장면별 음성을 만들고, 장면 길이·등장 시점·자막을 실제 목소리에 맞춰 타임라인을 다시 만든다.
6. 효과음과 챕터 마커를 넣는다. 챕터 마커는 장면 메모 마커와 다른 색으로 두고, 0:00 시작·3개 이상·각 10초 이상을 검사한 뒤 매번 마지막에 다시 단다.
7. 첫 렌더 전에 자막을 화면에 구울지 자막 파일로 올릴지, 업로드 채널·카테고리·공개 범위를 한 번에 정한다. 업로드는 YouTube 렌더 프리셋 job으로 하고, 제목·설명·챕터를 채운 설정은 렌더 프리셋으로 저장해 다시 쓴다. 업로드 완료는 Resolve 로그로 확인한다.

## 녹음 숨소리·쉼 정리

[akbun-davinciresolve-narration-cleanup](../plugins/akbun-editvideo/skills/akbun-davinciresolve-narration-cleanup/SKILL.md)은 숨소리를 대역별 레벨로 판정한다. 1~6kHz에 소음이 있고 목소리 배음(70~300Hz)이 없으며 8kHz 이상이 약한 0.12~0.8초 구간이 유성음과 떨어져 있으면 숨소리다. 들리는 숨소리 시각을 알려 주면 그 구간을 재서 규칙을 확인하고 녹음 전체에 다시 적용한다.

예: `$akbun-davinciresolve-narration-cleanup 02:25:02~02:25:10이 숨소리야. 이 주파수로 녹음 전체 숨소리를 지우고 긴 쉼도 줄여줘.`

0.3초 넘는 쉼은 0.27초로 줄이고 장면 사이에는 약 0.6초의 숨고르기를 남긴다. 결과는 장면별 -16 LUFS wav와 지운 구간 보고서다. 원본 녹음은 수정하지 않으며, 스펙트로그램 확인은 직접 듣기를 대신하지 않는다.
