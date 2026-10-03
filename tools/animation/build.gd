extends RefCounted
## A small rigid-part teaching rig. Production art can replace Polygon2D children.
static func create() -> Node2D:
	var actor := Node2D.new()
	actor.name = "Actor"
	var body := Node2D.new()
	body.name = "Body"
	actor.add_child(body)
	part(body, "Torso", Vector2(0, -95), Vector2(65, 100), Color("508caa"))
	part(body, "Head", Vector2(0, -175), Vector2(55, 55), Color("f0ca88"))
	var arm := Node2D.new()
	arm.name = "Arm"
	arm.position = Vector2(35, -135)
	body.add_child(arm)
	part(arm, "Upper", Vector2(0, 25), Vector2(20, 60), Color("f0ca88"))
	var forearm := Node2D.new()
	forearm.name = "Forearm"
	forearm.position = Vector2(0, 52)
	arm.add_child(forearm)
	part(forearm, "Lower", Vector2(0, 23), Vector2(16, 50), Color("d9a55e"))
	part(body, "LeftLeg", Vector2(-20, -25), Vector2(24, 50), Color("42627f"))
	part(body, "RightLeg", Vector2(20, -25), Vector2(24, 50), Color("42627f"))
	var player := AnimationPlayer.new()
	player.name = "AnimationPlayer"
	actor.add_child(player)
	var library := AnimationLibrary.new()
	var definitions := {
		"idle": [1.2, true, [0.0, -0.06, 0.0], [0.0, -0.10, 0.0]],
		"action": [0.8, false, [0.0, -1.2, 0.0], [0.0, -0.8, 0.0]],
		"exit": [1.0, false, [0.0, 0.2, 0.3], [0.0, 0.0, 0.0]],
		"return": [1.0, false, [0.3, 0.2, 0.0], [0.0, 0.0, 0.0]]}
	for clip: String in definitions:
		var values: Array = definitions[clip]
		var animation := Animation.new()
		animation.length = values[0]
		animation.loop_mode = Animation.LOOP_LINEAR if values[1] else Animation.LOOP_NONE
		track(animation, "Body/Arm:rotation", values[2])
		track(animation, "Body/Arm/Forearm:rotation", values[3])
		var heights := [0.0, 0.0, 0.0]
		if clip == "exit": heights = [0.0, 35.0, 80.0]
		if clip == "return": heights = [80.0, 35.0, 0.0]
		track(animation, "Body:position", [Vector2(0, heights[0]), Vector2(0, heights[1]), Vector2(0, heights[2])])
		library.add_animation(clip, animation)
	player.add_animation_library("", library)
	own(actor, actor)
	return actor

static func part(parent: Node, name: String, center: Vector2, size: Vector2, color: Color) -> void:
	var polygon := Polygon2D.new()
	polygon.name = name
	polygon.position = center
	polygon.color = color
	var half := size / 2
	polygon.polygon = PackedVector2Array([Vector2(-half.x, -half.y), Vector2(half.x, -half.y), half, Vector2(-half.x, half.y)])
	parent.add_child(polygon)

static func track(animation: Animation, path: String, values: Array) -> void:
	var index := animation.add_track(Animation.TYPE_VALUE)
	animation.track_set_path(index, NodePath(path))
	for i in range(values.size()):
		animation.track_insert_key(index, animation.length * i / (values.size() - 1), values[i])

static func own(node: Node, owner: Node) -> void:
	for child in node.get_children():
		child.owner = owner
		own(child, owner)
