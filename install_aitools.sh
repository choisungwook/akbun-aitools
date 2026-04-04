#!/bin/bash
# Install akbun-aitools to ~/.claude or a project directory.
# Two methods: Claude Code /plugin command (recommended) or direct file copy.
# Interactive: choose components, preview what will be installed, confirm before copying.
# Usage: ./install_aitools.sh

set -e

# ── Constants ─────────────────────────────────────────────────

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_SRC="$REPO_DIR/plugins/akbun-skills"
GLOBAL_CLAUDE="$HOME/.claude"

# ── Output helpers ────────────────────────────────────────────

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

# ── Install via plugin marketplace ────────────────────────────

show_plugin_instructions() {
  print_header "Plugin install (recommended)"
  echo "Run these commands in Claude Code:"
  echo ""
  log_info "Add marketplace:"
  echo "    /plugin marketplace add choisungwook/akbun-aitools"
  echo ""
  log_info "Install plugin:"
  echo "    /plugin install akbun-skills@akbun-aitools"
  echo ""
  log_info "Update later:"
  echo "    claude plugin update akbun-skills@akbun-aitools"
  echo ""
  log_ok "Plugin install includes skills, agents, and hooks."
}

# ── Discovery: list available components ──────────────────────

discover_skills() {
  SKILL_NAMES=()
  [ -d "$PLUGIN_SRC/skills" ] || return
  for dir in "$PLUGIN_SRC/skills"/*/; do
    [ -d "$dir" ] || continue
    SKILL_NAMES+=("$(basename "$dir")")
  done
}

discover_agents() {
  AGENT_NAMES=()
  [ -d "$PLUGIN_SRC/agents" ] || return
  for file in "$PLUGIN_SRC/agents"/*.md; do
    [ -f "$file" ] || continue
    AGENT_NAMES+=("$(basename "$file")")
  done
}

discover_hooks() {
  HOOK_SCRIPTS=()
  [ -d "$PLUGIN_SRC/hooks" ] || return
  for file in "$PLUGIN_SRC/hooks"/*.sh; do
    [ -f "$file" ] || continue
    HOOK_SCRIPTS+=("$(basename "$file")")
  done
}

discover_rules() {
  RULE_FILES=()
  [ -d "$REPO_DIR/.claude/rules" ] || return
  for file in "$REPO_DIR/.claude/rules"/*.md; do
    [ -f "$file" ] || continue
    RULE_FILES+=("$(basename "$file")")
  done
}

# ── Target selection ──────────────────────────────────────────

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

# ── Component selection ───────────────────────────────────────

choose_components() {
  DO_SKILLS=false DO_AGENTS=false DO_HOOKS=false DO_RULES=false

  print_header "Choose components"
  confirm "  Skills (${#SKILL_NAMES[@]} items)?" && DO_SKILLS=true
  confirm "  Agents (${#AGENT_NAMES[@]} items)?" && DO_AGENTS=true
  confirm "  Hooks  (${#HOOK_SCRIPTS[@]} scripts)?" && DO_HOOKS=true
  confirm "  Rules  (${#RULE_FILES[@]} files)?" && DO_RULES=true
}

# ── Preview ───────────────────────────────────────────────────

preview() {
  print_header "Preview: install to $TARGET"

  local has_selection=false

  if $DO_SKILLS && [ ${#SKILL_NAMES[@]} -gt 0 ]; then
    echo -e "  ${BOLD}Skills${RESET}"
    for name in "${SKILL_NAMES[@]}"; do log_info "$name"; done
    echo ""
    has_selection=true
  fi

  if $DO_AGENTS && [ ${#AGENT_NAMES[@]} -gt 0 ]; then
    echo -e "  ${BOLD}Agents${RESET}"
    for name in "${AGENT_NAMES[@]}"; do log_info "$name"; done
    echo ""
    has_selection=true
  fi

  if $DO_HOOKS && [ ${#HOOK_SCRIPTS[@]} -gt 0 ]; then
    echo -e "  ${BOLD}Hooks${RESET}"
    for name in "${HOOK_SCRIPTS[@]}"; do log_info "$name"; done
    echo ""
    has_selection=true
  fi

  if $DO_RULES && [ ${#RULE_FILES[@]} -gt 0 ]; then
    echo -e "  ${BOLD}Rules${RESET}"
    for name in "${RULE_FILES[@]}"; do log_info "$name"; done
    echo ""
    has_selection=true
  fi

  if ! $has_selection; then
    log_warn "No components selected."
    exit 0
  fi
}

# ── Install functions ─────────────────────────────────────────

install_skills() {
  mkdir -p "$TARGET/skills"
  cp -r "$PLUGIN_SRC/skills/." "$TARGET/skills/"
  log_ok "Skills → $TARGET/skills/"
}

install_agents() {
  mkdir -p "$TARGET/agents"
  cp -r "$PLUGIN_SRC/agents/." "$TARGET/agents/"
  log_ok "Agents → $TARGET/agents/"
}

install_hooks() {
  mkdir -p "$TARGET/hooks"
  for script in "${HOOK_SCRIPTS[@]}"; do
    cp "$PLUGIN_SRC/hooks/$script" "$TARGET/hooks/"
  done
  log_ok "Hooks → $TARGET/hooks/"

  if [ -f "$TARGET/settings.json" ]; then
    log_warn "Existing settings.json found. Merge hooks config manually."
  else
    log_warn "Add hooks config to settings.json manually."
  fi
}

install_rules() {
  mkdir -p "$TARGET/rules"
  cp -r "$REPO_DIR/.claude/rules/." "$TARGET/rules/"
  log_ok "Rules → $TARGET/rules/"
}

# ── Main ──────────────────────────────────────────────────────

print_header "akbun-aitools installer"
echo "  1) Plugin install — via Claude Code /plugin command (recommended)"
echo "  2) Direct install — copy files with cp"
echo ""
read -rp "  Choose [1/2]: " method

case "$method" in
  1) show_plugin_instructions; exit 0 ;;
  2) ;; # continue to direct install flow below
  *) echo "  Invalid choice. Enter 1 or 2." && exit 1 ;;
esac

# Direct install flow: discover → target → select → preview → confirm → install

discover_skills
discover_agents
discover_hooks
discover_rules

choose_target
choose_components
preview

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
