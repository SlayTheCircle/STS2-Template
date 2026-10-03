using Godot;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Scaffolding.Visuals.StateMachine;
using TemplateMod.Examples.Animation;

// Compile the interface wiring from the integration guide on both supported targets.
// Compiling the static binding alone does not check the factory interface namespace.
internal sealed class AnimationFactoryContract : IModCreatureCombatAnimationStateMachineFactory
{
    public ModAnimStateMachine TryCreateCombatAnimationStateMachine(Node visualsRoot)
        => ExampleCombatBinding.Create(visualsRoot);
}
