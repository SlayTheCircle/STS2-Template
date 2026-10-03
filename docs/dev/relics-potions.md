# 遗物与药水

共用机制与文本约定见[卡牌、Power 与支援](cards.md)。骨架各带一件示例（初始遗物与示例药水）。

## 1. 基类与注册（内容发现与资源槽）

- 遗物：`[RegisterRelic(typeof(<Short>RelicPool))]` + 继承 **`<Short>RelicBase`**（图标三槽已按类名自动解析，**不要写任何图标代码**）
- 药水：`[RegisterPotion(typeof(<Short>PotionPool))]` + 继承 **`<Short>PotionBase`**（图标双槽自动）
- 池是 TypeList 模式，注册特性即自动聚合，无需改任何共享文件。

## 2. 遗物骨架（以示例初始遗物为基准）

- 稀有度 `RelicRarity`：Common / Uncommon / Rare / Shop / Event
- 「战斗开始时」类效果：回合开始钩子 + `AfterCombatEnd` 重置标记的组合
- 触发时 `Flash();` 打闪光；持续型状态可用计数器（查 vanilla 同类遗物的 counter API）
- 需要自定义可见 Power 的，按 [Power 约定](cards.md)维护实现与双语本地化

## 3. 药水骨架（vanilla Ashwater 是好模板）

```csharp
public override PotionRarity Rarity => PotionRarity.Common;
public override PotionUsage Usage => PotionUsage.CombatOnly;   // 治疗类用 AnyTime
public override TargetType TargetType => TargetType.Self;
protected override async Task OnUse(PlayerChoiceContext choiceContext, Creature? target) { ... }
```

- 目标自己以外的队友需要 `TargetType.AnyPlayer`（参考 Ashwater 的选人写法）
- 药水数值不升级，无 OnUpgrade
- **PowerCmd.Apply 在场外不会赋予战斗 Power**——AnyTime 药水不得假定场外 Power 会自然带入下一场

## 4. 本地化与生命周期

- 遗物键：`STS2_<MOD>_RELIC_<类名蛇形大写>.{title,description,flavor}`
- 药水键：`STS2_<MOD>_POTION_<类名蛇形大写>.{title,description}`（无 flavor）
- 描述占位符／富文本规范见 [cards.md](cards.md)
- 药水的机制名词悬停经 `AdditionalHoverTips` 挂（模板约定；ModPotionTemplate 封死 ExtraHoverTips 由基类统一拼装）

持久状态使用实际序列化约定；战斗临时标记在对应钩子重置，Flash 与计数器反映实际触发。[消费账簿示例](../../examples/relics/ExampleSpendLedger.cs)展示 SavedProperty、Owner 检查与显示更新；它只计商店购买，不把全部金币减少当消费。跨战斗宿主、临时复制与存档回放的完整说明见[状态手册](state.md)。

## 5. 变更与验收

同步中英文本、数值、使用目标、资源槽与设计差异。依据行为检查战斗开始／结束、回合重置、场外使用、多人目标及读档；图标需确认静态、小／大图动效和描边，不能仅凭主图存在认为接入完成。
