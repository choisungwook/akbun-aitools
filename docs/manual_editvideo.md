# 영상 편집 스킬 사용자 매뉴얼

이 문서는 `akbun-editvideo` 플러그인의 스킬을 어떤 상황에 고르고, 각 스킬이 어떤 문제를 해결하는지 안내한다. 실제 작업 지침과 세부 조건은 연결된 `SKILL.md`가 기준이다.

영상·Resolve 용어는 [용어사전](terms_editvideo.md)을 참고한다.

스킬은 이름을 직접 불러 사용할 수 있다. 예: `$akbun-vlog-prepared-devtalk`. 전체 작업을 맡는 workflow 스킬은 필요한 하위 스킬 문서를 읽어 순서대로 진행하고, 각 하위 스킬은 원하는 단계만 따로 요청할 때 쓴다.

## 어떤 흐름을 고를까

| 상황 | 시작할 스킬 | 해결하는 문제와 동작 |
|---|---|---|
| 아직 촬영 전이고 경험을 영상 이야기로 만들고 싶음 | [akbun-vlog-prepared-devtalk](../plugins/akbun-editvideo/skills/akbun-vlog-prepared-devtalk/SKILL.md) | 한 번에 하나씩 인터뷰하며 실제 경험을 5–7분 이야기로 정리하고, 비트·샷·스케치·촬영 계획까지 준비한다. 얼굴 비노출을 전제로 하고 모션그래픽 도구는 미리 정하지 않는다. |
| 이야기는 정했고 촬영 방법만 필요함 | [akbun-vlog-shootplan](../plugins/akbun-editvideo/skills/akbun-vlog-shootplan/SKILL.md) | 촬영 장비·음성·화면 녹화의 역할과 촬영 순서를 정한다. 불필요한 장면을 과하게 찍지 않도록 핵심 샷을 고른다. |
| 특정 샷의 카메라 구도와 빛을 정하고 싶음 | [akbun-vlog-shotsketch](../plugins/akbun-editvideo/skills/akbun-vlog-shotsketch/SKILL.md) | 이야기 비트에 필요한 한 샷의 프레임, 카메라 위치, 동작, 조명과 얼굴 비노출 확인을 그림과 표로 만든다. |
| 전체 이야기에서 어떤 장면을 어떤 순서로 찍을지 보고 싶음 | [akbun-vlog-storyboard](../plugins/akbun-editvideo/skills/akbun-vlog-storyboard/SKILL.md) | 확정된 비트를 음성·B-roll·화면 녹화·필요한 그래픽 아이디어에 연결하고 핵심 setup을 스케치한다. |
| 말소리 있는 개발자 영상의 촬영 클립을 편집하고 싶음 | [davinciresolve-story-devtalk](../plugins/akbun-editvideo/skills/davinciresolve-story-devtalk/SKILL.md) | 전사·스토리 비트·컷·화면·자막·그래픽·오디오 작업을 조율한다. 촬영 전 이야기 기획은 `akbun-vlog-prepared-devtalk`에서 시작한다. |
| 얼굴 없이 보이스오버로 공부·경험·기술 가이드·제품을 설명하고 싶음(목소리는 나중에 녹음해도 됨) | [akbun-davinciresolve-workflow-voiceover](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow-voiceover/SKILL.md) | 대본을 먼저 확정하고, 가이드 음성으로 화면·오버레이를 맞춘 뒤 최종 보이스오버를 복제본에서 교체한다. 감독 연출표로 움직임·오버레이·효과음의 박자를 정하고 편집 뒤 점검한다. |
| 말소리 없는 여행 영상 전체를 편집하고 싶음 | [akbun-davinciresolve-workflow](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/SKILL.md) | 원본 타임라인을 보존하면서 촬영 시간순 타임라인부터 컷, 색보정, 요청된 Look, 개인정보 보호, 자막, 오디오, 출력까지 단계별로 진행한다. |
| 한 단계만 처리하고 싶음 | 아래의 해당 작업별 스킬 | 전체 workflow를 쓰지 않고 필요한 색보정·컷·자막·오디오·출력만 따로 요청한다. |

## 시나리오별 사용 순서

아래는 실제 요청의 시작점과 인계 순서다. 전체 workflow를 시작하면 표의 하위 스킬을 일일이 다시 호출하지 않아도 된다. 이미 완료한 단계는 작업 로그·타임라인에서 확인한 뒤 필요한 단계만 이어간다.

| 상황·준비된 입력 | 시작과 이어지는 스킬 | 받게 되는 결과·직접 확인할 부분 |
|---|---|---|
| 촬영 전, “32주차 개발자 diary”라는 생각만 있음 | `akbun-vlog-prepared-devtalk` → 이야기 확정 후 `akbun-vlog-storyboard`·`akbun-vlog-shotsketch`·`akbun-vlog-shootplan` | 인터뷰에서 찾은 실제 사건, 5–7분 이야기, 얼굴 없는 샷·소리의 역할·녹음·촬영 순서. 경험과 내 말투가 맞는지 확인 |
| 얼굴 없이 녹음한 설명과 화면 녹화가 있음 | `davinciresolve-story-devtalk` → essay/project/reflection 선택 → beats → cut → subtitle → 필요한 그래픽 → 사운드 → 출력 | 확정 비트에 맞춘 편집본. 비트 시트, 얼굴 노출, 핵심 문장의 이해와 사운드 마커 확인 |
| 말 없는 여행 원본을 통째로 편집 | `akbun-davinciresolve-workflow` → 시간순 타임라인 → 트랙 준비 → 컷·색보정 → 선택 Look → 개인정보·자막 → 사운드 → 출력 | 원본을 보존한 여행 편집본. 시간순 배열, 주요 장면과 자연음, 검토 마커 확인 |
| 도시 클립의 리듬만 다듬고 싶음 | `akbun-davinciresolve-cut-new-york` → 바뀐 구간을 자막·사운드 스킬에 전달 | 와이드·미디엄·디테일과 움직임을 잇는 몽타주. 삭제 후보와 자막·소리의 새 위치 확인 |
| 컷은 끝났고 풍경 소리·효과음·음악을 함께 보강 | `davinciresolve-sfx-epidemicsound` → 필요하면 `davinciresolve-audio-delivery` | 오디오 직전 상태를 복제한 작업본, 환경음·동작음·필요한 여러 BGM, 검토 큐시트. `AUDIO_REVIEW` 순서로 들어보기 |
| 음악 후보만 비교하고 싶음 | `davinciresolve-bgm-epidemicsound`의 후보 단계 | 비트별 후보·선택 이유·전환 제안. 타임라인은 수정하지 않으며 장면의 감정과 음악이 맞는지 판단 |
| 이미 있는 BGM을 여러 곡으로 나누거나, 말할 때 잠시 빼고 재진입 | `davinciresolve-bgm-epidemicsound` → 사운드 공통 기준의 음악 편집·믹싱·마커 절 | 복제본에서 phrase·스템·tail·여백을 편집. 곡의 경계, 말 가림, 재진입 강도를 확인 |
| 카드·버튼·키워드 소리만 필요함 | `davinciresolve-sfx-epidemicsound`에 대상 이벤트/구간 지정 | 복제본의 지정 SFX만 편집. 기존 음악 유지, 강조 타이밍과 반복 피로 확인 |
| 사운드를 끝낸 뒤 컷 길이가 달라짐 | 컷 스킬의 변경 목록 → `davinciresolve-sfx-epidemicsound`의 컷 변경과 인계 | 앵커·스템·덕킹·전환·마커를 다시 맞춘 결과. 음악 phrase와 효과음 싱크가 어긋나지 않는지 확인 |
| 화면이 어둡고 야간 네온 분위기를 원함 | `akbun-davinciresolve-exposure` 및 필요한 WB·대비·채도 → `akbun-davinciresolve-look-tokyo-night` | 기본 밝기와 새 LOOK 노드가 분리된 결과. 실제 보기 환경에서 밝기·간판 디테일 확인. +1/+2스톱은 선택 비교 |
| 편집·믹스 완료, 업로드할 파일만 필요함 | 4K와 오디오 계측은 `davinciresolve-audio-delivery`; 현재 타임라인 해상도의 기본 프리셋은 `davinciresolve-export-youtube` | 렌더 파일과 수행한 검증 결과. `AUDIO_REVIEW` 미해결 목록 확인. 렌더 요청만으로 업로드하지 않음 |
| 여행 편집본은 끝났는데 도입부가 밋밋함 | `akbun-davinciresolve-searchhook` → 후보 선택 → 필요하면 `davinciresolve-sfx-epidemicsound` → 출력 | 훅 후보 3~5개와 추천, 완성 타임라인을 복제해 앞에 훅을 넣은 훅 타임라인. 제목·썸네일과 첫 5초가 같은 것을 말하는지, 문구가 사실인지, `HOOK_BGM` 마커의 음악 길이 보정 확인 |
| 공부한 기술을 튜토리얼처럼 설명하고 싶음. 화면 녹화와 결과물이 있음 | `akbun-davinciresolve-workflow-voiceover` → explainer 스타일 → 대본 → 감독 연출표 → 가이드 음성 → 조립 → 오버레이 → 최종 보이스오버 → 사운드 → 점검 | 결과를 먼저 보여 주는 도입, 단계별 챕터, 결과 카드와 진행 배지. 대본·연출표 두 번 확인, `VO_FIT`·`DIRECT`·`AUDIO_REVIEW` 마커 확인 |
| 새로 산 장비·도구를 소개하고 싶음. 카메라로 여러 각도를 찍을 수 있음 | `akbun-davinciresolve-style-product`로 촬영 각도 목록 확인 → 촬영 → `akbun-davinciresolve-workflow-voiceover` | 와이드·측면·탑다운·매크로·어깨 너머 샷 목록과 제품 옆 주석이 붙은 편집본. 사양·가격 문구가 사실인지 확인 |
| 편집은 됐는데 화면이 밋밋하거나 산만함 | `akbun-davinciresolve-director` 3절 점검 → 필요하면 연출표 수정 → `akbun-davinciresolve-overlay`·사운드 skill | 화면 변화와 효과음 짝, 변화 없는 긴 구간, 분당 효과음 수 표와 `DIRECT` 마커. 스크립트 표만 보지 말고 표시된 곳을 재생해 판단 |
| 결과 사진 몇 장만 본편 위에 띄우고 싶음 | `akbun-davinciresolve-overlay` | 둥근 카드와 등장·퇴장 움직임, 확인 스틸. 카드가 피사체·글자를 가리지 않는지 확인 |
| 완성한 가로 영상에서 Shorts 후보 추출 | `davinciresolve-youtube-shorts` | 별도 세로 후보, 원래 오디오 처리 보존. 잘린 말·음악 tail·세로 구도 확인 |

예: `$davinciresolve-sfx-epidemicsound 현재 여행 타임라인을 복제해서 바다→거리 전환과 현장음을 살리고, 필요한 여러 BGM도 연결해줘. 내가 들을 곳은 마커로 남겨줘.`

예: `$akbun-davinciresolve-searchhook 완성한 한강 산책 타임라인에서 훅 후보를 찾아줘. 제목은 아직 없으니 후보마다 제목도 같이 제안해줘.`

예: `$akbun-davinciresolve-workflow-voiceover 쿠버네티스 네트워크 정책을 공부한 노트로 설명 영상을 만들고 싶어. 화면 녹화는 있고, 목소리는 화면을 다 맞춘 뒤 녹음할게.`

예: `$davinciresolve-bgm-epidemicsound 32주차 diary의 집중→막힘→해결 흐름에 맞는 음악 후보만 보여줘. 아직 넣지는 말아줘.`

### 사운드 작업에서 확인할 것

효과음·환경음·여러 음악·스템·전환·믹싱의 실행 기준은 [사운드 디자인 스킬](../plugins/akbun-editvideo/skills/davinciresolve-sfx-epidemicsound/SKILL.md) 한곳에 있다. BGM 스킬은 음악만 요청하는 진입점이고, audio-delivery는 최종 파일의 출력·계측을 맡는다. Epidemic Sound 유료 계정은 Resolve Workflow Integration이나 연결된 MCP 중 사용 가능한 경로를 쓴다.

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

## 얼굴 없는 보이스오버 설명·제품 소개 영상

얼굴을 드러내지 않고 공부·경험·기술 가이드·제품을 목소리로 설명하는 영상은 [akbun-davinciresolve-workflow-voiceover](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow-voiceover/SKILL.md)로 시작한다. 이미 말하면서 찍은 클립이 있으면 아래 `말소리 있는 개발자 영상`의 devtalk 흐름이 맞고, 대본을 먼저 쓰고 목소리를 나중에 녹음하려면 이 흐름이 맞다. 참고 영상 3개를 분석한 수치가 두 스타일 skill의 `references/analysis.md`에 있다.

| 해결할 문제 | 스킬과 동작 |
|---|---|
| 대본부터 출력까지 전체 순서 | [akbun-davinciresolve-workflow-voiceover](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow-voiceover/SKILL.md): 대본·연출표를 확인받은 뒤 가이드 음성으로 화면을 맞추고, 최종 보이스오버는 `<이름>_vo_<일시>` 복제본에서 교체한다. 길이가 어긋난 문장은 Rose `VO_FIT` 마커로 알려 준다. |
| 공부·경험·튜토리얼을 어떤 화면 규칙으로 보여 줄지 | [akbun-davinciresolve-style-explainer](../plugins/akbun-editvideo/skills/akbun-davinciresolve-style-explainer/SKILL.md): 결과 먼저, 단계별 챕터 카드, 본편 위 결과 카드(폭 40%, 5~6프레임 페이드), 진행 배지, 화면 녹화 1.25초 확대, 챕터 경계 음악 비움. |
| 제품을 어떤 각도로 찍고 어떻게 보여 줄지 | [akbun-davinciresolve-style-product](../plugins/akbun-editvideo/skills/akbun-davinciresolve-style-product/SKILL.md): 한 장면을 와이드·측면·탑다운·매크로·어깨 너머로 찍고, 손으로 내미는 첫 등장, 히어로 샷 5초 push, 제품 옆 손글씨 주석과 2단 글자, 도입 매크로로 끝나는 결말. |
| 사진·영상·화면 캡처를 본편 위에 자연스럽게 띄우기 | [akbun-davinciresolve-overlay](../plugins/akbun-editvideo/skills/akbun-davinciresolve-overlay/SKILL.md): 둥근 카드를 `OVERLAY` 트랙에 놓고 pop·slide·fade를 키프레임으로 넣는다. 본편 push와 글자 타이핑 등장도 넣는다. 다른 트랙·마커·길이가 그대로인지 확인하고 스틸을 남긴다. |
| 움직임·효과음·음악이 서로 박자가 맞는지 | [akbun-davinciresolve-director](../plugins/akbun-editvideo/skills/akbun-davinciresolve-director/SKILL.md): 비트마다 화면 전환·움직임·오버레이·글자·효과음·음악 상태를 한 표로 정하고, 편집 뒤 화면 변화와 효과음의 짝, 긴 정지 구간을 점검해 Lavender `DIRECT` 마커를 남긴다. |

스타일이 헷갈리면 "무엇을 배웠고 어떻게 했나"가 중심이면 explainer, "이 물건이 무엇이고 어떻게 쓰나"가 중심이면 product를 고른다. 원리·트레이드오프 주장이 중심이면 기존 essay도 쓸 수 있다.

### DaVinci Resolve AI Assistant로 오버레이를 쓰는 법

AI Assistant에 요청할 때는 "무엇을, 어디에, 언제, 어떻게 들어오게"를 한 문장에 담으면 한 번에 들어간다. 위치는 화면 비율(왼쪽 아래가 0, 0), 길이는 초로 말하면 된다.

| 원하는 화면 | 요청 예 |
|---|---|
| 결과 사진을 옆에 띄움 | `$akbun-davinciresolve-overlay 01:00:12:00부터 4초 동안 result.png를 오른쪽 절반 가운데에 폭 40% 카드로, 6프레임 페이드로 넣어줘` |
| 두 결과를 비교 | `$akbun-davinciresolve-overlay 첫 시도 사진을 왼쪽, 개선 사진을 오른쪽에 폭 22% 세로 카드로 아래에서 올라오게 넣어줘` |
| 단계 완료 표시 | `$akbun-davinciresolve-overlay 단계가 끝날 때마다 오른쪽 위에 작은 배지를 튕기듯 넣어줘` |
| 제품 옆 주석 | `$akbun-davinciresolve-overlay 01:02:05:00에 제품 오른쪽 빈 공간에 손글씨로 '처음 켰을 때'를 타이핑되게 넣어줘` |
| 천천히 다가가는 화면 | `$akbun-davinciresolve-overlay 제품 전체가 보이는 01:03:10:00 클립을 끝까지 6% 천천히 확대해줘` |

- 카드와 글자는 컴파운드 클립이 아니라 일반 클립이다. 위치를 바꾸려면 "그 카드 지우고 왼쪽에 다시 넣어줘"라고 요청한다.
- 카드 테두리·그림자, 카드와 같은 순간의 짧은 본편 확대는 스크립트가 넣지 않는다. 필요하면 Fusion 페이지나 Inspector에서 넣도록 안내받는다.
- 글꼴은 SIL OFL 글꼴(Pretendard, Noto Serif KR, Nanum Pen Script)만 쓴다. Resolve에 없으면 설치 안내가 나온다.

### 보이스오버를 나중에 녹음할 때

1. 대본을 확정하면 휴대폰으로 대충 읽은 가이드 음성을 넣는다. 원하면 Resolve 음성 생성으로 만들 수 있지만 한국어 품질은 대표 문장으로 먼저 들어 본다.
2. 가이드 음성 길이에 맞춰 화면·오버레이를 끝낸다.
3. 마이크로 문장 번호를 말하고 녹음한 최종 음성을 준다. 복제본에서 교체되고, 가이드보다 0.5초 넘게 길거나 짧은 문장은 `VO_FIT` 마커로 표시된다.
4. 마커마다 샷 길이·문장 사이 쉼·카드 시작 중 어떻게 맞출지 고른다. 가이드 음성은 뮤트 트랙에 비교용으로 남는다.

## 말소리 있는 개발자 영상

### 촬영 후 편집 흐름

`davinciresolve-story-devtalk`은 촬영 클립이 있을 때 쓰는 편집 진행자다. 영상과 전사를 근거로 소재를 정리하고, 사용자가 확정한 이야기 비트에 맞춰 장면을 배열한다. 기본 길이는 5–7분이며, 일상·주차 diary도 단순한 할 일 목록 대신 맥락과 실제 사건·선택·변화를 중심으로 다룬다.

| 편집할 문제 | 스킬이 하는 일 |
|---|---|
| 클립에서 이야기 소재를 찾고 비트 순서로 배열 | [davinciresolve-beats-devtalk](../plugins/akbun-editvideo/skills/davinciresolve-beats-devtalk/SKILL.md): 음성을 전사해 사실과 근거를 정리하고 비트 시트를 제안한다. 타임라인 배열은 사용자가 확정한 뒤 진행한다. |
| 말의 군더더기를 덜고 이야기 호흡을 살림 | [davinciresolve-cut-devtalk](../plugins/akbun-editvideo/skills/davinciresolve-cut-devtalk/SKILL.md): 문장 단위로 침묵·필러·재녹음을 정리하되 의미 있는 멈춤은 남긴다. |
| 기술 원리나 트레이드오프를 설명 | [davinciresolve-style-essay](../plugins/akbun-editvideo/skills/davinciresolve-style-essay/SKILL.md): 주장과 근거를 중심으로 화면 녹화·자료·필요한 그래픽을 배치한다. |
| 프로젝트 진행이나 개발자 일상을 기록 | [davinciresolve-style-project](../plugins/akbun-editvideo/skills/davinciresolve-style-project/SKILL.md): 목표·장애·선택·결과의 변화를 화면과 내레이션으로 보여준다. |
| 구체적 경험에서 생각의 변화를 이야기 | [davinciresolve-style-reflection](../plugins/akbun-editvideo/skills/davinciresolve-style-reflection/SKILL.md): 상황·계기·생각·흔들림·결론의 흐름으로 편집한다. |
| 대사 자막, 키워드, 장면 설명 추가 | [davinciresolve-subtitle-devtalk](../plugins/akbun-editvideo/skills/davinciresolve-subtitle-devtalk/SKILL.md): 전사와 대조해 대사 자막과 필요한 강조·코멘트를 넣는다. 키워드·코멘트 Text+는 본편을 밀지 않고 `SUBTITLE` 트랙에 놓는다. |

편집 스타일이 헷갈리면 핵심이 `원리 설명`이면 essay, `진행과 결과`이면 project, `생각의 변화`이면 reflection을 고른다. 하루나 주차 diary라도 실제 경험의 진행이 중심이면 project, 사건 뒤 관점이 달라진 것이 중심이면 reflection이 적합하다.

## 말소리 없는 여행 영상

전체 순서를 맡길 때는 [akbun-davinciresolve-workflow](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/SKILL.md)를 쓴다. 이 workflow는 시간순 타임라인을 만들고 복제본에 비디오·오디오 트랙을 4개씩 준비한 뒤 작업을 이어간다. 그중 `HOOK` 오디오 트랙과 `HOOK_TEXT` 비디오 트랙은 편집이 끝난 뒤 훅을 만들 때 쓴다. 일부 작업만 원하면 아래 스킬을 직접 고른다.

| 원하는 작업 | 스킬과 동작 |
|---|---|
| 클립을 촬영 시각 순서로 새 타임라인에 배치 | [akbun-davinciresolve-timeline-chrono](../plugins/akbun-editvideo/skills/akbun-davinciresolve-timeline-chrono/SKILL.md): 기존 타임라인을 수정하지 않고 촬영 시각 메타데이터로 배열한다. |
| 빈 화면·불량 구간 컷, 흔들림 보정 | [davinciresolve-cut-travelflow](../plugins/akbun-editvideo/skills/davinciresolve-cut-travelflow/SKILL.md): 여행 장면과 자연음의 흐름을 기준으로 정리하고 삭제 전 검토 표시를 남긴다. |
| 도시 장면을 와이드·미디엄·디테일로 엮어 몽타주 구성 | [akbun-davinciresolve-cut-new-york](../plugins/akbun-editvideo/skills/akbun-davinciresolve-cut-new-york/SKILL.md): 건축·교통·거리의 움직임과 음악 리듬을 활용해 컷을 제안한다. 장면 삭제는 이유를 설명하고 사용자가 확인한 뒤 진행한다. |
| 여행 자막과 장소·시간 챕터 | [davinciresolve-subtitle-travelnote](../plugins/akbun-editvideo/skills/davinciresolve-subtitle-travelnote/SKILL.md): 장소·시간·분위기를 짧은 한글 자막과 챕터로 전달한다. 자막 Text+는 본편과 마커를 밀지 않고 `SUBTITLE` 트랙에 놓는다. |
| 완성본 앞에 붙일 훅(콜드 오픈·인트로) 찾기 | [akbun-davinciresolve-searchhook](../plugins/akbun-editvideo/skills/akbun-davinciresolve-searchhook/SKILL.md): 완성 타임라인의 장면을 채점해 훅 후보를 제안하고, 고른 후보만 완성 타임라인의 복제본 맨 앞에 넣는다. 영상·효과음은 함께 밀리고 잠근 BGM은 제자리에 남아 음악이 이어지며, 어긋난 음악 길이는 보정할 곳을 알려 준다. 화면 텍스트는 `HOOK_TEXT` 트랙에 일반 Text+ 클립으로 놓이므로 클립을 선택해 Inspector에서 문구를 바로 고친다. 완성 타임라인은 수정하지 않는다. |
| 여행 영상 오디오와 최종 파일 | [davinciresolve-audio-delivery](../plugins/akbun-editvideo/skills/davinciresolve-audio-delivery/SKILL.md): 사운드 공통 스킬로 준비한 믹스를 YouTube용 파일로 렌더하고 오디오·영상 결과를 계측한다. |

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
| 챕터 카드·비교표 등 모션그래픽 만들기 | [davinciresolve-gfx-hyperframes](../plugins/akbun-editvideo/skills/davinciresolve-gfx-hyperframes/SKILL.md): HyperFrames로 그래픽 카드를 만든다. 촬영 전 기획에서는 먼저 그래픽의 목적만 정하고, 사용할 제작 도구는 결정된 경우에만 이 스킬을 선택한다. |
| 영상 분위기에 맞는 배경음악 후보 찾기 | [davinciresolve-bgm-epidemicsound](../plugins/akbun-editvideo/skills/davinciresolve-bgm-epidemicsound/SKILL.md): Epidemic Sound 후보와 이유를 제시하고, 요청하면 공통 사운드 기준으로 여러 곡·스템·전환을 편집한다. |
| 효과음·환경음·여러 BGM 사운드 디자인 | [davinciresolve-sfx-epidemicsound](../plugins/akbun-editvideo/skills/davinciresolve-sfx-epidemicsound/SKILL.md): 타임라인을 복제해 현장음·효과음·음악을 설계·믹싱하고 검토 지점을 마커로 남긴다. |
| YouTube Shorts 후보 만들기 | [davinciresolve-youtube-shorts](../plugins/akbun-editvideo/skills/davinciresolve-youtube-shorts/SKILL.md): 선택한 타임라인에서 세로 영상 후보를 만들고 원본과 오디오 구성을 보존한다. |
| YouTube 기본 렌더 출력 | [davinciresolve-export-youtube](../plugins/akbun-editvideo/skills/davinciresolve-export-youtube/SKILL.md): 타임라인 해상도에 맞는 YouTube 렌더 프리셋을 고르고 결과 해상도를 확인한다. |

## 측정·촬영 규칙을 읽는 법

- Look은 [공통 측정 규약](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/references/look-scopes.md)에 따라 같은 유효 영상 영역·물체 ROI를 비교한다. 99 IRE 이상 비율은 클리핑과 다르며 RGB 채널·디테일을 별도로 본다.
- 노출 스크립트의 0–1020 밝기 근사치와 스톱·IRE를 바꿔 쓰지 않는다. +1/+2스톱은 선택 비교이며 중간값·무조정도 가능하다.
- [Pivot 로컬 표](../plugins/akbun-editvideo/skills/akbun-davinciresolve-contrast/references/pivot-reference.md)는 인터넷 검색 없이 사용할 수 있다. DWG의 노드 연결은 입력 CST→노출→WB→대비→채도·선택 보정→출력 CST이며, 대비를 먼저 조정할 수 있다.
- devtalk는 주 음성(내레이션)을 화면과 구분하며 주장 문장을 두 번 녹음할 의무가 없다. 컷 수·샷 길이는 출발점이고 이야기의 pause·자료 읽기 시간을 보존한다. 그래픽 도구가 미정이면 아이디어를 유지하고 다른 편집을 진행한다.
- 1.2.5부터 오버레이·감독·설명형/제품 스타일·보이스오버 workflow가 추가됐다. 스타일 수치는 참고 영상 일부 구간을 0.5초 간격으로, 나머지를 10·20초 간격으로 본 결과라 출발점이다. 범위는 각 스타일의 `references/analysis.md`에 있다.
- 1.2.0부터 SFX 스킬이 공통 사운드 디자인을 맡고 BGM·출력 스킬이 이를 참조한다. 이전의 효과음 개수·단일 BGM·고정 상대 레벨 규칙은 장면별 검청 기준으로 바뀌었다.
- 1.1.0부터 도시 컷 스킬은 `davinciresolve-cut-citymontage`에서 `akbun-davinciresolve-cut-new-york`로 변경됐다. 저장한 호출문은 새 이름으로 바꾼다.

## 버전과 세부 절차

이 매뉴얼은 스킬 선택을 돕는 안내서다. DaVinci Resolve AI Assistant 2026.9 기준으로 사용하며, 특정 버전·도구·스크립트 조건, 입력 확인, 되돌리기, 검증 방법은 각 스킬의 `SKILL.md`에서 확인한다. 그래픽 제작 도구를 아직 선택하지 않았다면 기획 단계에서는 그래픽 아이디어만 정리하고, 도구를 정한 뒤 해당 제작 스킬을 사용한다.
