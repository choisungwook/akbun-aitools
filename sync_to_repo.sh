#!/bin/bash
# Sync akbun-* skills and agents from ~/.claude to this repo's plugin directory.
# Interactive: preview changes, confirm before syncing, and bump plugin version.
# Usage: ./sync_to_repo.sh

set -e

# ── Constants ─────────────────────────────────────────────────

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$REPO_DIR/plugins/akbun-skills"
PLUGIN_JSON="$PLUGIN_DIR/.claude-plugin/plugin.json"
SOURCE_DIR="$HOME/.claude"
PREFIX="akbun-"

# ── Output helpers ────────────────────────────────────────────

BOLD='\033[1m' GREEN='\033[0;32m' CYAN='\033[0;36m' YELLOW='\033[0;33m' RED='\033[0;31m' RESET='\033[0m'

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

# ── Discovery: find what will be synced ───────────────────────

discover_skills() {
  local src="$SOURCE_DIR/skills"
  SKILLS=()
  [ -d "$src" ] || return
  for dir in "$src"/${PREFIX}*; do
    [ -d "$dir" ] || continue
    SKILLS+=("$(basename "$dir")")
  done
}

discover_agents() {
  local src="$SOURCE_DIR/agents"
  AGENTS=()
  [ -d "$src" ] || return
  for file in "$src"/${PREFIX}*; do
    [ -f "$file" ] || continue
    AGENTS+=("$(basename "$file")")
  done
}

# ── Preview: show what will be synced ─────────────────────────

preview() {
  print_header "Preview: ~/.claude → plugins/akbun-skills"

  if [ ${#SKILLS[@]} -gt 0 ]; then
    echo -e "  ${BOLD}Skills (${#SKILLS[@]})${RESET}"
    for name in "${SKILLS[@]}"; do
      log_info "$name"
    done
  else
    log_warn "No ${PREFIX}* skills found"
  fi

  echo ""

  if [ ${#AGENTS[@]} -gt 0 ]; then
    echo -e "  ${BOLD}Agents (${#AGENTS[@]})${RESET}"
    for name in "${AGENTS[@]}"; do
      log_info "$name"
    done
  else
    log_warn "No ${PREFIX}* agents found"
  fi

  echo ""
}

# ── Sync: copy files to repo ─────────────────────────────────

sync_skills() {
  [ ${#SKILLS[@]} -eq 0 ] && return
  mkdir -p "$PLUGIN_DIR/skills"
  for name in "${SKILLS[@]}"; do
    rsync -a --delete "$SOURCE_DIR/skills/$name/" "$PLUGIN_DIR/skills/$name/"
    log_ok "skill: $name"
  done
}

sync_agents() {
  [ ${#AGENTS[@]} -eq 0 ] && return
  mkdir -p "$PLUGIN_DIR/agents"
  for name in "${AGENTS[@]}"; do
    cp "$SOURCE_DIR/agents/$name" "$PLUGIN_DIR/agents/$name"
    log_ok "agent: $name"
  done
}

# ── Version bump ──────────────────────────────────────────────

bump_version() {
  if [ ! -f "$PLUGIN_JSON" ]; then
    log_warn "plugin.json not found, skipping version bump"
    return
  fi

  local current
  current=$(jq -r '.version' "$PLUGIN_JSON")
  echo -e "  Current version: ${BOLD}$current${RESET}"
  echo ""
  echo "  Bump type:"
  echo "    1) patch  (x.y.Z)"
  echo "    2) minor  (x.Y.0)"
  echo "    3) major  (X.0.0)"
  echo "    4) skip"
  echo ""
  read -rp "  Choose [1/2/3/4]: " bump_type

  local major minor patch
  IFS='.' read -r major minor patch <<< "$current"

  case "$bump_type" in
    1) patch=$((patch + 1)) ;;
    2) minor=$((minor + 1)); patch=0 ;;
    3) major=$((major + 1)); minor=0; patch=0 ;;
    4) log_info "Version unchanged: $current"; return ;;
    *) log_warn "Invalid choice, skipping"; return ;;
  esac

  local new_version="$major.$minor.$patch"
  local tmp
  tmp=$(mktemp)
  jq --arg v "$new_version" '.version = $v' "$PLUGIN_JSON" > "$tmp" && mv "$tmp" "$PLUGIN_JSON"
  log_ok "Version bumped: $current → $new_version"
}

# ── Main ──────────────────────────────────────────────────────

discover_skills
discover_agents

if [ ${#SKILLS[@]} -eq 0 ] && [ ${#AGENTS[@]} -eq 0 ]; then
  log_warn "Nothing to sync. No ${PREFIX}* items found in $SOURCE_DIR"
  exit 0
fi

preview

if ! confirm "Proceed with sync?"; then
  echo "Aborted."
  exit 0
fi

print_header "Syncing"
sync_skills
sync_agents

print_header "Version bump"
bump_version

echo "----------------------------------------"
log_info "Done. Review changes:"
echo "  git diff plugins/"
