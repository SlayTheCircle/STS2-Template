using STS2RitsuLib.Scaffolding.Characters;

namespace TemplateMod.Examples.Animation;

/// <summary>Replace only the combat scene; other scene slots keep their current paths.</summary>
public static class ExampleAssetProfile
{
    public static CharacterAssetProfile WithNativeCombat(CharacterAssetProfile profile, string scenePath)
    {
        var scenes = profile.Scenes!;
        return profile with
        {
            Scenes = new CharacterSceneAssetSet(scenePath, scenes.EnergyCounterPath,
                scenes.MerchantAnimPath, scenes.RestSiteAnimPath),
            Spine = null
        };
    }
}
