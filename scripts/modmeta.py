#!/usr/bin/env python3
"""模组身份派生：全仓 mod id / 短名 / 本地化前缀的唯一计算点。

清单（根目录唯一的 *.json）是身份唯一事实源；本模块供各 Python 审计共用，
Bash 侧的等价实现位于 scripts/dev-env.sh（MOD_ID/MOD_SHORT/MOD_LOC_PREFIX）。
身份限定 STS2-<PascalName>；复合键按当前 RitsuLib NormalizePublicStem 规范化。
"""

import json
import re
import sys
from pathlib import Path

_ID_RE = re.compile(r"^STS2-[A-Z][A-Za-z0-9]*$")


def public_stem(value: str) -> str:
    """对应 RitsuLib 0.6.2 的 NormalizePublicStem，包括缩写和驼峰边界。"""
    value = re.sub(r"[^A-Za-z0-9]+", "_", value.strip())
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return re.sub(r"_+", "_", value).strip("_").upper()


class ModMetaError(SystemExit):
    pass


def manifest_path(root: Path) -> Path:
    """根目录必须恰好存在一个 *.json 清单。"""
    candidates = sorted(p for p in root.glob("*.json") if p.is_file() and p.name != "global.json")
    if len(candidates) != 1:
        raise ModMetaError(
            f"错误: 根目录应恰有一个模组清单 json（找到 {len(candidates)} 个: {[p.name for p in candidates]}）。"
        )
    return candidates[0]


def _load(root: Path) -> dict:
    path = manifest_path(root)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModMetaError(f"错误: 清单 {path.name} 不是合法 JSON: {exc}") from exc
    mod_id = data.get("id")
    if not isinstance(mod_id, str) or not _ID_RE.match(mod_id):
        raise ModMetaError(f"错误: 清单 id 不合法: {mod_id!r}（应为 STS2-X 形态）。")
    if path.stem != mod_id:
        raise ModMetaError(f"错误: 清单文件名 {path.name} 与 id {mod_id} 不一致。")
    return data


def mod_id(root: Path) -> str:
    return _load(root)["id"]


def short(root: Path) -> str:
    return mod_id(root).rsplit("-", 1)[-1]


def loc_prefix(root: Path) -> str:
    return public_stem(mod_id(root)) + "_"


def src_dir(root: Path) -> Path:
    path = root / "src" / mod_id(root)
    if not path.is_dir():
        raise ModMetaError(f"错误: 缺少内容工程目录 {path}。")
    return path


def base_class(root: Path, kind: str) -> str:
    """kind: card/relic/potion/power/support_enchantment/event/keywords/pool 前缀名。"""
    return short(root) + {
        "card": "CardBase",
        "relic": "RelicBase",
        "potion": "PotionBase",
        "power": "PowerBase",
        "support_enchantment": "SupportEnchantment",
        "event": "EventBase",
        "keywords": "Keywords",
    }[kind]


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(f"MOD_ID={mod_id(root)}")
    print(f"MOD_SHORT={short(root)}")
    print(f"MOD_LOC_PREFIX={loc_prefix(root)}")
    print(f"SRC_DIR={src_dir(root)}")
