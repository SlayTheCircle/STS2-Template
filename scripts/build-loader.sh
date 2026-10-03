#!/usr/bin/env bash
# 构建工坊变体引导壳:固定对 0.107.1(两版 API 下限)编译,单份产物在两个游戏目标上运行。
# 引用目录用专用变量注入(csproj 读 MOD_LOADER_GAME_REFS),不受 GAME_REFS_DIR 干扰;产物收纳到 mods-dist/loader/。
set -euo pipefail
source "$(dirname "$0")/dev-env.sh"
LOADER_REFS="${MOD_LOADER_GAME_REFS:-$MOD_ROOT/libs/game-0.107.1}"
[[ -f "$LOADER_REFS/sts2.dll" ]] || { echo "错误: 缺 0.107.1 编译引用:$LOADER_REFS" >&2; exit 1; }
export MOD_LOADER_GAME_REFS="$LOADER_REFS"
mod_dotnet build "$MOD_ROOT/src/$MOD_ID.Loader/$MOD_ID.Loader.csproj" -c Release
BUILT="$MOD_ROOT/src/$MOD_ID.Loader/bin/Release/net9.0/$MOD_ID.Loader.dll"
if [[ "$(strings -n 6 "$BUILT" | grep -c 'ModInitializer' || true)" -eq 0 ]]; then
    echo '错误: 引导壳 dll 缺少 ModInitializer 入口。' >&2
    exit 1
fi
mkdir -p "$MOD_ROOT/mods-dist/loader"
# 程序集身份是 <MOD_ID>.Loader,文件名落位为模组 id 同名的 <MOD_ID>.dll。
cp "$BUILT" "$MOD_ROOT/mods-dist/loader/$MOD_ID.dll"
echo "引导壳就绪: mods-dist/loader/$MOD_ID.dll (程序集 $MOD_ID.Loader)"
