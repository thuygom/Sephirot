#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT_DIR/skills/sephirot-tree-builder"

if [[ ! -f "$SOURCE_DIR/SKILL.md" ]]; then
  echo "Missing skill source: $SOURCE_DIR" >&2
  exit 1
fi

install_one() {
  local target_root="$1"
  local target_dir="$target_root/sephirot-tree-builder"
  mkdir -p "$target_root"
  rm -rf "$target_dir"
  cp -R "$SOURCE_DIR" "$target_dir"
  echo "Installed: $target_dir"
}

usage() {
  cat <<'EOF'
Usage:
  scripts/install-agent-skill.sh codex
  scripts/install-agent-skill.sh claude
  scripts/install-agent-skill.sh both
  scripts/install-agent-skill.sh project-claude

Targets:
  codex          -> ${CODEX_HOME:-$HOME/.codex}/skills/sephirot-tree-builder
  claude         -> $HOME/.claude/skills/sephirot-tree-builder
  project-claude -> .claude/skills/sephirot-tree-builder in this repo
EOF
}

target="${1:-both}"
case "$target" in
  codex)
    install_one "${CODEX_HOME:-$HOME/.codex}/skills"
    ;;
  claude)
    install_one "$HOME/.claude/skills"
    ;;
  both)
    install_one "${CODEX_HOME:-$HOME/.codex}/skills"
    install_one "$HOME/.claude/skills"
    ;;
  project-claude)
    install_one "$ROOT_DIR/.claude/skills"
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
