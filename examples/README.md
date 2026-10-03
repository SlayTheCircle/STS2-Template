# 可选实现示例

这些文件用于展示完整的小模块接线，不参加默认内容程序集编译，不会改变模板的三张示例卡或默认解锁状态。派生时其中的模板身份随 init 改名；采用后将模型移入自己的 `src/<ModId>/Content/` 对应模块，并按设计改名、改数值和更新文本。

| 示例 | 展示的契约 | 使用指南 |
|---|---|---|
| [角色动画](animation/) | 中性几何角色、审查配置、状态机与实例生命周期 | [动画入门](../docs/dev/animation/README.md) |
| [计算伤害](cards/ExampleCalculatedAttack.cs) | 三件套、静态倍率、预览与真实卡源、升级基准 | [卡牌](../docs/dev/cards.md) |
| [X 费用](cards/ExampleXGuard.cs) | HasEnergyCostX、结算时读取 ResolveEnergyXValue | [卡牌](../docs/dev/cards.md) |
| [临时复制](cards/ExampleCopyCard.cs) | 无色 token 外观、手牌选择、取消、原类型战斗副本 | [状态与复制](../docs/dev/state.md) |
| [保存卡牌增量](cards/ExampleRecordedGuard.cs) | SavedProperty、变量同步、克隆隔离、读档升级回放 | [状态与复制](../docs/dev/state.md) |
| [跨房间消费计数](relics/ExampleSpendLedger.cs) | 遗物宿主、归属检查、保存和计数器更新 | [遗物与药水](../docs/dev/relics-potions.md) |
| [休息事件](events/ExampleRestEvent.cs) | Act 注册、事件基线、肖像、选项和结果页 | [事件](../docs/dev/events.md) |
| [两章时间线接线](timeline/ExampleTimeline.cs) | 故事顺序、布局、角色解锁、卡牌解锁与获得条件 | [世界线](../docs/dev/worldline.md) |

配套双语文本在 [localization/zhs](localization/zhs/) 与 [localization/eng](localization/eng/)。只合并所采用模块的键，不覆盖自己已有的 JSON 表。卡牌登记花名册或 roster-policy 的 token/additions，并供齐类名对应素材；事件和章节另有资源接线。角色动画另提供无需美术输入的几何教学示例，按动画入门独立运行。

时间线例子使用三张示例奖励卡，并以铁甲战士结束一局解锁模板角色、模板角色获胜解锁三卡。采用时一起复制时间线四个文件和三张奖励卡，先确认自己的自然条件；在 ModEntry 的程序集归属注册之后调用一次 ExampleTimeline.Register。不要同时添加等效注册特性。各模块的游戏验收入口见所属指南。

编译验证工程为 [ContentExamples](../tests/ContentExamples/ContentExamples.csproj)。它链接这里的真实源码，与模板内容一起使用配对引用编译，保护示例 API 漂移。其托管探针只验证计算变量初始化、保存卡牌增量、克隆隔离和升级回放；不调用事件或时间线 UI，不测试遗物的原生图形初始化，也不替代游戏存档验收。
