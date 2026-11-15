#!/bin/bash
# git push·gh pr create 직전에만 동작한다. plugin·규칙·결정을 바꿨는데 knowledges/가 그대로면 막는다.
# KNOW_RANGE: 비교 범위(시험용). 기본은 origin/main...HEAD.

cmd=$(jq -r '.tool_input.command // empty')
# 따옴표 안의 글(커밋 메시지 등)은 빼고 본다. git·gh 뒤의 전역 옵션(-C x, -c k=v, -R o/r)과 gh pr new 별칭도 잡는다.
bare=$(printf '%s' "$cmd" | sed -E "s/\"[^\"]*\"//g; s/'[^']*'//g")
printf '%s' "$bare" | grep -Eq '(^|[;&|(){}[:space:]])(git([[:space:]]+-[cC][[:space:]]+[^[:space:]]+|[[:space:]]+--[^[:space:]]+)*[[:space:]]+push|gh([[:space:]]+-R[[:space:]]+[^[:space:]]+)*[[:space:]]+pr[[:space:]]+(create|new))([;&|(){}[:space:]]|$)' || exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

changed=$(git diff --name-only "${KNOW_RANGE:-origin/main...HEAD}" 2>/dev/null) || exit 0
echo "$changed" | grep -Eq '^(plugins/|docs/adr/|scripts/|AGENTS\.md$)' || exit 0
echo "$changed" | grep -q '^knowledges/' && exit 0

{
  echo "knowledges/가 갱신되지 않았다. push·PR 전에 아래를 같은 브랜치에 커밋한다."
  echo "- knowledges/log.md: 오늘 날짜 아래 무엇이 바뀌었는지 한 줄"
  echo "- 바뀐 plugin·규칙·결정·검사의 concept(knowledges/plugins|policies|decisions|checks/): 본문, 설계 판단과 버린 대안, generated"
  echo "바뀐 경로:"
  echo "$changed" | grep -E '^(plugins/|docs/adr/|scripts/|AGENTS\.md$)' | cut -d/ -f1-2 | sort -u | sed 's/^/  /'
} >&2
exit 2
