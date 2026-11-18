# 现行卡表

<!-- 生成文件:scripts/export-card-table.py 从源码 ctor 与 zhs 本地化生成,勿手改。 -->
<!-- 过时校验:check.sh 调用 --check;再生成:python3 scripts/export-card-table.py -->

共 3 张（含衍生 token）。效果文本为当前运行文本;升级数值以源码与游戏内为准。
稀有度颜色对照：普通=白卡，罕见=蓝卡，稀有=金卡。
原案数值与设计过程见[技术历史](../history/design/README.md)。

## 初始卡（2）

| 卡牌 | 稀有度 | 费用 | 类型 | 效果 |
|---|---|---|---|---|
| 示例防御 | 初始 | 1 | 技能 | 获得{Block:diff()}点[gold]格挡[/gold]。 |
| 示例打击 | 初始 | 1 | 攻击 | 造成{Damage:diff()}点伤害。 |

## 能力（1）

| 卡牌 | 稀有度 | 费用 | 类型 | 效果 |
|---|---|---|---|---|
| 示例昂扬 | 罕见 | 1 | 能力 | 本场战斗中，你造成的伤害+{TemplateVigorPower:diff()}。 |
