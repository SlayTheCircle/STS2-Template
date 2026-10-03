# 构建、部署与素材管线

模组身份（id／短名／本地化键前缀）由根目录模组清单派生，`scripts/dev-env.sh` 统一导出 `MOD_ID`／`MOD_SHORT`／`MOD_LOC_PREFIX`；脚本与工作流不硬编码这些值。

## 配置与引用

工具版本和本机变量见 [贡献指南](../../CONTRIBUTING.md)。脚本加载根目录可信 `.local-dev.env`；公开示例不含实际本机路径。游戏引用从 GAME_DIR 复制到 GAME_REFS_DIR，RitsuLib 包通过 RITSULIB_DIR 选择。游戏引用版本与 RITSULIB_TARGET 不一致时中止。花名册默认读取公开的 docs/history/design/card-roster.txt；可用 ROSTER_DESIGN_FILE 检查另一卡表，不设置时无需任何私有文件。

```bash
./scripts/restore-refs.sh [游戏安装目录]
./scripts/fetch-godot.sh
./scripts/doctor.sh
```

Godot 自动下载脚本将 Linux x86_64 标准版放到不追踪的 .tools 目录。已有共享工具可直接配置 GODOT_EXE；SDK 版本由 global.json 选择，DOTNET_EXE 指向已有安装。

## VSCode／WSL 编辑器环境

开发脚本读取 .local-dev.env 后可以用 DOTNET_EXE 的绝对路径构建。编辑器的 C# 项目服务不会自动执行该 Bash 文件，必须能从自身环境找到 SDK；终端里构建成功不能证明扩展宿主的 SDK 发现正常。

手工安装 SDK 时，将安装根目录加入 PATH，并设置 DOTNET_ROOT。例如 SDK 安装在用户目录的 .dotnet 下，可在本机环境配置中使用：

```sh
export DOTNET_ROOT="$HOME/.dotnet"
export PATH="$DOTNET_ROOT:$DOTNET_ROOT/tools:$PATH"
```

这些命令用于对应安装位置，其他安装方式按实际路径设置；说明见 [Microsoft 手工安装文档](https://learn.microsoft.com/en-us/dotnet/core/install/linux-scripted-manual)。VSCode Remote 在 WSL 启动时不加载普通 shell 启动文件，应使用其用户级 server-env-setup 启动配置，并按 Bourne shell 语法维护。修改后需重启远程 Server，单独改终端 PATH 或重载编辑器窗口不能保证更新现有 Server 的环境，见 [VSCode WSL 环境说明](https://code.visualstudio.com/docs/remote/wsl#_advanced-environment-setup-script)。

C# 扩展自身使用的 .NET Runtime 与项目所需 SDK 分别发现。dotnetAcquisitionExtension.existingDotnetPath 用于扩展运行宿主，不应将它当作项目 SDK 选择器；项目 SDK 仍按 global.json 与可发现安装选择。

编辑器直接加载 csproj 时，游戏引用与 RitsuLib 同样必须可见。可在本机环境设置 GAME_REFS_DIR／RITSULIB_DIR，或准备 csproj 的默认 libs/game／libs/RitsuLib。Linux／WSL 可在 libs/RitsuLib 尚不存在时，用本地符号链接指向已准备的完整包；此目录被整体忽略，真实路径不进入公开文件。不要将项目专用引用变量写成所有工作区共享的固定值。

遇到 SDK 错误先在对应 WSL 环境运行 dotnet --list-sdks 与 dotnet --version，再核对项目是否能直接评估；遇到 MSB4019 或缺程序集时继续检查依赖路径。分别报告 SDK 发现、项目加载与实际编译的结果。

## 分层构建

```bash
./scripts/check.sh --source-only  # Git 边界、文档、公开卡表、本地化和文本资源
./scripts/build.sh --dll-only    # 当前游戏引用下编译 DLL；不生成安装目录
./scripts/prep-art.sh            # ART_SOURCE_DIR 母版 → assets 成品
./scripts/check.sh --full        # 源码检查 + 环境 + 完整构建
./scripts/build.sh               # 完整素材检查、编译、导入、打包和 PCK 验证
./scripts/verify-pck.sh           # 检查已有 PCK 的必需纹理、尺寸与本地化
./scripts/package.sh             # 重建完整包，再按清单／游戏目标版本生成候选 ZIP（MOD_PACKAGE_CHANNEL=release 为公开措辞）
```

源码检查不依赖游戏 DLL、Godot 或多媒体。完整构建先检查素材和引用，再在临时目录组装，经 PCK 验证成功后复制到 `mods-dist/$MOD_ID/`。入口必须存在。导入失败会输出诊断并中止。编译和素材检查不能替代实际游戏验收。

## PCK 布局

- 本地化：`res://$MOD_ID/localization/语言/表.json`。
- 自有资源：`assets/$MOD_ID/` → `res://$MOD_ID/`。
- 全局资源：`assets/global/` → `res://`；用于引擎按全局路径推导的资源（如纪元立绘）。
- 带 .import 的源图不重复入包；侧车与 res://.godot/imported/ 纹理一起分发。
- .tscn 文本场景引用游戏本体 C# 类，独立 Godot 只验证纹理与包数据，完整角色场景仍需游戏加载。

## 部署与分诊

```bash
./scripts/deploy.sh [游戏安装目录]
./scripts/triage-log.sh [游戏日志路径]
```

当前部署脚本服务于 WSL 下的 Windows 游戏，依赖 TASKLIST_EXE。游戏运行或进程检测失败时拒绝部署。文件占用则中止；不得改名让路。**游戏递归扫描 `mods/` 下一切含清单的目录**：备份目录留在 `mods/` 内或改名（如 `.disabled`）都拦不住加载，同 id 双目录会撞车——备份与废弃安装必须移出 `mods/`。缺日志时只能报告未取得证据，不能据此认定无错误。

## 发行工作流

tag `v*` 可触发 [Release 工作流](../../.github/workflows/release.yml)，main 推送可触发 [Compile 工作流](../../.github/workflows/compile.yml)。私有输入 CI 仅在设置 BUILD_INPUTS_REPO variable 后启用，源码检查无需凭据。输入仓包含 game-refs/<版本>/ 与 RitsuLib；美术仓由 ART_REPO variable 选择，默认当前 GitHub 仓库名加 -art。两者使用 REFS_TOKEN 只读 secret，外部维护者可准备自己的输入，不要求组织访问权。双目标构建由 package.sh 编排，不从单一 min_game_version 推断兼容。发行说明取 CHANGELOG 对应段落，成功后创建草稿；实际 Actions 与发行物仍须维护者验收。配置步骤见[新仓上手](onboarding.md)。

本机 package.sh 不要求上述变量或 secret；两版引用分别由 MOD_GAME_REFS_1110 与 MOD_GAME_REFS_1071 指定，Loader 使用 MOD_LOADER_GAME_REFS。

Steam 工坊发布为本地手工步（`local_dev/workshop/publish.sh`，私有，脚手架见 `templates/workshop/`）：从 Release 工件取内容经 SteamCMD 上传至固定物品，描述单源 `description.bbcode` 使用真实换行——steamcmd 的 VDF 不解析 `\n` 转义，会按字面透传。取件按 tag 精确匹配文件名，目录里的历史工件会撞坏通配符。

模板现有适配包括 Power 伤害加成签名、角色动画声明，以及 `Content/Compat/` 的 FromCard／CardPlay.GetPlayer 垫片。csproj 按 `RITSULIB_TARGET` 自动注入 `MOD_GAME_0107_1`；不承诺未使用的克隆、LoseBlock 或卡牌去向 API 已有垫片。新增调用先核对两个版本原版与 RitsuLib，再在对应 Compat 模块处理实际差异。双目标回归：分别以 `RITSULIB_TARGET=0.107.1 GAME_REFS_DIR=<0.107.1 引用>` 与默认环境跑 `build.sh --dll-only`，两目标 0 错误且警告剖面一致方为通过。注意声明层错误会让编译在方法体绑定前中止——必须迭代到零错误，以警告回归确认绑定完整。变体候选布局与游戏内状态见 [STATUS](../../STATUS.md)。

完整 build.sh 按实际 RITSULIB_TARGET 写入平铺安装清单的 min_game_version，不改根源码清单；package.sh 为各目标保存匹配的内容 DLL/清单，工坊根 Loader 声明共同下限。DLL-only 仍不更新安装目录。开发期可按显式批次运行源码/完整本机检查，发行候选包要求花名册延后项清零。

Loader 按两版共有的 API 下限 0.107.1 编译：`scripts/build-loader.sh` 输出到 `mods-dist/loader/`，不刷新已有工坊目录或 ZIP。构建变体包时须重新执行 package.sh；产物更新不等于部署授权。游戏程序集登记规则见[架构](architecture.md#变体-loader-与游戏模型发现)。[Loader 验证](../../tests/LoaderProbe/README.md) 使用真实游戏 DLL 检查选择、依赖拒绝与模型发现，仍须用实际游戏复验完整初始化、资源和菜单。

## 候选部署与工坊更新核对

`deploy.sh [游戏目录] [候选Mod目录]` 接受平铺或变体布局目录。两次进程检测分别在备份前和复制前执行，检测失败或游戏运行时停止。旧安装与 SHA-256 记录保存在 `local_dev/deployments/`，位于游戏扫描的 mods 树之外；完整复制嵌套目录后核对文件集合及字节。失败时保留备份和候选清单供诊断，再次部署前仍需关闭游戏。

工坊脚手架要求显式 tag 和 `WORKSHOP_OWNER`。已有 `publishedfileid.txt` 必须是有效的非零 ID；上传前通过 Steam 官方元数据 API 核对 ID、应用、所有者、简介正文与链接。仅统一换行与首尾空白，正文变更需先同步。网络失败会中止本次发布；读取缓存登录状态由 SteamCMD 完成，脚本保留已有缓存。

更新仅写入内容、已核对的简介及可选 `changenote.txt`，保留线上标题、封面和可见性。首次创建从 SteamCMD 回写的 VDF 提取物品 ID，随后执行线上核对；如未读到 ID，按提示查找已创建的物品并回填，避免重复首发。已有派生仓的私有脚本按差异更新，初始化保留已有文件。

`description.bbcode` 是工坊页面长期简介；`changenote.txt` 是本次发行的更新说明，两者分别维护。需要更新说明时，在发布目录手工创建 UTF-8 文本文件，填写版本与主要变化，可附 Release 链接；按工坊读者需要组织文字，无需与 CHANGELOG 逐字一致。发布前将既有文件更新为本次内容。渲染器将文件正文写入 VDF 的 `changenote` 字段并保留真实换行；没有文件时省略该字段。初始化不创建占位说明。

上传成功后重新下载核对：运行 SteamCMD 的 `+workshop_download_item 2868840 <物品ID> validate +quit`，以输出显示的目录为准，用 `python3 scripts/distribution/delivery.py <候选目录> <下载目录>` 比较全部文件。原始日志留私有工作区，公开记录保留版本与验证结论。
