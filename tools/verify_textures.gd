extends RefCounted

static func verify(contract: Dictionary) -> int:
	var failures := 0
	for item in contract.get("textures", []):
		var path: String = item["path"]
		var texture := ResourceLoader.load(path, "Texture2D") as Texture2D
		if texture == null or texture.get_width() <= 0 or texture.get_height() <= 0:
			push_error("PCK 纹理不可加载: " + path)
			failures += 1
			continue
		if item.has("size"):
			var size: Array = item["size"]
			if Vector2i(texture.get_width(), texture.get_height()) != Vector2i(int(size[0]), int(size[1])):
				push_error("PCK 纹理尺寸错误: " + path)
				failures += 1
		if item.get("transparent", false):
			var pixels := texture.get_image()
			if pixels == null or pixels.is_empty() or pixels.get_pixel(0, 0).a > 0.01:
				push_error("PCK 图标缺透明边缘: " + path)
				failures += 1
	for path in contract.get("files", []):
		if not FileAccess.file_exists(path):
			push_error("PCK 缺文件: " + path)
			failures += 1
	return failures
