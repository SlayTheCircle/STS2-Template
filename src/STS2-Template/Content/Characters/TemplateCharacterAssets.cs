using STS2RitsuLib.Content;
using STS2RitsuLib.Scaffolding.Characters;

namespace TemplateMod.Content.Characters;

/// <summary>原版资产借用基线；衍生仓从这里逐槽替换，不在入口堆资源路径。</summary>
internal static class TemplateCharacterAssets
{
    public static void Register()
    {
        CharacterAssetProfile fallback = CharacterAssetProfiles.Ironclad();
        CharacterUiAssetSet ui = fallback.Ui!;
        // 转场材质明确借用已验证的通用淡入淡出；拖尾由 Ironclad 配置供齐。
        CharacterAssetProfile profile = fallback.WithUi(new CharacterUiAssetSet(
            ui.IconTexturePath, ui.IconOutlineTexturePath, ui.IconPath,
            ui.CharacterSelectBgPath, ui.CharacterSelectIconPath, ui.CharacterSelectLockedIconPath,
            "res://materials/transitions/fade_transition_mat.tres", ui.MapMarkerPath));
        string entry = ModContentRegistry.GetCompoundId(ModEntry.ModId, "character", nameof(Template)).ToLowerInvariant();
        ModContentRegistry.For(ModEntry.ModId).RegisterCharacterAssetReplacement(entry, profile);
    }
}
