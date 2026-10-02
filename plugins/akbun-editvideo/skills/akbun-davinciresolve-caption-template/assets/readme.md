# Akbun 자막 템플릿 사용설명서

## 템플릿 선택

| 이름 | 용도 | 기본 동작 |
|---|---|---|
| Akbun Cinema | 기본 대사·설명 자막 | 하단 중앙, 흰 글자, 얇은 검은 외곽선, 애니메이션 없음 |
| Akbun Typewriter | 요청한 타이핑 자막 | 손글씨 문장을 왼쪽 정렬로 순차 공개, 선택형 밑줄·원 |
| Akbun Keyword | 요청한 키워드 타이틀 | 작은 안내 문장 뒤 큰 연노랑 명조 키워드 공개 |

스타일을 따로 지정하지 않으면 **Akbun Cinema**를 사용한다. Cinema에는 타이핑·페이드·이동·강조·효과음을 자동 추가하지 않는다. 아래 배포 파일에는 참고 영상이나 캡처가 포함되지 않는다.

## macOS 설치

1. 이 폴더의 `Akbun-Caption-*.drfx`를 다운로드한다. `.setting` 파일들은 수정·백업용 원본이므로 함께 설치할 필요는 없다.
2. 사용할 글꼴을 설치한다. 아래 글꼴 표를 참고한다.
3. Finder에서 `.drfx`를 더블클릭하고 Resolve의 설치 창에서 설치한다. 일반 미디어 Import가 아니다.
4. Edit → Effects → Titles에서 `Akbun Cinema`를 검색한다. 목록에 없으면 프로젝트를 저장하고 Resolve를 재실행한다.
5. 본편 위의 비어 있는 별도 비디오 트랙(`SUBTITLE` 또는 `CAPTION`)에 드래그한다. 기존 클립 사이에 끼워 넣지 않는다.

설치는 현재 macOS 사용자 라이브러리에 남아 다음 프로젝트에서도 쓸 수 있다. 사용자 계정·설치 폴더 삭제나 포맷 후에는 다시 설치한다. 이 폴더를 백업으로 보관한다. 같은 제목의 수동 `.setting`과 DRFX를 중복 설치하지 않는다.

수동 설치가 필요하면 Fusion Effects Library의 Templates → Edit → Titles 메뉴에서 Show Folder로 실제 폴더를 확인한다. 일반 경로는 `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates/Edit/Titles/`이다. 여기에 `Akbun` 폴더를 만들고 `.setting` 3개를 복사한다.

## Cinema 편집

클립 선택 → Inspector에서 다음을 바꾼다. Fusion에서는 그룹을 열어 `CINEMA_TEXT`를 편집할 수 있다.

| 컨트롤 | 설명 |
|---|---|
| Text | 표시할 전체 문장. 한 줄 우선, 최대 두 줄 |
| Font / Style | 기본 `Source Han Sans KR` / `Regular` |
| Text Size | 기본 0.04. 실제 픽셀 높이는 폰트·해상도에 따라 달라짐 |
| Position | 기본 X 0.5, Y 0.1. Fusion Y는 아래쪽이 0이며 글자 아래를 기준으로 정렬함 |
| Line Spacing | 기본 1.15. 두 줄 간격 |
| Text Red / Green / Blue | 기본 흰색 1 / 1 / 1 |
| Outline Width / Opacity | 검은 외곽선 두께 0.035, 불투명도 0.85. 상대값이며 픽셀 단위가 아님 |

글자 높이는 화면 높이의 약 3.5~4.5%, 좌우 여백 8% 이상, 하단 여백 8~10%를 출발점으로 확인한다. 긴 문장은 크기를 계속 줄이지 말고 의미 단위로 나눈다. 밝은 장면과 어두운 장면에서 읽히는지, 얼굴·코드·시연을 가리지 않는지 확인한다. 검은 레터박스가 있으면 실제 영상 영역에 맞춰 위치를 조정한다. 세로 영상에는 위치·폭을 별도로 맞춘다.

클립 길이는 Edit 페이지에서 조절한다. 시작부터 끝까지 문장 전체가 정적으로 표시되며, 클립 페이드와 전환도 기본으로 추가하지 않는다. 대사 자막은 실제 발화의 시작·끝과 문구를 맞춘다.

## Typewriter와 Keyword 편집

- Typewriter: Text / Font / Style / Text Size, Position / Scale을 조절한다. Reveal Duration 0.65는 클립 길이의 65% 동안 공개한다는 뜻이다. Reveal Delay + Duration은 1 이하로 둔다.
- Keyword: `Keyword StyledText`, Font / Style / Size / Center / 색을 조절한다. 안내 문장은 처음 25%, 키워드는 30~60% 구간에 공개된다. 키워드 시간 변경은 Fusion `KEYWORD_TEXT.End` 표현식에서 한다.
- 밑줄·원은 기본 숨김이다. 해당 Visibility를 1로 바꾸고 Position / Width / Height / 색을 조절한다. 강조는 단어를 자동 추적하지 않으므로 문구·줄바꿈을 바꾼 뒤 다시 맞춘다.
- `CIRCLE Draw Length`는 원 둘레 공개량이다. 강조 애니메이션과 효과음은 요청할 때 별도로 추가하며 패키지에 음원은 포함하지 않는다.

## 글꼴

| 템플릿 | 기본 글꼴 | 공식 배포 |
|---|---|---|
| Cinema | Source Han Sans KR Regular (본고딕, SIL OFL) | [Adobe Source Han Sans](https://github.com/adobe-fonts/source-han-sans) |
| Typewriter / Keyword 안내 문장 | omyu pretty Regular (오뮤 다예쁨체) | [제작자 배포와 이용조건](https://omyudiary.com/product/detail.html?product_no=73) |
| Keyword 핵심 단어 | NanumMyeongjoOTF Regular (나눔명조, SIL OFL) | [Google Fonts](https://github.com/google/fonts/tree/main/ofl/nanummyeongjo) |

폰트 파일은 동봉하지 않는다. macOS 서체 관리자에서 공식 TTF/OTF를 설치하고 Resolve의 실제 글꼴 이름과 굵기를 확인한다. 설치본의 이름이 다르면 Inspector에서 선택한다. 기본 폰트가 없으면 자동 대체 결과로 완료하지 않는다. Cinema의 대안은 Pretendard 또는 Noto Sans KR이며 바꾼 뒤 글자 크기와 줄바꿈을 확인한다.

## AI agent 호출

```text
$akbun-davinciresolve-caption-template로 이 문장을 기본 영화식 자막으로 만들어줘.
$akbun-davinciresolve-caption-template로 0분 12초부터 3초간 본편 위 비디오 트랙에 자막을 넣어줘.
$akbun-davinciresolve-caption-template로 타이핑 자막과 빨간 밑줄을 만들어줘.
```

플러그인 설치 후 새 호출명을 사용한다. 대사 자막에는 전사 또는 자막 문구·시간을 함께 준다. 템플릿만 요청하면 프로젝트 본편에 자동 배치하지 않는다.

## 문제 해결과 검증 범위

- 제목이 없음: 설치를 완료했는지 확인하고 Resolve를 재실행한다.
- 한글이 깨짐/모양이 다름: 해당 폰트의 설치 여부와 Inspector의 Font / Style을 확인한다.
- 글자가 잘림: 문장을 나누고 최대 두 줄·안전 영역을 확인한다.
- 배경 영상이 밀림: 잘못된 insert 배치를 되돌리고 비어 있는 상위 비디오 트랙에 겹쳐 놓는다.
- 타이핑이 적용됨: Cinema 대신 Typewriter/Keyword를 사용했는지 확인한다.

패키지 검사는 파일 무결성을 확인할 뿐 실제 설치·전체 영상의 가독성·오디오 검청을 대신하지 않는다. 프로젝트마다 대표 자막을 밝은 장면과 어두운 장면에서 확인한 뒤 전체에 적용한다.
