# Readwise MCP 수집 절차

`PULSE_SOURCE=mcp`일 때 SKILL.md 2절을 Readwise MCP 도구로 수행하는 순서다. cli 모드는 `scripts/collect_readwise.py`가 같은 일을 하므로 이 문서를 읽지 않는다.

## 문서

`reader_list_documents`를 location마다 따로 호출한다. 호출 파라미터:

```json
{
  "location": "feed",
  "limit": 100,
  "updated_after": "<yesterday_start_utc>",
  "response_fields": ["title", "site_name", "location", "saved_at", "reading_time", "url", "source_url", "summary"],
  "page_cursor": null
}
```

- `location`은 `feed`, `new`, `later` 세 값을 각각 돌린다. `shortlist`, `archive`는 호출하지 않는다.
- 응답에 `nextPageCursor`가 있으면 같은 파라미터에 `page_cursor`만 바꿔 다시 호출한다. 없을 때까지 반복한다.
- `updated_after`는 `updated_at` 기준이고 `updated_before`가 없다. 그래서 어제 이전에 저장했지만 어제 읽거나 옮긴 문서도 섞여 온다. 응답을 그대로 믿지 않고 아래 필터를 반드시 적용한다.

날짜 필터:

- 각 문서의 `saved_at`을 `PULSE_TZ`로 변환한다.
- `yesterday_start_local <= saved_at < today_start_local`인 문서만 처리 대상이다.
- 범위 밖 문서는 "날짜 필터 제외 건수"에 더하고 버린다.
- 같은 문서 ID가 두 location에서 나오면 하나만 남긴다.

집계:

- 저장 수: 처리 대상 중 `location`이 `new` 또는 `later`
- RSS 수: 처리 대상 중 `location`이 `feed`
- 전체 수집 건수: 필터·중복 제거 전 문서 수
- 날짜 필터 제외 건수

## 하이라이트

`readwise_list_highlights` 호출 파라미터:

```json
{
  "highlighted_at_gt": "<yesterday_start_utc>",
  "page_size": 100,
  "response_fields": ["text", "note", "book_title", "book_source_url", "highlighted_at"],
  "page": 1
}
```

- 응답에 다음 페이지가 있으면 `page`를 1씩 올려 끝까지 읽는다.
- `highlighted_at`을 `PULSE_TZ`로 변환해 어제 반개구간 안의 것만 남긴다.

## 본문

처리 대상 문서마다 `reader_get_document_details`를 한 번씩 호출한다.

```json
{ "document_id": "<id>" }
```

- 응답의 Markdown 본문으로 요약한다. 오류가 나면 재시도하지 않고 "본문 로드 실패"로 표시한다.
- 처리 대상이 아닌 문서(날짜 필터 제외)는 호출하지 않는다.
