#!/usr/bin/env bash
# 从配置的美术母版生成资源；各类派生职责位于 scripts/art/。
# 通用卡图与图标已接入;角色/能量计/事件/纪元资源按公开槽位契约扩展。
set -euo pipefail
source "$(dirname "$0")/dev-env.sh"
SRC="${ART_SOURCE_DIR:-}"
[[ -n "$SRC" && -d "$SRC" ]] || { echo '错误: 请配置存在的 ART_SOURCE_DIR。' >&2; exit 1; }
source "$MOD_ROOT/scripts/art/common.sh"
source "$MOD_ROOT/scripts/art/mappings.sh"
source "$MOD_ROOT/scripts/art/validate-sources.sh"
DST="$MOD_ROOT/assets/$MOD_ID/images"
source "$MOD_ROOT/scripts/art/cards.sh"
source "$MOD_ROOT/scripts/art/icons.sh"
