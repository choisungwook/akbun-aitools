#!/bin/bash
# git push·gh pr create 직전에만 동작한다. plugin·규칙·결정·검사를 바꿨는데 knowledges/에 log와 의사결정이 없으면 막는다.
# Claude Code·Codex: stdin .tool_input.command, 막으면 stderr + exit 2.
# Antigravity(--agy): stdin .toolCall.args.CommandLine, 막으면 stdout {"decision":"deny"}, 아니면 {}.
# KNOW_RANGE: 비교 범위(시험용). 기본은 origin/main...HEAD.

agy=0; [ "$1" = --agy ] && agy=1
pass() { [ $agy = 1 ] && echo '{}'; exit 0; }

# Codex는 command를 argv 배열로 줄 수 있어 공백으로 잇는다.
cmd=$(jq -r '(.tool_input.command // .toolCall.args.CommandLine // "") | if type == "array" then join(" ") else . end')
# 따옴표 안의 글(커밋 메시지 등)은 빼고 본다. git·gh 뒤의 전역 옵션(-C x, -c k=v, -R o/r)과 gh pr new 별칭도 잡는다.
bare=$(printf '%s' "$cmd" | sed -E "s/\"[^\"]*\"//g; s/'[^']*'//g")
printf '%s' "$bare" | grep -Eq '(^|[;&|(){}[:space:]])(git([[:space:]]+-[cC][[:space:]]+[^[:space:]]+|[[:space:]]+--[^[:space:]]+)*[[:space:]]+push|gh([[:space:]]+-R[[:space:]]+[^[:space:]]+)*[[:space:]]+pr[[:space:]]+(create|new))([;&|(){}[:space:]]|$)' || pass
cd "${CLAUDE_PROJECT_DIR:-.}" && cd "$(git rev-parse --show-toplevel)" || pass

range="${KNOW_RANGE:-origin/main...HEAD}"
changed=$(git diff --name-only "$range" 2>/dev/null) || pass
echo "$changed" | grep -Eq '^(plugins/|docs/adr/|scripts/|AGENTS\.md$)' || pass

missing=""
echo "$changed" | grep -q '^knowledges/log\.md$' || missing="$missing
- knowledges/log.md: 오늘 날짜 아래 무엇이 바뀌었는지 한 줄"
# 의사결정: knowledges/decisions/의 결정 문서를 추가·수정하거나, 남길 결정이 없으면 log에 '결정 없음: <이유>' 줄을 더한다(규칙을 인용한 '<이유>' 자리표시는 세지 않는다).
echo "$changed" | grep -q '^knowledges/decisions/' || git diff "$range" -- knowledges/log.md | grep -q '^+.*결정 없음: [^<]' || missing="$missing
- knowledges/decisions/: 이번 변경의 의사결정(무엇을 정했나, 이유, 버린 대안). 되돌리기 어려우면 docs/adr/에 원본을 두고 미러를 만든다. 남길 결정이 없으면 log.md 줄에 '결정 없음: <이유>'"
[ -z "$missing" ] && pass

msg="knowledges/에 기록이 빠졌다. push·PR 전에 같은 브랜치에 커밋한다.$missing
- 바뀐 plugin·규칙·검사의 concept(knowledges/plugins|policies|checks/)도 본문과 generated를 고친다
바뀐 경로:
$(echo "$changed" | grep -E '^(plugins/|docs/adr/|scripts/|AGENTS\.md$)' | cut -d/ -f1-2 | sort -u | sed 's/^/  /')"
if [ $agy = 1 ]; then
  jq -n --arg r "$msg" '{decision: "deny", reason: $r}'
  exit 0
fi
echo "$msg" >&2
exit 2
