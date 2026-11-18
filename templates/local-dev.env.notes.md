# local_dev 私有侧说明(脚手架)

`local_dev/` 整个目录不入库。init-mod.sh 已在此生成:

- `workshop/publish.sh` —— 工坊发布脚本(config.sh 已按本 Mod 预填;STEAMCMD 环境变量指向本机 steamcmd)
- `workshop/description.bbcode` —— 工坊描述单源(VDF 不解析 \n 转义,必须真实换行)
- 需自备:`workshop/cover.jpg`(≥512²,建议 1024² JPEG)、`publishedfileid.txt`(首发后自动生成)

已生成 `README.md` 与 `workspace.md`；填写本 Mod 设计和通用依赖的实际路径。工具与依赖见根目录 `.local-dev.env`。
