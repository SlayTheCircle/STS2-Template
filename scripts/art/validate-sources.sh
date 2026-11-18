# 全量再生成前检查母版；缺输入时失败，不能靠已有成品伪装交付完成。
# 映射为空时各项检查自然通过；衍生仓登记映射后此脚本自动开始强制对应母版。
# 立绘/头像/能量等非映射母版的需求，衍生仓在此按自身清单追加 require_art_source 行。
require_art_source() {
    [[ -f "$SRC/$1" ]] || { echo "错误: 美术母版缺失: $1" >&2; return 1; }
}

validate_mapping() {
    local -n mapping="$1"
    local path
    for path in "${!mapping[@]}"; do require_art_source "$path"; done
}
for family in CARDS RELICS POTIONS POWERS ENCHANTMENTS; do validate_mapping "$family"; done
if [[ -n "$SUPPORT_BADGE_SOURCE" ]]; then require_art_source "$SUPPORT_BADGE_SOURCE"; fi
