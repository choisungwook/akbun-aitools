#!/usr/bin/env python3
"""Collect yesterday's Readwise Reader documents and Readwise highlights into one JSON file.

Yesterday is the half-open interval [yesterday 00:00, today 00:00) in --tz (default Asia/Seoul).
Requires READWISE_TOKEN in the environment. The token is never printed.
Exit codes: 0 ok, 2 missing token, 3 API failure.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

READER_LIST = "https://readwise.io/api/v3/list/"
HIGHLIGHT_EXPORT = "https://readwise.io/api/v2/export/"
LOCATIONS = ("feed", "new", "later")
CONTENT_LIMIT = 8000
WORDS_PER_MINUTE = 238


class ApiError(RuntimeError):
  pass


def api_get(url: str, params: dict[str, Any], token: str) -> dict[str, Any]:
  query = urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
  request = urllib.request.Request(f"{url}?{query}", headers={"Authorization": f"Token {token}"})
  for attempt in range(5):
    try:
      with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
      if err.code == 429 and attempt < 4:
        time.sleep(int(err.headers.get("Retry-After", "5")))
        continue
      raise ApiError(f"HTTP {err.code} on {url}") from err
    except urllib.error.URLError as err:
      raise ApiError(f"network error on {url}: {err.reason}") from err
  raise ApiError(f"rate limited on {url}")


def parse_iso(value: str | None) -> datetime | None:
  if not value:
    return None
  parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
  return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def is_http_url(value: str | None) -> bool:
  return bool(value) and value.startswith(("http://", "https://"))


def pick_output_url(source_url: str | None, reader_url: str | None) -> str | None:
  if is_http_url(source_url):
    return source_url
  if is_http_url(reader_url):
    return reader_url
  return None


def display_site_name(site_name: str | None) -> str | None:
  if is_http_url(site_name):
    return urllib.parse.urlparse(site_name).netloc or site_name
  return site_name


def html_to_text(raw: str | None) -> str:
  if not raw:
    return ""
  text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
  text = re.sub(r"<br\s*/?>|</p>|</h\d>|</li>", "\n", text, flags=re.I)
  text = re.sub(r"<[^>]+>", " ", text)
  text = html.unescape(text)
  text = re.sub(r"[ \t]+", " ", text)
  text = re.sub(r"\n\s*\n+", "\n", text)
  return text.strip()[:CONTENT_LIMIT]


def reading_time(word_count: int | None) -> str | None:
  if not word_count:
    return None
  return f"{max(1, round(word_count / WORDS_PER_MINUTE))} min"


def compute_range(tz: ZoneInfo, target: date | None) -> dict[str, Any]:
  now_local = datetime.now(tz)
  day = target or (now_local.date() - timedelta(days=1))
  start_local = datetime(day.year, day.month, day.day, tzinfo=tz)
  end_local = start_local + timedelta(days=1)
  return {
    "timezone": tz.key,
    "date": day.isoformat(),
    "start_local": start_local.isoformat(),
    "end_local": end_local.isoformat(),
    "start_utc": start_local.astimezone(timezone.utc).isoformat(),
    "end_utc": end_local.astimezone(timezone.utc).isoformat(),
    "_start": start_local,
    "_end": end_local,
  }


def collect_documents(token: str, window: dict[str, Any], tz: ZoneInfo) -> tuple[list[dict[str, Any]], dict[str, int]]:
  seen: set[str] = set()
  documents: list[dict[str, Any]] = []
  stats = {"collected_total": 0, "excluded_by_date": 0, "duplicates": 0, "saved": 0, "rss": 0}
  for location in LOCATIONS:
    cursor: str | None = None
    while True:
      page = api_get(READER_LIST, {"location": location, "updatedAfter": window["start_utc"], "pageCursor": cursor}, token)
      for doc in page.get("results", []):
        stats["collected_total"] += 1
        saved_at = parse_iso(doc.get("saved_at"))
        if saved_at is None or not (window["_start"] <= saved_at < window["_end"]):
          stats["excluded_by_date"] += 1
          continue
        if doc["id"] in seen:
          stats["duplicates"] += 1
          continue
        seen.add(doc["id"])
        stats["rss" if location == "feed" else "saved"] += 1
        documents.append({
          "id": doc["id"],
          "title": doc.get("title"),
          "site_name": display_site_name(doc.get("site_name")),
          "location": location,
          "category": doc.get("category"),
          "saved_at_local": saved_at.astimezone(tz).isoformat(),
          "reading_time": reading_time(doc.get("word_count")),
          "url": doc.get("url"),
          "source_url": doc.get("source_url"),
          "output_url": pick_output_url(doc.get("source_url"), doc.get("url")),
          "summary": doc.get("summary"),
        })
      cursor = page.get("nextPageCursor")
      if not cursor:
        break
  return documents, stats


def attach_content(token: str, documents: list[dict[str, Any]]) -> int:
  failed = 0
  for doc in documents:
    try:
      page = api_get(READER_LIST, {"id": doc["id"], "withHtmlContent": "true"}, token)
      results = page.get("results", [])
      text = html_to_text(results[0].get("html_content")) if results else ""
      if text:
        doc["content"] = text
      else:
        doc["content_error"] = "empty content"
        failed += 1
    except ApiError as err:
      doc["content_error"] = str(err)
      failed += 1
  return failed


def collect_highlights(token: str, window: dict[str, Any], tz: ZoneInfo) -> list[dict[str, Any]]:
  highlights: list[dict[str, Any]] = []
  cursor: str | None = None
  while True:
    page = api_get(HIGHLIGHT_EXPORT, {"updatedAfter": window["start_utc"], "pageCursor": cursor}, token)
    for book in page.get("results", []):
      for item in book.get("highlights", []):
        highlighted_at = parse_iso(item.get("highlighted_at"))
        if highlighted_at is None or not (window["_start"] <= highlighted_at < window["_end"]):
          continue
        highlights.append({
          "text": item.get("text"),
          "note": item.get("note"),
          "book_title": book.get("title"),
          "book_source_url": book.get("source_url") if is_http_url(book.get("source_url")) else None,
          "highlighted_at_local": highlighted_at.astimezone(tz).isoformat(),
        })
    cursor = page.get("nextPageCursor")
    if not cursor:
      break
  return highlights


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--tz", default=os.environ.get("PULSE_TZ") or "Asia/Seoul", help="IANA timezone (default Asia/Seoul)")
  parser.add_argument("--date", help="Target day YYYY-MM-DD in --tz (default: yesterday)")
  parser.add_argument("--with-content", action="store_true", help="Fetch each document body (one request per document)")
  parser.add_argument("--out", help="Write JSON here instead of stdout")
  args = parser.parse_args()

  token = os.environ.get("READWISE_TOKEN")
  if not token:
    print("READWISE_TOKEN is not set", file=sys.stderr)
    return 2

  tz = ZoneInfo(args.tz)
  window = compute_range(tz, date.fromisoformat(args.date) if args.date else None)
  try:
    documents, stats = collect_documents(token, window, tz)
    stats["content_failed"] = attach_content(token, documents) if args.with_content else 0
    highlights = collect_highlights(token, window, tz)
  except ApiError as err:
    print(str(err), file=sys.stderr)
    return 3

  result = {
    "range": {k: v for k, v in window.items() if not k.startswith("_")},
    "stats": {**stats, "highlights": len(highlights)},
    "documents": documents,
    "highlights": highlights,
  }
  payload = json.dumps(result, ensure_ascii=False, indent=2)
  if args.out:
    with open(args.out, "w", encoding="utf-8") as handle:
      handle.write(payload)
  else:
    print(payload)
  return 0


if __name__ == "__main__":
  sys.exit(main())
