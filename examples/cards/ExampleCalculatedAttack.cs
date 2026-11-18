using System;
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
public sealed class ExampleCalculatedAttack : TemplateCardBase
{
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
    {
        new CalculationBaseVar(3m),
        new ExtraDamageVar(1m),
        new CalculatedDamageVar(ValueProp.Move).WithMultiplier(
            static (card, _) => card.CombatState is null ? 0m : card.Owner.Creature.Block),
    };

    public ExampleCalculatedAttack() : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy) { }

    protected override async Task OnPlay(PlayerChoiceContext context, CardPlay play)
    {
        ArgumentNullException.ThrowIfNull(play.Target);
        decimal amount = base.DynamicVars.CalculatedDamage.Calculate(play.Target);
        await DamageCmd.Attack(amount).FromCard(this, play).Targeting(play.Target).Execute(context);
    }

    protected override void OnUpgrade() => base.DynamicVars.CalculationBase.UpgradeValueBy(2m);
}
