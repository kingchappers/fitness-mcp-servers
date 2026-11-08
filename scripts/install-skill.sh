#!/usr/bin/env bash
# Install the fitness-insights skill for Claude Code (user-level) or package it for claude.ai.
#
#   bash scripts/install-skill.sh            # symlink into ~/.claude/skills
#   bash scripts/install-skill.sh --check    # exit 0 if installed and current, 1 otherwise
#   bash scripts/install-skill.sh --zip      # build dist/fitness-insights.zip for claude.ai upload
set -euo pipefail

SKILL_NAME="fitness-insights"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/.claude/skills/$SKILL_NAME"
TARGET_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/$SKILL_NAME"

is_installed() {
  [[ -L "$TARGET_DIR" && "$(readlink "$TARGET_DIR")" == "$SOURCE_DIR" ]]
}

check() {
  if is_installed; then
    echo "installed: $TARGET_DIR -> $SOURCE_DIR"
    return 0
  fi
  if [[ -e "$TARGET_DIR" ]]; then
    echo "conflict: $TARGET_DIR exists but is not a symlink to this repo"
  else
    echo "not installed: run 'bash scripts/install-skill.sh'"
  fi
  return 1
}

install() {
  if is_installed; then
    echo "already installed: $TARGET_DIR"
    return 0
  fi
  if [[ -e "$TARGET_DIR" || -L "$TARGET_DIR" ]]; then
    if [[ -L "$TARGET_DIR" ]]; then
      echo "replacing stale symlink: $TARGET_DIR -> $(readlink "$TARGET_DIR")"
      rm "$TARGET_DIR"
    else
      local backup="$TARGET_DIR.bak.$(date +%s)"
      echo "backing up existing skill: $TARGET_DIR -> $backup"
      mv "$TARGET_DIR" "$backup"
    fi
  fi
  mkdir -p "$(dirname "$TARGET_DIR")"
  ln -s "$SOURCE_DIR" "$TARGET_DIR"
  echo "installed: $TARGET_DIR -> $SOURCE_DIR"
}

package_zip() {
  local out="$REPO_ROOT/dist/$SKILL_NAME.zip"
  mkdir -p "$REPO_ROOT/dist"
  rm -f "$out"
  (cd "$REPO_ROOT/.claude/skills" && zip -qr "$out" "$SKILL_NAME")
  echo "built: $out (upload in claude.ai: Settings > Capabilities > Skills)"
}

case "${1:-}" in
  --check) check ;;
  --zip) package_zip ;;
  "") install ;;
  *) echo "usage: $0 [--check|--zip]" >&2; exit 2 ;;
esac
