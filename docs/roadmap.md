# 路线图

当前内容和验收记录以 [STATUS.md](../STATUS.md) 为准。

## 当前主线

1. 按各衍生 Mod 的实战反馈迭代模板：回流通用修复（Loader、审计、管线），保持 `.template-origin` 的版本可追溯。
2. 世界线／先古对话等角色 Mod 深层模块：文档指南完善，视需求决定是否提供可选代码模块。
3. 模板机制自身的演进记录在[变更记录](../CHANGELOG.md)；版本以 CHANGELOG 与 `.template-origin` 的 version 与快照字段记录——**模板仓不打 git tag**（tag 会触发 Release 构建，模板无发行物）。

## 观察项

- 第三个 Mod 出现或游戏版本再次破坏加载链时，将变体 Loader 抽为组织共享库（现行决策见[方案取舍](history/decisions.md)）。
- 补齐具体衍生仓的角色、能量、事件与纪元额外资源断言；Base 家族必需纹理已由共享契约生成。

当前不承诺完成时间或未验证平台兼容性。
