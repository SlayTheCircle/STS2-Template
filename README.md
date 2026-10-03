# STS2-Template · 杀戮尖塔 2 Mod 模板

[English](README.en.md)

SlayTheCircle 组织的《杀戮尖塔 2》Mod 模板：从可玩角色 Mod 的完整工程蒸馏而来，自带双游戏分支（0.107.1 稳定版／0.111.0 测试版）的编译、打包、发布管线与变体 Loader，以及文档三分体系与源码审计套件。本仓库不是可游玩的 Mod——它是新 Mod 的起点。

模板 main 始终只保留一个 `chore(init)` 根提交，更新通过 `force-with-lease` 覆盖，不保留连续提交历史；派生 Mod 仓保留正常开发历史。维护与同步约定见[模板仓历史策略](docs/dev/workflow.md#模板仓历史策略)及[模板回流](docs/dev/onboarding.md#6-模板回流)。

## 用法

在 GitHub 上点 **Use this template**（或 `gh repo create SlayTheCircle/<新Mod> --template SlayTheCircle/STS2-Template`）得到新仓库，然后：

```bash
git clone <你的新仓库> && cd <你的新仓库>
git config core.hookspath .githooks    # 激活提交前审计（每次克隆后都要做）
scripts/init-mod.sh STS2-<Mod> <PascalName> --cn-name "<中文名>"
```

`init-mod.sh` 完成全部改名（清单、源码目录、命名空间、Base 家族、本地化键、脚本与工作流引用），自验源码检查，并生成私有导航与工坊配置。外部维护者可用 `--repo Owner/Repository` 指定自己的发行仓库。仓库建设与凭据配置见[新仓上手](docs/dev/onboarding.md)。

## 模板提供什么

- **编译骨架**：角色 + 示例卡 3 张及遗物／能力／药水／附魔各一，双目标条件编译（0.107.1 垫片内建）；配齐依赖后运行 `build.sh --dll-only`。
- **分发基建**：变体 Loader（工坊物品按当前游戏版本选择并登记内容程序集）、双目标打包、tag 触发的草稿 Release 工作流（CHANGELOG 段落提取发行说明）。
- **审计套件**：仓库边界、文档链接、本地化覆盖、占位符、花名册、卡表生成七件，pre-commit 与 CI 双重执行。
- **文档体系**：架构／工程规范／验证纪律／工作流等契约文档 + 事故账本与决策记录骨架。
- **可选角色动画**：[从零开始](docs/dev/animation/README.md)，用几何示例学习预览、动作与接线，再接入自己的素材。

## 不提供什么

美术与音频母版（媒体不入公开仓；完整构建自行提供母版目录并配置 `ART_SOURCE_DIR`）、游戏与 RitsuLib 二进制（编译引用来自你自己的游戏安装）、世界线／先古对话等角色 Mod 深层模块的代码（对应文档以「可选模块」形式提供接线指南）。

## 开发

前置：Bash、Python 3.11+、由 `global.json` 选择的 .NET SDK；完整素材构建另需 Godot 4.5.1 标准版与本地美术。

```bash
cp .local-dev.env.example .local-dev.env   # 填写本机依赖与工具位置
./scripts/check.sh --source-only           # 源码检查，不要求游戏 DLL 或美术
./scripts/restore-refs.sh                  # 从 GAME_DIR 复制编译引用
./scripts/build.sh --dll-only              # 只编译 DLL
```

详细配置与构建步骤见[贡献指南](CONTRIBUTING.md)及[构建管线](docs/dev/pipeline.md)。本机开发工作区存在时，先阅读私有入口 `local_dev/README.md`。

## 文档

- [文档导航](docs/README.md) · [开发规范](docs/dev/README.md) · [设计资料](docs/design/README.md) · [技术历史](docs/history/README.md)
- [新仓上手](docs/dev/onboarding.md)：从本模板派生一个新 Mod 的完整清单。
- [内容开发 SOP](docs/dev/content-sop.md)：从设计稿到可玩 Mod 的推荐路径（指导性质）。
- [验证指南](docs/dev/testing.md)：源码、编译、素材、PCK 与游戏验收的运行方法和证据边界。
- [变更记录](CHANGELOG.md) · 社区文件：[行为准则](CODE_OF_CONDUCT.md)、[安全策略](SECURITY.md)、[获取帮助](SUPPORT.md)、[贡献署名](CREDITS.md)。

## 许可

原创软件采用 [MIT](LICENSE)，范围见[许可说明](LICENSING.md)和[第三方说明](THIRD_PARTY_NOTICES.md)。变体 Loader 的实现源自 [RitsuLib](https://github.com/BAKAOLC/STS2-RitsuLib) 生态的加载方案，衍生说明见第三方文档。

本项目自 [STS2-Navia](https://github.com/SlayTheCircle/STS2-Navia) 提炼而来，开发说明、工具与排错经验在本仓独立维护。遇到本仓尚未覆盖的疑难时，可将原项目作为补充参考；贡献署名见 [CREDITS](CREDITS.md)。
