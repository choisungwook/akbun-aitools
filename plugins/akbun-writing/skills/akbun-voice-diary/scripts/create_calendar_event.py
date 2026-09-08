#!/usr/bin/env python3
"""Create an Apple Calendar event (macOS only).

Usage: create_calendar_event.py <title> <YYYY-MM-DD> [--start HH:MM] [--minutes N] [--calendar <name>] [--notes-file <path>]
Skips creation when an event with the same title already starts on that day.
"""
from __future__ import annotations

import argparse
import datetime
import platform
import subprocess
import sys

APPLESCRIPT = """
on run argv
  set eventTitle to item 1 of argv
  set y to (item 2 of argv) as integer
  set mo to (item 3 of argv) as integer
  set d to (item 4 of argv) as integer
  set h to (item 5 of argv) as integer
  set mi to (item 6 of argv) as integer
  set durationMinutes to (item 7 of argv) as integer
  set calName to item 8 of argv
  set eventNotes to item 9 of argv

  set startDate to current date
  set day of startDate to 1
  set year of startDate to y
  set month of startDate to mo
  set day of startDate to d
  set hours of startDate to h
  set minutes of startDate to mi
  set seconds of startDate to 0
  set endDate to startDate + (durationMinutes * minutes)
  set dayStart to startDate - (h * hours) - (mi * minutes)
  set dayEnd to dayStart + (1 * days)

  tell application "Calendar"
    if not (exists calendar calName) then make new calendar with properties {name:calName}
    tell calendar calName
      set dupes to (every event whose summary is eventTitle and start date is greater than or equal to dayStart and start date is less than dayEnd)
      if (count of dupes) > 0 then return "exists"
      make new event with properties {summary:eventTitle, start date:startDate, end date:endDate, description:eventNotes}
    end tell
  end tell
  return "created"
end run
"""


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("title")
  parser.add_argument("date", help="YYYY-MM-DD")
  parser.add_argument("--start", default="10:00", help="HH:MM (default 10:00)")
  parser.add_argument("--minutes", type=int, default=60)
  parser.add_argument("--calendar", default="공부")
  parser.add_argument("--notes-file", default="")
  args = parser.parse_args()

  if platform.system() != "Darwin":
    print("Apple Calendar is only available on macOS", file=sys.stderr)
    return 2

  try:
    day = datetime.date.fromisoformat(args.date)
    start = datetime.time.fromisoformat(args.start)
  except ValueError as exc:
    print(f"invalid date/time: {exc}", file=sys.stderr)
    return 2

  notes = ""
  if args.notes_file:
    with open(args.notes_file, encoding="utf-8") as fh:
      notes = fh.read()

  argv = [
    "osascript", "-",
    args.title,
    str(day.year), str(day.month), str(day.day),
    str(start.hour), str(start.minute),
    str(args.minutes),
    args.calendar,
    notes,
  ]
  result = subprocess.run(argv, input=APPLESCRIPT, capture_output=True, text=True)
  if result.returncode != 0:
    print(result.stderr.strip(), file=sys.stderr)
    return 1
  status = result.stdout.strip()
  print(f"{status}: {args.title} @ {day} {args.start} ({args.calendar})")
  return 0


if __name__ == "__main__":
  sys.exit(main())
