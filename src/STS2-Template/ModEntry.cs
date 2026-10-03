using HarmonyLib;
using MegaCrit.Sts2.Core.Modding;
using STS2RitsuLib.Content;
using STS2RitsuLib.Interop;

namespace TemplateMod;

/// <summary>
/// Mod 入口。加载清单见仓库根 STS2-Template.json;本文件只做注册接线,
/// 游戏内容逻辑全部位于 Content/ 下的纯模型类中。
/// </summary>
[ModInitializer("Init")]
public static class ModEntry
{
    public const string ModId = "STS2-Template";

    public static void Init()
    {
        // 归属声明:让本程序集内的 RitsuLib 自动注册特性([RegisterCard]/[RegisterCharacter]/…)正确归属到本 mod。
        // 必须第一条;内容注册全部由各模型类上的特性完成,本入口不再手工登记内容清单。
        ModTypeDiscoveryHub.RegisterModAssembly(ModId, typeof(ModEntry).Assembly);

        // 机制关键词注册(有机制名词时启用;文本在 localization/{lang}/card_keywords.json):
        //   ModKeywordRegistry.For(ModId).RegisterCardKeywordOwnedByLocNamespace("MYMECHANIC");
        // 常量与悬停助手见 Content/Keywords/TemplateKeywords.cs。

        Content.Characters.TemplateCharacterAssets.Register();

        // 自带 Harmony 补丁:ModInitializer 通道与游戏自动 PatchAll 是官方二选一语义——
        // 本类有 [ModInitializer] 则游戏只调 Init() 不再自动 PatchAll;有补丁类时必须在此手动补。
        new Harmony(ModId + ".patches").PatchAll(typeof(ModEntry).Assembly);
    }
}
