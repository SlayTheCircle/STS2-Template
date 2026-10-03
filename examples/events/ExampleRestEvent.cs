using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Acts;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using TemplateMod.Content.Events;

namespace TemplateMod.Examples.Events;

[RegisterActEvent(typeof(Overgrowth))]
public sealed class ExampleRestEvent : TemplateEventBase
{
    public override EventAssetProfile AssetProfile => new(
        InitialPortraitPath: "res://STS2-Template/images/events/ExampleRestEvent.png");
    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[] { new HealVar(5m) };

    protected override IReadOnlyList<EventOption> GenerateInitialOptions() => new[]
    {
        new EventOption(this, Rest, InitialOptionKey("REST")),
        new EventOption(this, Leave, InitialOptionKey("LEAVE")),
    };

    private async Task Rest()
    {
        await CreatureCmd.Heal(base.Owner!.Creature, base.DynamicVars.Heal.BaseValue);
        SetEventFinished(PageDescription("RESTED"));
    }

    private Task Leave()
    {
        SetEventFinished(PageDescription("LEFT"));
        return Task.CompletedTask;
    }
}
