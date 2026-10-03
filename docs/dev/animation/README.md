# 从零开始制作角色动画

本模块提供可选的 Godot 原生角色动画路线。默认角色仍使用既有资产档案；采用本模块时再接入自制形象。动画形态由角色设计决定，可以是刚性部件、网格、逐帧或混合；工具围绕场景与 AnimationPlayer 工作。

## 先理解四个概念

- **部件**：可独立移动的图像或形状，例如头、手、道具。转轴决定旋转中心。
- **骨骼与节点层级**：父节点移动时带动子节点；骨骼还能通过权重影响网格。刚性部件也可以直接挂在 Node2D 层级下。
- **动画轨道**：在时间轴上记录位置、旋转、可见性等属性。AnimationPlayer 按这些记录播放。
- **状态机**：决定什么时候播放哪个动作，例如受击打断待机，动作结束后返回待机。它与“动作画成什么样”分别维护。

## 第一次运行：只需 Godot

安装 Godot **4.5.1 标准版**。在 Bash 中从仓库根执行下列命令，将 `GODOT_EXE` 替换为自己的可执行文件路径；已有开发环境可先 `source scripts/dev-env.sh`。此示例由代码绘制几何部件，适合先学习工具操作。

```bash
GODOT_EXE=/absolute/path/to/godot
"$GODOT_EXE" --headless --path tools/animation --script run.gd -- --mode check --spec ../../examples/animation/review.json
"$GODOT_EXE" --audio-driver Dummy --path tools/animation --script run.gd -- --mode preview --spec ../../examples/animation/review.json
```

预期：第一条输出 `passed: true`；第二条打开几何角色，提供动作选择、暂停、慢放、时间拖动、显示缩放和关节连线。关闭窗口即退出。Linux / WSL 的预览需要图形会话；无桌面环境可用 `xvfb-run -a` 运行下述渲染检查。`--headless` 用于结构检查，像素验收使用真实渲染器。

示例用 `idle/action/exit/return` 演示循环、一次动作、离场及回位；离场只是教学位移。真实角色自行设计倒下、消散、撤退、跪地或其他表现，并给出适用的过渡与可见性要求。

## 接下来走哪条路

| 目标 | 下一步 |
|---|---|
| 制作自己的素材、考虑使用生图 | [素材与动作设计](production.md) |
| 加载自己的场景、导出预览、检查候选包 | [工具与验收](review.md) |
| 把动作接入游戏战斗事件 | [游戏接线](integration.md) |
| 排查变形、穿层与版本混淆 | [工程案例](../../history/animation-lessons.md) |

模板工具通过中性示例验证通用行为；具体角色的画风、物理观感和游戏表现由其预览与试玩记录确认。首次制作建议先完成待机和一个短动作，再扩展整套动作，优先验证游戏中角色尺寸与资源接线。
