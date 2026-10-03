# 영상 편집 스킬 사용자 매뉴얼

이 문서는 `akbun-editvideo` 플러그인의 스킬을 어떤 상황에 고르고, 각 스킬이 어떤 문제를 해결하는지 안내한다. 실제 작업 지침과 세부 조건은 연결된 `SKILL.md`가 기준이다.

영상·Resolve 용어는 [용어사전](terms_editvideo.md)을 참고한다.

스킬은 이름을 직접 불러 사용할 수 있다. 예: `$akbun-vlog-prepared-devtalk`. 전체 작업을 맡는 workflow 스킬은 필요한 하위 스킬 문서를 읽어 순서대로 진행하고, 각 하위 스킬은 원하는 단계만 따로 요청할 때 쓴다.

## 어떤 흐름을 고를까

| 상황 | 시작할 스킬 | 해결하는 문제와 동작 |
|---|---|---|
| 아직 촬영 전이고 경험을 영상 이야기로 만들고 싶음 | [akbun-vlog-prepared-devtalk](../plugins/akbun-editvideo/skills/akbun-vlog-prepared-devtalk/SKILL.md) | 한 번에 하나씩 인터뷰하며 실제 경험을 5–7분 이야기로 정리하고, 비트·샷·스케치·촬영 계획까지 준비한다. 얼굴 비노출을 전제로 하고 모션그래픽 도구는 미리 정하지 않는다. |
| 특정 샷의 카메라 구도와 빛을 정하고 싶음 | [akbun-vlog-shotsketch](../plugins/akbun-editvideo/skills/akbun-vlog-shotsketch/SKILL.md) | 이야기 비트에 필요한 한 샷의 프레임, 카메라 위치, 동작, 조명과 얼굴 비노출 확인을 그림과 표로 만든다. |
| 전체 이야기에서 어떤 장면을 어떤 순서로 찍을지 보고 싶음 | [akbun-vlog-storyboard](../plugins/akbun-editvideo/skills/akbun-vlog-storyboard/SKILL.md) | 확정된 비트를 음성·B-roll·화면 녹화·필요한 그래픽 아이디어에 연결하고 핵심 setup을 스케치한다. |
| 말소리 없는 여행 영상 전체를 편집하고 싶음 | [akbun-davinciresolve-workflow](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/SKILL.md) | 원본 타임라인을 보존하면서 촬영 시간순 타임라인부터 컷, 색보정, 요청된 Look, 개인정보 보호, 자막, 오디오, 출력까지 단계별로 진행한다. |
| 글·PPTX·이미지로 설명 영상을 새로 만들고 싶음 | [akbun-davinciresolve-explainer](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer/SKILL.md) | 대본·스토리보드를 확인한 뒤 장면별 Fusion 타이틀을 만든다. Inspector에서 글자·표시·등장 시점·위치를 고치고 대본·가이드·스틸을 받는다. |
| 한 단계만 처리하고 싶음 | 아래의 해당 작업별 스킬 | 전체 workflow를 쓰지 않고 필요한 색보정·컷·자막·오디오·출력만 따로 요청한다. |

## 시나리오별 사용 순서

아래는 실제 요청의 시작점과 인계 순서다. 전체 workflow를 시작하면 표의 하위 스킬을 일일이 다시 호출하지 않아도 된다. 이미 완료한 단계는 작업 로그·타임라인에서 확인한 뒤 필요한 단계만 이어간다.

| 상황·준비된 입력 | 시작과 이어지는 스킬 | 받게 되는 결과·직접 확인할 부분 |
|---|---|---|
| 촬영 전, “32주차 개발자 diary”라는 생각만 있음 | `akbun-vlog-prepared-devtalk` → 이야기 확정 후 `akbun-vlog-storyboard`·`akbun-vlog-shotsketch` | 인터뷰에서 찾은 실제 사건, 5–7분 이야기, 얼굴 없는 샷·소리의 역할·녹음·촬영 순서. 경험과 내 말투가 맞는지 확인 |
| 말 없는 여행 원본을 통째로 편집 | `akbun-davinciresolve-workflow` → 시간순 타임라인 → 트랙 준비 → 컷·색보정 → 선택 Look → 개인정보·자막 → 사운드 → 출력 | 원본을 보존한 여행 편집본. 시간순 배열, 주요 장면과 자연음, 검토 마커 확인 |
| 도시 클립의 리듬만 다듬고 싶음 | `akbun-davinciresolve-cut-new-york` → 바뀐 구간을 자막·사운드 스킬에 전달 | 와이드·미디엄·디테일과 움직임을 잇는 몽타주. 삭제 후보와 자막·소리의 새 위치 확인 |
| 컷은 끝났고 풍경 소리·효과음·음악을 함께 보강 | `davinciresolve-sfx-epidemicsound` → 필요하면 `davinciresolve-export-youtube` | 오디오 직전 상태를 복제한 작업본, 환경음·동작음·필요한 여러 BGM, 검토 큐시트. `AUDIO_REVIEW` 순서로 들어보기 |
| 음악 후보만 비교하고 싶음 | `davinciresolve-bgm-epidemicsound`의 후보 단계 | 비트별 후보·선택 이유·전환 제안. 타임라인은 수정하지 않으며 장면의 감정과 음악이 맞는지 판단 |
| 이미 있는 BGM을 여러 곡으로 나누거나, 말할 때 잠시 빼고 재진입 | `davinciresolve-bgm-epidemicsound` → 사운드 공통 기준의 음악 편집·믹싱·마커 절 | 복제본에서 phrase·스템·tail·여백을 편집. 곡의 경계, 말 가림, 재진입 강도를 확인 |
| 카드·버튼·키워드 소리만 필요함 | `davinciresolve-sfx-epidemicsound`에 대상 이벤트/구간 지정 | 복제본의 지정 SFX만 편집. 기존 음악 유지, 강조 타이밍과 반복 피로 확인 |
| 사운드를 끝낸 뒤 컷 길이가 달라짐 | 컷 스킬의 변경 목록 → `davinciresolve-sfx-epidemicsound`의 컷 변경과 인계 | 앵커·스템·덕킹·전환·마커를 다시 맞춘 결과. 음악 phrase와 효과음 싱크가 어긋나지 않는지 확인 |
| 화면이 어둡고 야간 네온 분위기를 원함 | `akbun-davinciresolve-exposure` 및 필요한 WB·대비·채도 → `akbun-davinciresolve-look-tokyo-night` | 기본 밝기와 새 LOOK 노드가 분리된 결과. 실제 보기 환경에서 밝기·간판 디테일 확인. +1/+2스톱은 선택 비교 |
| 편집·믹스 완료, 업로드할 파일만 필요함 | 타임라인 해상도에 맞는 기본 프리셋은 `davinciresolve-export-youtube` | 렌더 파일과 수행한 검증 결과. `AUDIO_REVIEW` 미해결 목록 확인. 렌더 요청만으로 업로드하지 않음 |
| 완성한 가로 영상에서 Shorts 후보 추출 | `davinciresolve-youtube-shorts` | 별도 세로 후보, 원래 오디오 처리 보존. 잘린 말·음악 tail·세로 구도 확인 |

예: `$davinciresolve-sfx-epidemicsound 현재 여행 타임라인을 복제해서 바다→거리 전환과 현장음을 살리고, 필요한 여러 BGM도 연결해줘. 내가 들을 곳은 마커로 남겨줘.`


예: `$davinciresolve-bgm-epidemicsound 32주차 diary의 집중→막힘→해결 흐름에 맞는 음악 후보만 보여줘. 아직 넣지는 말아줘.`

### 사운드 작업에서 확인할 것

효과음·환경음·여러 음악·스템·전환·믹싱의 실행 기준은 [사운드 디자인 스킬](../plugins/akbun-editvideo/skills/davinciresolve-sfx-epidemicsound/SKILL.md) 한곳에 있다. BGM 스킬은 음악만 요청하는 진입점이고, `davinciresolve-export-youtube`는 기본 프리셋 출력과 결과 해상도 확인을 맡는다. Epidemic Sound 유료 계정은 Resolve Workflow Integration이나 연결된 MCP 중 사용 가능한 경로를 쓴다.

오디오 편집은 `<기존 이름>_sound_<일시>` 복제본에서 진행한다. 음악이 잠깐 사라지는 여백, 곡 전환·재진입, 창작적 효과와 판단이 필요한 곳은 Sand `AUDIO_REVIEW` 마커로 찾는다. 노트의 정확한 TC·의도·대안·적용 여부를 읽고 전후로 들어보면 된다. AI가 자체 검청한 상태와 사용자가 승인한 상태는 구분한다. 후속 렌더는 이 복제본을 사용한다.

분당 효과음 수·BGM 한 곡·고정 페이드 길이를 강제하지 않는다. 장면의 감정·말의 이해·싱크·공간의 연속성과 실제 청감으로 판단한다. 참고 영상의 상품·광고·채널 홍보는 제작 조건으로 사용하지 않는다. 분석 자료는 `Downloads/`에서 수동 정리해도 되지만 프로젝트가 참조하는 최종 음원은 별도 `audio-assets/` 같은 유지할 위치에 둔다.

## 장면별 사운드 효과 시나리오

효과음·환경음과 음악을 함께 다루면 [davinciresolve-sfx-epidemicsound](../plugins/akbun-editvideo/skills/davinciresolve-sfx-epidemicsound/SKILL.md), 음악만 찾거나 편집하면 [davinciresolve-bgm-epidemicsound](../plugins/akbun-editvideo/skills/davinciresolve-bgm-epidemicsound/SKILL.md)를 쓴다. 아래 표의 `사운드`와 `BGM`은 각각 이 두 스킬을 가리킨다. 편집은 복제본에서 진행하고 사용자가 들을 부분을 `AUDIO_REVIEW`로 표시한다.

검색 예시는 특정 음원이나 필수 조합이 아니다. 쓸 만한 원음이 있으면 먼저 살리고, 표의 소리를 전부 추가하지 않는다. 영문 표현의 뜻과 검색어 조합법은 [사운드 검색 용어](terms_editvideo.md#브이로그-사운드-검색-용어)를 참고한다.

| 장면·해결할 문제 | 사용할 스킬·소리의 역할 | 검색어 예시 | 직접 들어볼 부분 |
|---|---|---|---|
| 아침에 책상 정리·커피 준비로 하루를 시작 | 사운드: 방의 바닥 소리 위에 컵 내려놓기·물 따르기 등 실제 동작만 보강 | `room tone`, `cup ceramic`, `coffee pour`; 음악은 `warm acoustic` | 컵·물소리의 어택이 손동작에 맞는지, 조용한 아침보다 과장되지 않는지 |
| 코딩·타이핑·마우스 조작이 밋밋함 | 사운드: 원음이 부족한 동작에만 짧고 가까운 소리 추가 | `keyboard typing soft`, `mouse click`, `desk tap` | 키 입력과 어긋나거나 같은 소리가 반복돼 거슬리지 않는지 |
| 화면 녹화에서 결과·버튼·키워드를 강조 | 사운드: 꼭 알아차려야 하는 변화에만 작은 악센트 | `soft click`, `pop`, `notification chime` | 핵심 단어를 가리지 않는지, 실제 시스템 알림과 혼동되지 않는지 |
| 긴 작업 과정을 타임랩스로 압축 | 사운드 또는 BGM: 음악의 반복 리듬으로 시간 경과를 표현하고 필요할 때만 시작·끝 강조 | `lofi instrumental`, `light percussion`, `subtle pulse`; 강조는 `short whoosh` | 빠른 타이핑 소리로 화면을 과하게 채우지 않았는지, 음악 접합부가 반복 티를 내는지 |
| 작업 중 막힘·버그 발견 뒤 잠시 생각함 | 사운드: 음악이나 드럼을 덜어내고 room tone·짧은 여백 유지. 긴장이 필요할 때만 낮은 질감 추가 | `room tone quiet`, `subtle drone`; 음악은 `minimal tension` | 평범한 실수를 공포·재난처럼 과장하지 않는지, 무음이 의도적으로 들리는지 |
| 테스트 성공·문제 해결·전후 비교 결과 공개 | 사운드: 결과가 보이는 순간에 악센트, 필요한 경우 음악 재진입 | `soft impact`, `bright chime`, `gentle swell`; 음악은 `hopeful instrumental` | 성공을 설명하는 말과 충돌하지 않는지, 효과음을 빼도 결과가 이해되는지 |
| 걷기·거리·카페·기차 등 장소가 바뀜 | 사운드: 다음 장소의 환경음을 먼저 들려주는 J-cut 또는 이전 여운을 남기는 L-cut | `footsteps pavement`, `city ambience distant`, `cafe ambience`, `train interior` | 실제 공간·거리·시점에 맞는지, 화면 밖 소리의 연결이 자연스러운지 |
| 바다·숲·비 오는 창가에서 풍경을 오래 보여줌 | 사운드: 파도·바람·비 등 장면의 주인공 소리를 살리고 음악은 필요할 때만 사용 | `ocean waves gentle`, `wind trees`, `rain window`; 음악은 `ambient sparse` | 음악 없이도 공간이 이어지는지, 바람·저역·레이어가 과하지 않은지 |
| 챕터 카드·지도·화면 이동이 뚝 끊겨 보임 | 사운드: 움직임 방향·무게에 맞는 전환음을 필요한 경계에만 배치 | `soft whoosh`, `short swish`, `reverse swell` | 소리의 최고점이 카드 도착·장면 변화에 맞는지, 매 컷 같은 전환이 반복되지 않는지 |
| 회고에서 중요한 한 문장을 또렷하게 전달 | 사운드 또는 BGM: 멜로디·드럼을 줄이거나 음악을 빼고 말과 여백을 전면에 배치 | `reflective piano`, `minimal underscore`, `warm pad` | 말의 시작과 끝, 호흡이 들리는지. 슬픈 음악으로 감정을 강요하지 않는지 |
| 집중→막힘→해결에 맞춰 BGM 여러 곡 연결 | BGM: 비트별 곡·스템·여백을 정하고 phrase 끝에서 연결 | `laid back electronic` → `minimal tension` → `gentle uplifting` | 곡 간 코드·리듬·음량 충돌, 급격한 분위기 변화. 같은 key만으로 연결을 확정하지 않음 |
| 하루·주차 diary를 조용히 마무리 | 사운드 또는 BGM: 마지막 생활음·음악의 종지·잔향 중 필요한 끝을 선택 | `soft chime`, `gentle swell`, `reflective acoustic` | 마지막 말·잔향이 렌더 끝에서 잘리지 않는지, 불필요한 마무리 효과가 없는지 |

요청 예: `$davinciresolve-sfx-epidemicsound 책상에서 코딩하는 구간은 원래 타이핑 소리를 살리고, 테스트 성공 화면에만 작은 악센트를 넣어줘. 설명 중에는 음악이 물러나게 하고 검토 지점을 표시해줘.`

요청 예: `$davinciresolve-bgm-epidemicsound 집중→막힘→해결 비트에 맞는 후보를 찾아줘. lo-fi나 minimal underscore부터 비교하되, 기존 곡의 스템을 줄이거나 음악을 빼는 선택도 포함해줘.`

## 말소리 있는 개발자 영상

### 촬영 후 편집 흐름

촬영 후에는 아래 스타일·자막 스킬과 사운드 스킬을 필요한 작업별로 고른다.

| 편집할 문제 | 스킬이 하는 일 |
|---|---|
| 기술 원리나 트레이드오프를 설명 | [davinciresolve-style-essay](../plugins/akbun-editvideo/skills/davinciresolve-style-essay/SKILL.md): 주장과 근거를 중심으로 화면 녹화·자료·필요한 그래픽을 배치한다. |
| 프로젝트 진행이나 개발자 일상을 기록 | [davinciresolve-style-project](../plugins/akbun-editvideo/skills/davinciresolve-style-project/SKILL.md): 목표·장애·선택·결과의 변화를 화면과 내레이션으로 보여준다. |
| 대사 자막, 키워드, 장면 설명 추가 | [davinciresolve-subtitle-devtalk](../plugins/akbun-editvideo/skills/davinciresolve-subtitle-devtalk/SKILL.md): 전사와 대조해 대사 자막과 필요한 강조·코멘트를 넣는다. 키워드·코멘트 Text+는 본편을 밀지 않고 `SUBTITLE` 트랙에 놓는다. |

편집 스타일은 핵심이 `원리 설명`이면 essay, `진행과 결과`이면 project를 고른다.

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

## 개인정보, 그래픽, 음악, 출력

| 필요 | 스킬과 동작 |
|---|---|
| 영상에서 얼굴·번호판·개인정보 가리기 | [davinciresolve-face-privacy](../plugins/akbun-editvideo/skills/davinciresolve-face-privacy/SKILL.md): Color 페이지에서 가릴 대상을 추적하고 타임라인에 확인 표시를 남긴다. |
| Fusion에서 특정 영역만 모자이크 | [davinciresolve-face-mosaic](../plugins/akbun-editvideo/skills/davinciresolve-face-mosaic/SKILL.md): 새 Mosaic Blur 노드와 마스크로 필요한 영역을 가린다. |
| 기사·블로그·논문을 본편 위에 발췌해 보여주기 | [akbun-davinciresolve-article-overlay](../plugins/akbun-editvideo/skills/akbun-davinciresolve-article-overlay/SKILL.md): Resolve Fusion으로 밝은 발췌 패널을 만들고 선택한 문장에 밑줄·원·하이라이트를 붙인다. Epidemic Sound MCP 음원을 SFX 트랙에 동기화하고 삽입 불가 시 분·초·길이·검색어·트랙을 채팅으로 안내한다. |
| 영화식 기본 자막·타이핑 자막을 재사용 템플릿으로 만들기 | [akbun-davinciresolve-caption-template](../plugins/akbun-editvideo/skills/akbun-davinciresolve-caption-template/SKILL.md): 외형 지정이 없으면 하단 중앙의 정적 Cinema를 사용하고, 요청 시 타이핑·키워드·밑줄·원을 만든다. DRFX를 Downloads에 생성하고 macOS 설치법을 안내한다. |
| 영상 분위기에 맞는 배경음악 후보 찾기 | [davinciresolve-bgm-epidemicsound](../plugins/akbun-editvideo/skills/davinciresolve-bgm-epidemicsound/SKILL.md): Epidemic Sound 후보와 이유를 제시하고, 요청하면 공통 사운드 기준으로 여러 곡·스템·전환을 편집한다. |
| 효과음·환경음·여러 BGM 사운드 디자인 | [davinciresolve-sfx-epidemicsound](../plugins/akbun-editvideo/skills/davinciresolve-sfx-epidemicsound/SKILL.md): 타임라인을 복제해 현장음·효과음·음악을 설계·믹싱하고 검토 지점을 마커로 남긴다. |
| YouTube Shorts 후보 만들기 | [davinciresolve-youtube-shorts](../plugins/akbun-editvideo/skills/davinciresolve-youtube-shorts/SKILL.md): 선택한 타임라인에서 세로 영상 후보를 만들고 원본과 오디오 구성을 보존한다. |
| YouTube 기본 렌더 출력 | [davinciresolve-export-youtube](../plugins/akbun-editvideo/skills/davinciresolve-export-youtube/SKILL.md): 타임라인 해상도에 맞는 YouTube 렌더 프리셋을 고르고 결과 해상도를 확인한다. |

### 기사 발췌 오버레이 사용

`$akbun-davinciresolve-article-overlay`에 기사 URL/본문/캡처와 대상 타임라인·표시 구간을 준다. 예: “이 글을 0분 12초부터 5초 동안 띄우고 핵심 문장에 빨간 밑줄과 Marker stroke 효과음을 넣어줘.” 강조는 선택 사항이며 밑줄·원·하이라이트 중 필요한 방식과 색을 지정할 수 있다.

AI agent가 참고 프레임을 직접 확인한 뒤 패널·글자·강조를 구성하고, 복제본에서 본편보다 위의 별도 비디오 트랙에 같은 시간으로 겹쳐 배치한다. 대상 구간이 비어 있는 기존 오버레이 트랙은 재사용하고, 없으면 새 `ARTICLE_OVERLAY` 트랙을 만든다. 본편 트랙에 발췌를 끼워 넣거나 기존 영상의 길이를 밀지 않는다. 원문 캡처는 이미지로 남고 재조판한 문구는 Text+로 수정할 수 있다. 대사 자막은 위의 자막 스킬을 고른다.

편집 후에는 발췌 클립을 선택하고 Fusion 페이지에서 해당 노드를 선택해 Inspector로 고친다. 실제 트랙·클립·노드 이름과 수정 항목을 AI가 함께 안내한다.

| 수정할 것 | 기본 컨트롤 |
|---|---|
| 본문 발췌 전체 위치·크기 | `ARTICLE_LAYOUT`의 Center·Size. 본문·패널·강조가 함께 움직임 |
| 밑줄·원 위치·크기·두께 | `UNDERLINE_01` / `CIRCLE_01` 계열의 LAYOUT·SHAPE 노드 |
| 빨강을 다른 색으로 변경 | 해당 강조의 COLOR 노드 색상 피커 |
| 강조 숨기기 | 해당 강조의 MERGE 노드 Blend |

밑줄·원은 원문 이미지에 합쳐 굽지 않고 독립된 편집 요소로 남긴다. 정적 위치·색 컨트롤은 애니메이션과 분리하므로 재생해도 사용자 수정값을 덮어쓰지 않는다. 대표 클립에서 이동·크기·색·숨김을 바꿨다가 복원하고 저장 후 컨트롤을 확인해야 수정 가능 검증이 끝난다.

검증은 실제 Edit 합성 캡처와 저장 후 컴포지션 재열기로 한다. PNG는 요청 길이 대신 기본 스틸 길이로 들어갈 수 있어 실제 길이를 확인하고 교정해야 한다. 원의 write-on과 페이드 제어는 사용자의 위치·색·숨김 제어와 분리한다.

분석 캡처는 macOS `/tmp` 임시 디렉터리에 둔다. Resolve가 참조하는 실제 이미지·음원은 import 전에 `article-assets/`·`audio-assets/` 같은 유지할 출력 폴더로 저장한다. 참고 영상의 초와 편집 타임라인의 경과 시간·Resolve TC는 구분한다. 원문을 확인하지 못하면 인용문을 만들지 않으며, 효과음 다운로드나 배치가 실패하면 미삽입 큐시트를 채팅에 남긴다.

## 측정·촬영 규칙을 읽는 법

- Look은 [공통 측정 규약](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/references/look-scopes.md)에 따라 같은 유효 영상 영역·물체 ROI를 비교한다. 99 IRE 이상 비율은 클리핑과 다르며 RGB 채널·디테일을 별도로 본다.
- 노출 스크립트의 0–1020 밝기 근사치와 스톱·IRE를 바꿔 쓰지 않는다. +1/+2스톱은 선택 비교이며 중간값·무조정도 가능하다.
- [Pivot 로컬 표](../plugins/akbun-editvideo/skills/akbun-davinciresolve-contrast/references/pivot-reference.md)는 인터넷 검색 없이 사용할 수 있다. DWG의 노드 연결은 입력 CST→노출→WB→대비→채도·선택 보정→출력 CST이며, 대비를 먼저 조정할 수 있다.
- devtalk는 주 음성(내레이션)을 화면과 구분하며 주장 문장을 두 번 녹음할 의무가 없다. 컷 수·샷 길이는 출발점이고 이야기의 pause·자료 읽기 시간을 보존한다. 그래픽 도구가 미정이면 아이디어를 유지하고 다른 편집을 진행한다.
- 1.2.0부터 SFX 스킬이 공통 사운드 디자인을 맡고 BGM 스킬이 이를 참조한다. 이전의 효과음 개수·단일 BGM·고정 상대 레벨 규칙은 장면별 검청 기준으로 바뀌었다.
- 1.1.0부터 도시 컷 스킬은 `davinciresolve-cut-citymontage`에서 `akbun-davinciresolve-cut-new-york`로 변경됐다. 저장한 호출문은 새 이름으로 바꾼다.

## 버전과 세부 절차

이 매뉴얼은 스킬 선택을 돕는 안내서다. DaVinci Resolve AI Assistant 2026.9 기준으로 사용하며, 특정 버전·도구·스크립트 조건, 입력 확인, 되돌리기, 검증 방법은 각 스킬의 `SKILL.md`에서 확인한다. 그래픽 제작 도구를 아직 선택하지 않았다면 기획 단계에서는 그래픽 아이디어만 정리하고, 도구를 정한 뒤 해당 제작 스킬을 사용한다.

## 재사용 자막 템플릿

`$akbun-davinciresolve-caption-template`에 문구·표시 시간을 준다. 외형 지정이 없으면 `Akbun Cinema`가 기본이다. 하단 중앙·흰 글자·검은 외곽선이며 애니메이션·효과음은 없다. Source Han Sans KR Regular, 한 줄 우선·최대 두 줄을 사용하고 대표 자막의 가독성을 확인한다. workflow의 자동 스타일 선택만으로 이 기본값을 바꾸지 않는다. 타이핑·키워드를 요청하면 참고 영상/구간을 줄 수 있다. AI가 `/tmp`에 직접 캡처해 글자 공개 순서·정렬·색을 분석한다. 문장형 `Akbun Typewriter`와 큰 세리프 키워드형 `Akbun Keyword`는 Text+·도형으로 구성해 문구와 강조를 다시 편집할 수 있다.

템플릿만 요청하면 `~/Downloads/Akbun-Caption/<내용해시>/`의 `.drfx`·setting 3개·`readme.md` 사용설명서를 받는다. Finder에서 더블클릭해 Resolve에 설치하고 Edit → Effects → Titles에서 찾아 본편 위의 별도 비디오 트랙에 드래그한다. 이 설치는 다음 프로젝트에도 유지되며 폰트는 별도다. 원본 패키지는 백업한다.

Inspector에서 문구·위치·크기와 밑줄/원의 Visibility를 조절한다. 문장형 Reveal Duration은 클립 길이에 대한 비율이며 기본 0.65다. 타이핑·키워드의 글꼴은 오뮤 다예쁨체·나눔명조를 기본으로 확인하고 OFL 대안으로 나눔손글씨 펜을 안내한다. 문구 변경 뒤 강조 위치는 다시 맞춘다. Epidemic Sound 연결이 안 되면 효과음의 분·초·길이·검색어·오디오 트랙을 채팅으로 받는다.

호출명 변경: `davinciresolve-article-overlay` → `akbun-davinciresolve-article-overlay`, `davinciresolve-caption-template` → `akbun-davinciresolve-caption-template`. 이전 호출명 대신 새 이름을 사용한다.

## 문서에서 설명 영상 만들기

[akbun-davinciresolve-explainer](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer/SKILL.md)는 촬영본 없이 글·PPTX·이미지를 설명형 모션그래픽으로 바꾼다. PPTX는 슬라이드마다 한 장면으로 배치를 옮기고, 글은 장면을 설계하며, 설명용 이미지는 구조와 글자를 도형·Text+로 다시 만든다. 스타일 참고용 이미지는 스타일만 추출한다.

예: `$akbun-davinciresolve-explainer 이 PPTX를 설명 영상으로 만들어줘. 글자와 등장 시점을 Edit Inspector에서 바꿀 수 있게 남겨줘.`

1. 기술 내용·계산을 확인하고 회사명·실제 IP 등 민감 정보를 제거한다.
2. 대본·스토리보드를 확인한다. PPTX는 내레이션만 확인하며 이미 승인한 내용은 다시 묻지 않는다.
3. 별도 1920×1080 타임라인에 비디오·오디오 각 5개 트랙과 장면별 Fusion 타이틀을 만든다. fps는 지정값·프로젝트 값을 사용하고 새 프로젝트에 기준이 없으면 24fps로 시작한다.
4. 장면별 마지막 프레임과 대표 중간 프레임, Inspector 수정·트림·환경설정 복원을 확인한다.
5. 타임라인, 시작 시각·길이·내레이션을 담은 대본, 편집 가이드, 검수 스틸을 받는다. 녹음이 없으면 A1은 비어 있으며 대본만 제공한다.

Edit 페이지에서 클립 선택 → Inspector → Video → Title의 그룹을 펼친다. 글자 칸, 보이기 체크박스, 클립 시작 기준 등장 시점(초), 위치 이동을 바꿀 수 있다. 위치 `(0.5, 0.5)`는 원래 자리다. 도형·색 수정은 Fusion의 Template 내부에서 하며 Timing 노드는 유지한다.

배경·본문·선·정상 강조·문제의 기본 5색과 노랑 채움 안 검정 글자 예외를 사용한다. 전환은 약 0.3초로 24fps에서 7프레임, 30fps에서 9프레임이다. 결과는 편집 가능한 타임라인이며 외부 MP4로 대체하지 않는다. Resolve 연결이나 필수 기능이 없으면 대본·스토리보드와 미적용 항목을 전달한다.
