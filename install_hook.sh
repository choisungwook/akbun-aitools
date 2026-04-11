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

# --- settings.json snippet 생성 ---

show_settings_snippet() {
  local hook_name="$1"
  local settings_json="${HOOKS_DIR}/${hook_name}/install/settings.json"

  echo ""
  echo -e "${BOLD}========================================${NC}"
  echo -e "${BOLD} settings.json 설정 안내${NC}"
  echo -e "${BOLD}========================================${NC}"
  echo ""
  echo -e "아래 내용을 ${CYAN}${SETTINGS_FILE}${NC} 의 ${CYAN}\"hooks\"${NC} 항목에 추가하세요."
  echo ""

  jq '.hooks' "$settings_json"

  echo ""
  echo -e "${YELLOW}주의:${NC} 이미 hooks 항목이 있다면 기존 배열에 추가하세요."
  echo ""
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

  # 선택 메뉴
  show_menu "${hooks[@]}"
  local selected
  selected=$(select_hook "${hooks[@]}")

  echo ""
  info "\"${selected}\" hook을 설치합니다."
  echo ""

  # 의존성 확인
  check_dependencies "$selected"

  # 스크립트 복사
  copy_scripts "$selected"

  # settings.json snippet 안내
  show_settings_snippet "$selected"

  success "설치가 완료되었습니다!"
  echo ""
}

main "$@"
