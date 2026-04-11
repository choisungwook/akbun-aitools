#!/bin/bash
set -euo pipefail

# --- 상수 ---

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOKS_DIR="${SCRIPT_DIR}/hooks"
INSTALL_BASE="$HOME/.claude/hooks"
SETTINGS_FILE="$HOME/.claude/settings.json"

# --- 색상 ---

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# --- 출력 헬퍼 ---

info() {
  echo -e "${CYAN}[INFO]${NC} $1"
}

success() {
  echo -e "${GREEN}[OK]${NC} $1"
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# --- hook 스캔 ---

scan_hooks() {
  local hooks=()
  for dir in "${HOOKS_DIR}"/*/; do
    if [[ -f "${dir}install/settings.json" ]]; then
      hooks+=("$(basename "$dir")")
    fi
  done
  echo "${hooks[@]}"
}

# --- hook 설명 출력 ---

get_hook_description() {
  local hook_name="$1"
  local readme="${HOOKS_DIR}/${hook_name}/README.md"
  if [[ -f "$readme" ]]; then
    head -3 "$readme" | tail -1
  else
    echo "(설명 없음)"
  fi
}

# --- 선택 메뉴 ---

show_menu() {
  local hooks=("$@")

  echo ""
  echo -e "${BOLD}사용 가능한 hook 목록:${NC}"
  echo ""
  for i in "${!hooks[@]}"; do
    local desc
    desc=$(get_hook_description "${hooks[$i]}")
    echo -e "  ${BOLD}$((i + 1))${NC}) ${hooks[$i]}"
    echo -e "     ${desc}"
  done
  echo ""
}

select_hook() {
  local hooks=("$@")
  local choice

  while true; do
    read -rp "설치할 hook 번호를 선택하세요 (q: 종료): " choice

    if [[ "$choice" == "q" ]]; then
      info "설치를 취소합니다."
      exit 0
    fi

    if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#hooks[@]} )); then
      echo "${hooks[$((choice - 1))]}"
      return
    fi

    warn "올바른 번호를 입력하세요 (1-${#hooks[@]})"
  done
}

# --- 의존성 확인 ---

check_dependencies() {
  local hook_name="$1"
  local missing=()

  if ! command -v jq &>/dev/null; then
    missing+=("jq")
  fi
  if ! command -v shasum &>/dev/null; then
    missing+=("shasum")
  fi

  if [[ ${#missing[@]} -gt 0 ]]; then
    error "필수 의존성이 없습니다: ${missing[*]}"
    echo ""
    echo "설치 방법:"
    echo "  macOS:  brew install ${missing[*]}"
    echo "  Ubuntu: sudo apt install ${missing[*]}"
    exit 1
  fi

  success "의존성 확인 완료 (jq, shasum)"
}

# --- 작업 선택 ---

show_action_menu() {
  echo ""
  echo -e "${BOLD}작업을 선택하세요:${NC}"
  echo ""
  echo -e "  ${BOLD}1${NC}) 설치"
  echo -e "  ${BOLD}2${NC}) 제거"
  echo ""
}

select_action() {
  local choice

  while true; do
    read -rp "번호를 선택하세요 (q: 종료): " choice

    if [[ "$choice" == "q" ]]; then
      info "종료합니다."
      exit 0
    fi

    if [[ "$choice" == "1" ]]; then
      echo "install"
      return
    elif [[ "$choice" == "2" ]]; then
      echo "uninstall"
      return
    fi

    warn "올바른 번호를 입력하세요 (1-2)"
  done
}

# --- hook 제거 ---

uninstall_hook() {
  local hook_name="$1"
  local dst="${INSTALL_BASE}/${hook_name}"

  if [[ ! -d "$dst" ]]; then
    warn "${dst} 디렉터리가 존재하지 않습니다. 이미 제거되었거나 설치되지 않았습니다."
    return
  fi

  read -rp "${dst} 디렉터리를 삭제하시겠습니까? (y/N): " confirm
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    info "제거를 취소합니다."
    exit 0
  fi

  rm -rf "$dst"
  success "${dst} 디렉터리를 삭제했습니다."
}

uninstall_settings() {
  local hook_name="$1"

  if [[ ! -f "$SETTINGS_FILE" ]]; then
    warn "settings.json 파일이 없습니다."
    return
  fi

  if ! jq -e --arg pattern "hooks/${hook_name}/" '.hooks // {} | to_entries[] | .value[] | .hooks[] | .command | contains($pattern)' "$SETTINGS_FILE" &>/dev/null; then
    warn "settings.json에 ${hook_name} hook 설정이 없습니다."
    return
  fi

  cp "$SETTINGS_FILE" "${SETTINGS_FILE}.bak"
  info "백업 생성: ${SETTINGS_FILE}.bak"

  local tmp
  tmp=$(mktemp)
  jq --indent 2 --arg pattern "hooks/${hook_name}/" '
    .hooks |= (
      to_entries | map(
        .value |= map(
          select(.hooks | any(.command | contains($pattern)) | not)
        )
        | select(.value | length > 0)
      ) | from_entries
    )
    | if .hooks == {} then del(.hooks) else . end
  ' "$SETTINGS_FILE" > "$tmp"

  mv "$tmp" "$SETTINGS_FILE"
  success "settings.json에서 hook 설정을 제거했습니다."
}

# --- 스크립트 복사 ---

copy_scripts() {
  local hook_name="$1"
  local src="${HOOKS_DIR}/${hook_name}/scripts"
  local dst="${INSTALL_BASE}/${hook_name}"

  if [[ -d "$dst" ]]; then
    warn "${dst} 디렉터리가 이미 존재합니다."
    read -rp "덮어쓰시겠습니까? (y/N): " overwrite
    if [[ "$overwrite" != "y" && "$overwrite" != "Y" ]]; then
      info "설치를 취소합니다."
      exit 0
    fi
  fi

  mkdir -p "$dst"

  local count=0
  for script in "${src}"/*.sh; do
    if [[ -f "$script" ]]; then
      cp "$script" "$dst/"
      chmod +x "${dst}/$(basename "$script")"
      count=$((count + 1))
    fi
  done

  success "${count}개 스크립트를 ${dst}/ 에 복사했습니다."
}

# --- settings.json 자동 설정 ---

install_settings() {
  local hook_name="$1"
  local snippet="${HOOKS_DIR}/${hook_name}/install/settings.json"

  if [[ ! -f "$SETTINGS_FILE" ]]; then
    mkdir -p "$(dirname "$SETTINGS_FILE")"
    echo '{}' > "$SETTINGS_FILE"
    info "settings.json 파일을 생성했습니다."
  fi

  if jq -e --arg pattern "hooks/${hook_name}/" '.hooks // {} | to_entries[] | .value[] | .hooks[] | .command | contains($pattern)' "$SETTINGS_FILE" &>/dev/null; then
    warn "settings.json에 ${hook_name} hook이 이미 등록되어 있습니다. 건너뜁니다."
    return
  fi

  cp "$SETTINGS_FILE" "${SETTINGS_FILE}.bak"
  info "백업 생성: ${SETTINGS_FILE}.bak"

  local tmp
  tmp=$(mktemp)
  jq -s --indent 2 '
    .[0] as $existing | .[1] as $new |
    $existing | .hooks = (
      ($new.hooks | keys) | reduce .[] as $key (
        ($existing.hooks // {});
        .[$key] = ((.[$key] // []) + $new.hooks[$key])
      )
    )
  ' "$SETTINGS_FILE" "$snippet" > "$tmp"

  mv "$tmp" "$SETTINGS_FILE"
  success "settings.json에 hook 설정을 추가했습니다."
}

# --- 메인 ---

main() {
  echo ""
  echo -e "${BOLD}Claude Code Hook 설치 도구${NC}"
  echo ""

  # hook 스캔
  local hooks_str
  hooks_str=$(scan_hooks)

  if [[ -z "$hooks_str" ]]; then
    error "설치 가능한 hook이 없습니다."
    exit 1
  fi

  local hooks
  read -ra hooks <<< "$hooks_str"

  # 작업 선택
  show_action_menu
  local action
  action=$(select_action)

  # hook 선택 메뉴
  show_menu "${hooks[@]}"
  local selected
  selected=$(select_hook "${hooks[@]}")

  echo ""

  if [[ "$action" == "install" ]]; then
    info "\"${selected}\" hook을 설치합니다."
    echo ""

    # 의존성 확인
    check_dependencies "$selected"

    # 스크립트 복사
    copy_scripts "$selected"

    # settings.json 자동 설정
    install_settings "$selected"

    success "설치가 완료되었습니다!"
  else
    info "\"${selected}\" hook을 제거합니다."
    echo ""

    # 스크립트 디렉터리 삭제
    uninstall_hook "$selected"

    # settings.json 자동 제거
    uninstall_settings "$selected"

    success "제거가 완료되었습니다!"
  fi

  echo ""
}

main "$@"
