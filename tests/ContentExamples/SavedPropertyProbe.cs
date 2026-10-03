using System.Reflection;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;
using MegaCrit.Sts2.Core.Saves.Runs;
using TemplateMod.Examples.Cards;

internal static class SavedPropertyProbe
{
    public static void Initialize()
    {
        // 独立进程只初始化这张卡的属性元数据；不启动全游戏模型和网络 ID 表。
#if MOD_GAME_0107_1
        SavedPropertiesTypeCache.InjectTypeIntoCache(typeof(ExampleRecordedGuard));
#else
        typeof(ModelIdSerializationCache).GetField("_initialized", BindingFlags.Static | BindingFlags.NonPublic)!.SetValue(null, true);
        ModelIdSerializationCache.CacheSavedPropertiesForTypeDebug(typeof(ExampleRecordedGuard));
#endif
    }
}
