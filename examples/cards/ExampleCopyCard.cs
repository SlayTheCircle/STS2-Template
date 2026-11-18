using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using STS2RitsuLib.Interop.AutoRegistration;
using TemplateMod.Content.CardPools;
using TemplateMod.Content.Cards;

namespace TemplateMod.Examples.Cards;

[RegisterCard(typeof(TemplateCardPool))]
public sealed class ExampleCopyCard : TemplateCardBase
{
    public override CardPoolModel VisualCardPool => ModelDb.CardPool<ColorlessCardPool>();
    public override IEnumerable<CardKeyword> CanonicalKeywords => new[] { CardKeyword.Exhaust };

    public ExampleCopyCard() : base(1, CardType.Skill, CardRarity.Token, TargetType.Self) { }

    protected override async Task OnPlay(PlayerChoiceContext context, CardPlay play)
    {
        var prefs = new CardSelectorPrefs(base.SelectionScreenPrompt, 1) { Cancelable = true };
        CardModel? selected = (await CardSelectCmd.FromHand(context, base.Owner, prefs,
            card => card.Type == CardType.Attack || card.Type == CardType.Power, this)).FirstOrDefault();
        if (selected is null)
            return;

        // CreateClone 保留原卡类型/效果。这里仅添加战斗副本，不改变原卡或主卡组。
        CardModel copy = selected.CreateClone();
        await CardPileCmd.AddGeneratedCardToCombat(copy, PileType.Hand, base.Owner);
    }
}
