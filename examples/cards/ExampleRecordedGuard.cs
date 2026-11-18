using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Saves.Runs;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using TemplateMod.Content.CardPools;
using TemplateMod.Content.Cards;

namespace TemplateMod.Examples.Cards;

[RegisterCard(typeof(TemplateCardPool))]
public sealed class ExampleRecordedGuard : TemplateCardBase
{
    private int _extraBlock;
    public override bool GainsBlock => true;
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[] { new BlockVar(3m, ValueProp.Move) };

    [SavedProperty]
    public int ExtraBlock
    {
        get => _extraBlock;
        set
        {
            AssertMutable();
            // 保存独立增量，读档随后重放升级；避免把升级量写入状态后再加一次。
            base.DynamicVars.Block.BaseValue += value - _extraBlock;
            _extraBlock = value;
        }
    }

    public ExampleRecordedGuard() : base(1, CardType.Skill, CardRarity.Common, TargetType.Self) { }
    protected override Task OnPlay(PlayerChoiceContext context, CardPlay play) =>
        CreatureCmd.GainBlock(base.Owner.Creature, base.DynamicVars.Block, play);
    protected override void OnUpgrade() => base.DynamicVars.Block.UpgradeValueBy(2m);
}
