---
name: davinciresolve-audio-delivery
description: DaVinci Resolve에서 사운드 디자인 공통 스킬로 믹스를 준비하고 YouTube용 4K 파일을 렌더해 해상도·fps·길이·오디오·LUFS·True Peak를 검증한다. "오디오 믹싱해줘", "4K로 렌더해줘", "유튜브 업로드 준비" 요청에 사용한다. 효과음·BGM·믹싱은 davinciresolve-sfx-epidemicsound를 참조하며 업로드는 명시 요청 때만 한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# davinciresolve-audio-delivery

최종 믹스의 파일 출력과 검증을 맡는다. 효과음·BGM·믹싱을 요청받으면 먼저 [사운드 디자인 공통 스킬](../davinciresolve-sfx-epidemicsound/SKILL.md)을 읽어 요청 범위만 수행한다. 그 스킬의 복제 타임라인 ID·큐시트·트랙 맵을 넘겨받아 출력하고, 이미 준비된 믹스를 다시 배치하지 않는다.

## 오디오 작업 참조

- 타임라인 복제, 원음 보존, 트랙, SFX·여러 BGM 편집, EQ·덕킹·레벨 판단: 공통 스킬 1–6절.
- 검토 마커·미적용 항목·사용자 확인·작업 로그: 공통 스킬 7–8절.
- 컷 변경 반영: 공통 스킬 8절. 링크·source in/out·속도를 확인하고 긴 음악 cue를 단순 이동하지 않는다.
- 출력만 요청한 경우 기존 믹스를 바꾸지 않는다. 측정 실패로 믹스를 수정해야 하면 공통 스킬의 복제 절차부터 적용한다.

`AUDIO_REVIEW`가 남으면 검토용 프리뷰와 최종 승인 상태를 구분한다. 미적용·검증 실패를 숨기거나 사용자 승인으로 기록하지 않는다. 파일 출력 요청은 업로드 요청과 다르다.

## 출력

렌더 전 설치된 Resolve의 사용 가능한 포맷·코덱을 확인한다. 운영체제·에디션·버전에 따라 다르므로 실제 목록을 우선한다.

```bash
python3 -c "import DaVinciResolveScript as dvr; p = dvr.scriptapp('Resolve').GetProjectManager().GetCurrentProject(); print(p.GetRenderFormats()); print(p.GetRenderCodecs('mp4'))"
```

| 항목 | 값 | 없을 때 |
|---|---|---|
| 해상도 | 3840×2160 | - |
| 프레임레이트 | 타임라인 프레임레이트(`akbun-davinciresolve-workflow` 1단계에서 확정) | - |
| 비디오 코덱 | H.264(기본) 또는 H.265(사용자 지정) | H.265 없으면 H.264로 바꾸고 로그에 적음 |
| 비트레이트 | 30fps 이하: H.264 45 Mbps, H.265 30 Mbps. 60fps: H.264 68 Mbps, H.265 45 Mbps(YouTube 4K 권장) | - |
| 오디오 | AAC, 48 kHz, 320 kbps, 스테레오 | AAC 없으면 Linear PCM으로 렌더한 뒤 `ffmpeg -c:v copy -c:a aac -b:a 320k`로 변환하고 로그에 적음 |
| 파일명 | `<작업 타임라인 이름>_youtube4k.mp4` | - |
| 저장 위치 | `<출력 폴더>/render/` | 사용자가 지정한 경로를 우선 사용한다. 같은 이름 파일이 있으면 덮어쓰지 않고 사용자에게 알린다 |

렌더 후 파일을 검사한다. Resolve가 없어도 돌릴 수 있게 `ffprobe`를 쓴다.

```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels:format=duration -of default=noprint_wrappers=1 "<렌더 파일>"
```

| 항목 | 통과 기준 |
|---|---|
| 해상도 | 3840×2160 |
| 프레임레이트 | 타임라인과 동일 |
| 길이 | `duration`(초) × 타임라인 프레임레이트를 반올림한 프레임 수가 타임라인 프레임 수와 1프레임 이내 |
| 오디오 스트림 | AAC 스트림 1개, 48 kHz, 2채널 |
| 라우드니스 | 이 저장소의 YouTube 기본 납품 목표: 통합 -14 LUFS ±1, True Peak -1 dBTP 이하. 다른 납품 목표를 명시한 경우 그 값과 이유를 기록 |
| 재생 | 처음·중간·끝을 재생해 미디어 누락·의도하지 않은 검은 화면/무음이 없음. 의도한 black·fade·여백은 큐시트와 대조 |

라우드니스는 **최종 인코딩된 파일 전체**를 측정한다. 이는 이 저장소의 납품 기본값이며 모든 플랫폼의 강제 규격이나 짧은 효과음의 목표값이 아니다. 목표에 맞추려고 의도한 여백·강약을 망가뜨리면 믹스 의도와 차이를 보고하고 납품 목표를 조정한다.

```bash
ffmpeg -i "<렌더 파일>" -af ebur128=peak=true -f null - 2>&1 | tail -12
```

하나라도 실패하면 렌더 설정을 고쳐 다시 렌더하고, 실패 항목과 원인을 로그에 적는다. 같은 항목이 2번 연속 실패하면 멈추고 사용자에게 알린다.

## YouTube 업로드

- YouTube 직접 업로드는 사용자가 요청할 때만 한다. 사용자가 직접 업로드를 명시하면 제목·설명·공개 상태·카테고리·썸네일·저장 위치를 채워 바로 진행한다. 공개 상태가 지정되지 않으면 비공개로 둔다.
- 기본 공개 상태는 비공개(Private)로 설정한다. 사용자가 바꾸라고 하기 전에는 공개·일부 공개로 올리지 않는다.
- 제목과 설명은 타임라인에서 확인한 장소·장면만 사용해 작성한다. 챕터는 `davinciresolve-subtitle-travelnote` 목록과 타임라인 마커를 맞추고 첫 장은 `00:00`으로 시작한다.
- 사용자가 요청하면 서로 다른 클립에서 3개의 16:9 썸네일 후보를 추출한다. 문구 요청이 있으면 Avenir Next Condensed나 Arial Black 등 설치된 굵은 글꼴을 우선하고, 얼굴이 보이는 프레임은 프라이버시 마스크가 반영된 결과에서 추출한다. 후보를 보여 주고 선택한 후보를 업로드 설정에 지정한다.
- 제목, 설명, 챕터, 장비(iPhone, Insta360 Luna Ultra), 음악 출처(Epidemic Sound 곡명·아티스트), 썸네일을 함께 적용한다. 모르는 장비·곡 정보는 지어내지 않는다.
- Deliver의 `Location`은 렌더 파일 저장 폴더다. 사용자가 Home/Downloads를 지정하면 `/Users/<사용자>/Downloads`에 저장한다. YouTube 지리적 촬영 위치와 구분한다.
- 설명란 초안을 작업 로그에 남긴다.

## 작업 로그

공통 사운드 스킬의 큐시트를 중복 작성하지 않고 작업본 ID와 큐시트 경로를 인계받는다. `검증` 절에는 실제 렌더 파일 경로, 해상도·fps·길이·코덱·sample rate·채널, 통합 LUFS·True Peak, 검청한 구간, 남은 `AUDIO_REVIEW`를 적는다. 측정하지 않은 값을 예시에서 복사하지 않는다.

## 하지 않는 것

- 타임라인 프레임레이트 변경, 이 4K 납품 요청에서 임의로 4K 미만 출력
- 렌더 파일 검사 없이 완료 보고
- 사용자 요청 없는 업로드, 비공개 아닌 기본 공개 상태
- 출처·장비·검증값 추측, 미해결 마커를 사용자 승인으로 처리
