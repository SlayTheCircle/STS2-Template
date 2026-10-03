# 架构与约定

## 注册体系（属性式自注册）

- 全部内容挂在 RitsuLib 特性上：`[RegisterCard(typeof(<Short>CardPool))]` / `[RegisterPower]` / `[RegisterRelic(typeof(<Short>RelicPool))]` / `[RegisterPotion(typeof(<Short>PotionPool))]` / `[RegisterCharacter]`。
- 池是 `TypeListCardPoolModel` 系（成员自动聚合，`GenerateAllCards` 被密封，**不需要也不允许**改池文件加内容）。
- `ModEntry.Init()` 做接线：`ModTypeDiscoveryHub.RegisterModAssembly`（归属声明，**必第一条**）、关键词注册（本 Mod 的机制词）、角色资产档案 `RegisterCharacterAssetReplacement`（复合条目键 `sts2_<mod>_character_<short>`）、显式 Harmony PatchAll（有补丁类时）。

### 变体 Loader 与游戏模型发现

工坊候选布局由根目录 Loader 选择并加载 `lib/game-<目标>/<ModId>.dll`，PCK 由根清单的 `has_pck` 走游戏原生挂载。根壳和内容 DLL 的程序集身份必须不同（壳带 `.Loader` 后缀），以避免同一个 AssemblyLoadContext 内同名冲突；**壳的文件名必须等于 mod id**——游戏按文件名发现 `<id>.dll`。

RitsuLib 的 `RegisterModAssembly` 建立库内的发现与归属关系；**不能假定它已经完成游戏模型扫描所需的程序集登记**。当前库在发现管线中尝试调用原生关联 API，但 0.107.1 没有该 API。`GameAssemblyRegistration` 显式维护游戏侧登记：0.111.0 经原生 `ModManager.AssociateAssemblyWithMod` 追加内容程序集；0.107.1 经 `OnModDetected` 在加载完成后将单个 `Mod.assembly` 槽改为内容程序集。旧版初始化器返回后会写入根壳，提前改槽会被覆盖。事件只处理本次加载的 Mod 实例，错误加载不暴露内容。

若内容 DLL 未进入游戏侧登记，`ReflectionHelper.ModTypes` 仍只扫描根壳，ModelDb 不会创建角色、卡牌与池模型；RitsuLib 随后解析已登记角色会抛 ModelNotFoundException。验证入口与证据边界见 [Loader 验证](../../tests/LoaderProbe/README.md)，游戏内状态见 [STATUS](../../STATUS.md)。

Loader 按两版游戏共有 API 的下限（0.107.1）编译一次；身份只有三个常量（ModId／VariantDllName／manifest 名）。

## 复合 ID（本地化与条目键的唯一约定）

`<规范化ModId>_{CATEGORY}_<规范化类名>`，遵循 RitsuLib `NormalizePublicStem`，由 `scripts/modmeta.py` 统一实现。例如 `STS2-SilverTongue` 前缀为 `STS2_SILVER_TONGUE_`，`APIStrike` 类名段为 `API_STRIKE`。卡 `.title/.description`；可见 Power 三件套 `.title/.description/.smartDescription`；遗物三件含 `.flavor`；药水两键；关键词 `STS2_<MOD>_KEYWORD_*`；角色 16 键。**PowerVar 占位符例外**：`{XxxPower:diff()}` 用**类名**不经前缀。新表可随时并入 pck 合并路径（`localization/<lang>/<table>.json`）。

## Base 家族（新内容一律继承，勿直接继承 RitsuLib 模板）

| 基类 | 职责 |
|---|---|
| `Content/Cards/<Short>CardBase` | 卡图按类名解析 `images/cards/<类名>.png`，缺图回退 RitsuLib 占位；4 参构造转发 |
| `Content/Relics/<Short>RelicBase` | 遗物三槽（主图/`_outline` 描边/大图复用主图）——**缺槽 = 游戏 NOPE 缺图纹理** |
| `Content/Potions/<Short>PotionBase` | 药水双槽（主图+描边） |
| `Content/Powers/<Short>PowerBase` | 可见 Power 图标按类名解析（CustomIconPath 与 CustomBigIconPath 两个资源槽都要供图）；隐藏 Power（内部标记）直接继承 `PowerModel`；内建 0.107 伤害加成签名垫片 |
| `Content/Enchantments/<Short>SupportEnchantment` | 支援附魔家族基线（标记判据、徽记回落、词条悬停） |
| `Content/Events/<Short>EventBase` | 事件基线（如启用事件模块） |

## 目录布局

公开检查通过 `scripts/content/` 共用内容索引：扫描整个 Content 下的具体 Base 后代，沿本仓抽象继承链发现；抽象家族不算内容件。类名、注册 ID 与资源身份保持稳定，移动目录不使内容退出花名册、本地化、变量或纹理检查。静态扫描不解析 C# using 别名、partial 合并或外部自定义继承链；复杂写法按模块扩展扫描并编译验证，不把源码门禁当完整类型系统。

```
src/<ModId>/            内容程序集（命名空间 <Short>Mod）
src/<ModId>.Loader/     工坊变体引导壳（<Short>Mod.Loader）
tests/LoaderProbe/      Loader 隔离验证（本地运行）
localization/{zhs,eng}/ 11 张表（cards/powers/relics/potions/characters/
                         card_keywords/card_selection/events/enchantments/epochs/ancients）
assets/<ModId>/         Godot 导入工程与自有资源（媒体不入库）
assets/global/          全局路径资源（如纪元立绘）
scripts/                参数化脚本与审计（身份从清单派生）
templates/              私有侧脚手架（init 时拷入 local_dev/）
local_dev/              本机私有工作区（整体忽略）
```

角色资产档案由 `Content/Characters/<Short>CharacterAssets.cs` 管理，在入口显式登记。`CharacterAssetProfiles.Ironclad()` 借用全部原版槽位，转场材质明确替换为通用淡入淡出；衍生仓逐槽替换。档案（`CharacterAssetProfile`）覆盖全部实际使用槽：场景 ×6（常规／技能／受击／倒下／商店／休息点）、图像 ×8、转场与拖尾。缺槽的故障形态各异（转场材质缺失→开局资源异常；出牌轨迹缺失→牌堆动画队列冻结）。模板骨架全部借原版资产；衍生仓逐槽替换。
