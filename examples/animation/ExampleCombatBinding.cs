using System;
using System.Runtime.CompilerServices;
using Godot;
using MegaCrit.Sts2.Core.Nodes.Combat;
using STS2RitsuLib.Scaffolding.Visuals.StateMachine;
using STS2RitsuLib.Scaffolding.Visuals.StateMachine.Backends;

namespace TemplateMod.Examples.Animation;

/// <summary>One state machine per visual instance, disposed when that instance leaves the tree.</summary>
public static class ExampleCombatBinding
{
    private static readonly ConditionalWeakTable<Node, ExampleAnimationGraph> Graphs = new();

    public static ModAnimStateMachine Create(Node visualsRoot)
    {
        if (Graphs.TryGetValue(visualsRoot, out var existing)) return existing.Machine;
        var creature = (visualsRoot.GetParent() as NCreature)?.Entity
            ?? throw new InvalidOperationException("Visual root must belong to NCreature.");
        var player = visualsRoot.GetNode<AnimationPlayer>("Visuals/Rig/AnimationPlayer");
        var backend = new GodotAnimationPlayerBackend(player);
        var graph = new ExampleAnimationGraph(backend, () => creature.IsAlive);
        Graphs.Add(visualsRoot, graph);
        visualsRoot.TreeExiting += () =>
        {
            graph.Machine.Dispose();
            backend.Dispose();
            Graphs.Remove(visualsRoot);
        };
        return graph.Machine;
    }
}
