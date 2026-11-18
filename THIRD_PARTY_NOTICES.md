# 第三方依赖与来源说明 / Third-party notices

本说明记录开发与运行时依赖，许可范围见 [LICENSING.md](LICENSING.md)。候选 ZIP 分发本项目 DLL、PCK、清单和许可说明，未附带下列依赖的 DLL、工具二进制或游戏源码。

| 项目 | 用途与来源 | 上游许可／条款 |
|---|---|---|
| [RitsuLib](https://github.com/BAKAOLC/STS2-RitsuLib) | 内容注册、资源扩展、关键词和解锁接线；由玩家另行安装对应版本 | [MIT](https://github.com/BAKAOLC/STS2-RitsuLib/blob/main/LICENSE)，Copyright (c) 2026 OLC |
| [Harmony](https://github.com/pardeike/Harmony) | 运行时补丁；编译引用从对应游戏安装取得 | [MIT](https://github.com/pardeike/Harmony/blob/master/LICENSE)，Copyright (c) 2017 Andreas Pardeike |
| [Godot Engine](https://godotengine.org/) | 标准版编辑器用于资源导入与打包；GodotSharp 编译引用由游戏安装提供 | [MIT 及上游组件声明](https://godotengine.org/license/)，具体附属组件以实际使用版本为准 |
| [Slay the Spire 2](https://www.megacrit.com/) | 游戏 API、运行时与原版资源；贡献者从自己的安装取得引用 | [Mega Crit Content Policy](https://megacrit.com/content-policy/) 及适用游戏／平台条款；本项目不授予游戏权利 |

.NET SDK 用于编译，当前发行包不附带 SDK 或 .NET 运行时。构建所需版本见 global.json 和贡献指南。

## 直接借用与发行核对

变体 Loader 的分发布局沿用 RitsuLib 生态的既有约定（根引导壳 + `mod-variants.manifest` + `lib/game-<目标>/` 变体目录，参考 RandomForeseer 工坊物品形态）；实现为本项目原创，未复制第三方代码。

上述上游许可在 2026-10-02 核对；实际发行应按所用版本保存和复核对应声明。后续若直接复制第三方代码或随包分发其组件，须补齐原版权、许可文本和具体来源，不能只用本项目的版权行替代。

## English summary

The current package does not bundle RitsuLib, Harmony, Godot, .NET, or game reference assemblies. RitsuLib and Harmony use MIT; Godot's licensing page also covers its third-party components. Game and platform terms apply separately. The variant loader follows the distribution layout convention of the RitsuLib ecosystem (root bootstrap shell + variants manifest + per-target lib directories, as popularized by the RandomForeseer workshop item); its implementation is original to this project. Any copied third-party code or newly bundled dependency must retain its original copyright and applicable license notices.
