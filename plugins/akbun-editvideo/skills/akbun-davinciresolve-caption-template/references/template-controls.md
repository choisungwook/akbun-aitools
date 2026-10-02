# 템플릿 컨트롤과 macOS 설치

## 설치와 보관

1. `package_template.py`가 반환한 `~/Downloads/Akbun-Caption/Akbun-Caption-<내용해시>.drfx`를 Finder에서 더블클릭한다.
2. Resolve의 템플릿 설치 창에서 설치한다. 목록이 즉시 갱신되지 않으면 프로젝트를 저장하고 Resolve를 재실행한다.
3. Edit → Effects → Titles에서 `Akbun Typewriter`, `Akbun Keyword`를 검색하고 본편보다 위의 빈 비디오 트랙으로 드래그한다.
4. 클립 선택 → Inspector에서 문구·폰트·위치·타이핑 비율과 강조 표시를 바꾼다. Fusion 페이지에서는 그룹을 열어 내부 도형까지 수정할 수 있다.

`.drfx`를 Media Pool의 일반 영상 Import로 불러오는 절차가 아니다. 설치 파일은 현재 macOS 사용자 라이브러리에 남아 다음 프로젝트에서도 사용할 수 있다. 재부팅으로 없어지지 않지만 사용자 계정/설치 폴더 삭제, 초기화, 재설치 방식에 따라 사라질 수 있으므로 Downloads의 원본을 백업한다. 폰트는 별도 설치다.

DRFX 안에는 `Edit/Titles/Akbun/*.setting`이 들어간다. 수동 설치가 필요하면 Fusion Effects Library의 Templates → Edit → Titles에서 메뉴의 Show Folder로 실제 설치 위치를 연다. macOS 일반 경로는 `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates/Edit/Titles/`이다. 사용자가 설치 경로를 재정의했으면 앱이 보여 주는 경로를 따른다. 동일한 제목의 DRFX와 수동 setting을 중복 설치하지 않는다.

근거는 설치된 Resolve의 `Developer/Fusion Templates/README.txt`에 있는 Fusion Titles, Template Paths, DRFX Bundles 절이다. DRFX는 설치 패키지이며 편집본의 `.comp` 파일과 역할이 다르다.

## 컨트롤

템플릿의 `InstanceInput`은 내부 입력을 Inspector에 노출한다. Label은 UI용이고 API에서는 실제 ID를 읽는다. 다음은 번들 원본의 매핑이다.

| Inspector | 내부 노드·입력 | 의미 |
|---|---|---|
| Text / Font / Style / Text Size | CAPTION_TEXT의 StyledText / Font / Style / Size | 문장·글꼴·굵기·크기 |
| Text Red / Green / Blue | CAPTION_TEXT의 Red1 / Green1 / Blue1 | 글자색 |
| Position / Scale | CAPTION_LAYOUT의 Center / Size | 글·강조 전체 위치·크기 |
| Reveal Duration (0-1) | CAPTION_TEXT.RevealDuration | 클립 길이 대비 공개 시간 비율. 문장형 기본 0.65 |
| Reveal Delay (0-1) | CAPTION_TEXT.RevealDelay | 클립 길이 대비 공개 시작 지연. Delay + Duration이 1을 넘지 않게 조절 |
| UNDERLINE Visibility | UNDERLINE_MERGE.Blend | 0 숨김, 1 표시 |
| UNDERLINE Position / Width / Height | UNDERLINE_SHAPE의 Center / Width / Height | 위치·길이·두께 |
| UNDERLINE Red / Green / Blue | UNDERLINE_COLOR의 TopLeftRed / Green / Blue | 선 색 |
| CIRCLE Visibility | CIRCLE_MERGE.Blend | 0 숨김, 1 표시 |
| CIRCLE Position / Width / Height / Stroke Width | CIRCLE_SHAPE의 Center / Width / Height / BorderWidth | 위치·가로·세로·획 두께 |
| CIRCLE Draw Length | CIRCLE_SHAPE.WriteLength | 둘레 공개량. 기본 1, 시간 애니메이션은 agent가 선택 적용 |
| CIRCLE Red / Green / Blue | CIRCLE_COLOR의 TopLeftRed / Green / Blue | 원 색 |
| Keyword StyledText / Font / Style / Size / Center / Red1 / Green1 / Blue1 | KEYWORD_TEXT의 동명 입력 | 키워드형 전용 |

키워드형은 안내 문장이 처음 25%, 키워드가 30~60% 구간에 공개된다. 현재 키워드 공개 시간은 `KEYWORD_TEXT.End` 표현식의 0.3/0.3 값이다. Edit Inspector에 없는 시간 제어가 노출됐다고 안내하지 않는다. 타이밍을 바꿀 때 Fusion에서 해당 표현식을 수정하거나 제거하고 키프레임을 넣는다.

## agent 수정

원본 `.setting`을 배포 자산으로 유지하고 클립 인스턴스에서 수정한다. Text+의 `End`는 UTF-8 문자열 바이트를 자르는 방식이 아니므로 한글 조합이 깨지지 않게 전체 문자열을 두고 공개량을 조절한다. 텍스트를 바꾼 뒤 줄 수·강조 위치는 직접 캡처해 다시 맞춘다. 강조는 단어를 자동 추적하지 않는다.

전체 이동은 `CAPTION_LAYOUT`에서, 특정 강조의 이동은 각 SHAPE에서 한다. Fusion 정규화 좌표는 아래쪽 원점이므로 캡처 픽셀 y를 사용할 때 같은 캔버스 기준 `1-y/H`로 변환한다. 전체 이동 전 로컬 도형 좌표와 화면 좌표를 섞지 않는다.

`GetInputList()`로 실제 ID를 확인하고 `SetInput()` 뒤 다시 읽는다. 가져온 그룹은 `GetToolList(False)`에서 내부 Text+를 찾을 수 있으며 숨은 원본이나 다른 클립을 수정하지 않는다. SaveSettings/ExportFusionComp 뒤 다시 불러와 화면·컨트롤을 확인한다. Import 성공만으로 합성이나 설치 완료를 보고하지 않는다.

검증용 comp에는 MediaOut이 필요하다. 템플릿 `.setting`의 단일 그룹 출력은 `MainOutput1`이며 comp의 MediaOut에 연결한다. 테스트 컴포지션은 `/tmp`에 둔다. Resolve가 standalone Fusion comp의 Saver 렌더를 지원하지 않는 상황에서는 테스트 타임라인에서 Viewer/ExportCurrentFrameAsStill로 확인한다.
