#!/bin/sh
# Builds a one pager from a content file. The PDF, a PNG preview and the HTML land in out/.
#
#   ./build.sh content/acme.json          light and dark
#   ./build.sh content/acme.json light    one mode: light, dark or both
#
# Anything after the mode goes to the builder as is, for example: --density tight --name my-file
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ $# -lt 1 ]; then
  sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//' >&2
  exit 1
fi
CONTENT="$1"
MODE="${2:-both}"
[ $# -ge 2 ] && shift 2 || shift 1
exec python3 "$HERE/.claude/skills/bluefyn-one-pager/scripts/one_pager.py" "$CONTENT" --out "$HERE/out" --mode "$MODE" "$@"
