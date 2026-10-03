using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Interop.AutoRegistration;

namespace TemplateMod.Content.Powers;

/// <summary>
/// 示例昂扬(可见 Power):你造成的伤害 +Amount。
/// 顺带演练 0.107 伤害加成签名垫片——子类只覆写五参 Core,双目标共用同一份逻辑。
/// </summary>
[RegisterPower]
public sealed class TemplateVigorPower : TemplatePowerBase
{
    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override decimal ModifyDamageAdditiveCore(Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? card)
        => base.Owner == dealer ? base.Amount : 0m;
}
