# 接入战斗动画

适用基线为本模板的游戏 0.107.1／0.111.0 与配对 RitsuLib。示例源码通过 [ContentExamples](../../../tests/ContentExamples/ContentExamples.csproj) 编译；实际游戏场景需在自己的角色中接入并试玩。

## 先分开内层角色与游戏外壳

内层是普通 Godot Node2D 场景：部件、骨骼、材质与 AnimationPlayer。它可独立预览和打包。游戏外壳挂接原版 `NCreatureVisuals`，并提供 `%Visuals`、`%Bounds`、`%CenterPos`、`%IntentPos`、`%TalkPos`、`%FormVfx` 节点；尺寸和标记位置按角色填写。参照当前版本原版角色场景核对类型与 unique-name 设置。

示例外壳见 [character.tscn](../../../examples/animation/character.tscn)，标记位置适配几何示例，可直接查看节点结构。建议层级为 `角色外壳/Visuals/Rig/AnimationPlayer`。外壳脚本资源是 `res://src/Core/Nodes/Combat/NCreatureVisuals.cs`，游戏运行时提供该脚本；标准版 Godot 工具使用内层场景。

## 采用可选状态机示例

1. 将 [ExampleAnimationGraph.cs](../../../examples/animation/ExampleAnimationGraph.cs) 与 [ExampleCombatBinding.cs](../../../examples/animation/ExampleCombatBinding.cs) 移入内容程序集的视觉模块，按角色改名。
2. CharacterModel 实现 `IModCreatureCombatAnimationStateMachineFactory`（命名空间 `STS2RitsuLib.Scaffolding.Content`），方法如下：

```csharp
using Godot;
using STS2RitsuLib.Scaffolding.Content;
using STS2RitsuLib.Scaffolding.Visuals.StateMachine;
using TemplateMod.Examples.Animation;

// 将下面的方法加入实现该接口的角色类。
public ModAnimStateMachine TryCreateCombatAnimationStateMachine(Node visualsRoot)
    => ExampleCombatBinding.Create(visualsRoot);
```

3. 将 [ExampleAssetProfile.cs](../../../examples/animation/ExampleAssetProfile.cs) 一并移入，在 CharacterAssets 注册前执行 `profile = ExampleAssetProfile.WithNativeCombat(profile, "res://STS2-Template/scenes/characters/character.tscn")`，再用修改后的 profile 调用现有 `RegisterCharacterAssetReplacement`。它保留其他场景槽并清除借用的 Spine 资产集。将场景及依赖纳入 PCK，并在 `assets/validation.json` 登记关键额外文件。
4. 对照自己的动作修改触发映射、循环与返回规则，设置 `AttackAnimDelay`／`CastAnimDelay` 对应动作关键帧。示例将 Attack／Cast／Hit 汇入 action，将 Dead／Revive 映射为 exit／return；正式角色可拆分成任意设计动作。
5. 两个游戏目标分别编译示例和内容程序集，再验证实际游戏加载与触发。

每个视觉实例有自己的状态机；离开场景树时释放状态机与 backend。一次动作结束后读取当前生命状态选择返回目标，避免中途状态变化后回到过时姿势。死亡状态由恢复触发离开，普通攻击不应将其覆盖。

扩展低血量、技能补充动作或预热时，将视觉订阅放在独立模块，按角色与主线程筛选。先核对游戏已有触发，避免一次出牌重复启动动作；用战斗生命周期宿主承载纯视觉订阅，保持与可被移除的遗物解耦。

## 游戏拥有的属性

原版夹击等机制会改变 `%Visuals` 的缩放符号。内部动作保持其朝向控制，部件排序使用局部节点顺序或经验证的相对层级。奖励与地图前景、祖先显隐／透明度也属于游戏外部控制。

复活和再次待机需要恢复曾修改的节点、网格、材质与绘制顺序。可变 ShaderMaterial 按实例独立，防止一个角色的死亡参数影响另一个角色。具体断言跟随角色使用的状态与部件编写。

## 将教学角色放入自己的素材工程

从仓库根运行，先配置 Bash 的 `GODOT_EXE`：

```bash
mkdir -p assets/STS2-Template/scenes/characters/rig
"$GODOT_EXE" --headless --path tools/animation --script run.gd -- --mode save --out "$PWD/assets/STS2-Template/scenes/characters/rig/actor.tscn"
cp examples/animation/character.tscn assets/STS2-Template/scenes/characters/character.tscn
```

派生时路径中的模板身份由初始化脚本改写。完成上面的源码接线后按正常流程构建 PCK、关闭游戏、备份部署并试玩。示例的几何动作是教学内容，真实美术与动作可逐步替换内层场景。标准版 Godot 中只打开 `rig/actor.tscn` 预览，外壳的 C# 绑定由游戏提供。
