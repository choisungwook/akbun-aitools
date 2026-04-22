#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGINS_DIR="${SCRIPT_DIR}/plugins"
INSTALL_BASE="$HOME/plugins"
MARKETPLACE_FILE="$HOME/.agents/plugins/marketplace.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

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

scan_plugins() {
  local plugins=()
  for dir in "${PLUGINS_DIR}"/*/; do
    if [[ -f "${dir}.codex-plugin/plugin.json" ]]; then
      plugins+=("$(basename "$dir")")
    fi
  done
  echo "${plugins[@]}"
}

get_plugin_description() {
  local plugin_name="$1"
  local manifest="${PLUGINS_DIR}/${plugin_name}/.codex-plugin/plugin.json"
  if [[ -f "$manifest" ]]; then
    jq -r '.description // "(설명 없음)"' "$manifest"
  else
    echo "(설명 없음)"
  fi
}

show_menu() {
  local plugins=("$@")

  echo ""
  echo -e "${BOLD}사용 가능한 Codex plugin 목록:${NC}"
  echo ""
  for i in "${!plugins[@]}"; do
    local desc
    desc=$(get_plugin_description "${plugins[$i]}")
    echo -e "  ${BOLD}$((i + 1))${NC}) ${plugins[$i]}"
    echo -e "     ${desc}"
  done
  echo ""
}

select_plugin() {
  local plugins=("$@")
  local choice

  while true; do
    read -rp "설치할 plugin 번호를 선택하세요 (q: 종료): " choice

    if [[ "$choice" == "q" ]]; then
      info "작업을 취소합니다."
      exit 0
    fi

    if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#plugins[@]} )); then
      echo "${plugins[$((choice - 1))]}"
      return
    fi

    warn "올바른 번호를 입력하세요 (1-${#plugins[@]})"
  done
}

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
    fi

    if [[ "$choice" == "2" ]]; then
      echo "uninstall"
      return
    fi

    warn "올바른 번호를 입력하세요 (1-2)"
  done
}

check_dependencies() {
  local missing=()

  if ! command -v jq &>/dev/null; then
    missing+=("jq")
  fi

  if [[ ${#missing[@]} -gt 0 ]]; then
    error "필수 의존성이 없습니다: ${missing[*]}"
    echo ""
    echo "설치 방법:"
    echo "  macOS:  brew install ${missing[*]}"
    echo "  Ubuntu: sudo apt install ${missing[*]}"
    exit 1
  fi

  success "의존성 확인 완료 (${missing[*]:-jq})"
}

ensure_marketplace_file() {
  if [[ ! -f "$MARKETPLACE_FILE" ]]; then
    mkdir -p "$(dirname "$MARKETPLACE_FILE")"
    cat > "$MARKETPLACE_FILE" <<'EOF'
{
  "name": "local-plugins",
  "interface": {
    "displayName": "Local Plugins"
  },
  "plugins": []
}
EOF
    info "marketplace.json 파일을 생성했습니다."
  fi
}

copy_plugin() {
  local plugin_name="$1"
  local src="${PLUGINS_DIR}/${plugin_name}"
  local dst="${INSTALL_BASE}/${plugin_name}"

  mkdir -p "$INSTALL_BASE"

  if [[ -d "$dst" ]]; then
    warn "${dst} 디렉터리가 이미 존재합니다."
    read -rp "덮어쓰시겠습니까? (y/N): " overwrite
    if [[ "$overwrite" != "y" && "$overwrite" != "Y" ]]; then
      info "설치를 취소합니다."
      exit 0
    fi
    rm -rf "$dst"
  fi

  mkdir -p "$dst"
  cp -R "${src}/." "$dst/"
  success "${plugin_name} plugin을 ${dst} 에 복사했습니다."
}

install_marketplace_entry() {
  local plugin_name="$1"
  local manifest="${PLUGINS_DIR}/${plugin_name}/.codex-plugin/plugin.json"
  local category

  category=$(jq -r '.interface.category // "Productivity"' "$manifest")

  ensure_marketplace_file

  local tmp
  tmp=$(mktemp)
  jq --indent 2 \
    --arg plugin_name "$plugin_name" \
    --arg category "$category" \
    '
    .plugins = (
      (.plugins // [])
      | map(select(.name != $plugin_name))
      + [
        {
          "name": $plugin_name,
          "source": {
            "source": "local",
            "path": ("./plugins/" + $plugin_name)
          },
          "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL"
          },
          "category": $category
        }
      ]
    )
    ' "$MARKETPLACE_FILE" > "$tmp"

  mv "$tmp" "$MARKETPLACE_FILE"
  success "marketplace.json에 ${plugin_name} plugin을 등록했습니다."
}

remove_plugin() {
  local plugin_name="$1"
  local dst="${INSTALL_BASE}/${plugin_name}"

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

remove_marketplace_entry() {
  local plugin_name="$1"

  if [[ ! -f "$MARKETPLACE_FILE" ]]; then
    warn "marketplace.json 파일이 없습니다."
    return
  fi

  if ! jq -e --arg plugin_name "$plugin_name" '.plugins // [] | any(.name == $plugin_name)' "$MARKETPLACE_FILE" &>/dev/null; then
    warn "marketplace.json에 ${plugin_name} plugin 설정이 없습니다."
    return
  fi

  cp "$MARKETPLACE_FILE" "${MARKETPLACE_FILE}.bak"
  info "백업 생성: ${MARKETPLACE_FILE}.bak"

  local tmp
  tmp=$(mktemp)
  jq --indent 2 --arg plugin_name "$plugin_name" '
    .plugins = ((.plugins // []) | map(select(.name != $plugin_name)))
  ' "$MARKETPLACE_FILE" > "$tmp"

  mv "$tmp" "$MARKETPLACE_FILE"
  success "marketplace.json에서 ${plugin_name} plugin 설정을 제거했습니다."
}

main() {
  echo ""
  echo -e "${BOLD}Codex Plugin 설치 도구${NC}"
  echo ""

  local plugins_str
  plugins_str=$(scan_plugins)

  if [[ -z "$plugins_str" ]]; then
    error "설치 가능한 Codex plugin이 없습니다."
    exit 1
  fi

  local plugins
  read -ra plugins <<< "$plugins_str"

  check_dependencies

  show_action_menu
  local action
  action=$(select_action)

  show_menu "${plugins[@]}"
  local selected
  selected=$(select_plugin "${plugins[@]}")

  echo ""

  if [[ "$action" == "install" ]]; then
    info "\"${selected}\" plugin을 설치합니다."
    echo ""

    copy_plugin "$selected"
    install_marketplace_entry "$selected"

    success "설치가 완료되었습니다!"
    info "필요하면 Codex를 다시 시작하거나 plugin 목록을 새로고침하세요."
  else
    info "\"${selected}\" plugin을 제거합니다."
    echo ""

    remove_plugin "$selected"
    remove_marketplace_entry "$selected"

    success "제거가 완료되었습니다!"
  fi

  echo ""
}

main "$@"
