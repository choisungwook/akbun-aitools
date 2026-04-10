#!/bin/bash
# enforce-terse-korean.sh — UserPromptSubmit hook
# Claude 응답 생성 전에 한국어 간결 모드 규칙을 additionalContext로 주입한다.
# 설정: AKBUN_TERSE_LEVEL 환경변수 (lite|full|ultra, 기본: full, off면 비활성)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RULES_FILE="$SCRIPT_DIR/terse-rules.txt"
LEVEL="${AKBUN_TERSE_LEVEL:-full}"

# stdin 소비 (UserPromptSubmit hook 입력, 사용하지 않음)
cat > /dev/null

# off면 아무것도 주입하지 않음
[[ "$LEVEL" == "off" ]] && exit 0

# 규칙 파일 없으면 fail-open
[[ ! -f "$RULES_FILE" ]] && exit 0

# 해당 레벨 섹션 추출
LEVEL_UPPER=$(echo "$LEVEL" | tr '[:lower:]' '[:upper:]')
RULES=$(awk -v level="TERSE-$LEVEL_UPPER" '
  $0 ~ "^# " level { found=1; next }
  /^# / && found { found=0 }
  found && NF { print }
' "$RULES_FILE")

# AUTO-CLARITY + BOUNDARY 섹션 항상 포함
AUTO=$(awk '/^# AUTO-CLARITY/{ f=1; next } /^# / && f { f=0 } f && NF { print }' "$RULES_FILE")
BOUNDARY=$(awk '/^# BOUNDARY/{ f=1; next } /^# / && f { f=0 } f && NF { print }' "$RULES_FILE")

# 규칙이 비어있으면 (잘못된 레벨) fail-open
[[ -z "$RULES" ]] && exit 0

CONTEXT="[간결 모드: ${LEVEL}] ${RULES} ${AUTO} ${BOUNDARY}"

jq -n --arg ctx "$CONTEXT" '{"additionalContext": $ctx}'
