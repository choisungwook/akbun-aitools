---
name: davinciresolve-bgm-epidemicsound
description: DaVinci Resolve 영상의 이야기·장면에 맞는 Epidemic Sound 배경음악 후보와 선택 이유를 제시하고, 요청하면 한 곡 또는 여러 곡·스템·여백을 편집한다. Workflow Integration 또는 연결된 MCP를 사용하며 복제 타임라인·음악 전환·믹싱·검토 마커는 davinciresolve-sfx-epidemicsound의 공통 기준을 따른다. "배경음악 골라줘", "BGM 후보 보여줘", "여러 음악 연결해줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-bgm-epidemicsound

음악만 요청할 때의 진입점이다. 먼저 [사운드 디자인 공통 기준](../davinciresolve-sfx-epidemicsound/SKILL.md)의 범위·환경·큐시트와 「여러 BGM과 음악 효과」를 읽는다. 그 문서가 복제·검색 경로·권한·자산 보관·트랙·믹싱·검토 마커·컷 변경의 유일한 기준이다.

1. 장면·내레이션·확정 비트와 유지할 곡을 확인한다. 장르나 BPM을 먼저 고정하지 않고 감정·말의 밀도·리듬으로 후보를 찾는다.
2. `비트/구간 | 후보 곡·아티스트·ID | 선택 이유 | 사용할 phrase/스템 | 전환·여백`을 제시한다. 한 곡이나 전 구간 BGM을 강제하지 않는다. 말이 있는 구간은 보컬 간섭을 확인하고 필요하면 instrumental/스템을 고른다.
3. 후보 요청만이면 여기서 끝낸다. 편집 요청이면 공통 기준의 복제본 확보 후 음악 관련 cue만 실행한다. 같은 사운드 작업의 SFX 단계가 만든 검증된 복제본이 있으면 그 ID를 이어받아 음악을 중복 추가하지 않는다.
4. 곡 전환·재진입·의도된 무음과 판단이 필요한 지점을 공통 기준의 `AUDIO_REVIEW`로 남기고 작업본·큐시트를 전달한다.

연결 불가나 미지원 기능도 공통 기준의 대안을 따른다. 렌더가 필요할 때만 `davinciresolve-audio-delivery`로 이어가며, BGM만 요청한 영상에 다른 효과음을 임의로 추가하지 않는다.
