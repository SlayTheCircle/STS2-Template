# 美术贡献需求

本页是模板骨架：各衍生 Mod 按自身内容填充资源清单。通用规格与管线约定如下。

## 通用规格

| 资源类别 | 规格约定 | 输出路径（相对 assets/&lt;ModId&gt;/） |
|---|---|---|
| 常规卡图 | 25:19 横图窗（参考 750×570） | `images/cards/<ClassName>.png` |
| 先古卡图 | 竖图窗（参考 606×852）；不要把常规比例套到先古卡上 | `images/cards/<ClassName>.png` |
| 遗物 | 256×256 透明底主图 + `_outline` 描边 + 大图 | `images/relics/` |
| 药水 | 256² 主图 + 描边 | `images/potions/` |
| 能力图标 | 256×256 透明底 | `images/powers/<ClassName>.png` |
| 附魔徽记 | 256²；同族效果可共用一枚徽记、以文本区分 | `images/enchantments/` |
| 能量计 | 透明主图；big 与 text 两枚 | `images/energy/` |
| 角色立绘／头像／手势 | 按 CharacterAssetProfile 各槽位规格 | `images/characters/`、`images/hands/` |
| 纪元肖像 | 全局域大图 + 272×174 缩略图 | `assets/global/images/timeline/epoch_portraits/` |

## 管线约定

- 母版不入公开仓；组织内使用组织私有美术仓（`STS2-<Mod>-art`），外部维护者可以使用自己的私有目录或美术仓，均经 `ART_SOURCE_DIR` 接入。完整相对路径（含扩展名）绑定类名，目录与文件名不要求一致；派生步骤见[素材手册](../dev/assets.md)。
- Base 家族按类名约定解析路径、缺图回退占位；新增资源槽时同步更新 `audit-assets.py` 的检查面与派生脚本映射。
- 工坊封面为独立预览图，不进游戏资源包； Steam 推荐 JPG／PNG。上传图保留标题文字并检查小尺寸辨识度。
- 修改输入映射时同步更新派生脚本和资源使用方。完整素材与 PCK 检查不能代替游戏内验收。
