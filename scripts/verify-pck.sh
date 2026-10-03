#!/usr/bin/env bash
# 默认验证本地化和模型资源契约;--localization-only 用于无媒体的模板检查。
set -euo pipefail
source "$(dirname "$0")/dev-env.sh"
mod_require_godot
export MOD_PCK="${MOD_PCK:-$MOD_ROOT/mods-dist/$MOD_ID/$MOD_ID.pck}"
[[ -f "$MOD_PCK" ]] || { echo '错误: PCK 不存在；先完整构建。' >&2; exit 1; }
[[ "$#" -le 1 && ( "${1:-}" == '' || "$1" == --localization-only ) ]] || { echo '用法: verify-pck.sh [--localization-only]' >&2; exit 2; }
export MOD_ASSET_CONTRACT=''
if [[ "${1:-}" != --localization-only ]]; then
    contract="$(mktemp)"
    trap 'rm -f "$contract"' EXIT
    python3 "$MOD_ROOT/scripts/asset_contract.py" "$MOD_ROOT" > "$contract"
    export MOD_ASSET_CONTRACT="$contract"
fi
"$GODOT_EXE" --headless --script "$MOD_ROOT/tools/verify_pck.gd"
