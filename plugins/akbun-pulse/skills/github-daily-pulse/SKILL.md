---
name: github-daily-pulse
description: 오늘 00:00부터 실행 시각까지 내 GitHub 계정이 접근 가능한 모든 repo에서 갱신된 issue·discussion·merged PR·open/draft PR을 모아 한글 복습 문서(시간·핵심작업·모든 작업)로 만들고, 기본은 Gmail로 나에게 보내며 실패하면 Apple Notes에 저장한다. "오늘 GitHub 활동 정리", "데일리 펄스", "오늘 뭐 했는지 PR·issue 요약해서 메일로", "오늘 작업 복습 문서" 같은 요청에 사용한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# github-daily-pulse

하루가 끝날 때 **오늘 내가 어떤 결정을 했고 왜 했는지**를 다시 읽을 수 있게 만드는 skill이다. GitHub에 흩어진 issue, discussion, PR을 한 문서로 모으고 사용자 손에 바로 들어가는 곳(Gmail, Apple Notes, Google Docs, md 파일)에 놓는다. 사용자에게 출력 방식을 묻지 않는다. 요청에 방식이 있으면 그대로, 없으면 기본 순서를 따른다.

## 1. 수집

번들 스크립트가 `gh` CLI로 접근 가능한 모든 repo(소유·협업·조직)를 훑어 오늘 00:00(로컬 시간)부터 지금까지 갱신된 항목을 JSON으로 만든다.

```bash
python3 <skill-dir>/scripts/collect_github_activity.py --out /tmp/github-daily-pulse.json
```

- 기본 범위는 로컬 시간 기준 오늘 00:00 ~ 실행 시각이다. 사용자가 "어제", "이번 주"처럼 다른 범위를 말하면 `--since`, `--until`(ISO 8601)로 바꾼다.
- JSON의 `items`에 repo, type(issue/pull_request/discussion), state(open/closed/merged/draft/answered), title, url, body, `comments_since`(범위 안에 달린 댓글)가 들어 있다. `errors`는 권한이나 네트워크로 못 읽은 repo다.
- 스크립트가 exit 2로 끝나면 `gh`가 없거나 로그인이 안 된 것이다. 이때는 GitHub MCP로 대신한다. `get_me`로 로그인을 얻고, `search_issues`·`search_pull_requests`에 `updated:>=YYYY-MM-DD involves:<login>` 조건을 넣어 같은 항목을 모은다. MCP 검색은 내가 관여한 항목만 잡히므로 문서 앞에 "MCP 폴백, 관여한 항목만 수집" 한 줄을 남긴다.
- 항목이 0개면 문서 본문에 "오늘 활동 없음"과 검사한 repo 수만 적고 그대로 전달한다.

## 2. 문서 작성

언어는 한글이다. 아래 구조를 그대로 쓴다. 헤더 이름을 바꾸거나 섹션을 추가하지 않는다.

```markdown
## 시간
2026-09-07 00:00 ~ 18:32 (KST) · repo 12개 검사, 활동 repo 3개

## 핵심작업
1. ...
2. ...

## 모든 작업
1. 주제
   - 의도: ...
   - 의사결정: ...
   - 복습 포인트: ...
   - 링크: owner/repo#12 (merged PR), owner/repo#15 (open issue)
```

작성 원칙:

- **시간**: 수집 범위와 타임존, 검사한 repo 수, 활동이 있던 repo 수를 한 줄에 쓴다. JSON의 `range`, `repos_scanned`, `repos_with_activity`를 그대로 쓴다.
- **핵심작업**: 3~5개. merged PR, 결정이 내려진 issue·discussion, 리뷰 댓글이 오간 PR을 우선한다. 한 줄에 무엇이 끝났고 무엇이 바뀌었는지 적는다. 단순 제목 복사가 아니라 결과를 적는다.
- **모든 작업**: 관련 항목을 **주제**로 묶는다. 같은 기능을 다루는 issue와 PR은 한 주제다. 주제 순서는 repo별로 묶고 그 안에서 갱신 시각 순으로 둔다.
  - `의도`: body와 댓글에서 왜 이 작업을 했는지를 뽑는다. 제목만 있고 근거가 없으면 "본문 없음"이라고 쓴다.
  - `의사결정`: 무엇을 선택했고 무엇을 버렸는지, 그 이유. 댓글에서 방향이 바뀐 경우 반드시 남긴다. 결정이 없으면 "결정 없음".
  - `복습 포인트`: 내일 다시 읽으면 좋을 것 하나. 되돌리기 어려운 결정, 남은 TODO, 미해결 리뷰 코멘트.
  - `링크`: `owner/repo#번호 (상태)` 형식. 상태는 merged PR / open PR / draft PR / closed PR / open issue / closed issue / discussion 중 하나.
- 다른 사람이 만든 항목도 포함한다. 접근 가능한 repo에서 오늘 일어난 일 전체가 대상이다. 작성자가 내가 아니면 `(by login)`을 링크 옆에 붙인다.
- 추측을 사실처럼 쓰지 않는다. JSON에 없는 내용은 만들지 않는다.

## 3. 전달

요청에 출력 방식이 있으면 그것만 실행한다. 없으면 아래 순서다. 어느 경우에도 사용자에게 어디로 보낼지 묻지 않는다.

1. **Gmail(기본)**: Gmail MCP `send_message`로 나에게 보낸다. 받는 사람은 Gmail 계정 주소이며, MCP가 주소를 주지 않으면 `git config user.email`, 그것도 없으면 `gh api user --jq .email` 순으로 정한다. 제목은 `[github-daily-pulse] YYYY-MM-DD`, 본문은 2단계 문서 그대로.
2. **Apple Notes(폴백)**: Gmail MCP가 없거나 `send_message`가 실패하면 문서를 md 파일로 저장한 뒤 실행한다.

   ```bash
   python3 <skill-dir>/scripts/create_apple_note.py "github-daily-pulse YYYY-MM-DD" /tmp/github-daily-pulse.md --folder "github-daily-pulse"
   ```

3. **md 파일(최종 폴백)**: macOS가 아니거나 Apple Notes도 실패하면 `~/github-daily-pulse/YYYY-MM-DD.md`에 저장한다.

사용자가 방식을 지정한 경우:

- `Google Docs`: Google Docs/Drive MCP로 `github-daily-pulse YYYY-MM-DD` 문서를 만든다. MCP가 없으면 md 파일로 저장하고 그 사실을 알린다.
- `md 파일`: 경로를 줬으면 그 경로, 없으면 `~/github-daily-pulse/YYYY-MM-DD.md`.
- `Apple Notes`, `Gmail`: 위 명령을 그대로 쓴다.

## 4. 응답

채팅에는 2단계 문서 전체를 먼저 보여주고, 마지막 줄에 전달 결과를 한 줄로 적는다. 예: `Gmail 전송 완료 → user@example.com`, `Gmail 실패(MCP 없음) → Apple Notes 저장`. 실패 원인은 한 줄로만 적고 긴 설명을 하지 않는다.
