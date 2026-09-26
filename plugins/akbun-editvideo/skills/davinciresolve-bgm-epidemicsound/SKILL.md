---
name: davinciresolve-bgm-epidemicsound
description: DaVinci Resolve Studio의 Epidemic Sound 플러그인(Workspace → Workflow Integrations → Epidemic Sound)에서 영상 클립과 말하는 내용의 분위기에 맞는 배경음악을 검색해 후보 몇 곡을 들어 보고, 1곡을 골라 왜 골랐는지 사용자에게 말한 뒤 A4 MUSIC 트랙에 넣고 곡명·아티스트를 작업 로그에 남긴다. "배경음악 골라줘", "BGM 후보 보여줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-bgm-epidemicsound

작업 타임라인의 클립과 비트 시트를 보고 그 영상에 맞는 배경음악을 Epidemic Sound 플러그인에서 고른다. 어떤 음악이 맞는지는 클립의 분위기·말의 속도·화면이 바뀌는 리듬을 보고 그때 판단하고, 미리 정한 장르나 BPM에 맞추지 않는다. 말소리를 가리는 보컬만 피한다.

후보 3~5곡을 들어 보고 1곡을 고른 뒤, 넣기 전에 사용자에게 "후보 N곡 중 <곡명> – <아티스트>를 골랐다, 이유는 …"라고 말한다. 다운로드는 라이선스 사용 기록이 남으므로 사용자 확인 뒤 한다(미리 허용했으면 보고만 한다). 곡은 `davinciresolve-story-devtalk` 트랙 배치의 A4 `MUSIC`에 영상 길이만큼 넣고 끝은 2초 페이드 아웃, 레벨은 `davinciresolve-audio-delivery`가 맞춘다. 작업 로그 `오디오` 절에 곡명·아티스트·후보 목록·선택 이유를 남긴다. 플러그인이 없거나 로그인이 안 됐으면 멈추고 안내한다.
