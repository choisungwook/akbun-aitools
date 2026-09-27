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
| 말소리 없는 여행 영상 전체를 편집하고 싶음 | [akbun-davinciresolve-workflow](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/SKILL.md) | 원본 타임라인을 보존하면서 촬영 시간순 타임라인부터 컷, 색보정, 개인정보 보호, 자막, 오디오, 출력까지 단계별로 진행한다. |
| 한 단계만 처리하고 싶음 | 아래의 해당 작업별 스킬 | 전체 workflow를 쓰지 않고 필요한 색보정·컷·자막·오디오·출력만 따로 요청한다. |

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
| 대사 자막, 키워드, 장면 설명 추가 | [davinciresolve-subtitle-devtalk](../plugins/akbun-editvideo/skills/davinciresolve-subtitle-devtalk/SKILL.md): 전사와 대조해 대사 자막과 필요한 강조·코멘트를 넣는다. |

편집 스타일이 헷갈리면 핵심이 `원리 설명`이면 essay, `진행과 결과`이면 project, `생각의 변화`이면 reflection을 고른다. 하루나 주차 diary라도 실제 경험의 진행이 중심이면 project, 사건 뒤 관점이 달라진 것이 중심이면 reflection이 적합하다.

## 말소리 없는 여행 영상

전체 순서를 맡길 때는 [akbun-davinciresolve-workflow](../plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/SKILL.md)를 쓴다. 이 workflow는 시간순 타임라인을 만들고 복제본에서 작업을 이어간다. 일부 작업만 원하면 아래 스킬을 직접 고른다.

| 원하는 작업 | 스킬과 동작 |
|---|---|
| 클립을 촬영 시각 순서로 새 타임라인에 배치 | [akbun-davinciresolve-timeline-chrono](../plugins/akbun-editvideo/skills/akbun-davinciresolve-timeline-chrono/SKILL.md): 기존 타임라인을 수정하지 않고 촬영 시각 메타데이터로 배열한다. |
| 빈 화면·불량 구간 컷, 흔들림 보정 | [davinciresolve-cut-travelflow](../plugins/akbun-editvideo/skills/davinciresolve-cut-travelflow/SKILL.md): 여행 장면과 자연음의 흐름을 기준으로 정리하고 삭제 전 검토 표시를 남긴다. |
| 여행 자막과 장소·시간 챕터 | [davinciresolve-subtitle-travelnote](../plugins/akbun-editvideo/skills/davinciresolve-subtitle-travelnote/SKILL.md): 장소·시간·분위기를 짧은 한글 자막과 챕터로 전달한다. |
| 여행 영상 오디오와 최종 파일 | [davinciresolve-audio-delivery](../plugins/akbun-editvideo/skills/davinciresolve-audio-delivery/SKILL.md): 현장음·효과음·음악을 섞고 YouTube용 파일을 렌더해 결과를 확인한다. |

## 색보정은 무엇을 고를까

전체 여행 workflow를 사용하면 컷 편집 뒤 필요한 색보정 단계가 순서대로 진행된다. 개별 문제만 다룰 때는 증상에 맞는 스킬 하나를 고른다. 밝기와 화이트밸런스는 서로 다른 조정이다. 해당 색 스킬들은 Color 페이지에 각각 새 라벨 노드를 만들어 조정이 서로 구분되게 한다.

| 보이는 문제 또는 요청 | 스킬과 동작 |
|---|---|
| 클립마다 밝기가 달라 컷이 튐 | [akbun-davinciresolve-exposure](../plugins/akbun-editvideo/skills/akbun-davinciresolve-exposure/SKILL.md): Waveform 측정값으로 밝기를 맞춘다. 화이트밸런스는 변경하지 않는다. |
| 조명이나 카메라에 따라 색온도가 달라 보임 | [akbun-davinciresolve-whitebalance](../plugins/akbun-editvideo/skills/akbun-davinciresolve-whitebalance/SKILL.md): 중립 픽셀의 RGB를 기준으로 클립 간 색 균형을 맞춘다. |
| Log 영상이 흐릿하고 물 빠진 것처럼 보임 | [akbun-davinciresolve-logconvert](../plugins/akbun-editvideo/skills/akbun-davinciresolve-logconvert/SKILL.md): Log 촬영 여부가 확인된 클립만 Rec.709로 변환한다. 촬영 형식이 불확실하면 추측해 변환하지 않는다. |
| 화면이 밋밋하거나 대비 조정이 필요함 | [akbun-davinciresolve-contrast](../plugins/akbun-editvideo/skills/akbun-davinciresolve-contrast/SKILL.md): Pivot 기준으로 대비를 조정하고 밝고 어두운 영역의 손실을 확인한다. |
| 변환·대비 후 색이 약함 | [akbun-davinciresolve-saturation](../plugins/akbun-editvideo/skills/akbun-davinciresolve-saturation/SKILL.md): 측정값이 낮은 클립의 채도만 보충한다. 채도를 낮추는 작업은 하지 않는다. |
| 하늘만 따로 진하게 하거나 밝기 조정 | [akbun-davinciresolve-sky](../plugins/akbun-editvideo/skills/akbun-davinciresolve-sky/SKILL.md): 하늘 색상 범위에 한해 채도와 밝기를 조절하고 적용 가능 여부를 확인한다. |

스코프 수치는 클립 간 일관성을 판단하는 근거이지, 최종 화면이 눈에 적절한 밝기라는 보장은 아니다. 사용자가 확인한 보기 환경에서는 예상보다 1–2스탑 올려야 정상 밝기로 보인 경험이 있으므로, 수치를 일괄 적용하지 말고 실제 모니터링 환경과 기준 화면에서 확인해 조정한다.

## 개인정보, 그래픽, 음악, 출력

| 필요 | 스킬과 동작 |
|---|---|
| 영상에서 얼굴·번호판·개인정보 가리기 | [davinciresolve-face-privacy](../plugins/akbun-editvideo/skills/davinciresolve-face-privacy/SKILL.md): Color 페이지에서 가릴 대상을 추적하고 타임라인에 확인 표시를 남긴다. |
| Fusion에서 특정 영역만 모자이크 | [davinciresolve-face-mosaic](../plugins/akbun-editvideo/skills/davinciresolve-face-mosaic/SKILL.md): 새 Mosaic Blur 노드와 마스크로 필요한 영역을 가린다. |
| 챕터 카드·비교표 등 모션그래픽 만들기 | [davinciresolve-gfx-hyperframes](../plugins/akbun-editvideo/skills/davinciresolve-gfx-hyperframes/SKILL.md): HyperFrames로 그래픽 카드를 만든다. 촬영 전 기획에서는 먼저 그래픽의 목적만 정하고, 사용할 제작 도구는 결정된 경우에만 이 스킬을 선택한다. |
| 영상 분위기에 맞는 배경음악 후보 찾기 | [davinciresolve-bgm-epidemicsound](../plugins/akbun-editvideo/skills/davinciresolve-bgm-epidemicsound/SKILL.md): Epidemic Sound에서 영상과 말의 분위기에 맞는 후보를 찾고 선택 이유를 기록한다. |
| 장면 전환·키워드에 효과음 추가 | [davinciresolve-sfx-epidemicsound](../plugins/akbun-editvideo/skills/davinciresolve-sfx-epidemicsound/SKILL.md): Epidemic Sound 효과음을 필요한 이벤트에 배치한다. |
| YouTube Shorts 후보 만들기 | [davinciresolve-youtube-shorts](../plugins/akbun-editvideo/skills/davinciresolve-youtube-shorts/SKILL.md): 선택한 타임라인에서 세로 영상 후보를 만들고 원본과 오디오 구성을 보존한다. |
| YouTube 기본 렌더 출력 | [davinciresolve-export-youtube](../plugins/akbun-editvideo/skills/davinciresolve-export-youtube/SKILL.md): 타임라인 해상도에 맞는 YouTube 렌더 프리셋을 고르고 결과 해상도를 확인한다. |

## 버전과 세부 절차

이 매뉴얼은 스킬 선택을 돕는 안내서다. DaVinci Resolve AI Assistant 2026.9 기준으로 사용하며, 특정 버전·도구·스크립트 조건, 입력 확인, 되돌리기, 검증 방법은 각 스킬의 `SKILL.md`에서 확인한다. 그래픽 제작 도구를 아직 선택하지 않았다면 기획 단계에서는 그래픽 아이디어만 정리하고, 도구를 정한 뒤 해당 제작 스킬을 사용한다.
