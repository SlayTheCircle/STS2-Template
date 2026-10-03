# 新仓上手（从模板派生）

从本模板派生一个新 Mod 的完整清单。逐步执行，每步的验证命令都应通过再进下一步。本页覆盖**基建**（仓库、凭据、环境）；从设计稿开始铺内容的推荐路径见[内容开发 SOP](content-sop.md)。

## 1. 建仓与派生

```bash
gh repo create SlayTheCircle/<新ModId> --template SlayTheCircle/STS2-Template --public
git clone git@github.com:SlayTheCircle/<新ModId>.git && cd <新ModId>
git config core.hookspath .githooks
scripts/init-mod.sh <新ModId> <PascalName> --cn-name "<中文名>" [--name "<英文名>"]
```

外部维护者可将建仓命令中的组织替换为自己的账户，并在初始化传入 `--repo Owner/Repository`；它配置 README 发行链接与工坊工件来源，不要求加入 SlayTheCircle。

本节只在尚未派生的模板上执行；派生仓从第 3 节配置自己的输入。身份恰为 `STS2-<PascalName>`。初始化默认只验源码；`--verify-build` 使用 `.local-dev.env` 的当前目标，改名前预检依赖、改名后编译。双目标回归分别执行。完成后 README 换视角、STATUS 清除模板验收声明，并删除一次性脚手架。

使用源码 ZIP 时先 `git init -b main`、`git add -A` 建立初始源码索引，再初始化；不要求先提交。已有历史的克隆须保持干净，暂存已有修改不会绕过预检。

## 2. 可选的私有输入 CI

本机编译、打包和实现设计不要求组织密钥。源码 CI 无 secret 可执行；私有输入构建默认不启用。

1. 自行准备只读构建输入仓，包含 `game-refs/0.111.0/`、`game-refs/0.107.1/` 与 `RitsuLib/` 完整包。组织成员可使用获准访问的 circle-refs；外部维护者使用自己的输入仓。
2. Actions variable `BUILD_INPUTS_REPO` 填 `Owner/Repository` 后启用 Compile 与 Release。设置 `REFS_TOKEN` secret，赋予所读取输入仓和美术仓的只读权限；不公开凭据或私人存放位置。
3. variable `ART_REPO` 可覆盖美术仓；默认当前 GitHub 仓库名加 `-art`。输入仓名和凭据不硬编码进源码。

## 3. 私有侧

1. 美术输入：组织内 Mod 创建组织私有仓 `<新ModId>-art`；外部维护者使用自己的私有母版目录或美术仓即可，不要求组织权限。配置 `.local-dev.env` 的 `ART_SOURCE_DIR`，按[素材手册](assets.md)绑定完整相对路径；手工交付目录不必改成固定结构。
2. `local_dev/`：init 已生成 README、工作区地图及工坊发布脚本、`config.sh`、描述骨架。已有私有导航、发布脚本、配置与描述会保留；填写本 Mod 的设计与依赖位置，既有发布脚本按原配置核对目标。整个目录不入库。
3. 工坊封面 `cover.jpg` 放 `local_dev/workshop/`（≥512²，建议 1024² JPEG）。

## 4. 本机环境

```bash
cp .local-dev.env.example .local-dev.env   # 填 GAME_DIR/RITSULIB_DIR 等
./scripts/restore-refs.sh                  # 从游戏安装复制编译引用
./scripts/check.sh --source-only           # 应绿
./scripts/build.sh --dll-only
```

RitsuLib 完整依赖包（含 `compat/`、`shared/`、`RitsuLib.References.props`）放 `libs/RitsuLib/`，或设置 RITSULIB_DIR 指向自己准备的完整包。组织共享位置是内部可选配置。

先按[素材规范](assets.md)设置映射并生成成品，再运行完整构建。角色逐槽修改 `Content/Characters/<Short>CharacterAssets.cs`；初始卡组、三池和示例文本同批替换。设计整理见[内容开发 SOP](content-sop.md)，发行验收见[验证纪律](testing.md)。

## 5. 首次发版

1. CHANGELOG 整理 Unreleased → `## [x.y.z]` 段（**段缺失或为空会中止 Release 构建**）；清单 version 同步。
2. 可先在本机 `./scripts/package.sh` 生成候选包，无需 GitHub 凭据。使用可选 Release 工作流时，配置第 2 节输入后提交、打 tag `vx.y.z`、推送，生成候选 ZIP 与**草稿** Release。模板仓自身不发行或打 tag。
3. 下载草稿工件覆盖安装到游戏 `mods/`（**先关游戏；备份移出 mods/，游戏递归扫描会加载备份目录**）试玩验收。
4. 验收通过：GitHub 草稿转正；工坊 `local_dev/workshop/publish.sh <Steam账号> <tag>` 首发（自动捕获物品 ID 回填 `publishedfileid.txt`，之后的更新走同 ID）。
5. 发布前在 `config.sh` 填 `WORKSHOP_OWNER`（工坊所有者个人主页的 SteamID64）。更新时脚本核对物品 ID、所属游戏、所有者和线上简介；简介有差异时先阅读线上版本并同步 `description.bbcode`。`changenote.txt` 可填写本次更新说明，更新保留线上标题、封面和可见性。
6. Steam 登录：首次需密码 + 手机令牌五位码（`--code` 模式静默读入）；成功一次后凭据缓存免密。VDF 描述不解析 `\n` 转义——描述单源 `description.bbcode` 用真实换行。

## 6. 模板回流

模板修了通用 bug 时，对照 `.template-origin` 的版本、`snapshotCommit` 与 `snapshotDigest` 同步。Commit 是派生前快照所在仓库的提交；GitHub Use this template 可能生成新历史，不能冒充上游提交。Digest 是派生前受跟踪文件名与内容的 SHA-256，可比对准确快照；无历史 ZIP 的 commit 为 null。回流提交注明来源，反向经验同样整理回模板。

上游模板采用[单快照历史策略](workflow.md#模板仓历史策略)，main 覆盖更新后，旧 `snapshotCommit` 可能无法再从上游取得。派生时保留来源快照及 `.template-origin`，后续结合版本、`snapshotDigest` 和保留的快照比对具体文件变化，不依赖连续上游提交或共同祖先进行同步。派生 Mod 仓保留自己的正常开发历史；回流改动在模板侧经审阅与验证后纳入下一份单提交快照。
