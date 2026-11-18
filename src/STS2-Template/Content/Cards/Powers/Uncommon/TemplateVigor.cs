using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Interop.AutoRegistration;
using TemplateMod.Content.CardPools;
using TemplateMod.Content.Powers;

namespace TemplateMod.Content.Cards;

/// <summary>
/// 示例昂扬(罕见能力):本场战斗中,你造成的伤害 +2。升级:数值 3。
/// 能力卡接线样例:PowerVar 声明数值,loc 用 {TemplateVigorPower:diff()} 引用(类名,不经前缀)。
/// </summary>
[RegisterCard(typeof(TemplateCardPool))]
public sealed class TemplateVigor : TemplateCardBase
{
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
    {
        new PowerVar<TemplateVigorPower>(2m),
    };

    public TemplateVigor()
        : base(1, CardType.Power, CardRarity.Uncommon, TargetType.Self)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<TemplateVigorPower>(choiceContext, base.Owner.Creature, base.DynamicVars["TemplateVigorPower"].BaseValue, base.Owner.Creature, this);
    }

    protected override void OnUpgrade()
    {
        base.DynamicVars["TemplateVigorPower"].UpgradeValueBy(1m);
    }
}
