#!/bin/bash
# Install akbun-aitools plugins to ~/.claude or a project directory.
# Recommended: use Claude Code marketplace install. Direct install copies
# skills and agents from selected plugin roots for local use.
# Usage: ./install_aitools.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
GLOBAL_CLAUDE="$HOME/.claude"
MARKETPLACE_REPO="choisungwook/akbun-aitools"
MARKETPLACE_NAME="akbun-aitools"

BOLD='\033[1m' GREEN='\033[0;32m' CYAN='\033[0;36m' YELLOW='\033[0;33m' RESET='\033[0m'

log_ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
log_info() { echo -e "  ${CYAN}→${RESET} $1"; }
log_warn() { echo -e "  ${YELLOW}!${RESET} $1"; }

print_header() {
  echo -e "\n${BOLD}$1${RESET}"
  echo "----------------------------------------"
}

confirm() {
  read -rp "$1 [y/N]: " answer
  [[ "$answer" =~ ^[Yy]$ ]]
}

PLUGIN_NAMES=()
PLUGIN_DIRS=()
PLUGIN_DESCRIPTIONS=()
SELECTED_INDEXES=()
RULE_FILES=()
DO_RULES=false
TARGET=""

ensure_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "jq is required for this script."
    exit 1
  fi
}

contains_index() {
  local needle="$1"
  local item
  for item in "${SELECTED_INDEXES[@]}"; do
    [ "$item" = "$needle" ] && return 0
  done
  return 1
}

discover_plugins() {
  PLUGIN_NAMES=()
  PLUGIN_DIRS=()
  PLUGIN_DESCRIPTIONS=()

  local plugin_json plugin_dir name description
  for plugin_json in "$REPO_DIR"/plugins/*/.claude-plugin/plugin.json; do
    [ -f "$plugin_json" ] || continue
    plugin_dir="$(cd "$(dirname "$plugin_json")/.." && pwd)"
    name="$(jq -r '.name' "$plugin_json")"
    description="$(jq -r '.description // ""' "$plugin_json")"
    PLUGIN_NAMES+=("$name")
    PLUGIN_DIRS+=("$plugin_dir")
    PLUGIN_DESCRIPTIONS+=("$description")
  done

  if [ "${#PLUGIN_NAMES[@]}" -eq 0 ]; then
    echo "No plugins found under $REPO_DIR/plugins"
    exit 1
  fi
}

discover_rules() {
  RULE_FILES=()
  local file
  for file in "$REPO_DIR"/.claude/rules/*.md; do
    [ -f "$file" ] || continue
    RULE_FILES+=("$(basename "$file")")
  done
}

list_plugin_components() {
  local plugin_dir="$1"
  local kind="$2"
  local path="$plugin_dir/$kind"
  local item

  [ -d "$path" ] || return

  if [ "$kind" = "skills" ]; then
    for item in "$path"/*; do
      [ -d "$item" ] || continue
      echo "    - $(basename "$item")"
    done
    return
  fi

  for item in "$path"/*; do
    [ -f "$item" ] || continue
    echo "    - $(basename "$item")"
  done
}

show_plugin_instructions() {
  local i

  print_header "Plugin install (recommended)"
  echo "Run these commands in Claude Code:"
  echo ""
  log_info "Add marketplace:"
  echo "    /plugin marketplace add $MARKETPLACE_REPO"
  echo ""
  log_info "Install a plugin:"
  for i in "${!PLUGIN_NAMES[@]}"; do
    echo "    /plugin install ${PLUGIN_NAMES[$i]}@$MARKETPLACE_NAME"
  done
  echo ""
  log_info "Reload current session after install:"
  echo "    /reload-plugins"
  echo ""
  log_info "Update later:"
  echo "    claude plugin marketplace update $MARKETPLACE_NAME"
  for i in "${!PLUGIN_NAMES[@]}"; do
    echo "    claude plugin update ${PLUGIN_NAMES[$i]}@$MARKETPLACE_NAME"
  done
  echo ""
  log_warn "Third-party marketplaces do not auto-update by default."
  log_warn "Repo-local hooks in .claude/hooks are not distributed by marketplace install."
}

choose_target() {
  print_header "Choose install scope"
  echo "  1) Global  — all projects ($GLOBAL_CLAUDE)"
  echo "  2) Project — specific project only"
  echo ""
  read -rp "  Choose [1/2]: " scope

  if [ "$scope" = "2" ]; then
    read -rp "  Project path: " project_path
    if [ ! -d "$project_path" ]; then
      echo "  Path not found: $project_path"
      exit 1
    fi
    TARGET="$project_path/.claude"
  else
    TARGET="$GLOBAL_CLAUDE"
  fi
}

choose_plugins() {
  local i token

  print_header "Choose plugins for direct install"
  for i in "${!PLUGIN_NAMES[@]}"; do
    printf "  %d) %s — %s\n" "$((i + 1))" "${PLUGIN_NAMES[$i]}" "${PLUGIN_DESCRIPTIONS[$i]}"
  done
  echo "  all) Install every plugin above"
  echo ""
  read -rp "  Choose number(s) or 'all': " selection

  SELECTED_INDEXES=()

  if [ "$selection" = "all" ]; then
    for i in "${!PLUGIN_NAMES[@]}"; do
      SELECTED_INDEXES+=("$i")
    done
    return
  fi

  for token in $selection; do
    case "$token" in
      ''|*[!0-9]*)
        echo "  Invalid choice: $token"
        exit 1
        ;;
    esac

    if [ "$token" -lt 1 ] || [ "$token" -gt "${#PLUGIN_NAMES[@]}" ]; then
      echo "  Choice out of range: $token"
      exit 1
    fi

    token=$((token - 1))
    if ! contains_index "$token"; then
      SELECTED_INDEXES+=("$token")
    fi
  done

  if [ "${#SELECTED_INDEXES[@]}" -eq 0 ]; then
    echo "  No plugins selected."
    exit 1
  fi
}

choose_extra_assets() {
  DO_RULES=false
  print_header "Optional extras"
  if [ "${#RULE_FILES[@]}" -gt 0 ]; then
    confirm "  Repo-local rules (${#RULE_FILES[@]} files)?" && DO_RULES=true
  else
    log_warn "No repo-local rules found."
  fi
}

preview() {
  local i idx plugin_name plugin_dir

  print_header "Preview: install to $TARGET"
  echo "  Selected plugins:"
  for idx in "${SELECTED_INDEXES[@]}"; do
    plugin_name="${PLUGIN_NAMES[$idx]}"
    plugin_dir="${PLUGIN_DIRS[$idx]}"
    echo "  - $plugin_name"
    list_plugin_components "$plugin_dir" "skills"
    list_plugin_components "$plugin_dir" "agents"
  done

  echo ""
  if $DO_RULES; then
    echo "  Repo-local rules:"
    for i in "${RULE_FILES[@]}"; do
      echo "    - $i"
    done
  else
    echo "  Repo-local rules: not selected"
  fi

  echo ""
  log_warn "Hooks under .claude/hooks are repo-local and are not copied by direct install."
}

install_plugin_assets() {
  local plugin_dir="$1"
  local plugin_name="$2"

  if [ -d "$plugin_dir/skills" ]; then
    mkdir -p "$TARGET/skills"
    cp -R "$plugin_dir/skills/." "$TARGET/skills/"
  fi

  if [ -d "$plugin_dir/agents" ]; then
    mkdir -p "$TARGET/agents"
    cp -R "$plugin_dir/agents/." "$TARGET/agents/"
  fi

  log_ok "$plugin_name → $TARGET"
}

install_rules() {
  mkdir -p "$TARGET/rules"
  cp -R "$REPO_DIR/.claude/rules/." "$TARGET/rules/"
  log_ok "Rules → $TARGET/rules/"
}

main() {
  local method idx

  ensure_jq
  discover_plugins
  discover_rules

  print_header "akbun-aitools installer"
  echo "  1) Plugin install — via Claude Code /plugin command (recommended)"
  echo "  2) Direct install — copy skills and agents with cp"
  echo ""
  read -rp "  Choose [1/2]: " method

  case "$method" in
    1)
      show_plugin_instructions
      exit 0
      ;;
    2)
      ;;
    *)
      echo "  Invalid choice. Enter 1 or 2."
      exit 1
      ;;
  esac

  choose_target
  choose_plugins
  choose_extra_assets
  preview

  if ! confirm "Proceed with direct install?"; then
    echo "Aborted."
    exit 0
  fi

  print_header "Installing"
  for idx in "${SELECTED_INDEXES[@]}"; do
    install_plugin_assets "${PLUGIN_DIRS[$idx]}" "${PLUGIN_NAMES[$idx]}"
  done

  if $DO_RULES; then
    install_rules
  fi

  echo "----------------------------------------"
  log_ok "Done."
}

main

if ! confirm "  Proceed with install?"; then
  echo "  Aborted."
  exit 0
fi

print_header "Installing"
$DO_SKILLS && install_skills
$DO_AGENTS && install_agents
$DO_HOOKS  && install_hooks
$DO_RULES  && install_rules

echo ""
log_ok "Install complete!"
