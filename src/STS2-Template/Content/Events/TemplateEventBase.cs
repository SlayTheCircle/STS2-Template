using System.Linq;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Runs;
using TemplateMod.Content.Characters;
using STS2RitsuLib.Scaffolding.Content;

namespace TemplateMod.Content.Events;

/// <summary>
/// 事件统一基线:限定事件仅在本角色在场时出现;多人时只要有一名即放行(事件归属者的体验优先)。
/// 事件立绘/背景由衍生仓按美术管线接入,布局走原版 default_event_layout。
/// </summary>
public abstract class TemplateEventBase : ModEventTemplate
{
    public override bool IsAllowed(IRunState runState)
    {
        return runState.Players.Any(p => p.Character is Template);
    }
}
