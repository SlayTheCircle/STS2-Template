using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Timeline;
using STS2RitsuLib.Timeline;
using STS2RitsuLib.Unlocks;
using TemplateMod.Content.Characters;

namespace TemplateMod.Examples.Timeline;

public static class ExampleTimeline
{
    // 由 ModEntry 在程序集归属注册之后调用一次；此例不同时使用属性注册。
    public static void Register()
    {
        var timeline = ModTimelineRegistry.For(ModEntry.ModId);
        timeline.RegisterStoryEpoch<ExampleStory, ExampleCharacterEpoch>();
        timeline.RegisterStoryEpoch<ExampleStory, ExampleCardsEpoch>();
        ModTimelineLayoutRegistry.RegisterAutoTimelineSlotBeforeEraColumn(
            typeof(ExampleCharacterEpoch), EpochEra.FarFuture0, ModEntry.ModId);
        ModTimelineLayoutRegistry.RegisterAutoTimelineSlotInEpochColumn(
            typeof(ExampleCardsEpoch), typeof(ExampleCharacterEpoch), ModEntry.ModId);

        var unlocks = ModUnlockRegistry.For(ModEntry.ModId);
        unlocks.RequireEpoch<Template, ExampleCharacterEpoch>();
        unlocks.UnlockCharacterAfterRunAs(typeof(Ironclad), typeof(ExampleCharacterEpoch));
        foreach (var cardType in new ExampleCardsEpoch().EnumerateUnlockCardTypes())
            unlocks.RequireEpoch(cardType, typeof(ExampleCardsEpoch));
        unlocks.UnlockEpochAfterWinAs<Template, ExampleCardsEpoch>();
    }
}
