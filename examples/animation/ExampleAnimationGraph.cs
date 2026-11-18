using System;
using STS2RitsuLib.Scaffolding.Visuals.StateMachine;

namespace TemplateMod.Examples.Animation;

/// <summary>Minimal trigger routing. Clip names describe roles, not a prescribed death pose.</summary>
public sealed class ExampleAnimationGraph
{
    public ModAnimStateMachine Machine { get; }

    public ExampleAnimationGraph(IAnimationBackend backend, Func<bool> isAlive)
    {
        var idle = new ModAnimState("idle", true);
        var action = new ModAnimState("action");
        var exit = new ModAnimState("exit");
        var returning = new ModAnimState("return");
        Machine = new ModAnimStateMachine(backend);
        bool CanAct() => isAlive() && Machine.Current != exit && Machine.Current != returning;
        foreach (string trigger in new[] { "Attack", "Cast", "Hit" })
            Machine.AddAnyState(trigger, action, CanAct);
        Machine.AddAnyState("Dead", exit, () => Machine.Current != exit);
        Machine.AddAnyState("Revive", returning, () => isAlive() && Machine.Current == exit);
        Machine.AnimationCompleted += state =>
        {
            if (Machine.Current == state && !state.IsLooping && state != exit)
                Machine.Start(isAlive() ? idle : exit);
        };
        Machine.Start(isAlive() ? idle : exit);
    }
}
