# 本地素材工程

本目录保留 Godot 导入工程配置。模板不携带任何媒体与文本场景；多媒体不入公开仓——实际图片位于本地素材树（组织私有美术仓的克隆，经 `ART_SOURCE_DIR` 接入），由完整构建使用。衍生仓的角色场景（.tscn 文本）放 `assets/<ModId>/scenes/`。

尺寸、资源布局与接入规范见 [素材文档](../docs/dev/assets.md)。没有素材的源码检出运行 `scripts/check.sh --source-only`；完整构建缺素材时中止。
