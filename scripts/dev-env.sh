#!/usr/bin/env bash
# 本机配置、工具选择与编译引用预检。供其他开发脚本 source。
# 身份约定：MOD_ID/MOD_SHORT/MOD_LOC_PREFIX 从根目录唯一清单派生（与 scripts/modmeta.py 同规则），
# 脚本与工作流一律引用这些变量，不得硬编码模组名。
MOD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOD_GODOT_VERSION="4.5.1"

# 保留调用者显式设置的值，本地可信配置只提供后备值。
mod_env_names=()
mod_env_values=()
for mod_name in GAME_DIR GAME_LOG GAME_REFS_DIR RITSULIB_DIR RITSULIB_TARGET DOTNET_EXE GODOT_EXE ART_SOURCE_DIR ROSTER_DESIGN_FILE TASKLIST_EXE MOD_GAME_REFS_1110 MOD_GAME_REFS_1071 MOD_LOADER_GAME_REFS; do
    if [[ -v "$mod_name" ]]; then
        mod_env_names+=("$mod_name")
        mod_env_values+=("${!mod_name}")
    fi
done
if [[ -f "$MOD_ROOT/.local-dev.env" ]]; then
    source "$MOD_ROOT/.local-dev.env"
fi
for mod_i in "${!mod_env_names[@]}"; do
    printf -v "${mod_env_names[$mod_i]}" '%s' "${mod_env_values[$mod_i]}"
done
unset mod_env_names mod_env_values mod_name mod_i

DOTNET_EXE="${DOTNET_EXE:-dotnet}"
GODOT_EXE="${GODOT_EXE:-$MOD_ROOT/.tools/godot/$MOD_GODOT_VERSION/Godot_v${MOD_GODOT_VERSION}-stable_linux.x86_64}"
GAME_REFS_DIR="${GAME_REFS_DIR:-$MOD_ROOT/libs/game}"
RITSULIB_DIR="${RITSULIB_DIR:-$MOD_ROOT/libs/RitsuLib}"
RITSULIB_TARGET="${RITSULIB_TARGET:-0.111.0}"
TASKLIST_EXE="${TASKLIST_EXE:-tasklist.exe}"
ROSTER_DESIGN_FILE="${ROSTER_DESIGN_FILE:-$MOD_ROOT/docs/history/design/card-roster.txt}"

# 模组身份派生：根目录恰一个模组清单 *.json（global.json 是 .NET SDK 钉版，豁免），
# 文件名与 id 一致（audit-repository 守护该不变量）。
mod_manifests=()
for mod_f in "$MOD_ROOT"/*.json; do
    [[ "$(basename "$mod_f")" == "global.json" ]] && continue
    mod_manifests+=("$mod_f")
done
if [[ "${#mod_manifests[@]}" -ne 1 || ! -f "${mod_manifests[0]}" ]]; then
    echo '错误: 根目录应恰有一个模组清单 json。' >&2
    return 1 2>/dev/null || exit 1
fi
MOD_MANIFEST="${mod_manifests[0]}"
MOD_ID="$(python3 "$MOD_ROOT/scripts/modmeta.py" "$MOD_ROOT" | sed -n 's/^MOD_ID=//p')" || return 1
MOD_SHORT="${MOD_ID##*-}"
MOD_LOC_PREFIX="$(PYTHONPATH="$MOD_ROOT/scripts" python3 -c 'import modmeta,sys; print(modmeta.public_stem(sys.argv[1]) + "_")' "$MOD_ID")"
if [[ -z "$MOD_ID" || "$MOD_MANIFEST" != "$MOD_ROOT/$MOD_ID.json" ]]; then
    echo "错误: 清单文件名与 id 不一致（id=$MOD_ID）。" >&2
    return 1 2>/dev/null || exit 1
fi
export MOD_ROOT MOD_MANIFEST MOD_ID MOD_SHORT MOD_LOC_PREFIX
export GAME_REFS_DIR RITSULIB_DIR RITSULIB_TARGET
export ROSTER_DESIGN_FILE

mod_dotnet() {
    (cd "$MOD_ROOT" && "$DOTNET_EXE" "$@")
}

mod_require_refs() {
    local mod_file mod_version
    for mod_file in sts2.dll GodotSharp.dll 0Harmony.dll release_info.json; do
        [[ -f "$GAME_REFS_DIR/$mod_file" ]] || {
            echo "错误: 编译引用不完整。配置 GAME_DIR 并运行 scripts/restore-refs.sh。" >&2
            return 1
        }
    done
    mod_version="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"].removeprefix("v"))' "$GAME_REFS_DIR/release_info.json")" || return 1
    [[ "$mod_version" == "$RITSULIB_TARGET" ]] || {
        echo "错误: 游戏引用版本 $mod_version 与 RITSULIB_TARGET=$RITSULIB_TARGET 不一致。" >&2
        return 1
    }
    [[ -f "$RITSULIB_DIR/RitsuLib.References.props" ]] || {
        echo "错误: 缺 RitsuLib.References.props；请配置 RITSULIB_DIR 指向完整依赖包。" >&2
        return 1
    }
    for mod_file in "compat/$RITSULIB_TARGET/STS2-RitsuLib.dll" "compat/$RITSULIB_TARGET/STS2-RitsuLib.Runtime.dll" shared/STS2-RitsuLib.Ui.dll shared/STS2-RitsuLib.Shared.dll shared/STS2-RitsuLib.Settings.dll; do
        [[ -f "$RITSULIB_DIR/$mod_file" ]] || {
            echo "错误: RitsuLib 依赖包缺少 $mod_file。" >&2
            return 1
        }
    done
}

mod_require_godot() {
    [[ -x "$GODOT_EXE" ]] || {
        echo "错误: 缺 Godot $MOD_GODOT_VERSION 标准版。运行 scripts/fetch-godot.sh 或配置 GODOT_EXE。" >&2
        return 1
    }
}
