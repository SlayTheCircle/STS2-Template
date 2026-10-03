using System;
using System.Collections.Generic;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Timeline.Scaffolding;
using TemplateMod.Examples.Cards;

namespace TemplateMod.Examples.Timeline;

public sealed class ExampleCardsEpoch : CardUnlockEpochTemplate
{
    public override string Id => "STS2_TEMPLATE_EXAMPLE_CARDS";
    public override string StoryId => ExampleStory.Key;
    protected override IEnumerable<Type> CardTypes => new[]
    {
        typeof(ExampleCalculatedAttack), typeof(ExampleRecordedGuard), typeof(ExampleXGuard),
    };
    public override EpochAssetProfile AssetProfile => new(
        PackedPortraitPath: "res://STS2-Template/images/timeline/example_cards.png",
        BigPortraitPath: "res://images/timeline/epoch_portraits/STS2_TEMPLATE_EXAMPLE_CARDS.png");
}
