#!/usr/bin/env bash
# 使用指定版本 Godot 导入本地素材并打包。
set -euo pipefail
source "$(dirname "$0")/dev-env.sh"
mod_require_godot
python3 "$MOD_ROOT/scripts/audit-assets.py"
export MOD_ROOT="$MOD_ROOT"
export MOD_PCK="${MOD_PCK:-$MOD_ROOT/mods-dist/$MOD_ID/$MOD_ID.pck}"
mkdir -p "$(dirname "$MOD_PCK")"
import_log="$(mktemp)"
trap 'rm -f "$import_log"' EXIT
if ! "$GODOT_EXE" --headless --path "$MOD_ROOT/assets" --import >"$import_log" 2>&1; then
    cat "$import_log" >&2
    echo '错误: Godot 素材导入失败。' >&2
    exit 1
fi
"$GODOT_EXE" --headless --script "$MOD_ROOT/tools/pack_mod.gd"
