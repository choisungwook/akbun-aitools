#!/bin/bash
# Check that all opening code blocks in a markdown file specify a language type.

file=$(jq -r '.tool_input.file_path // empty')

# Only check .md files
[[ "$file" != *.md ]] && exit 0
[[ ! -f "$file" ]] && exit 0

result=$(awk '
/^```[a-zA-Z]/ { in_block = 1; next }
/^```/ {
  if (!in_block) { print "Line " NR ": code block missing language type" }
  in_block = 0
}
' "$file")

if [[ -n "$result" ]]; then
  echo "Markdown lint error in $file:"
  echo "$result"
  exit 1
fi
