#!/usr/bin/env python3
"""Create an Apple Notes note from a Markdown file (macOS only).

Usage: create_apple_note.py <title> <markdown-file> [--folder <name>]
Markdown is converted to the small HTML subset Notes renders well: headings, lists, links, paragraphs.
"""
from __future__ import annotations

import argparse
import html
import platform
import re
import subprocess
import sys

LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

APPLESCRIPT = """
on run argv
  set noteTitle to item 1 of argv
  set noteBody to item 2 of argv
  set folderName to item 3 of argv
  tell application "Notes"
    if folderName is "" then
      make new note with properties {name:noteTitle, body:noteBody}
    else
      if not (exists folder folderName) then make new folder with properties {name:folderName}
      make new note at folder folderName with properties {name:noteTitle, body:noteBody}
    end if
  end tell
end run
"""


def inline(text: str) -> str:
  escaped = html.escape(text, quote=False)
  return LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', escaped)


def markdown_to_html(title: str, markdown: str) -> str:
  parts = [f"<h1>{html.escape(title)}</h1>"]
  in_list: str | None = None
  for raw in markdown.splitlines():
    line = raw.rstrip()
    heading = re.match(r"^(#{1,6})\s+(.*)$", line)
    bullet = re.match(r"^\s*[-*]\s+(.*)$", line)
    numbered = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
    if in_list and not (bullet or numbered):
      parts.append(f"</{in_list}>")
      in_list = None
    if heading:
      level = min(len(heading.group(1)) + 1, 6)
      parts.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
    elif bullet or numbered:
      tag = "ul" if bullet else "ol"
      if in_list != tag:
        if in_list:
          parts.append(f"</{in_list}>")
        parts.append(f"<{tag}>")
        in_list = tag
      parts.append(f"<li>{inline((bullet or numbered).group(1))}</li>")
    elif line.strip() == "":
      parts.append("<br>")
    else:
      parts.append(f"<div>{inline(line)}</div>")
  if in_list:
    parts.append(f"</{in_list}>")
  return "".join(parts)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("title")
  parser.add_argument("markdown_file")
  parser.add_argument("--folder", default="")
  args = parser.parse_args()

  if platform.system() != "Darwin":
    print("Apple Notes is only available on macOS", file=sys.stderr)
    return 2

  with open(args.markdown_file, encoding="utf-8") as fh:
    body = markdown_to_html(args.title, fh.read())

  result = subprocess.run(
    ["osascript", "-", args.title, body, args.folder],
    input=APPLESCRIPT,
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    print(result.stderr.strip(), file=sys.stderr)
    return 1
  print(f"created Apple Note: {args.title}")
  return 0


if __name__ == "__main__":
  sys.exit(main())
