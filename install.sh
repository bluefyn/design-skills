#!/bin/sh
# Copies the skills in this pack into a Claude Code skills folder.
#
#   ./install.sh                 install for you, in ~/.claude/skills
#   ./install.sh --project DIR   install for a repo, in DIR/.claude/skills
#   ./install.sh --force         replace skills that are already there
#
# A skill that already exists is left alone unless you pass --force.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude/skills"
FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --project) TARGET="$2/.claude/skills"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done
mkdir -p "$TARGET"
for dir in "$HERE"/skills/*/; do
  name="$(basename "$dir")"
  if [ -e "$TARGET/$name" ] && [ "$FORCE" -ne 1 ]; then
    echo "skipped   $name (already in $TARGET; pass --force to replace it)"
    continue
  fi
  rm -rf "$TARGET/$name"
  cp -R "$dir" "$TARGET/$name"
  echo "installed $name"
done
echo "Done. Start a new Claude Code session to pick the skills up."
