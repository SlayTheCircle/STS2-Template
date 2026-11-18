using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.HoverTips;
using STS2RitsuLib.Keywords;

namespace TemplateMod.Content.Keywords;

/// <summary>
/// 专有名词悬停解释的接线助手。机制名词先在 ModEntry 注册
/// (RegisterCardKeywordOwnedByLocNamespace),文本唯一权威来源为
/// localization/{lang}/card_keywords.json(键 = 常量 + ".title/.description")。
/// 修改机制实现时必须同步核对解释文本,文案不准就是事故。
/// </summary>
public static class TemplateKeywords
{
    /// <summary>示例:本模板机制词(启用时在 ModEntry 注册并补双语文本)。public const string Example = "STS2_TEMPLATE_KEYWORD_EXAMPLE";</summary>

    /// <summary>把已注册的关键词(若注册表可用)并入卡牌关键词集合。未注册时静默跳过,不抛错。</summary>
    public static void AddTo(HashSet<CardKeyword> set, params string[] ids)
    {
        foreach (string id in ids)
        {
            if (ModKeywordRegistry.TryGetCardKeyword(id, out CardKeyword keyword))
            {
                set.Add(keyword);
            }
        }
    }

    /// <summary>
    /// 把已注册关键词转为悬停提示。遗物/能力/药水/附魔等非卡牌模型的 <c>AdditionalHoverTips</c> 用
    /// (卡牌本体走 CanonicalKeywords,由卡牌悬停管线自动展开;这些模型没有该管线,须显式挂)。
    /// </summary>
    public static IEnumerable<IHoverTip> HoverTips(params string[] ids) => ids.ToHoverTips();
}
