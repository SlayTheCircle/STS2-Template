#!/usr/bin/env bash
# 完整构建，或 --dll-only 编译源码；DLL-only 不生成可安装的模组目录。
set -euo pipefail
source "$(dirname "$0")/dev-env.sh"
mode="${1:-full}"
if [[ "$#" -gt 1 || ( "$mode" != full && "$mode" != --dll-only ) ]]; then
    echo '用法: scripts/build.sh [--dll-only]' >&2
    exit 2
fi
mod_require_refs
if [[ "$mode" == full ]]; then
    mod_require_godot
    python3 "$MOD_ROOT/scripts/audit-assets.py"
fi
python3 "$MOD_ROOT/scripts/audit-placeholders.py"
python3 "$MOD_ROOT/scripts/audit-loc-coverage.py"
mod_dotnet build "$MOD_ROOT/src/$MOD_ID/$MOD_ID.csproj" -c Release
DLL="$MOD_ROOT/src/$MOD_ID/bin/Release/net9.0/$MOD_ID.dll"
if [[ "$(strings -n 6 "$DLL" | grep -c 'ModInitializer' || true)" -eq 0 ]]; then
    echo '错误: DLL 缺少 ModInitializer 入口。' >&2
    exit 1
fi
if [[ "$mode" == --dll-only ]]; then
    echo 'DLL 编译完成；未打包 PCK，未组装安装目录。'
    exit 0
fi
mkdir -p "$MOD_ROOT/mods-dist"
stage="$(mktemp -d "$MOD_ROOT/mods-dist/.build.XXXXXX")"
trap 'rm -rf "$stage"' EXIT
python3 "$MOD_ROOT/scripts/distribution/manifest.py" "$MOD_ROOT/$MOD_ID.json" "$stage/$MOD_ID.json" "$RITSULIB_TARGET"
cp "$DLL" "$stage/"
MOD_PCK="$stage/$MOD_ID.pck" "$MOD_ROOT/scripts/build-pck.sh"
MOD_PCK="$stage/$MOD_ID.pck" "$MOD_ROOT/scripts/verify-pck.sh"
OUT="$MOD_ROOT/mods-dist/$MOD_ID"
mkdir -p "$OUT"
cp "$stage/$MOD_ID.json" "$stage/$MOD_ID.dll" "$stage/$MOD_ID.pck" "$OUT/"
echo '完整构建与 PCK 验证完成：'
ls -l "$OUT"
