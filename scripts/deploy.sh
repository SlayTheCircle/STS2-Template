#!/usr/bin/env bash
# Usage: scripts/deploy.sh [game directory] [candidate mod directory]
set -euo pipefail
source "$(dirname "$0")/dev-env.sh"
GAME_DIR="${1:-${GAME_DIR:-}}"
[[ -n "$GAME_DIR" ]] || { echo '需要游戏目录参数或 GAME_DIR。' >&2; exit 1; }
SRC="${2:-$MOD_ROOT/mods-dist/$MOD_ID}"
python3 "$MOD_ROOT/scripts/distribution/deploy.py" \
    --source "$SRC" --game "$GAME_DIR" --mod-id "$MOD_ID" \
    --detector "$TASKLIST_EXE" --records "$MOD_ROOT/local_dev/deployments"
