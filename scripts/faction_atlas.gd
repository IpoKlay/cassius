extends AspectRatioContainer

const ATLAS := preload("res://assets/expedition/atlas.png")
const MASK := preload("res://assets/expedition/shore_distance.png")
const TINT := preload("res://shaders/cassius_factions.gdshader")
const SITES := {
	"west": Vector2(.173, .36), "north": Vector2(.52, .12),
	"south": Vector2(.375, .70), "east": Vector2(.83, .45),
	"altar": Vector2(.682, .634),
}
const COLORS := {
	"west": Color("#77965a"), "north": Color("#7eacc3"),
	"south": Color("#b65d42"), "east": Color("#a788c0"),
}
const PLACES := {
	"west": ["古树渡口", "Oldroot Ford"], "north": ["誓约石海岸", "Oathstone Coast"],
	"south": ["边境村落", "Border Village"], "east": ["冷银星塔", "Silverspire"],
}
const INK := Color("#171d25")
const GOLD := Color("#ffe3a1")
var options: Array = []
var overlay: Control

func _ready() -> void:
	ratio = float(ATLAS.get_width()) / ATLAS.get_height()
	stretch_mode = AspectRatioContainer.STRETCH_FIT
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var layer := TextureRect.new()
	layer.texture = ATLAS
	layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	layer.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var tint := ShaderMaterial.new()
	tint.shader = TINT
	tint.set_shader_parameter("water_mask", MASK)
	for id in COLORS:
		tint.set_shader_parameter(id, COLORS[id])
	layer.material = tint
	add_child(layer)
	overlay = Control.new()
	overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	overlay.draw.connect(_draw_map)
	overlay.resized.connect(overlay.queue_redraw)
	add_child(overlay)

func _draw_map() -> void:
	var log: Array = Game.route_log
	for i in range(1, log.size()):
		_route(log[i - 1], log[i], Color("#e0c899"), false)
	for id in options:
		_route(Game.region, id, GOLD, true)
	for id in COLORS:
		var name: String = Game.L(Game.REGIONS[id]["name"])
		_site(id, name, PLACES[id][1 if Game.lang == "en" else 0], COLORS[id].lightened(.45))
	if "altar" in options:
		_site("altar", Game.L("The Great Altar"), "", GOLD)

func _route(from: String, to: String, ink: Color, dashed: bool) -> void:
	if from == to: return
	var a: Vector2 = SITES[from] * overlay.size
	var b: Vector2 = SITES[to] * overlay.size
	var d := b - a
	var bend := (a + b) * .5 + d.orthogonal().normalized() * minf(d.length() * .10, 14)
	var steps := maxi(6, roundi(d.length() / 5.0))
	var points := PackedVector2Array()
	for i in range(steps + 1):
		var t := float(i) / steps
		points.append(a.lerp(bend, t).lerp(bend.lerp(b, t), t).round())
	for i in range(steps):
		if dashed and i % 2 != 0: continue
		overlay.draw_line(points[i], points[i + 1], INK, 3)
	for i in range(steps):
		if dashed and i % 2 != 0: continue
		overlay.draw_line(points[i], points[i + 1], ink, 1)

func _site(id: String, title: String, place: String, color: Color) -> void:
	var at: Vector2 = (SITES[id] * overlay.size).round()
	var active: bool = id == Game.region
	overlay.draw_colored_polygon(PackedVector2Array([
		at + Vector2(0, -5), at + Vector2(5, 0), at + Vector2(0, 5), at + Vector2(-5, 0),
	]), INK)
	overlay.draw_colored_polygon(PackedVector2Array([
		at + Vector2(0, -3), at + Vector2(3, 0), at + Vector2(0, 3), at + Vector2(-3, 0),
	]), GOLD if active or id in options else color)
	if active: overlay.draw_rect(Rect2(at - Vector2.ONE, Vector2(2, 2)), INK)
	var font: Font = Game.font
	var width := ceilf(maxf(font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x,
		font.get_string_size(place, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x)) + 8.0
	var pos := Vector2(clampf(at.x - width * .5, 1, maxf(1, overlay.size.x - width - 1)), at.y + 7).round()
	overlay.draw_rect(Rect2(pos, Vector2(width, 13 if place.is_empty() else 27)), INK)
	overlay.draw_rect(Rect2(pos, Vector2(width, 1)), color)
	overlay.draw_string(font, pos + Vector2(4, 11), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, color)
	if not place.is_empty():
		overlay.draw_string(font, pos + Vector2(4, 24), place, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("#faf0db"))
