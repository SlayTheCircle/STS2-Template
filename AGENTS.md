# STS2-Template · AI 协作入口

先读 [STATUS.md](STATUS.md)、[开发文档索引](docs/dev/README.md)、[贡献指南](CONTRIBUTING.md)。设计意图见[设计资料](docs/design/README.md)，文档与公开边界见[文档规范](docs/dev/documentation.md)。现有内容与限制由 STATUS 维护。

本机工作区存在时，继续阅读私有入口 `local_dev/README.md`，由它导航到实际路径、游戏源码、RitsuLib、参考 Mod 和设计材料。该入口不随仓库分发；公开文档不记录用户名、盘符布局或兄弟工程路径。

## 实施纪律

- 模块化与解耦优先；禁止新增或继续扩张上帝文件／函数／类。单目录平铺文件增多时优先建立有意义的子目录，移动时同步核对审计扫描、注册与资源身份；具体要求见[工程规范](docs/dev/style.md)。
- 新内容继承对应 Base 家族；属性注册、复合 ID、资源槽和伤害／格挡变量约定见开发文档。
- 优先查同游戏版本原版先例，再核对对应 RitsuLib API。检查自家实际接线后再下结论。
- 写入后回读文件和 diff，确认文件确实存在。运行构建管线时完整接收输出。
- 游戏运行中禁止部署。进程检测失败时拒绝部署；不得移除保护或改名让路。
- 多媒体不入公开仓；美术母版由组织私有美术仓承载，本地经 `ART_SOURCE_DIR` 接入。
- local_dev 整个目录保持忽略，不为子文件增加跟踪例外。有公开价值的内容提取到对应 docs 模块；本机路径写入私有配置和地图，公开规范使用逻辑资源名和可配置参数。
- 按风险验证。新增测试先说明保护的实际行为与合理缺陷；跳过和未验证如实报告。
- 名词解释须准确；已裁定的机制遵循现有设计，待追认项显式记录。
- 只有用户明确要求才 commit、push、开 PR、合并、打 tag、部署或重写历史。
- 上游模板仓 `SlayTheCircle/STS2-Template` 的 main 始终只保留一个 `chore(init)` 根提交；更新按[模板仓历史策略](docs/dev/workflow.md#模板仓历史策略)以显式 `force-with-lease` 覆盖。派生 Mod 仓保留正常开发历史；会产生外在影响的操作仍需维护者授权。

## 模板谱系

本仓库与上游模板的派生关系记录在 `.template-origin`（模板仓库见 README 脚注）。身份改名只在派生时一次完成；不要手工散改身份令牌（清单 id、命名空间、Base 家族、本地化键前缀）。模板侧的通用修复按回流流程同步，不单向分叉。

## 常用验证

```bash
./scripts/check.sh --source-only
./scripts/build.sh --dll-only
./scripts/check.sh --full
```

源码检查不要求多媒体或游戏 DLL。完整检查要求本机依赖和完整素材，仍不能替代游戏内验收。脚本加载 `.local-dev.env`；格式与变量见公开示例和 CONTRIBUTING。
