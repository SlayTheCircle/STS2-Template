extends RefCounted
## Normalize resource declarations and references without rewriting user strings.
const Validation = preload("validate.gd")
const DECLARATION = '(?m)^\\[(ext_resource|sub_resource)\\b[^\\n]*\\bid="([^"]+)"'
const REFERENCE = '(ExtResource|SubResource)\\("([^"]+)"\\)'

static func normalized(content: String) -> String:
	var mapping := {}
	var declarations := RegEx.create_from_string(DECLARATION)
	for found: RegExMatch in declarations.search_all(content):
		var key := found.get_string(1) + ":" + found.get_string(2)
		mapping[key] = "part_%03d" % (mapping.size() + 1)
	var tokens := RegEx.create_from_string(DECLARATION + "|" + REFERENCE)
	var result := ""
	var cursor := 0
	for found: RegExMatch in tokens.search_all(content):
		var group := 2 if found.get_start(2) >= 0 else 4
		var kind := found.get_string(1) if group == 2 else ("ext_resource" if found.get_string(3) == "ExtResource" else "sub_resource")
		var start := found.get_start(group)
		var end := found.get_end(group)
		result += content.substr(cursor, start - cursor)
		result += mapping.get(kind + ":" + found.get_string(group), found.get_string(group))
		cursor = end
	return result + content.substr(cursor)

static func save(tree: SceneTree, actor: Node2D, spec: Dictionary, path: String) -> Error:
	if not path.ends_with(".tscn"): return ERR_INVALID_PARAMETER
	var temporary := path.trim_suffix(".tscn") + ".building.tscn"
	var result := await save_candidate(tree, actor, spec, path, temporary)
	if FileAccess.file_exists(temporary): DirAccess.remove_absolute(temporary)
	return result

static func save_candidate(tree: SceneTree, actor: Node2D, spec: Dictionary, path: String, temporary: String) -> Error:
	var packed := PackedScene.new()
	var result := packed.pack(actor)
	if result != OK: return result
	result = ResourceSaver.save(packed, temporary)
	if result != OK: return result
	var content := normalized(FileAccess.get_file_as_string(temporary))
	var file := FileAccess.open(temporary, FileAccess.WRITE)
	if file == null: return FileAccess.get_open_error()
	file.store_string(content)
	file.close()
	# Validate serialized bytes, not just the original in-memory scene.
	var reloaded := ResourceLoader.load(temporary, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	if reloaded == null: return ERR_INVALID_DATA
	var candidate := reloaded.instantiate() as Node2D
	var twin := reloaded.instantiate() as Node2D
	if candidate == null or twin == null:
		if candidate != null: candidate.free()
		if twin != null: twin.free()
		return ERR_INVALID_DATA
	tree.root.add_child(candidate)
	tree.root.add_child(twin)
	await tree.process_frame
	var errors := Validation.check(candidate, spec, twin)
	candidate.free()
	twin.free()
	if not errors.is_empty():
		push_error("Saved scene failed validation: " + str(errors))
		return ERR_INVALID_DATA
	if not FileAccess.file_exists(path) or FileAccess.get_file_as_string(path) != content:
		file = FileAccess.open(path, FileAccess.WRITE)
		if file == null: return FileAccess.get_open_error()
		file.store_string(content)
		file.close()
	return OK
