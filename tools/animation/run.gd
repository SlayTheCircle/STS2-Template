extends SceneTree
const Config = preload("config.gd")
const Builder = preload("build.gd")
const Validation = preload("validate.gd")
const Renderer = preload("render.gd")
const Viewer = preload("viewer.gd")
const SceneIO = preload("scene_io.gd")

func _initialize() -> void: call_deferred("run")

func run() -> void:
	var args := OS.get_cmdline_user_args()
	var options := {}
	for i in range(0, args.size(), 2):
		if i + 1 >= args.size(): push_error("Arguments require --key value pairs"); quit(2); return
		options[args[i].trim_prefix("--")] = args[i + 1]
	var spec_path: String = options.get("spec", "../../examples/animation/review.json")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(spec_path))
	var problem := Config.problem(parsed)
	if not problem.is_empty(): push_error(problem); quit(2); return
	var spec: Dictionary = parsed
	if options.has("pck") and not ProjectSettings.load_resource_pack(options.pck):
		push_error("Cannot mount PCK"); quit(2); return
	var actor: Node2D
	var twin: Node2D
	if options.has("scene"):
		var scene := load(options.scene) as PackedScene
		if scene == null: push_error("Cannot load scene"); quit(2); return
		actor = scene.instantiate() as Node2D
		twin = scene.instantiate() as Node2D
	else:
		actor = Builder.create()
		twin = Builder.create()
	if actor == null or twin == null: push_error("Expected Node2D root"); quit(2); return
	root.add_child(actor)
	root.add_child(twin)
	await process_frame
	var errors := Validation.check(actor, spec, twin)
	twin.free()
	root.remove_child(actor)
	var mode: String = options.get("mode", "preview")
	if not errors.is_empty():
		print(JSON.stringify({"passed": false, "errors": errors})); actor.free(); quit(1); return
	if mode in ["canvas", "frames", "preview"] and DisplayServer.get_name() == "headless":
		push_error("This mode needs a renderer; use a display or xvfb-run, without --headless")
		actor.free(); quit(2); return
	match mode:
		"check":
			print(JSON.stringify({"passed": true, "clips": spec.clips.keys(), "samples_per_clip": spec.samples}))
			actor.free(); quit()
		"canvas":
			errors = await Renderer.canvas(self, actor, spec)
			print(JSON.stringify({"passed": errors.is_empty(), "errors": errors}))
			quit(0 if errors.is_empty() else 1)
		"frames":
			if not options.has("out"): push_error("frames requires --out directory"); quit(2); return
			var fps := int(options.get("fps", "30"))
			if fps < 1 or fps > 120: push_error("fps must be 1..120"); quit(2); return
			var exported := await Renderer.frames(self, actor, spec, options.out, fps)
			quit(0 if exported else 1)
		"save":
			if not options.has("out"): push_error("save requires --out scene.tscn"); quit(2); return
			var result := await SceneIO.save(self, actor, spec, options.out)
			actor.free(); quit(0 if result == OK else 1)
		"preview": Viewer.show(self, actor, spec)
		_: push_error("Unknown mode: " + mode); actor.free(); quit(2)
