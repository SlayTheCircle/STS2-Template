extends RefCounted
## Validate review data before constructing scenes or writing outputs.
static func problem(spec: Variant) -> String:
	if not spec is Dictionary: return "Review JSON must be an object"
	if not spec.has_all(["player", "clips", "samples", "view", "world_z", "foreground_z"]):
		return "Review requires player, clips, samples, view and canvas layers"
	if not spec.player is String or spec.player.is_empty(): return "player must be a node path"
	if not spec.clips is Dictionary or spec.clips.is_empty(): return "clips must be a nonempty object"
	for clip in spec.clips:
		if not clip is String or clip.is_empty() or clip in [".", ".."] or clip.contains("/") or clip.contains("\\"):
			return "Use flat clip names for this tool"
		if not spec.clips[clip] is bool: return "Clip loop flags must be booleans"
	if not number(spec.samples) or spec.samples < 2 or spec.samples > 10000 or spec.samples != int(spec.samples):
		return "samples must be an integer in 2..10000"
	if not spec.view is Dictionary or not spec.view.has_all(["width", "height", "position", "scale"]):
		return "view requires width, height, position and scale"
	for key in ["width", "height"]:
		if not number(spec.view[key]) or spec.view[key] < 1 or spec.view[key] > 8192:
			return "View size must be in 1..8192"
	if not number(spec.view.scale) or spec.view.scale <= 0: return "view.scale must be positive"
	if not spec.view.position is Array or spec.view.position.size() != 2: return "position requires [x,y]"
	for value in spec.view.position:
		if not number(value): return "position must contain finite numbers"
	for key in ["world_z", "foreground_z"]:
		if not number(spec[key]) or absf(spec[key]) > 4096: return "Canvas layers must be in -4096..4096"
	if not spec.get("transitions", []) is Array: return "transitions must be an array"
	for pair in spec.get("transitions", []):
		if not pair is Array or pair.size() != 4: return "Transition requires [clip,time,clip,time]"
		if not pair[0] is String or not pair[2] is String: return "Transition clip names must be strings"
		if not spec.clips.has(pair[0]) or not spec.clips.has(pair[2]): return "Transition references undeclared clip"
		for index in [1, 3]:
			if not number(pair[index]) or pair[index] < 0 or pair[index] > 1: return "Transition times must be in 0..1"
	if not spec.get("joint_links", []) is Array: return "joint_links must be an array"
	for link in spec.get("joint_links", []):
		if not link is Array or link.size() != 2 or not link[0] is String or not link[1] is String:
			return "joint_links requires pairs of node paths"
	return ""

static func number(value: Variant) -> bool:
	return (value is float or value is int) and is_finite(float(value))
