using System.Reflection;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Saves.Runs;
using TemplateMod.Examples.Cards;

internal static class ContractProbe
{
    public static int Run()
    {
        SavedPropertyProbe.Initialize();
        // 直接构造仅用于隔离探针；游戏内容从 ModelDb 取 canonical 模型。
        var attack = new ExampleCalculatedAttack();
        if (attack.DynamicVars.CalculatedDamage.BaseValue != 3m)
            throw new InvalidOperationException("计算伤害的初始化基准错误");

        var guardCanonical = new ExampleRecordedGuard();
        typeof(CardModel).GetField("_canonicalInstance", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(guardCanonical, guardCanonical);
        var guard = (ExampleRecordedGuard)guardCanonical.ToMutable();
        guard.ExtraBlock = 5;
        var clone = (ExampleRecordedGuard)guard.ClonePreservingMutability();
        clone.ExtraBlock = 7;
        if (guard.DynamicVars.Block.BaseValue != 8m || clone.DynamicVars.Block.BaseValue != 10m)
            throw new InvalidOperationException("战斗实例的克隆共享了可变变量");
        var guardRestored = (ExampleRecordedGuard)guardCanonical.ToMutable();
        SavedProperties.From(guard)!.Fill(guardRestored);
        guardRestored.UpgradeInternal();
        if (guardRestored.ExtraBlock != 5 || guardRestored.DynamicVars.Block.BaseValue != 10m)
            throw new InvalidOperationException("保存的独立状态与升级回放不一致");
        Console.WriteLine("PASS: 计算变量初始化；卡牌增量保存/恢复；卡牌克隆隔离与升级回放。未启动游戏或验证 UI。");
        return 0;
    }
}
