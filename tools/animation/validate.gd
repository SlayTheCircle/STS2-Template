extends RefCounted
## Checks declared behavior; limb anatomy and artistic quality belong to the character.
static func pose(node: Node, prefix := "") -> Dictionary:
	var result := {}
	if node is Node2D:
		result[prefix] = [node.transform, node.visible, node.modulate, node.z_index]
		if node is Polygon2D: result[prefix].append(node.polygon.duplicate())
	if node is CanvasItem and node.material is ShaderMaterial:
		var uniforms := {}
		for uniform in node.material.shader.get_shader_uniform_list():
			uniforms[uniform.name] = node.material.get_shader_parameter(uniform.name)
		result[prefix + ":shader"] = uniforms
	for child in node.get_children():
		result.merge(pose(child, prefix + "/" + str(child.name)))
	return result

static func seek(player: AnimationPlayer, clip: String, fraction: float) -> void:
	player.play(clip)
	player.pause()
	player.seek(player.get_animation(clip).length * fraction, true)

static func check(actor: Node, spec: Dictionary, twin: Node) -> Array[String]:
	var errors: Array[String] = []
	var player := actor.get_node_or_null(NodePath(spec.player)) as AnimationPlayer
	if player == null:
		errors.append("AnimationPlayer missing: " + str(spec.player))
		return errors
	var reference := pose(twin)
	for clip: String in spec.clips:
		if not player.has_animation(clip):
			errors.append("Missing animation: " + clip)
			continue
		var animation := player.get_animation(clip)
		if animation.length <= 0:
			errors.append("Animation length must be positive: " + clip)
			continue
		if (animation.loop_mode != Animation.LOOP_NONE) != bool(spec.clips[clip]):
			errors.append("Loop flag differs: " + clip)
		errors.append_array(track_errors(player, animation, clip))
	# Reject unresolved tracks before sampling: Godot otherwise skips them with a warning.
	if not errors.is_empty(): return errors
	for clip: String in spec.clips:
		for i in range(int(spec.samples)):
			seek(player, clip, float(i) / (int(spec.samples) - 1))
			finite_nodes(actor, errors)
		if pose(twin) != reference: errors.append("Other instance changed during " + clip)
	for pair: Array in spec.get("transitions", []):
		if not player.has_animation(pair[0]) or not player.has_animation(pair[2]): continue
		seek(player, pair[0], pair[1])
		var before := pose(actor)
		seek(player, pair[2], pair[3])
		if before != pose(actor): errors.append("Discontinuous declared transition: " + str(pair))
	return errors

static func track_errors(player: AnimationPlayer, animation: Animation, clip: String) -> Array[String]:
	var errors: Array[String] = []
	var root := player.get_node_or_null(player.root_node)
	for index in range(animation.get_track_count()):
		if not animation.track_is_enabled(index): continue
		var path := animation.track_get_path(index)
		var names := path.get_concatenated_names()
		var target := root.get_node_or_null(NodePath(names if not names.is_empty() else ".")) if root != null else null
		if target == null:
			errors.append("Unresolved track node: " + clip + " / " + str(path))
			continue
		if animation.track_get_type(index) not in [Animation.TYPE_VALUE, Animation.TYPE_BEZIER]: continue
		if path.get_subname_count() == 0:
			errors.append("Missing track property: " + clip + " / " + str(path))
			continue
		# Expression supports nested Object, Resource, vector and dictionary properties,
		# including valid null values, without treating engine warnings as a result.
		var expression := Expression.new()
		var source := "target"
		for subindex in range(path.get_subname_count()):
			source += "[" + JSON.stringify(str(path.get_subname(subindex))) + "]"
		var parsed := expression.parse(source, PackedStringArray(["target"]))
		if parsed == OK: expression.execute([target], null, false)
		if parsed != OK or expression.has_execute_failed():
			errors.append("Unresolved track property: " + clip + " / " + str(path))
	return errors

static func finite_nodes(node: Node, errors: Array[String]) -> void:
	if node is Node2D:
		if not node.transform.is_finite(): errors.append("Non-finite transform: " + str(node.get_path()))
	if node is Polygon2D:
		for point in node.polygon:
			if not point.is_finite(): errors.append("Non-finite mesh: " + str(node.get_path()))
	for child in node.get_children(): finite_nodes(child, errors)
