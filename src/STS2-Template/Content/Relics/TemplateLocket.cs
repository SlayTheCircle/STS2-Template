using MegaCrit.Sts2.Core.Entities.Relics;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using TemplateMod.Content.RelicPools;

namespace TemplateMod.Content.Relics;

/// <summary>
/// 示例坠饰(初始遗物):结构演示件——初始遗物挂 StartingRelics,无战斗钩子。
/// 补战斗效果时按对应生命周期钩子实现;战斗临时状态在 AfterCombatEnd 重置。
/// </summary>
[RegisterRelic(typeof(TemplateRelicPool))]
public sealed class TemplateLocket : TemplateRelicBase
{
    public override RelicRarity Rarity => RelicRarity.Common;
}
