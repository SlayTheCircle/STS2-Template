# 状态、复制与存档

状态归属先于实现。按[工程规范](style.md)把机制状态留在拥有它的卡牌、Power 或遗物中；不同模块通过明确入口协作。不为了保存一个计数器引入全局状态管理器，也不在正常取消路径上做异常回滚框架。

## 先写作用域契约

| 状态 | 通常宿主 | 复制、保存与清理 |
|---|---|---|
| 战斗持续效果 | 当前生物的 Power | 使用原版战斗生命周期；新战斗重新建立，不能承担场外状态 |
| 战斗卡实例的数值/标记 | 战斗卡及 DynamicVars | 明确战斗克隆要继承什么；不修改 ModelDb 的 canonical 模型 |
| 主卡组中永久记录 | 卡牌 SavedProperty | 经游戏卡牌序列化恢复；核对升级与附魔回放 |
| 跨房间/跨战斗累计 | 遗物 SavedProperty | 本局持续保存，按设计消费或重置；归属是遗物 Owner |
| 存档级角色进度 | 游戏进度/解锁注册入口 | 章节条件用 RitsuLib 解锁规则；不借“曾见过先古”改变初始遗物 |

在设计对照中记录初始值、写入入口、复制规则、保存规则、消费时点和清理时点。作用域未裁定时先做小原型，不能用代码默认值替设计者决定。多人判断使用效果实际拥有者，随机效果使用所属 RunState 的匹配 RNG，不从界面顺序或系统 Random 推断结果。

## 复制原卡与生成新卡

[ExampleCopyCard](../../examples/cards/ExampleCopyCard.cs)是同版本原版 DualWield 接线的简化示范：从手牌选攻击/能力，正常取消时直接返回，选定后调用 `selected.CreateClone()`，再经 `CardPileCmd.AddGeneratedCardToCombat` 放入拥有者手牌。原卡和主卡组保持原设计状态。例子的 token 自身采用原版 ColorlessCardPool 外观；复制出来的牌仍保留被选牌的类型、效果和原有外观。

`CreateClone` 用于战斗副本；局内永久复制走 `ICardScope.CloneCard`，新卡走该作用域的 `CreateCard`。查对应版本 CardModel、ICardScope 与 DualWield；不要从任意场外卡调用 CreateClone，也不要用 `new` 创建运行时游戏模型。0.111.0 的跨玩家 `CreateCloneForPlayer` 不属于模板现有兼容垫片，新增使用须处理 0.107.1 差异。

复制“整张卡”不等于给新模型复制一段效果代码。设计若要求新名称/颜色/图像且保留原效果，先明确是否保留原模型类型并在自家 Base 中根据实例标记覆写展示；若必须成为另一模型，应由该机制明确保存原卡描述和状态、重建需要的效果，而不是通过反射调用任意 OnPlay。费用覆盖、X 值、升级、附魔、临时修正、额外出牌与卡源分别裁定。模板不预置通用卡牌解释器。

涉及“选牌→消耗→生成”时先完成选择并读取快照，再按设计顺序提交动作。选择为空和取消是正常返回；不要在选定前消耗原卡或机制资源。基础出牌已支付的能量是否退回属于设计要求，单纯 return 不代表整次出牌被撤销。

## 保存卡牌自身状态

[ExampleRecordedGuard](../../examples/cards/ExampleRecordedGuard.cs)用 SavedProperty 保存独立格挡增量。setter 调用 AssertMutable，按新旧增量差更新 BlockVar，升级另加基准值。这个分离是必要的：原版 CardModel.FromSerializable 先填 SavedProperties，再恢复附魔、重放升级；把“已经包含升级的总值”保存后再升级会重复加值。

SavedProperty 适用于该版本支持的类型：例如 int、bool、string、ModelId、SerializableCard 和对应已支持集合；不能直接保存 Godot 节点、委托或任意 CardModel 引用。查看同版本 SavedProperties、SavedPropertyAttribute 和原版 MadScience 的状态属性。需要保存源卡时用 SerializableCard，并明确所属作用域/Owner、重建时点、允许的嵌套和临时状态；原版 ToSerializable 不承诺保存全部战斗临时效果。

标量字段随克隆复制；可变集合要在 `DeepCloneFields` 调用 base 后复制，事件订阅在 `AfterCloned` 调用 base 后清空。只处理自己声明的集合/事件，不重新实现引擎已处理的 DynamicVars、费用、附魔和关键词复制。例如自家 List 状态使用 `new List<int>(_values)`，不能让原牌与副本共用列表。

## 保存跨战斗计数

[ExampleSpendLedger](../../examples/relics/ExampleSpendLedger.cs)从原版 MawBank/Nunchaku 的宿主规则提取：AfterItemPurchased 核对 player 是本遗物 Owner，写入 SavedProperty，setter 更新计数器。该事件是商店购买，不是所有金币减少；如设计包括事件消费，按同版本实际金币命令与钩子接入，并区分 Spent、丢失和获得。奖励前后的扣减与再次触发顺序由遗物机制拥有者维护。

场外 AnyTime 药水不能通过 PowerCmd.Apply 保存“下一场代价”。需要持久机制就指定真实宿主与消费规则；否则按设计使用 CombatOnly。不同药水不会因此统一引入隐藏遗物或全局服务。

## 验收

源码检查只核对可识别的变量声明与消费，DLL 编译只证明 API 可用。托管示例探针使用真实 DynamicVars、克隆与 SavedProperties，显式提供该卡的 canonical 关联及属性元数据，未启动完整游戏模型/网络表；运行方法见[验证纪律](testing.md)。遗物基类含 Godot 原生 StringName 静态初始化，纯托管进程不能替代其游戏宿主。

按具体变更验证：取消/空选择、正常选择、升级/附魔/临时费用副本、原牌与副本独立写入、新生成牌、战斗结束、场外使用、Owner/多人随机源，以及实际存读档后的数值和 UI。托管 Fill 加 UpgradeInternal 不等于真实战斗中途存档或跨机器同步已经通过。
