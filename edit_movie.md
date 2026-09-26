# 말하는 개발자 브이로그 편집 가이드

`akbun-editvideo` plugin으로 얼굴 없이 목소리로 말하는 개발자 브이로그를 촬영 계획부터 4K 렌더까지 만드는 순서다. skill은 촬영 전 3개, 편집 workflow 1개와 그 단계 skill 6개, 편집 스타일 3개다. 규칙의 원본은 각 skill의 `SKILL.md`이고 이 문서는 어느 것을 언제 부르는지만 적는다.

## 전제

- 화자는 얼굴을 드러내지 않는다. 화면에는 얼굴 없는 클립·화면 녹화·그래픽 카드만 나가고 말소리는 그 위에 흐른다.
- 촬영은 대부분 집 안 책상이다. B-roll 종류는 제한하지 않는다.
- 총길이는 10분 미만이다.
- 장비는 카메라·보조 카메라·마이크·화면 녹화로만 부른다.

## 촬영 전

| 순서 | skill | 언제 | 결과물 |
|---|---|---|---|
| 1 | `akbun-vlog-shootplan` | 주제만 있을 때 | 질문표 8개 → 스타일 선택 → 비트 시트, 장비 역할, 얼굴 없는 프레이밍, 말하기 가이드가 담긴 `shoot-plan_<날짜>.md` |
| 2 | `akbun-vlog-storyboard` | 계획서를 컷 단위로 보고 싶을 때 | 비트마다 그림(또는 이미지 프롬프트) + 표(음성, B-roll, 화면 녹화 내용, 카드, 분량), 끝에 OBS 화면 녹화 순서표와 설정 |
| 3 | `akbun-vlog-shotsketch` | 특정 샷의 카메라 구도가 헷갈릴 때 | 한 컷 스케치와 카메라 높이·거리·각도·자세 표 |

이 셋은 편집을 하지 않는다. 계획서가 없이 storyboard를 부르면 shootplan의 질문표를 먼저 돌린다. 촬영 뒤 얼굴이 들어간 클립은 파일명 끝에 `_face`를 붙인다. 편집 단계가 그 클립을 소리로만 쓴다.

## 촬영 뒤

`davinciresolve-story-devtalk` 하나를 부른다. 이 skill은 workflow 선언이라 아래 단계 skill의 `SKILL.md`를 순서대로 읽어 수행한다. 클립이 없으면 중단하고 shootplan을 안내한다.

| 순서 | skill | 하는 일 | 사용자가 할 일 |
|---|---|---|---|
| 0 | `davinciresolve-style-essay` / `-project` / `-reflection` | 구조·컷 리듬·글자 값의 기준 문서. 주제 유형으로 자동 선택 | 다른 스타일을 원하면 지정 |
| 1~3 | `davinciresolve-beats-devtalk` | 전사, 얼굴 탐지 인벤토리, 비트 시트 제안, 비트 순서로 A1 음성·V1 화면 나열 | 비트 시트 확정(유일한 필수 확인) |
| 4 | `davinciresolve-cut-devtalk` | 침묵·재녹음·필러 컷, 같은 화면 최대 길이를 넘으면 화면 교체 | 없음 |
| 5 | `davinciresolve-subtitle-devtalk` | 대사 자막, 키워드·번호 제목·코멘트 Text+. Pretendard, 최소 글자 크기 | 글꼴 미설치면 설치 |
| 6 | `davinciresolve-gfx-hyperframes` | HyperFrames 카드 렌더 후 V2 삽입 | 없음 |
| 7 | `davinciresolve-sfx-epidemicsound` | 카드·키워드·전환 자리에 효과음 A3 | 다운로드 확인 |
| 8 | `davinciresolve-bgm-epidemicsound` | 후보 몇 곡 → 1곡 선택 보고 → A4 | 다운로드 확인 |
| 9 | `davinciresolve-video-editor` 4·6·8·10단계 | 색, 타인 얼굴 모자이크, 믹싱, 4K 렌더 | 렌더·업로드 확인 |

단계 skill은 단독으로도 부른다. 타임라인을 손으로 짰으면 `davinciresolve-cut-devtalk`부터, 자막만 다시 넣으려면 `davinciresolve-subtitle-devtalk`만 부른다. 단독 호출 시 스타일이 없으면 `davinciresolve-story-devtalk`의 스타일 선택 표로 먼저 정한다.

## 스타일 고르는 기준

| 주제 유형 | 스타일 | 특징 |
|---|---|---|
| 기술 원리·개념·트레이드오프 설명 | `essay` | 카드·자료 40%, 같은 화면 최대 8초, 대사 자막 없음, 키워드 강조 |
| 내가 무엇을 만드는 과정 | `project` | 화면 녹화 위주, 같은 화면 최대 40초, 타임랩스, 장면 코멘트 자막 |
| 회고·개인 생각, 그 외 | `reflection` | B-roll 위 내레이션, 같은 화면 최대 6초, 모든 대사에 자막, 콜드 오픈 |

## 첫 실행 전 환경

- DaVinci Resolve Studio 20 이상. 조작은 Resolve MCP(`run_script`) 또는 외부 스크립팅. 전사는 Studio의 `TranscribeAudio`, 없으면 mlx-whisper.
- Pretendard 또는 Noto Sans KR(SIL OFL) 설치.
- Node 22 이상과 ffmpeg. `npx hyperframes --help`가 동작해야 카드를 만든다.
- Epidemic Sound 플러그인 로그인(Workspace → Workflow Integrations → Epidemic Sound).

## 호출 예시

Claude Code에서 skill 이름으로 부른다.

```text
/akbun-vlog-shootplan 컨테이너가 VM보다 빨리 뜨는 이유를 설명하는 영상, 아직 안 찍었어
/akbun-vlog-storyboard 위 계획서를 컷별로 그려주고 OBS로 뭘 녹화할지 정리해줘
/davinciresolve-story-devtalk 촬영한 클립으로 스토리부터 BGM까지 끝까지 편집해줘
/davinciresolve-subtitle-devtalk 자막만 다시 넣어줘
```

skill별 한 줄 예시는 `plugins/akbun-editvideo/.codex-plugin/plugin.json`의 `defaultPrompt`에 있다.
