extends Node2D
## Preview-only joint links selected by the character's review configuration.
var actor: Node2D
var links: Array = []
func _process(_delta: float) -> void: queue_redraw()
func _draw() -> void:
	for link: Array in links:
		var a := actor.get_node_or_null(NodePath(link[0])) as Node2D
		var b := actor.get_node_or_null(NodePath(link[1])) as Node2D
		if a != null and b != null:
			var start := to_local(a.global_position)
			var end := to_local(b.global_position)
			draw_line(start, end, Color.CYAN, 2)
			draw_circle(start, 4, Color.ORANGE)
			draw_circle(end, 4, Color.ORANGE)
