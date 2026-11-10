#!/bin/sh
# Installs the Bluefyn design skills for Claude Code. Run it with --help to see the options.
#
# It works from a clone of the repo, and it works piped from GitHub with no clone:
#   curl -fsSL https://raw.githubusercontent.com/bluefyn/design-skills/main/install.sh | sh -s -- --workspace ~/bluefyn-design
set -e

REPO_URL="${BLUEFYN_SKILLS_REPO:-https://github.com/bluefyn/design-skills.git}"

usage() {
  cat <<'EOF'
Installs the Bluefyn design skills for Claude Code.

  ./install.sh                   install the skills for you, in ~/.claude/skills
  ./install.sh --project DIR     install the skills for a repo, in DIR/.claude/skills
  ./install.sh --workspace DIR   make a design workspace in DIR: the skills, the brand
                                 files, an example and a build script, ready for Claude
  ./install.sh --force           replace skills (and a workspace's brand files) that are
                                 already there

A skill that already exists is left alone unless you pass --force.
EOF
}

MODE=user
DEST=""
FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --project|--workspace)
      [ -n "$2" ] || { echo "$1 needs a folder" >&2; exit 1; }
      MODE="${1#--}"; DEST="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

# Find the pack: next to this script, or a fresh copy from GitHub when the script was piped in.
HERE="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ ! -f "$HERE/skills/bluefyn-design/SKILL.md" ]; then
  command -v git >/dev/null 2>&1 || { echo "git is needed to download the skills" >&2; exit 1; }
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  echo "downloading the skills from $REPO_URL"
  git clone --quiet --depth 1 "$REPO_URL" "$TMP/design-skills"
  HERE="$TMP/design-skills"
fi

case "$MODE" in
  user) TARGET="$HOME/.claude/skills" ;;
  project) TARGET="$DEST/.claude/skills" ;;
  workspace) mkdir -p "$DEST"; WS="$(cd "$DEST" && pwd)"; TARGET="$WS/.claude/skills" ;;
esac

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

if [ "$MODE" != workspace ]; then
  echo "Done. Start a new Claude Code session to pick the skills up."
  exit 0
fi

# ---------------------------------------------------------------- workspace
# brand/ and build.sh belong to the installer and follow the pack on --force.
# CLAUDE.md, README.md, content/, dreams/ and out/ belong to the person and are never overwritten.

# brand/ is a visible door to the one pack the skills read, so there is a single copy of every file.
# Where links are not possible, the files are copied instead.
link_or_copy() {
  ( cd "$WS/brand" && ln -s "../.claude/skills/bluefyn-design/$1" "$2" ) 2>/dev/null \
    || cp -R "$TARGET/bluefyn-design/$1" "$WS/brand/$2"
}
if [ -e "$WS/brand" ] && [ "$FORCE" -ne 1 ]; then
  echo "skipped   brand/ (already there; pass --force to replace it)"
else
  rm -rf "$WS/brand"
  mkdir -p "$WS/brand"
  for item in logo avatars banners patterns; do
    link_or_copy "assets/brand/$item" "$item"
  done
  link_or_copy "assets/fonts" "fonts"
  link_or_copy "assets/tokens.css" "tokens.css"
  link_or_copy "references/brand-book.pdf" "brand-book.pdf"
  echo "installed brand/"
fi

if [ -e "$WS/build.sh" ] && [ "$FORCE" -ne 1 ]; then
  echo "skipped   build.sh"
else
  cp "$HERE/workspace/build.sh" "$WS/build.sh"
  chmod +x "$WS/build.sh"
  echo "installed build.sh"
fi

for file in CLAUDE.md README.md; do
  if [ -e "$WS/$file" ]; then
    echo "kept      $file"
  else
    cp "$HERE/workspace/$file" "$WS/$file"
    echo "wrote     $file"
  fi
done

mkdir -p "$WS/content" "$WS/dreams" "$WS/out"
if [ -e "$WS/content/acme.json" ]; then
  echo "kept      content/acme.json"
else
  cp "$HERE/skills/bluefyn-one-pager/examples/acme.json" "$WS/content/acme.json"
  echo "wrote     content/acme.json"
fi

cat <<EOF

The workspace is ready in $WS

Build the example:   cd "$WS" && ./build.sh content/acme.json
Work with Claude:    open the folder in Claude Code (or run \`claude\` in it) and ask for a one pager
EOF
