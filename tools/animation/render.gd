extends RefCounted
const Validation = preload("validate.gd")

static func viewport(tree: SceneTree, actor: Node2D, spec: Dictionary) -> SubViewport:
	var view := SubViewport.new()
	view.size = Vector2i(spec.view.width, spec.view.height)
	view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	tree.root.add_child(view)
	var background := ColorRect.new()
	background.size = view.size
	background.color = Color("14212b")
	background.z_index = -100
	view.add_child(background)
	var world := Node2D.new()
	world.name = "World"
	world.z_index = int(spec.world_z)
	view.add_child(world)
	world.add_child(actor)
	actor.position = Vector2(spec.view.position[0], spec.view.position[1])
	actor.scale = Vector2.ONE * float(spec.view.scale)
	return view

static func pixels(view: SubViewport) -> int:
	var image := view.get_texture().get_image()
	if image == null or image.is_empty(): return -1
	image.convert(Image.FORMAT_RGBA8)
	var bytes := image.get_data()
	var count := 0
	for i in range(0, bytes.size(), 4):
		if maxi(maxi(absi(bytes[i]-bytes[0]), absi(bytes[i+1]-bytes[1])), absi(bytes[i+2]-bytes[2])) > 4: count += 1
	return count

static func canvas(tree: SceneTree, actor: Node2D, spec: Dictionary) -> Array[String]:
	var errors: Array[String] = []
	var view := viewport(tree, actor, spec)
	var player := actor.get_node(NodePath(spec.player)) as AnimationPlayer
	Validation.seek(player, spec.clips.keys()[0], 0)
	await tree.process_frame
	await RenderingServer.frame_post_draw
	if pixels(view) <= 0: errors.append("Fixture did not render a visible actor")
	var overlay := ColorRect.new()
	overlay.size = view.size
	overlay.color = Color("704050")
	overlay.z_index = int(spec.foreground_z)
	view.add_child(overlay)
	for clip: String in spec.clips:
		for fraction in [0.0, 0.5, 1.0]:
			Validation.seek(player, clip, fraction)
			await tree.process_frame
			await RenderingServer.frame_post_draw
			if pixels(view) != 0: errors.append("Actor leaked above foreground: " + clip)
	overlay.hide()
	view.get_node("World").modulate.a = 0
	await tree.process_frame
	await RenderingServer.frame_post_draw
	if pixels(view) != 0: errors.append("Actor ignored ancestor fade")
	view.queue_free()
	return errors

static func frames(tree: SceneTree, actor: Node2D, spec: Dictionary, output: String, fps: int) -> bool:
	if DirAccess.dir_exists_absolute(output):
		var directory := DirAccess.open(output)
		if directory == null or not directory.get_files().is_empty() or not directory.get_directories().is_empty():
			push_error("Frame output directory must be empty: " + output)
			return false
	var view := viewport(tree, actor, spec)
	var player := actor.get_node(NodePath(spec.player)) as AnimationPlayer
	var manifest := {"fps": fps, "clips": []}
	for clip: String in spec.clips:
		var folder := output.path_join(clip)
		DirAccess.make_dir_recursive_absolute(folder)
		var length := player.get_animation(clip).length
		var count := int(ceil(length * fps)) + 1
		for i in range(count):
			Validation.seek(player, clip, minf(float(i) / fps / length, 1))
			await tree.process_frame
			await RenderingServer.frame_post_draw
			var error := view.get_texture().get_image().save_png(folder.path_join("%04d.png" % i))
			if error != OK:
				push_error("Frame save failed: " + folder)
				view.queue_free()
				return false
		manifest.clips.append({"name": clip, "frames": count, "length": length})
	var file := FileAccess.open(output.path_join("manifest.json"), FileAccess.WRITE)
	if file == null: return false
	file.store_string(JSON.stringify(manifest, "  "))
	view.queue_free()
	return true
