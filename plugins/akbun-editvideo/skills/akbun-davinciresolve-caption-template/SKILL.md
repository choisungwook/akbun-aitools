---
name: akbun-davinciresolve-caption-template
description: DaVinci Resolve에서 손글씨 느낌의 타이핑 자막과 노란 세리프 키워드 타이틀을 재사용 Fusion Title 템플릿으로 만들고 별도 비디오 트랙에 겹쳐 배치한다. 선택형 밑줄·원 강조, macOS DRFX 설치 안내, Epidemic Sound 효과음 또는 분·초 큐시트를 제공한다. 참고 영상의 자막 스타일이나 재사용 자막 템플릿 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-caption-template

Codex·Claude 등 agent가 Resolve 기본 Text+와 Fusion 도형으로 편집 가능한 **타이핑 자막(typewriter caption)**을 만든다. 대사 자동 전사나 기사 발췌 패널은 각각 [devtalk 자막](../davinciresolve-subtitle-devtalk/SKILL.md), [기사 오버레이](../akbun-davinciresolve-article-overlay/SKILL.md)가 맡는다.

## 입력과 참고 분석

참고 영상/구간, 사용할 문구, 대상 프로젝트·타임라인·배치 구간을 구분한다. 참고 영상의 시간은 배치 시간이 아니다. 템플릿만 요청했으면 패키징·미리보기·설치 안내까지 하고 실제 본편에 넣지 않는다.

참고 파일이 있으면 [프레임 캡처 도구](../akbun-davinciresolve-article-overlay/scripts/capture_reference.py)를 사용해 `/tmp` 아래 임시 디렉터리에 캡처한다. 각 프레임을 직접 열어 읽는다. 먼저 0.5초 간격으로 등장 전·등장·완성·문장 교체·퇴장을 보고, 글자 증가 경계는 약 0.1초 간격으로 다시 본다. 원본이 없으면 링크/경로를 요청하고 확인 전에는 참고 분석 완료나 스타일 일치를 주장하지 않는다.

추출 대상은 글자 높이·여백·정렬·색·표시 순서·읽는 시간이다. 원본 인물·문장·밈 이미지·브랜드·출처 맥락을 배포 자산에 복제하지 않는다. 다른 소재의 예문으로 검증한다. 스크린샷만으로 원본 SFX를 들었다고 말하지 않는다.

## 화면 규칙

| 요소 | 재사용 기준 |
|---|---|
| 문장형 | 투명 배경, 흰 손글씨 느낌, 왼쪽 정렬, 1~2줄. 문장 전체의 줄바꿈과 위치를 먼저 고정한 뒤 글자를 순차 공개한다. 타이핑 중 글자가 중앙으로 재정렬되면 안 된다. |
| 배치 | 프레임 가장자리 8~12% 이상 안쪽을 출발점으로 하되 얼굴·손·시연 내용을 피한 빈 공간을 고른다. 좌하단·우하단을 고정하지 않는다. |
| 크기 | 문장 글자 실측 높이 약 화면 높이 4~5%부터 시작한다. Text+ Size 숫자를 실제 글자 높이 비율로 간주하지 않는다. 휴대폰 크기로 보고 읽기 어려우면 키운다. |
| 타이핑 | Text+ `End`(Write On End)로 공개한다. 내장 템플릿은 클립 길이의 65% 동안 등장 후 정지한다. 문장 발화에 맞게 공개 구간을 조절하고 완성 상태를 읽을 시간을 확보한다. 타자 커서는 기본으로 넣지 않는다. |
| 키워드형 | 작은 흰 안내 문장 아래 큰 연노랑 `#FFE67A` 세리프 키워드를 둔다. 키워드 크기는 안내 문장의 약 2~3배부터 조절한다. 안내 문장→키워드 순서로 공개한다. |
| 퇴장 | 기본은 클립 끝에서 사라짐. 컷과 발화에 맞춰 짧은 페이드를 선택할 수 있으며 흔들림·과한 팝업을 임의로 추가하지 않는다. |
| 강조 | 밑줄·원은 기본 숨김. 요청 시 하나를 켜고 위치·폭·높이·두께·색을 개별 조절한다. 기본 빨강이며 글자 획을 가리지 않는다. |

참고 화면의 보조 사진은 자막 자체와 구분한다. 요청한 자료가 있을 때만 별도 오버레이로 추가하며 원본의 밈을 그대로 배포하지 않는다.

## 템플릿 선택과 제작

정적인 문구·단일 스타일만 필요하면 Resolve 기본 **Text**로 충분한지 먼저 판단한다. 글자 순차 공개와 개별 강조 도형이 필요하면 **Text+ 기반 Fusion Title**을 쓴다. 글자를 PNG나 영상으로 굽지 않는다.

- [Akbun Typewriter.setting](assets/Akbun%20Typewriter.setting): 문장형, 타이핑 시간·문구·폰트·전체 위치·밑줄·원 제어.
- [Akbun Keyword.setting](assets/Akbun%20Keyword.setting): 작은 안내 문장과 노란 키워드, 각 텍스트·폰트·크기·키워드 위치·색 제어.
- `.setting`은 편집 가능한 원본이고 `.drfx`는 이를 설치하는 ZIP 패키지다. [패키징 스크립트](scripts/package_template.py)는 `~/Downloads/Akbun-Caption/`에 생성하고 **설치하지 않는다**. 동일 내용은 같은 파일을 재사용하며 다른 기존 파일을 덮어쓰지 않는다.

스킬 디렉터리에서 패키징한다.

```bash
uv run --python 3.12 scripts/package_template.py
```

제작·수정·설치 안내에는 [템플릿 컨트롤과 macOS 설치](references/template-controls.md)를 읽는다. 기본 글꼴은 이 환경에서 확인한 `omyu pretty` Regular와 `NanumMyeongjoOTF` Regular이며 파일은 포함하지 않는다. 다른 컴퓨터에서는 Resolve의 실제 글꼴 목록에서 이름과 굵기를 확인한다. 없으면 아래 추천 글꼴 설치 또는 이미 있는 적합한 글꼴 선택을 안내하고, 대체가 발생했음을 알린다.

## 한글 무료 글꼴

| 용도 | 추천 | 공식 출처 |
|---|---|---|
| 손글씨 문장 | 오뮤 다예쁨체 (`omyu pretty`) | [제작자 무료 배포](https://omyudiary.com/product/detail.html?product_no=73). 별도 이용조건 확인, 폰트 파일을 템플릿에 재배포하지 않음 |
| OFL 손글씨 대안 | 나눔손글씨 펜 (`Nanum Pen Script`) | [Google Fonts 원본·라이선스](https://github.com/google/fonts/tree/main/ofl/nanumpenscript) |
| 명조 키워드 | 나눔명조 (`Nanum Myeongjo`, 설치본에 따라 `NanumMyeongjoOTF`) | [Google Fonts 원본·OFL](https://github.com/google/fonts/tree/main/ofl/nanummyeongjo) |
| 단정한 고딕 대안 | Pretendard | [공식 배포·OFL](https://github.com/orioncactus/pretendard). 손글씨 질감은 달라짐 |

무료는 저작권 없음을 뜻하지 않는다. 원본 영문 폰트를 확인 없이 특정 폰트라고 단정하지 않는다. macOS는 공식 TTF/OTF를 서체 관리자에서 설치한 후 Resolve 목록에서 확인한다.

## 본편에 적용할 때

Resolve MCP의 현재 버전·API를 확인하고 없으면 로컬 스크립팅 또는 UI를 사용한다. **타임라인 안의 본편보다 위에 있는 별도 비디오 트랙**에 같은 시간으로 겹친다. subtitle 트랙이나 기존 본편 클립의 Fusion에 넣지 않는다.

1. 현재 타임라인을 복제하고 원본/작업본 ID, fps, 시작 TC, 클립 시작·끝, 마커와 길이를 기록한다. 재개라면 이전 작업본을 확인한다.
2. 상위의 비어 있는 자막 전용 비디오 트랙을 찾거나 `CAPTION` 트랙을 추가한다. V2 등 번호를 고정하지 않는다.
3. 설치된 Title을 UI로 해당 트랙에 드래그하거나, 준비된 미디어 풀 Fusion Title을 `AppendToTimeline`의 `trackIndex`·`recordFrame`으로 배치한다. [배치·프레임 주의사항](../akbun-davinciresolve-article-overlay/references/resolve-compositing.md)의 비리플 원칙을 따른다. 타임라인 중간에서 `InsertFusionTitleIntoTimeline`을 호출하지 않는다.
4. 해당 클립 인스턴스만 수정한다. 타이핑 시간은 기본 비율을 발화에 맞춰 조절하며, 정밀한 발화 동기화가 필요하면 해당 `End` 표현식을 제거한 뒤 실제 comp 시작 프레임 기준 키프레임을 넣는다. 문구를 글자마다 바꾸는 방식은 줄바꿈·정렬이 흔들리므로 쓰지 않는다.
5. 텍스트가 완전히 나온 뒤 선택한 밑줄·원을 표시한다. 원의 write-on은 `CIRCLE_SHAPE.WriteLength`를 사용하고, 길이 0에서 남는 점은 Merge Blend로 숨긴다. 강조 애니메이션은 기본 패키지에 없으므로 요청 시 클립에 작성한다.
6. 기존 클립·마커·길이가 그대로인지 다시 읽는다. cue ID/클립 ID로 재실행 중복을 막는다.

## 효과음

Epidemic Sound MCP의 실제 검색·미리듣기·다운로드 지원 여부를 확인한다. 가능하면 [공통 사운드 스킬](../davinciresolve-sfx-epidemicsound/SKILL.md)의 연결·배치·믹싱 절차를 적용해 영구 `audio-assets/`에 다운로드하고 빈 `SFX_CAPTION` 오디오 트랙에 넣는다. 기존 BGM 교체로 범위를 넓히지 않는다.

| 화면 이벤트 | 영상 분야 SFX 용어·검색어 | 동기화 |
|---|---|---|
| 글자 순차 공개 | Typing / Typewriter / `soft keyboard typing`, `typewriter keys` | 첫 글자~마지막 글자. 내레이션을 가리면 생략하거나 드문 클릭만 사용 |
| 핵심 단어 등장 | Soft pop / UI click / `subtle pop`, `soft click` | 키워드가 읽히는 첫 프레임 |
| 밑줄·원 그리기 | Marker stroke / Scribble / `marker on paper`, `pencil scribble` | 획 시작~완성 |
| 위치 이동을 추가한 경우 | Short whoosh / `soft short whoosh` | 이동 시작~정착. 정적 타이핑에 무조건 붙이지 않음 |

MCP 없음·다운로드 실패·배치 실패면 **채팅에** `경과 분:초.밀리초 | 길이 | SFX·검색어 | 동기화 기준 | 트랙 | 미삽입 사유` 표를 출력한다. 실제 타임라인이 있으면 Resolve TC·fps·시작 TC도 병기한다. 템플릿만 만든 경우 아래처럼 **템플릿 시작 기준 예시**로 명시하고 원본 영상에 이미 넣었다고 하지 않는다.

| 템플릿 경과 시간 | 길이 | SFX·검색어 | 기준 | 트랙 | 상태 |
|---|---|---|---|---|---|
| 0분 00.000초 | 1.95초 | Typing / soft keyboard typing | 3초 문장형의 공개 구간 | SFX_CAPTION | 미삽입: 연결 불가, 예시 |
| 0분 01.950초 | 0.30초 | Marker stroke / marker on paper | 선택형 밑줄 시작 | SFX_CAPTION | 미삽입: 강조 선택 시 예시 |

음원 시작점과 들리는 어택을 구분하고 실제 싱크·gain·검청 여부를 기록한다. 분석 PNG·임시 음원을 최종 Resolve 외부 참조로 남기지 않는다.

## 완료 검증

- Resolve에서 빈 글자·공개 중간·완성·문장 교체·클립 끝을 `/tmp`에 캡처해 각각 직접 연다. 한글 깨짐, 고정된 왼쪽 정렬, 줄바꿈, 읽힘, 투명 합성을 확인한다. API 성공만으로 화면 적용을 판정하지 않는다.
- 문구·위치·글꼴 변경, 밑줄/원 표시·색·폭 변경을 실제로 시험하고 기본값을 복원한다. 저장 후 다시 열어 제어와 연결이 남아 있는지 확인한다.
- 서로 다른 클립 길이에서 타이핑이 끝나고 정지 시간이 남는지 확인한다. 프레임레이트가 바뀌면 비율과 실제 읽는 시간을 모두 확인한다.
- 테스트는 별도 테스트 프로젝트/타임라인에 두고 원래 프로젝트로 돌아간다. 템플릿 설치만 안내하는 요청에서는 사용자 템플릿 라이브러리에 자동 설치하지 않는다.
- 패키지 경로·설치법·호출 예·사용 폰트·검증 범위·미삽입 SFX를 간결하게 전달한다. 설치·본편 적용·오디오 검청을 각각 구분한다.
