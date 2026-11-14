extends Control
## One-shot UI flourishes drawn over the menus:
##   "border" - gold sparks race around a window's frame as it opens
##   "seal"   - a red wax seal is pressed where a choice was made (burst of wax + gold flecks)

var mode := "border"
var rect := Rect2()
var at := Vector2.ZERO
var t := 0.0
var life := 0.8
var bits: Array = []


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_preset(Control.PRESET_FULL_RECT)
	size = Vector2(480, 270)
	if mode == "seal":
		life = 0.9
		for i in 22:
			var a := randf() * TAU
			bits.append({"p": at, "v": Vector2.from_angle(a) * randf_range(30, 90), "c": Color(0.75, 0.12, 0.1) if i % 3 else Color(1.0, 0.82, 0.38), "s": 1.0 if i % 4 else 2.0})


func _perimeter(u: float) -> Vector2:
	## u in [0,1) walks the rectangle's edge clockwise from the top-left corner
	var w := rect.size.x
	var h := rect.size.y
	var d := fposmod(u, 1.0) * 2.0 * (w + h)
	if d < w:
		return rect.position + Vector2(d, 0)
	d -= w
	if d < h:
		return rect.position + Vector2(w, d)
	d -= h
	if d < w:
		return rect.position + Vector2(w - d, h)
	d -= w
	return rect.position + Vector2(0, h - d)


func _process(delta: float) -> void:
	t += delta
	for b in bits:
		b["p"] = Vector2(b["p"]) + Vector2(b["v"]) * delta
		b["v"] = Vector2(b["v"]) * 0.9 + Vector2(0, 60) * delta
	if t >= life:
		queue_free()
	queue_redraw()


func _draw() -> void:
	var k := t / life
	if mode == "border":
		# four runners leave from the corners and chase each other round the frame
		for r in 4:
			for trail in 7:
				var u := r * 0.25 + k * 0.5 - trail * 0.006
				var p := _perimeter(u).round()
				var a := (1.0 - k) * (1.0 - trail / 7.0)
				var c := Color(1.0, 0.9, 0.55, a) if trail < 2 else Color(0.95, 0.65, 0.25, a * 0.8)
				draw_rect(Rect2(p - Vector2(1, 1), Vector2(2 if trail < 2 else 1, 2 if trail < 2 else 1)), c)
		# a soft flash along the frame at the start
		if k < 0.25:
			draw_rect(rect.grow(1), Color(1.0, 0.85, 0.5, (0.25 - k) * 2.0), false, 1.0)
	else:
		# the seal itself: a red disc that lands, squashes, and fades with a gold stamp
		var land: float = clamp(k * 5.0, 0.0, 1.0)
		var r := 9.0 * (1.6 - 0.6 * land)
		var fade: float = clamp((1.0 - k) * 2.0, 0.0, 1.0)
		draw_circle(at, r + 1.0, Color(0.35, 0.05, 0.05, fade))
		draw_circle(at, r, Color(0.72, 0.12, 0.1, fade))
		draw_circle(at + Vector2(-2, -2), r * 0.45, Color(0.85, 0.25, 0.2, fade))
		draw_arc(at, r * 0.62, 0.0, TAU, 16, Color(1.0, 0.8, 0.4, fade), 1.0)
		draw_rect(Rect2(at - Vector2(1, 3), Vector2(2, 6)), Color(1.0, 0.82, 0.4, fade))
		draw_rect(Rect2(at - Vector2(3, 1), Vector2(6, 2)), Color(1.0, 0.82, 0.4, fade))
		for b in bits:
			draw_rect(Rect2(Vector2(b["p"]).round(), Vector2(b["s"], b["s"])), Color(b["c"].r, b["c"].g, b["c"].b, fade))
