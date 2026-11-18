# 动画工具与验收

工具入口为 `tools/animation/run.gd`，独立 Godot 工程位于同目录。参数放在 Godot 的 `--` 后，使用 `--key value` 成对传入。路径相对 `tools/animation`；输出推荐绝对路径。每种模式先执行结构检查，错误以非零退出码返回。

| 参数 | 用途 |
|---|---|
| `--spec` | 审查 JSON，示例见 [review.json](../../../examples/animation/review.json) |
| `--scene` | 自己的 Node2D 场景路径；省略时生成几何示例 |
| `--pck` | 可选的实际候选 PCK，加载后按 `--scene res://...` 查资源 |
| `--mode` | `check` 结构检查、`canvas` 渲染检查、`preview` 交互预览、`frames` 导出帧、`save` 保存场景 |
| `--out` | `frames` 的目录或 `save` 的 `.tscn` 路径 |
| `--fps` | 导出帧率，默认 30，范围 1–120 |

## 配置如何改

`player` 是相对角色根节点的 AnimationPlayer 路径。`clips` 把动作名映射到是否循环；工具目前使用无斜杠的平面动作名。`samples` 控制每段动作等间隔检查数，范围 2–10000。`transitions` 每项为 `[前动作, 归一化时间, 后动作, 归一化时间]`，只列设计上要求完全相同的端点。渐变过渡或有意跳变另作针对性检查。

`view` 设置画布宽高、角色位置和缩放；确保角色在画面内，四周有背景余量。`world_z` 与 `foreground_z` 模拟游戏内容及前景层级。`joint_links` 为预览连线的节点路径对；它展示连接位置，适用于刚性节点或 Bone2D。

通用结构检查包括动作存在、循环标记、启用轨道的目标节点及值／贝塞尔轨道的属性路径、有限坐标、声明的过渡端点与另一实例的姿势／Shader 参数隔离。骨长、地面接触、轮廓穿插等约束按角色和动作补充；采样密度根据运动速度与缺陷位置选择。

## 渲染与导出

在 Bash 中从仓库根、配置好 `GODOT_EXE` 后：

```bash
"$GODOT_EXE" --audio-driver Dummy --path tools/animation --script run.gd -- --mode canvas --spec ../../examples/animation/review.json
mkdir -p local_dev/animation-review
"$GODOT_EXE" --audio-driver Dummy --path tools/animation --script run.gd -- --mode frames --spec ../../examples/animation/review.json --out "$PWD/local_dev/animation-review" --fps 30
"$GODOT_EXE" --headless --path tools/animation --script run.gd -- --mode save --spec ../../examples/animation/review.json --out "$PWD/local_dev/animation-review/actor.tscn"
```

渲染检查先确认角色确实可见，再覆盖不透明前景，最后令祖先透明；分别捕捉层级越界和淡出失效。`frames` 输出按动作分目录的 PNG 及 `manifest.json`，属于审查产物。输出目录必须不存在或为空；重复导出使用新的空目录，避免旧尾帧或已删除动作混入。需要视频时可使用自己配置的编码器，例如 `ffmpeg -framerate 30 -i <动作目录>/%04d.png <输出视频>`；实际游戏播放保存的场景。

`save` 仅改写资源声明与引用中的 ID，保留用户字符串；规范化后重载临时场景并执行结构检查，通过后才写入正式输出。内容相同时保留已有文件与修改时间。

独立工具加载纯 Godot 角色内层场景；带游戏 C# 类型的外层场景在实际游戏验证。预览大小是显示尺度的近似，最终仍核对游戏中的摄像机、Bounds 和 UI 位置。

## 反馈记录与发行核对

每个预览保留场景／PCK 哈希、配置、工具版本及生成命令。审查记录“动作＋时间点＋正常／慢放／放大尺度＋现象”，方便复现。母图、姿态和播放节奏分别确认。

发行时从实际 ZIP 提取 PCK，再用 `--pck` 和其内层 `--scene` 重跑检查。纹理导入前后可能重新编码；确认已接受美术进入发行包时，可比较解码像素及场景／脚本内容。部署与下载链路则比较原始字节：

```bash
python3 scripts/distribution/delivery.py <发行包解压后的Mod目录> <安装或工坊下载的Mod目录> --record local_dev/animation-review/delivery.json
```

实际游戏检查覆盖启动、待机／动作触发、攻击时点、朝向翻转、死亡与恢复、奖励页／地图遮挡、重进房间及多角色实例。采用哪些玩法状态，就验证对应生命周期。
