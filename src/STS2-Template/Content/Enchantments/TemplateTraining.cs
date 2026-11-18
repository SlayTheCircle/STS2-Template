using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;

namespace TemplateMod.Content.Enchantments;

/// <summary>
/// 示例特训(支援附魔):被附魔的攻击牌造成的伤害 +Amount(本场战斗)。
/// 走 EnchantDamageAdditive 专用钩子——先于遗物/能力等其他伤害修改,预览口径一致。
/// </summary>
[RegisterEnchantment]
public sealed class TemplateTraining : TemplateSupportEnchantment
{
    public override bool CanEnchantCardType(CardType cardType) => cardType == CardType.Attack;

    public override decimal EnchantDamageAdditive(decimal originalDamage, ValueProp props) => Amount;
}
