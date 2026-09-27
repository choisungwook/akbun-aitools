---
name: akbun-youtube-plan-channel-settings
description: YouTube 채널을 처음 만들었거나 설정을 점검할 때 YouTube Studio의 채널 단위 설정을 YAML 채널 설정표로 만드는 skill. YouTube 공식 문서에 있는 설정과 제한만 다룬다. 채널 키워드, 아동용 여부(항상 아니요), 자동 더빙, 기능 사용 자격, 업로드 기본 설정(설명 템플릿·태그·카테고리·언어·댓글 검토), 채널 설명·연락처·워터마크, 채널 이름과 설명의 번역을 항목마다 Studio 위치·넣을 값·제한·공식 문서 주소와 함께 적는다. 설명 템플릿에는 촬영 장비와 배경음악 목록이 항상 들어간다. 화면은 조작하지 않는다. "유튜브 채널 세팅해줘", "채널 설정 점검해줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-youtube-plan-channel-settings

채널에 한 번 해 두는 설정을 YAML 채널 설정표로 만든다. 사용자가 표를 보고 YouTube Studio에서 직접 바꾼다. 영상 하나의 값은 [`akbun-youtube-set-video-metadata`](../akbun-youtube-set-video-metadata/SKILL.md), 번역 등록은 [`akbun-youtube-translate-title-description`](../akbun-youtube-translate-title-description/SKILL.md)이 맡고, 두 skill은 이 문서의 `fixed`와 `description_template`을 그대로 쓴다.

## 규칙

아래는 이 skill이 지키는 규칙과 고정 값이다.

```yaml
rules:
  source_of_truth: YouTube 공식 문서
  not_in_official_docs: 넣지 않는다        # 크리에이터의 권장, 노출 효과 주장
  operates_screen: false
  never_invent: [링크, 이메일, 장비 이름, 곡 이름, 검색량]
  menu_names: 한국어 Studio 기준. 화면의 이름이 다르면 같은 뜻의 항목을 찾고 실제 이름을 적는다
  done_by_user: [로그인, 본인 확인, 전화번호 인증, 신분증·영상 인증]

fixed:
  made_for_kids: false                    # 이 채널은 아동용 영상을 올리지 않는다. 묻지 않는다
  translated_by: AI                       # 번역은 이 skill을 실행하는 AI가 직접 한다

defaults:
  sub_target_languages: [영어, 일본어, 프랑스어, 중국어(간체)]
```

## 입력

아래는 시작 전에 확인할 입력이다. `when_missing`이 `ask`면 멈추고 묻는다.

```yaml
inputs:
  - id: channel_topic
    description: 채널이 다루는 주제 한 줄
    when_missing: ask
  - id: main_target
    description: 메인 타겟 국가와 언어. 하나만 정한다
    when_missing: ask
  - id: sub_target_languages
    when_missing: defaults.sub_target_languages를 쓴다
  - id: equipment
    description: 촬영 장비 목록. 설명 템플릿에 항상 들어간다
    when_missing: ask
  - id: has_speech
    description: 영상에 말소리가 있는지
    when_missing: ask
  - id: comment_moderation
    description: 댓글 검토 수준
    options: [없음, 기본, 엄격, 모두 보류]
    when_missing: ask
  - id: links
    description: 설명에 넣을 고정 링크
    when_missing: 비운다
  - id: contact_email
    when_missing: 비운다
  - id: current_values
    description: 지금 Studio에 들어 있는 값
    when_missing: 현재 값을 "확인 필요"로 적는다
```

## 설정 항목

아래는 채널 설정표에 넣는 항목 전체다. 이 목록에 없는 설정은 다루지 않는다.

```yaml
settings:
  - id: channel_keywords
    studio_path: 설정 → 채널 → 기본 정보 → 키워드
    value: 채널 주제를 나타내는 단어
    limit: 합쳐서 500자
    source: https://developers.google.com/youtube/v3/docs/channels

  - id: made_for_kids
    studio_path: 설정 → 채널 → 고급 설정 → 시청자층
    value: 아니요, 채널을 아동용으로 설정하지 않습니다
    fixed: true
    source: https://support.google.com/youtube/answer/9527654

  - id: auto_dubbing
    studio_path: 설정 → 채널 → 고급 설정 → 자동 더빙 허용
    value:
      has_speech_true: 켠다
      has_speech_false: 바꾸지 않는다
    note: 말소리가 없거나 음악만 있는 영상은 자동 더빙 대상이 아니다
    source: https://support.google.com/youtube/answer/15569972

  - id: feature_eligibility
    studio_path: 설정 → 채널 → 기능 사용 자격
    value: 현재 단계만 적는다
    done_by: user
    unlocks:
      intermediate:
        how: 전화번호 인증
        features: [15분 넘는 영상, 맞춤 썸네일]
      advanced:
        how: 채널 기록 또는 신분증·영상 인증
        features: [설명의 클릭되는 링크, 댓글 고정, 다국어 오디오, 제목·썸네일 A/B 테스트]
    source: https://support.google.com/youtube/answer/9890437

  - id: upload_default_description
    studio_path: 설정 → 업로드 기본 설정 → 기본 정보 → 설명
    value: description_template으로 만든 글
    limit: 5,000바이트
    source: https://support.google.com/youtube/answer/2660027

  - id: upload_default_tags
    studio_path: 설정 → 업로드 기본 설정 → 기본 정보 → 태그
    value: 채널의 모든 영상에 맞는 단어
    limit: 합쳐서 500자. 쉼표도 센다. 공백이 있는 태그는 따옴표 2자를 더 센다
    note: 태그는 영상이 발견되는 데 작은 역할만 한다. 자주 틀리는 철자가 있을 때 쓸모 있다
    source: https://support.google.com/youtube/answer/146402

  - id: upload_default_category
    studio_path: 설정 → 업로드 기본 설정 → 고급 설정 → 카테고리
    value: 채널 주제에 가장 가까운 하나
    source: https://support.google.com/youtube/answer/2660027

  - id: upload_default_language
    studio_path: 설정 → 업로드 기본 설정 → 고급 설정 → 동영상 언어, 제목 및 설명 언어
    value: main_target의 언어
    note: 동영상 언어가 없으면 번역을 추가하기 전에 언어를 고르라고 나온다
    source: https://support.google.com/youtube/answer/6289575

  - id: upload_default_comments
    studio_path: 설정 → 업로드 기본 설정 → 고급 설정 → 댓글
    value: inputs.comment_moderation
    options:
      없음: 댓글을 보류하지 않는다
      기본: 부적절할 수 있는 댓글을 보류한다
      엄격: 부적절할 수 있는 댓글을 더 넓게 보류한다
      모두 보류: 모든 댓글을 보류한다
    source: https://support.google.com/youtube/answer/9483359

  - id: channel_description
    studio_path: 맞춤설정 → 프로필 → 설명
    value: 채널이 무엇인지 설명하는 글
    limit: 1,000자
    source: https://developers.google.com/youtube/v3/docs/channels

  - id: contact_email
    studio_path: 맞춤설정 → 프로필 → 연락처 정보
    value: inputs.contact_email
    source: https://support.google.com/youtube/answer/2657964

  - id: watermark
    studio_path: 맞춤설정 → 프로필 → 동영상 워터마크
    value: 사용자가 준 이미지 파일
    limit: 최소 150×150 픽셀, 정사각형, 1MB 미만
    display_time_options: [동영상 끝(마지막 15초), 맞춤 시작 시간, 전체 동영상]
    source: https://support.google.com/youtube/answer/10456525

  - id: channel_translation
    studio_path: 맞춤설정 → 프로필 → 언어 → 추가
    value: sub_target_languages마다 번역한 채널 이름과 설명
    translated_by: AI
    rules:
      - 채널 이름은 고유명사다. 뜻을 풀지 않고 그 언어의 문자로 옮기거나 그대로 둔다
      - 원문에 없는 내용을 더하지 않는다
      - 링크와 이메일은 그대로 둔다
    source: https://support.google.com/youtube/answer/2657964

notes:
  - 업로드 기본 설정은 브라우저로 올린 영상에만 적용된다. 모바일이나 편집 프로그램으로 올린 영상에는 적용되지 않는다
  - 업로드 기본 설정은 이미 올린 영상을 바꾸지 않는다
```

## 설명 템플릿

아래는 영상 설명의 구조다. 촬영 장비와 배경음악은 항상 들어가고 목록으로 쓴다.

```yaml
description_template:
  limit: 5,000바이트(UTF-8). 한글·일본어·중국어는 한 글자가 3바이트다
  forbidden_characters: ["<", ">"]
  sections:                      # 이 순서로 쓴다. 섹션 사이는 빈 줄 하나
    - id: summary
      required: true
      scope: 영상마다
      format: 이 영상이 무엇인지 1~2문장
    - id: chapters
      required: false
      scope: 영상마다
      format: 한 줄에 "시각 제목"
      rules: [첫 시각은 00:00, 3개 이상, 시간순, 챕터 하나는 10초 이상]
      source: https://support.google.com/youtube/answer/9884579
    - id: equipment
      required: true
      scope: 채널 공통. 영상마다 다르면 그 영상의 값으로 바꾼다
      heading: 촬영 장비
      format: 목록. 한 줄에 "- 장비 이름"
    - id: bgm
      required: true
      scope: 영상마다
      heading: 배경음악
      format: 목록. 한 줄에 "- 곡 이름 - 아티스트"
    - id: links
      required: false
      scope: 채널 공통
    - id: hashtags
      required: false
      rules: [띄어쓰기 없이 쓴다, 60개를 넘으면 전부 무시된다, 제목 옆에는 3개까지 보인다]
      source: https://support.google.com/youtube/answer/6390658
  upload_default: summary, chapters, bgm 목록은 비우고 제목 줄만 둔다
  example: |
    비 오는 날 제주 동쪽 해안을 걸었습니다.

    00:00 성산 출발
    03:12 종달리 해안
    08:40 세화 해변

    촬영 장비
    - iPhone 17 Pro
    - Insta360 Luna Ultra

    배경음악
    - Slow Tide - Example Artist

    #제주 #여행브이로그
```

## 산출물

아래는 채널 설정표의 형식이다. 출력 폴더에 `youtube-channel-settings.yaml`로 저장하고 대화에도 같은 내용을 보여 준다. 출력 폴더를 모르면 묻는다.

```yaml
channel: 채널 이름
main_target: {country: 대한민국, language: 한국어}
sub_target_languages: [영어, 일본어, 프랑스어, 중국어(간체)]
created: 2026-09-27
settings:                        # settings 항목의 순서 그대로
  - id: channel_keywords
    studio_path: 설정 → 채널 → 기본 정보 → 키워드
    current: 확인 필요
    value: 여행 브이로그, 걷기 여행, 국내 여행
    length: 21/500
    status: todo                 # todo | keep | user_action
    source: https://developers.google.com/youtube/v3/docs/channels
values:
  description_template: |
    촬영 장비
    - iPhone 17 Pro

    배경음악
  channel_translations:
    en: {name: 채널 이름, description: 번역한 설명}
```

## 완료 확인

아래를 모두 만족해야 끝난다.

```yaml
done_when:
  - settings의 모든 항목이 표에 있고 source가 있다
  - made_for_kids가 false다
  - description_template에 촬영 장비와 배경음악 섹션이 목록 형식으로 있다
  - limit이 있는 값은 실제로 센 길이가 적혀 있다
  - 저장한 YAML 파일이 파싱된다
  - 지어낸 값이 없다
```
