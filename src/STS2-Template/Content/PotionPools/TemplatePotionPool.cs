using Godot;
using STS2RitsuLib.Scaffolding.Content;

namespace TemplateMod.Content.PotionPools;

/// <summary>药水池(TypeList 模式):成员由 [RegisterPotion(typeof(TemplatePotionPool))] 特性聚合。</summary>
public sealed class TemplatePotionPool : TypeListPotionPoolModel
{
    public override string EnergyColorName => "ironclad";

    public override Color LabOutlineColor => new Color("E8B23A");
}
