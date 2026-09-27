---
name: akbun-youtube-analyze-my-videos
description: 내 YouTube 채널의 영상들을 나란히 놓고 무엇이 되고 무엇이 안 되는지 분석하는 skill. YouTube Studio 분석의 내보내기 파일과 공개 정보로 영상마다 노출수·노출 클릭률·평균 시청 지속 시간·조회수를 한 표에 모으고, 내 채널의 중앙값과 비교해 잘된 영상과 안된 영상을 함께 본다. 영상마다 막힌 곳(노출, 클릭, 시청)을 찾고 제목·썸네일의 약속과 첫 30초를 대조한 뒤, 관찰과 가설을 구분해 다음 영상에서 바꿀 한 가지를 YAML 보고서로 낸다. 지표의 뜻과 해석은 YouTube 공식 문서를 따른다. 화면은 조작하지 않는다. "내 유튜브 영상 분석해줘", "왜 조회수가 안 나오는지 봐줘", "다음에 뭘 바꿔야 해" 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-youtube-analyze-my-videos

내 영상들을 한 표에 나란히 놓고 비교한다. 영상을 하나씩 따로 보면 보이지 않는 차이를 찾고, 다음 영상에서 시험할 한 가지를 정한다. 결과는 YAML 보고서 하나다.

## 규칙

아래는 이 skill이 지키는 규칙이다.

```yaml
rules:
  priority:                               # 충돌하면 위가 이긴다
    - YouTube 공식 문서
    - 분석 방법(method)
  operates_screen: false
  separate:
    observation: 데이터에 실제로 있는 것
    hypothesis: 왜 그런지에 대한 추정. 다음 영상으로 확인하기 전에는 사실로 쓰지 않는다
  evidence:
    - 잘된 영상만 보지 않는다. 같은 특징을 가진 안된 영상도 함께 센다
    - 영상 하나로 패턴을 말하지 않는다. 영상 3개 이상에서 같은 방향일 때만 패턴으로 적는다
    - 결과의 원인은 하나가 아닐 수 있다. 제목만이 아니라 썸네일, 구조, 전달 방식도 본다
  compare_with: 내 채널의 다른 영상. 다른 채널의 숫자와 비교하지 않는다
  never:
    - 조회수나 구독자 증가를 약속한다
    - 데이터에 없는 숫자를 채운다
    - 다른 채널의 제목이나 썸네일을 그대로 가져오라고 권한다
  out_of_scope:
    - 다른 채널을 조사해 새 주제를 찾는 일
    - 고객 전환과 판매 경로
```

## 지표

아래는 쓰는 지표와 공식 문서의 뜻이다. 해석은 `read_as`만 따른다.

```yaml
metrics:
  - id: impressions
    name: 노출수
    meaning: 썸네일이 YouTube에서 시청자에게 보인 횟수
    source: https://support.google.com/youtube/answer/16767369

  - id: ctr
    name: 노출 클릭률
    meaning: 썸네일을 본 뒤 영상을 시청한 비율
    read_as:
      - 채널과 영상의 절반은 2%에서 10% 사이다
      - 노출이 늘면 내려갈 수 있다. 핵심 시청자 밖의 새 시청자에게 보이기 때문이다
      - 올린 직후의 높은 값은 충성 시청자의 반응일 수 있다
      - 검색은 노출이 적고 클릭률이 높다. 홈은 노출이 많고 클릭률이 낮다
      - 노출수와 트래픽 소스 없이 클릭률만 비교하지 않는다
    source: https://support.google.com/youtube/answer/16767369

  - id: average_view_duration
    name: 평균 시청 지속 시간
    meaning: 시청 한 번의 평균 시청 시간
    source: https://support.google.com/youtube/answer/9314415

  - id: retention
    name: 시청 지속 시간 보고서
    requires: 영상 길이 60초 이상, 조회수 100회 이상
    segments:
      인트로: 처음 30초 뒤에도 보고 있는 시청자의 비율
      인기 장면: 이탈한 시청자가 거의 없는 구간
      급상승 구간: 다시 보거나 공유한 구간
      하락 구간: 건너뛰거나 시청을 그만둔 구간
    typical: 길이가 비슷한 내 최신 영상 10개와 비교한 값
    studio_path: 콘텐츠 → 영상의 분석 → 개요 또는 참여도
    source: https://support.google.com/youtube/answer/9314415

  - id: recommendation_signals
    name: 추천 시스템이 보는 신호
    signals:
      호소력: 시청자가 영상을 고르는지, 무시하거나 관심 없음을 누르는지
      참여도: 시청자가 계속 보는지
      만족도: 시청자가 영상을 즐겼는지
    note: 업로드 빈도는 이 신호에 없다
    source: https://support.google.com/youtube/answer/16559650
```

## 입력

아래는 시작 전에 확인할 입력이다.

```yaml
inputs:
  - id: channel_url
    description: 내 채널 주소
    when_missing: ask
  - id: studio_export
    description: YouTube Studio 분석에서 내보낸 파일
    how:
      - 분석 → 고급 모드
      - 측정항목에서 조회수, 시청 시간, 평균 시청 지속 시간, 노출수, 노출 클릭률, 구독자를 고른다
      - 현재 뷰 내보내기 → 파일 형식 선택
    limit: 500행
    source: https://support.google.com/youtube/answer/9717005
    when_missing: 공개 정보만으로 진행하고 노출·클릭·시청 진단은 "데이터 없음"으로 적는다
  - id: period
    description: 분석할 기간이나 영상 수
    when_missing: 최신 영상 12개
  - id: traffic_sources
    description: 영상별 트래픽 소스
    when_missing: 클릭률을 영상끼리 비교할 때 "트래픽 소스 확인 필요"를 적는다
  - id: intended_promise
    description: 영상마다 제목과 썸네일이 약속하려던 것
    when_missing: 제목과 썸네일을 보고 적은 뒤 사용자에게 확인받는다
```

## 공개 정보 모으기

아래 명령은 내 채널의 영상 ID, 제목, 길이(초), 조회수를 `|`로 구분해 출력한다.

```bash
yt-dlp --flat-playlist --print "%(id)s | %(title)s | %(duration)s | %(view_count)s" "https://www.youtube.com/@내채널/videos"
```

아래 명령은 영상 하나의 썸네일과 자막을 받는다. 영상 파일은 받지 않는다.

```bash
yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg --write-auto-subs --sub-langs "ko" -o "%(id)s.%(ext)s" "https://youtu.be/영상ID"
```

## 분석 방법

아래는 분석 순서다. `method`는 YouTube 공식 문서가 아니라 크리에이터의 분석 방법에서 온 것이고, 지표의 해석은 위 `metrics`가 우선한다.

```yaml
method:
  - step: 1
    name: 한 표에 나란히 놓기
    do:
      - 영상마다 제목, 썸네일 파일, 게시일, 길이, 조회수, 노출수, 노출 클릭률, 평균 시청 지속 시간을 한 줄로 적는다
      - 평균 조회율을 계산한다. 평균 시청 지속 시간 ÷ 영상 길이
      - 게시 후 지난 날짜가 크게 다른 영상은 같은 줄에서 비교하지 않고 표시해 둔다

  - step: 2
    name: 내 채널 기준 정하기
    do:
      - 조회수의 중앙값을 구한다
      - 영상마다 ratio를 구한다. 조회수 ÷ 중앙값
      - ratio가 5 이상이면 outlier로 표시한다
      - ratio 위 3개와 아래 3개를 항상 함께 뽑는다

  - step: 3
    name: 영상마다 막힌 곳 찾기
    diagnose:
      노출: 노출수가 채널 중앙값보다 적다. 주제의 시청자 풀이 좁거나 경쟁이 심할 수 있다
      클릭: 노출수는 비슷한데 노출 클릭률이 낮다. 제목과 썸네일을 본다
      시청: 클릭은 되는데 평균 조회율이나 인트로 비율이 낮다. 첫 30초와 하락 구간을 본다
    do:
      - 영상마다 셋 중 가장 약한 곳 하나를 고른다
      - 시청 지속 시간 보고서가 있으면 하락 구간의 시각과 그때 화면에 있던 것을 적는다

  - step: 4
    name: 약속과 영상 대조하기
    check:
      packaging:
        - 제목과 썸네일이 함께 하나의 약속을 하는가
        - 썸네일만 봐도 누구를 위한 무슨 영상인지 알 수 있는가
      opening:                            # 첫 30초
        promise: 시청자가 클릭한 이유를 바로 확인해 주는가
        proof: 이 영상을 믿고 볼 이유를 보여 주는가
        plan: 영상이 어디로 가는지 알려 주는가
      delivery:
        - 영상이 약속한 것을 실제로 주는가
        - 편집과 화면이 이해를 돕는가, 움직임만 더하는가
      format:
        - 직접 겪은 과정을 증거와 함께 보여 주는가, 일반론을 설명하는가
        - 구조는 무엇인가. 목록, 과정 기록, 비교, 도전

  - step: 5
    name: 패턴 찾기
    do:
      - 위 3개에 공통이고 아래 3개에 없는 특징을 찾는다
      - 그 특징을 가진 다른 영상을 전부 세고 안된 것도 함께 적는다
      - 채널의 다른 영상과 시청자가 겹치지 않는 영상이 outlier면 따로 표시한다. 조회수가 높아도 채널에는 덜 도움이 될 수 있다

  - step: 6
    name: 다음에 시험할 한 가지 정하기
    do:
      - 가설 하나를 고른다
      - 바꿀 변수는 하나로 한다. 썸네일, 제목 형식, 첫 30초, 주제, 길이 중 하나
      - 볼 지표와 영상 수를 정한다. 영상 4개 이상으로 본다
      - 어떤 결과면 가설을 버릴지 미리 적는다
    note: 꾸준히 올리는 이유는 알고리즘의 보상이 아니라 비교할 데이터를 모으는 것이다
```

## 산출물

아래는 보고서의 형식이다. 출력 폴더에 `youtube-video-analysis-{YYYYMMDD}.yaml`로 저장하고 대화에도 요약을 보여 준다.

```yaml
channel: 채널 이름
period: 2026-07-01 ~ 2026-09-27
created: 2026-09-27
data_sources: [studio_export, public]
baseline:
  videos: 12
  median_views: 840
  median_ctr: 3.1
  median_average_percentage_viewed: 38
videos:
  - video_id: AbCdEfGhIjK
    title: 한강 자전거 40km, 해 질 때까지
    published: 2026-08-14
    length_sec: 612
    views: 5100
    ratio: 6.1
    outlier: true
    impressions: 61000
    ctr: 5.4
    average_view_duration_sec: 281
    average_percentage_viewed: 46
    weakest: null                         # 노출 | 클릭 | 시청 | null
    promise: 한강을 따라 해 질 때까지 달리는 하루
    opening: {promise: true, proof: false, plan: true}
    format: 과정 기록
    notes: 3분 40초 하락 구간, 같은 구도의 주행 장면이 50초 이어짐
patterns:
  - observation: 과정 기록 형식 4개 중 3개가 ratio 2 이상
    supporting: [AbCdEfGhIjK, BcDeFgHiJkL, CdEfGhIjKlM]
    counter: [DeFgHiJkLmN]
hypotheses:
  - id: h1
    statement: 썸네일에 도착 장면을 쓰면 노출 클릭률이 오른다
    based_on: 썸네일에 도착 장면이 있는 영상 3개의 클릭률이 중앙값보다 높음
    confidence: low                       # low | medium | high
next_experiment:
  hypothesis: h1
  change: 썸네일
  keep: [주제, 제목 형식, 길이]
  metric: ctr
  videos: 4
  discard_when: 4개 중 3개 이상이 중앙값 이하
missing:
  - 트래픽 소스가 없어 클릭률 비교는 참고용임
```

## 완료 확인

아래를 모두 만족해야 끝난다.

```yaml
done_when:
  - 모든 영상이 한 표에 있고 없는 값은 null이다
  - 잘된 영상과 안된 영상을 함께 봤다
  - 패턴마다 supporting과 counter가 있다
  - observation과 hypothesis가 섞이지 않았다
  - 클릭률을 말할 때 노출수와 트래픽 소스를 함께 적었다
  - next_experiment에서 바꾸는 변수가 하나다
  - 저장한 YAML 파일이 파싱된다
```
