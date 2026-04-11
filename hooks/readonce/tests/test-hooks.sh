#!/bin/bash
set -euo pipefail

# =============================================================================
# readonce hook 단위 테스트
#
# 사용법:
#   ./tests/test-hooks.sh
#
# 각 hook 스크립트에 모의 JSON을 stdin으로 넘기고
# exit code, stderr, 캐시 파일 상태를 검증한다.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPTS_DIR="$PLUGIN_DIR/scripts"

# --- 테스트 유틸리티 ---

setup_temp_dir() {
  TEMP_DIR=$(mktemp -d)
  TEST_FILE="$TEMP_DIR/sample.txt"
  TRANSCRIPT="$TEMP_DIR/fake-session.jsonl"
  CACHE_FILE="$TEMP_DIR/fake-session-read-cache.json"

  echo "hello world" > "$TEST_FILE"
  touch "$TRANSCRIPT"
}

cleanup_temp_dir() {
  rm -rf "$TEMP_DIR"
}

make_json() {
  local file_path="$1"
  local source="${2:-}"

  if [[ -n "$source" ]]; then
    # SessionStart 용
    cat <<EOF
{
  "session_id": "test-session",
  "transcript_path": "$TRANSCRIPT",
  "cwd": "$TEMP_DIR",
  "source": "$source"
}
EOF
  else
    # PreToolUse / PostToolUse 용
    cat <<EOF
{
  "session_id": "test-session",
  "transcript_path": "$TRANSCRIPT",
  "cwd": "$TEMP_DIR",
  "tool_input": {
    "file_path": "$file_path"
  }
}
EOF
  fi
}

PASS_COUNT=0
FAIL_COUNT=0

assert_exit_code() {
  local test_name="$1"
  local expected="$2"
  local actual="$3"

  if [[ "$actual" == "$expected" ]]; then
    echo "  PASS: $test_name (exit $actual)"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  FAIL: $test_name (expected exit $expected, got $actual)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

assert_file_exists() {
  local test_name="$1"
  local file="$2"

  if [[ -f "$file" ]]; then
    echo "  PASS: $test_name"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  FAIL: $test_name (file not found: $file)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

assert_file_not_exists() {
  local test_name="$1"
  local file="$2"

  if [[ ! -f "$file" ]]; then
    echo "  PASS: $test_name"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  FAIL: $test_name (file should not exist: $file)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

assert_cache_has_key() {
  local test_name="$1"
  local key="$2"
  local result
  result=$(jq -r --arg k "$key" 'has($k)' "$CACHE_FILE" 2>/dev/null || echo "false")

  if [[ "$result" == "true" ]]; then
    echo "  PASS: $test_name"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  FAIL: $test_name (key '$key' not found in cache)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

# --- 테스트 케이스 ---

test_post_read_creates_cache() {
  echo "[TEST] post-read: 첫 읽기 후 캐시 파일 생성"

  setup_temp_dir

  local exit_code=0
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/post-read.sh" || exit_code=$?

  assert_exit_code "exit 0 반환" 0 "$exit_code"
  assert_file_exists "캐시 파일 생성됨" "$CACHE_FILE"
  assert_cache_has_key "캐시에 sample.txt 존재" "sample.txt"

  cleanup_temp_dir
}

test_pre_read_allows_first_read() {
  echo "[TEST] pre-read: 캐시 없을 때 읽기 허용"

  setup_temp_dir

  local exit_code=0
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/pre-read.sh" || exit_code=$?

  assert_exit_code "exit 0 반환 (허용)" 0 "$exit_code"

  cleanup_temp_dir
}

test_pre_read_blocks_unchanged_file() {
  echo "[TEST] pre-read: 미변경 파일 읽기 차단"

  setup_temp_dir

  # 먼저 post-read로 캐시 생성
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/post-read.sh"

  # 같은 파일 다시 읽기 시도
  local exit_code=0
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/pre-read.sh" 2>/dev/null || exit_code=$?

  assert_exit_code "exit 2 반환 (차단)" 2 "$exit_code"

  cleanup_temp_dir
}

test_pre_read_allows_modified_file() {
  echo "[TEST] pre-read: 변경된 파일 읽기 허용"

  setup_temp_dir

  # 캐시 생성
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/post-read.sh"

  # 파일 내용 변경 (1초 대기로 mtime 차이 보장)
  sleep 1
  echo "modified content" > "$TEST_FILE"

  # 변경된 파일 읽기 시도
  local exit_code=0
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/pre-read.sh" 2>/dev/null || exit_code=$?

  assert_exit_code "exit 0 반환 (허용)" 0 "$exit_code"

  cleanup_temp_dir
}

test_pre_read_allows_nonexistent_file() {
  echo "[TEST] pre-read: 존재하지 않는 파일은 허용"

  setup_temp_dir

  local exit_code=0
  make_json "$TEMP_DIR/no-such-file.txt" | "$SCRIPTS_DIR/pre-read.sh" || exit_code=$?

  assert_exit_code "exit 0 반환 (허용)" 0 "$exit_code"

  cleanup_temp_dir
}

test_pre_read_blocks_touched_file() {
  echo "[TEST] pre-read: touch만 한 파일 (내용 동일) 차단"

  setup_temp_dir

  # 캐시 생성
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/post-read.sh"

  # mtime만 변경 (내용은 그대로)
  sleep 1
  touch "$TEST_FILE"

  # 읽기 시도 → sha256이 같으므로 차단되어야 함
  local exit_code=0
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/pre-read.sh" 2>/dev/null || exit_code=$?

  assert_exit_code "exit 2 반환 (hash 동일로 차단)" 2 "$exit_code"

  cleanup_temp_dir
}

test_session_start_clears_on_clear() {
  echo "[TEST] session-start: /clear 시 캐시 삭제"

  setup_temp_dir

  # 캐시 생성
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/post-read.sh"
  assert_file_exists "캐시 파일 존재 확인" "$CACHE_FILE"

  # /clear 시뮬레이션
  make_json "" "clear" | "$SCRIPTS_DIR/session-start.sh" || true

  assert_file_not_exists "캐시 파일 삭제됨" "$CACHE_FILE"

  cleanup_temp_dir
}

test_session_start_clears_on_compact() {
  echo "[TEST] session-start: compact 시 캐시 삭제"

  setup_temp_dir

  # 캐시 생성
  make_json "$TEST_FILE" | "$SCRIPTS_DIR/post-read.sh"

  # compact 시뮬레이션
  make_json "" "compact" | "$SCRIPTS_DIR/session-start.sh" || true

  assert_file_not_exists "캐시 파일 삭제됨" "$CACHE_FILE"

  cleanup_temp_dir
}

test_post_read_external_file() {
  echo "[TEST] post-read: 프로젝트 외부 파일은 절대 경로로 캐시"

  setup_temp_dir

  local external_file="/tmp/readonce-test-external-$$"
  echo "external" > "$external_file"

  local exit_code=0
  make_json "$external_file" | "$SCRIPTS_DIR/post-read.sh" || exit_code=$?

  assert_cache_has_key "절대 경로 key로 캐시됨" "$external_file"

  rm -f "$external_file"
  cleanup_temp_dir
}

# --- 실행 ---

main() {
  echo "========================================="
  echo "  akbun-readonce hook 테스트"
  echo "========================================="
  echo ""

  test_post_read_creates_cache
  echo ""
  test_pre_read_allows_first_read
  echo ""
  test_pre_read_blocks_unchanged_file
  echo ""
  test_pre_read_allows_modified_file
  echo ""
  test_pre_read_allows_nonexistent_file
  echo ""
  test_pre_read_blocks_touched_file
  echo ""
  test_session_start_clears_on_clear
  echo ""
  test_session_start_clears_on_compact
  echo ""
  test_post_read_external_file
  echo ""

  echo "========================================="
  echo "  결과: ${PASS_COUNT} passed, ${FAIL_COUNT} failed"
  echo "========================================="

  [[ "$FAIL_COUNT" -gt 0 ]] && exit 1
  exit 0
}

main
