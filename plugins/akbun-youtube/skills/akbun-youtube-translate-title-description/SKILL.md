---
name: akbun-youtube-translate-title-description
description: Codex computer use 전용. 업로드한 YouTube 영상의 한국어 제목과 설명을 AI가 직접 번역해 YouTube Studio의 언어 화면에 등록하는 skill. YouTube 공식 문서의 절차와 제한만 따른다. 기본 언어는 영어, 일본어, 프랑스어, 중국어(간체)이고 중국어는 언어 목록에 있을 때만 넣는다. 영상 ID로 한국어 원문을 읽고 YAML 번역표를 만들어 한 번 승인받은 뒤, 언어마다 언어 추가, 제목 및 설명 입력, 게시, 게시됨 확인을 반복한다. 제목은 100자, 설명은 5,000바이트 이내다. 촬영 장비와 배경음악 목록의 항목, 링크, 챕터 시각은 바꾸지 않는다. computer use가 없으면 번역표만 만든다. "유튜브 영상 다국어 설정해줘", "제목 설명 번역해서 등록해줘" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-youtube-translate-title-description

한국어 제목과 설명을 AI가 번역해 영상에 등록한다. 등록하면 그 언어를 쓰는 시청자에게 번역된 제목과 설명이 보인다. 화면을 다루는 규칙은 [`akbun-youtube-set-video-metadata`의 `Studio 화면 조작 규칙`](../akbun-youtube-set-video-metadata/SKILL.md#studio-화면-조작-규칙)을 그대로 따르고, 설명 구조는 [`akbun-youtube-plan-channel-settings`](../akbun-youtube-plan-channel-settings/SKILL.md)의 `description_template`을 따른다.

## 실행 수단

아래는 실행 수단과 번역 주체다.

```yaml
execution:
  requires: Codex computer use
  without_computer_use: 번역표만 만든다
  translated_by: AI                       # 이 skill을 실행하는 AI가 직접 번역한다. 번역 사이트를 열지 않는다
  urls:
    details: https://studio.youtube.com/video/{video_id}/edit
    languages: https://studio.youtube.com/video/{video_id}/translations
  url_fallback: 주소가 열리지 않으면 왼쪽 메뉴의 자막 또는 언어에서 영상 ID가 같은 영상을 고른다
  source: https://support.google.com/youtube/answer/6289575
```

## 대상 언어

아래는 기본 대상 언어와 Studio 언어 목록에서 고를 이름이다. 사용자가 언어를 말하면 그 목록을 쓴다.

```yaml
languages:
  - {order: 1, code: en, name: 영어, pick: 지역이 붙지 않은 영어}
  - {order: 2, code: ja, name: 일본어, pick: 일본어}
  - {order: 3, code: fr, name: 프랑스어, pick: 지역이 붙지 않은 프랑스어}
  - order: 4
    code: zh-Hans
    name: 중국어(간체)
    pick: 중국어(간체)
    when_not_listed: 건너뛰고 알린다
    traditional: 사용자가 요청할 때만 더한다
```

## 입력

아래는 시작 전에 확인할 입력이다.

```yaml
inputs:
  - id: video_id
    when_missing: ask
  - id: channel_name
    when_missing: ask
  - id: source_text
    description: 세부정보 화면에 저장된 한국어 제목과 설명
    when_missing: 세부정보 화면에서 읽는다
    stop_when: 제목이 파일 이름이거나 설명에 촬영 장비·배경음악 목록이 없다
    then: akbun-youtube-set-video-metadata를 먼저 하라고 알린다
  - id: video_language
    when_missing: 한국어로 넣어도 되는지 묻고 승인받으면 넣는다
  - id: subtitle_files
    description: 언어별로 번역한 .srt 파일
    when_missing: 자막을 건너뛴다
  - id: thumbnail_files
    description: 언어별 썸네일
    when_missing: 썸네일을 건너뛴다
```

## 번역 규칙

아래는 AI가 번역할 때 지키는 규칙이다.

```yaml
translation:
  limits:
    title: 100자. 공백을 포함해 실제로 센다
    description: 5,000바이트(UTF-8). 일본어·중국어는 한 글자가 3바이트다
    forbidden_characters: ["<", ">"]
    source: https://developers.google.com/youtube/v3/docs/videos
  when_title_over_limit: 핵심 단어를 앞에 두고 덜 중요한 말을 뺀다. 문장 중간에서 자르지 않는다
  translate:
    - 제목
    - 설명의 문장
    - 챕터 제목
    - 섹션 제목(촬영 장비, 배경음악)
    - 해시태그                             # 개수는 원문과 같게, 띄어쓰기 없이
  keep:
    - 촬영 장비 목록의 항목
    - 배경음악 목록의 항목
    - 챕터 시각
    - 링크
    - 이메일
  place_names: 그 언어에서 통하는 표기로 쓴다. 표기를 모르면 로마자로 두고 note에 "표기 확인 필요"를 적는다
  style:
    all: 그 언어를 쓰는 사람이 검색하고 말하는 표현으로 쓴다. 원문에 없는 사실과 과장을 더하지 않는다
    ja: 정중체(です・ます)
    fr: 시청자를 vous로 부른다. "?", "!", ":" 앞에 공백을 둔다
    zh-Hans: 대륙에서 쓰는 어휘
  korean_only_words: 줄임말과 유행어는 뜻을 풀어 쓴다
  section_headings:
    촬영 장비: {en: Gear, ja: 撮影機材, fr: Matériel, zh-Hans: 拍摄设备}
    배경음악: {en: Music, ja: BGM, fr: Musique, zh-Hans: 背景音乐}
```

## 절차

아래는 실행 순서다.

```yaml
procedure:
  - step: 1
    name: 원문 읽기
    do:
      - 실행 수단을 확인한다. computer use가 없으면 원문을 받아 3단계까지만 한다
      - 세부정보 화면을 열고 채널과 영상 ID를 확인한다
      - 제목, 설명, 동영상 언어를 읽는다
  - step: 2
    name: 언어 화면의 현재 값 읽기
    do:
      - 언어 화면을 연다
      - 언어마다 제목 및 설명 열의 상태를 읽는다. 값이 있으면 열어서 읽는다
      - YouTube가 자동으로 번역한 값도 현재 값으로 적는다
  - step: 3
    name: 번역표 만들기
    do:
      - languages 순서로 제목과 설명을 번역한다
      - 제목은 글자 수, 설명은 UTF-8 바이트를 실제로 센다
      - 출력 폴더에 youtube-translations-{video_id}.yaml로 저장하고 대화에 보여 준다
  - step: 4
    name: 승인 받기
    do:
      - 번역표 전체를 한 번 승인받는다
      - 사용자가 요청에서 확인 없이 등록하라고 했으면 이 단계를 건너뛴다
  - step: 5
    name: 언어마다 등록하기
    repeat: languages 순서로 한 언어씩 끝낸다
    do:
      - 그 언어의 행이 없으면 언어 추가를 누르고 목록에서 고른다
      - 행에 뜬 언어 이름이 대상 언어와 같은지 확인한다. 다르면 그 행을 쓰지 않고 다시 고른다
      - 제목 및 설명 열의 추가를 누른다. 값이 있으면 수정을 누른다
      - 제목을 붙여 넣고 다시 읽는다
      - 설명을 붙여 넣고 다시 읽는다. 줄바꿈과 챕터 시각이 원문과 같은 줄에 있는지 본다
      - 게시를 누른다
      - 제목 및 설명 열이 게시됨으로 바뀌었는지 확인한다
    optional:
      subtitle: 자막 열에서 추가, 파일 업로드, 타이밍 포함 순으로 올리고 게시한다
      thumbnail: 그 언어 행에서 올린다
    out_of_scope: 오디오 열                # choisungwook/akbun-aitools#201
  - step: 6
    name: 검증하기
    do:
      - 언어 화면을 새로 고치고 등록한 언어가 모두 게시됨인지 본다
      - 언어마다 다시 열어 제목과 설명을 번역표와 비교한다
      - 세부정보 화면의 원문이 바뀌지 않았는지 확인한다
      - 언어마다 result를 match, mismatch, unverified 중 하나로 적는다
```

## 산출물

아래는 번역표의 형식이다. 작업 로그도 같은 파일에 남긴다.

```yaml
channel: 채널 이름
video_id: AbCdEfGhIjK
source_language: ko
created: 2026-09-27
source:
  title: 한강 자전거 40km, 해 질 때까지
  description: |
    한강을 따라 40km를 달렸습니다.

    촬영 장비
    - iPhone 17 Pro

    배경음악
    - Slow Tide - Example Artist
translations:
  - code: en
    current: {title: null, description: null}
    title: Cycling 40 km Along the Han River Until Sunset
    title_length: 46/100
    description: |
      I rode 40 km along the Han River.

      Gear
      - iPhone 17 Pro

      Music
      - Slow Tide - Example Artist
    description_length: 91/5000 bytes
    note: null                   # 표기 확인 필요 | 기존 값을 덮어씀 | 제목을 줄임
    approved: false
    result: null                 # match | mismatch | unverified
  - code: ja
    current: {title: null, description: null}
    title: 漢江サイクリング40km、日が暮れるまで
    title_length: 20/100
    description: |
      漢江沿いを40km走りました。

      撮影機材
      - iPhone 17 Pro

      BGM
      - Slow Tide - Example Artist
    description_length: 101/5000 bytes
    note: null
    approved: false
    result: null
log:
  - {time: "15:10", language: en, action: 제목 및 설명 게시, result: match}
  - {time: "15:21", language: zh-Hans, action: 언어 추가, result: 목록에 있음}
```

## 완료 확인

아래를 모두 만족해야 끝난다.

```yaml
done_when:
  - 등록한 언어가 모두 게시됨이다
  - 모든 제목이 100자 이내이고 모든 설명이 5,000바이트 이내다
  - 촬영 장비와 배경음악 목록의 항목, 링크, 챕터 시각이 원문과 같다
  - 원문에 없는 내용이 번역에 없다
  - 세부정보 화면의 원문이 시작할 때와 같다
  - 건너뛴 언어와 이유를 알렸다
  - 저장한 YAML 파일이 파싱된다
```
