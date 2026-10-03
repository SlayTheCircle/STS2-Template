using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using TemplateMod.Content.CardPools;
using TemplateMod.Content.Cards;

namespace TemplateMod.Examples.Cards;

[RegisterCard(typeof(TemplateCardPool))]
public sealed class ExampleXGuard : TemplateCardBase
{
    protected override bool HasEnergyCostX => true;
    public override bool GainsBlock => true;
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[] { new BlockVar(3m, ValueProp.Move) };

    public ExampleXGuard() : base(0, CardType.Skill, CardRarity.Uncommon, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext context, CardPlay play)
    {
        int count = ResolveEnergyXValue();
        for (int i = 0; i < count; i++)
            await CreatureCmd.GainBlock(base.Owner.Creature, base.DynamicVars.Block, play);
    }

    protected override void OnUpgrade() => base.DynamicVars.Block.UpgradeValueBy(1m);
}
