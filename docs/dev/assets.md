# 素材规范

## 跟踪与来源

多媒体不入公开仓，不使用 LFS；母版与图像由贡献者自己的目录或私有美术仓承载，组织仓约定 `STS2-<Mod>-art`，经 `ART_SOURCE_DIR` 接入。文本 .tscn、.tres、.gd 和素材导入工程配置可随源码维护。PNG、母版、音视频、字体、编译纹理、导入缓存与侧车是本地输入或产物。各衍生仓填写自身素材授权范围（见[许可范围](../../LICENSING.md)），不因软件 MIT 许可而授权媒体。

源码采用 MIT，素材的具体权利与分发仍单独确认，见 [许可范围](../../LICENSING.md)。完整包中的多媒体不因附带 LICENSE 而自动采用 MIT。

素材母版由 ART_SOURCE_DIR 定位，实际本机目录由私有导航维护。[prep-art](../../scripts/prep-art.sh) 协调裁切、命名和派生；母版映射与各类生成职责位于 [scripts/art](../../scripts/art/)，assets 中的成品用于 Godot 导入和打包。普通 DLL 编译不要求美术；完整包构建要求全部资源存在。**模板骨架不带任何美术**：Base 家族缺图回退占位，衍生仓登记母版映射后，prep-art 已可生成卡图、遗物／药水描边、Power 与附魔图标；角色、能量、事件与纪元按槽位契约扩展。

## 尺寸与布局

| 类型 | 入包规格 | 路径 |
|---|---|---|
| 常规卡图 | 750×570，25:19；母版建议 1254×954 或等比 | images/cards/类名.png |
| 先古卡图 | 606×852，竖版 | images/cards/类名.png |
| 遗物 | 256²，主图及派生 _outline | images/relics/ |
| 药水 | 256²，主图及派生 _outline | images/potions/ |
| 可见 Power | 256²，供小／大图两个资源槽 | images/powers/ |
| 附魔徽记 | 256²，透明底；同族可共用统一徽记 | images/enchantments/ |
| 能量图标 | big 256²，text 24² | images/energy/ |
| 世界线立绘 | 1672×941 | 全局 images/timeline/epoch_portraits/ |
| 事件肖像 | 1672×941 母版，由事件图窗适配 | images/events/类名.png |
| 选人半身 | 手工母版 637×917，派生宽 264 | images/characters/ |

普通资源挂在 `res://$MOD_ID/`；世界线立绘按引擎推导使用全局路径。源图先由 Godot 导入，PCK 包含侧车和 .godot/imported 编译纹理；有侧车的源 PNG 不重复入包。

## 接入与验收

1. 对照母版、素材映射、代码和当前画面核对，不仅依赖旧需求单。
2. 补齐映射与派生逻辑，再生成素材。只覆盖生成文件可能在重跑时丢失。全量再生成要求所有已映射母版与角色／剧情输入齐全；缺件时在写入前失败，不以已有成品掩盖缺失。脚本保留已有输出与导入侧车，按字节更新生成结果；不清空资源目录，也不以母版 mtime 或成品已存在为理由跳过更新。未使用的旧资源需单独核对消费方再清理。
3. 输出剥离元数据并按字节比较，相同内容不替换；不得只依赖 mtime 判断母版变化。
4. 运行完整素材检查、构建与 PCK 验证，然后实测对应图窗、资源槽和动态效果。

能量计如需自定义，参考原版 NEnergyCounter 结构（Label、Layers、RotationLayers、EnergyVfxBack、EnergyVfxFront 节点；纹理在旋转层中显示，耗尽变暗与数值更新由原版驱动）。标准版 Godot 的 PCK 验证只证明纹理与场景文件入包，游戏 C# 生命周期和动效须在游戏内验收。

当前缺件与接线、验收状态由 STATUS 维护；公开的[美术贡献需求](../design/artwork.md)说明资源规格与贡献方式。占位图满足资源存在性时，仍需明确其美术状态。

## 通用母版派生与 PCK 断言

模板的 mappings.sh 已登记全部示例母版。各族映射的左侧为 ART_SOURCE_DIR 下的完整相对路径（含扩展名），右侧为实现类名；目录、中文名与后缀无需固定。可把手工交付的 PNG、JPEG、嵌套目录或别名文件直接绑定，保留原件。例如：

```bash
declare -A CARDS=(["交付卡图/生成牌/公告.jpg"]=MyAnnouncement)
declare -A POWERS=(["图标/聚焦图标.png"]=MyFocusPower)
```

以上是替换对应映射表的例子，不另写第二份同名数组。脚本由 ImageMagick 解码，再按游戏槽位输出 PNG；无法解码的母版返回失败，不靠后缀猜图像。先古卡类名登记到 ANCIENT_CARDS，专属附魔图登记到 ENCHANTMENTS。SUPPORT_BADGE_SOURCE 同样是完整相对路径，不用共享徽记时留空。

手工 ZIP 只作为交付容器：先解压到自己的私有母版位置，检查文档、图片、溯源图和缺槽，再人工确认绑定。不同包的目录名、括号、后缀、层级可以变化；不要求设计者重命名原件，也没有固定 ZIP 导入协议。组织内 Mod 的母版归组织私有美术仓，外部维护者可以使用自己的私有目录或美术仓，均通过同一个 ART_SOURCE_DIR 接口接入。

通用脚本生成卡图与所有图标资源槽；角色、能量计、事件和纪元应按本页契约增加模块并接入 prep-art。新增母版必须在 validate-sources 阶段检查，不能在写完其他文件后才发现缺失。

完整验证从 Base 家族的具体传递后代自动生成必需纹理清单，检查真实 PCK 内可加载性和尺寸；抽象辅助类不要求图，共享附魔徽记还检查透明边缘。其他资源在 assets/validation.json 登记，例如：

```json
{
  "textures": {
    "res://<ModId>/images/energy/custom_text.png": {"size": [24, 24], "transparent": true},
    "res://<ModId>/images/timeline/custom_thumb.png": {"size": [272, 174]}
  },
  "files": ["res://<ModId>/scenes/combat/custom_energy_counter.tscn"]
}
```

示例中的 ModId 与资源名替换为自己的实际逻辑名。场景文件入包不证明其 C# 生命周期正确。verify-pck.sh 默认验全部资源；--localization-only 只用于明确不验媒体的模板文本包检查，不能用于发行物验收。

## 图标审查页

生成素材后，从仓库根运行 [图标预览工具](../../scripts/art_review/preview.py)：

```bash
python3 scripts/art_review/preview.py --output local_dev/art-review/current
# 可选：与修改前的 images 目录对照，并载入人工判断。
python3 scripts/art_review/preview.py --output local_dev/art-review/current \
  --before <修改前images目录> --review <审查记录.json>
```

打开输出中的 `index.html`，检查明暗底、基准逻辑尺寸、24px 压力预览、128px 放大及已有描边。图片内嵌在页面中，可离线查看；`inventory.json` 保存资源名、显示名、逻辑尺寸与人工判断。工具仅读取素材，写入指定输出目录。

默认读取清单身份对应的 `assets/<ModId>/images/`，也可用 `--images` 指定其他 images 目录。名称默认来自 zhs 本地化，`--language eng` 可切换语言；共享徽记或未匹配本地化键的图片使用文件名。扫描 powers／relics／potions／enchantments／energy，`_outline` 图不单独列项。能量图以 `_text` 结尾时按 24px 预览，其余按 64px。这些尺寸用于审查，不改变入包规格，也不替代游戏内着色器、数值遮挡与 UI 缩放验收。

人工判断是可选 JSON，键为目录与文件名（不含扩展名）：

```json
{"powers/MyFocusPower": {"status": "待简化", "note": "浅底下轮廓不够清楚"}}
```

## 可选角色动画

从几何示例起步，逐步替换自己的部件、动作与游戏场景，见[动画入门](animation/README.md)。母版与补画经过确认后纳入素材映射；动作设计和工具配置跟随自己的角色。
