extends RefCounted
const Joints = preload("joints.gd")
const Renderer = preload("render.gd")
const Validation = preload("validate.gd")

static func show(tree: SceneTree, actor: Node2D, spec: Dictionary) -> void:
	var view := Renderer.viewport(tree, actor, spec)
	var picture := TextureRect.new()
	picture.texture = view.get_texture()
	picture.position = Vector2(130, 100)
	tree.root.add_child(picture)
	var controls := VBoxContainer.new()
	controls.position = Vector2(12, 12)
	controls.size.x = 850
	tree.root.add_child(controls)
	var row := HBoxContainer.new()
	controls.add_child(row)
	var clips := OptionButton.new()
	for clip: String in spec.clips: clips.add_item(clip)
	row.add_child(clips)
	var player := actor.get_node(NodePath(spec.player)) as AnimationPlayer
	clips.item_selected.connect(func(index: int): player.play(clips.get_item_text(index)))
	var toggle := Button.new()
	toggle.text = "Play / Pause"
	toggle.pressed.connect(func():
		if player.is_playing(): player.pause()
		else: player.play())
	row.add_child(toggle)
	var speed := OptionButton.new()
	for label in ["1x", "0.25x", "0.5x"]: speed.add_item(label)
	speed.item_selected.connect(func(index: int): player.speed_scale = [1.0, 0.25, 0.5][index])
	row.add_child(speed)
	var size := OptionButton.new()
	for label in ["100%", "50%", "25%"]: size.add_item(label)
	size.item_selected.connect(func(index: int): picture.scale = Vector2.ONE * [1.0, 0.5, 0.25][index])
	row.add_child(size)
	var joints := Joints.new()
	joints.actor = actor
	joints.links = spec.get("joint_links", [])
	actor.add_child(joints)
	joints.hide()
	var bones := CheckButton.new()
	bones.text = "Joint links"
	bones.toggled.connect(func(on: bool): joints.visible = on)
	row.add_child(bones)
	var progress := HSlider.new()
	progress.max_value = 1
	progress.step = 0.001
	progress.value_changed.connect(func(value: float): Validation.seek(player, clips.get_item_text(clips.selected), value))
	controls.add_child(progress)
	var hint := Label.new()
	hint.text = "Drag to pause and scrub. Scale approximates display size; verify final framing in game."
	controls.add_child(hint)
	player.play(clips.get_item_text(0))
