using Godot;
using STS2RitsuLib.Scaffolding.Content;

namespace TemplateMod.Content.RelicPools;

/// <summary>遗物池(TypeList 模式):成员由 [RegisterRelic(typeof(TemplateRelicPool))] 特性聚合。</summary>
public sealed class TemplateRelicPool : TypeListRelicPoolModel
{
    public override string EnergyColorName => "ironclad";

    public override Color LabOutlineColor => new Color("E8B23A");
}
