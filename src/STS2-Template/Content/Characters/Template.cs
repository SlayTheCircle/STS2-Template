using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Animation;
using STS2RitsuLib.Interop.AutoRegistration;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Relics;
using TemplateMod.Content.CardPools;
using TemplateMod.Content.Cards;
using TemplateMod.Content.PotionPools;
using TemplateMod.Content.RelicPools;
using TemplateMod.Content.Relics;

namespace TemplateMod.Content.Characters;

/// <summary>
/// 示例角色:资产档案由 TemplateCharacterAssets 显式借用铁甲,见 ModEntry 的接线。
/// 世界线等深层模块为可选代码(见 docs/dev/worldline.md)。
/// </summary>
[RegisterCharacter]
public sealed class Template : CharacterModel
{
    public override Color NameColor => new Color("E8B23AFF");

    public override CharacterGender Gender => CharacterGender.Feminine;

    // 角色不锁定——UnlocksAfterRunAs 维持 null。
    protected override CharacterModel? UnlocksAfterRunAs => null;

    public override int StartingHp => 75;

    public override int StartingGold => 99;

    public override CardPoolModel CardPool => ModelDb.CardPool<TemplateCardPool>();

    public override RelicPoolModel RelicPool => ModelDb.RelicPool<TemplateRelicPool>();

    public override PotionPoolModel PotionPool => ModelDb.PotionPool<TemplatePotionPool>();

    public override IEnumerable<CardModel> StartingDeck => new CardModel[]
    {
        ModelDb.Card<TemplateStrike>(),
        ModelDb.Card<TemplateStrike>(),
        ModelDb.Card<TemplateStrike>(),
        ModelDb.Card<TemplateStrike>(),
        ModelDb.Card<TemplateDefend>(),
        ModelDb.Card<TemplateDefend>(),
        ModelDb.Card<TemplateDefend>(),
        ModelDb.Card<TemplateDefend>(),
        ModelDb.Card<TemplateVigor>(),
        ModelDb.Card<TemplateVigor>(),
    };

    public override IReadOnlyList<RelicModel> StartingRelics => new RelicModel[] { ModelDb.Relic<TemplateLocket>() };

    public override float AttackAnimDelay => 0.15f;

    public override float CastAnimDelay => 0.4f;

    public override Color EnergyLabelOutlineColor => new Color("8A6210");

    public override Color DialogueColor => new Color("9A7B2D");

    public override Color MapDrawingColor => new Color("D4A017");

    public override Color RemoteTargetingLineColor => new Color("E8B23AFF");

    public override Color RemoteTargetingLineOutline => new Color("8A6210");

    // 占位:复用铁甲的切场音效,待配音接入后替换。
    public override string CharacterTransitionSfx => "event:/sfx/ui/wipe_ironclad";

#if !MOD_GAME_0107_1
    // 0.107.1 无此虚属性,其 GenerateAnimator 硬编码的默认映射与本覆写逐项相同,省略即等价。
    protected override List<(AnimState, string)> AnimationStates => new List<(AnimState, string)>
    {
        (new AnimState("attack"), "Attack"),
        (new AnimState("hurt"), "Hit"),
        (new AnimState("cast"), "Cast"),
    };
#endif

    public override List<string> GetArchitectAttackVfx()
    {
        return new List<string> { "vfx/vfx_attack_slash", "vfx/vfx_heavy_blunt", "vfx/vfx_bloody_impact" };
    }
}
