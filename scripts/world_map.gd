extends Control
## The map of the four realms around the inner sea.
## A living pixel atlas: moving water and surf, ships on the sea lanes, a serpent that surfaces,
## clouds and their shadows, birds, weather over each realm, the Great Altar smoking on its island.
## It charts the road the column has marched, and at a crossroads it is where the next road is chosen.

signal closed
signal chosen(region: String)

const MW := 720.0
const MH := 400.0
const VIEW := Rect2(14, 32, 452, 214)         # where the map shows on screen, inside the meander frame
const FORT := Vector2(183, 350)
const ALTAR := Vector2(360, 200)
const STOPS := {
	"south": [Vector2(226, 331), Vector2(319, 329), Vector2(404, 341), Vector2(484, 324)],
	"west": [Vector2(84, 266), Vector2(72, 219), Vector2(100, 180), Vector2(128, 144)],
	"north": [Vector2(235, 77), Vector2(318, 66), Vector2(400, 71), Vector2(487, 74)],
	"east": [Vector2(576, 151), Vector2(586, 184), Vector2(610, 217), Vector2(602, 253)],
}
const LABEL_AT := {"north": Vector2(360, 34), "east": Vector2(664, 300), "south": Vector2(470, 384), "west": Vector2(60, 110)}
const REGION_COL := {"north": Color(0.75, 0.86, 0.95), "east": Color(0.78, 0.62, 0.92), "south": Color(0.95, 0.72, 0.4), "west": Color(0.55, 0.85, 0.5)}
const GOLD := Color(1.0, 0.84, 0.42)
const INK := Color(0.1, 0.07, 0.06)

var choose_mode := false
var options: Array = []
var pan := Vector2.ZERO
var pan_target := Vector2.ZERO
var dragging := false
var drag_from := Vector2.ZERO
var t := 0.0
var sel := ""                 # the option whose card is open
var hover := ""
var land_img: Image
var map_rect: TextureRect
var fog_rect: TextureRect
var sea_mat: ShaderMaterial
var fog_mat: ShaderMaterial
var layer_over: Control
var reveal := Vector4.ZERO
var ships: Array = []
var serpent := {"t": -6.0, "p": Vector2.ZERO, "dir": 1.0}
var clouds: Array = []
var birds: Array = []
var parts: Array = []
var card: Control = null
var cloud_tex: Array = []
var ship_tex := {}


static func load_tex(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path)
	if FileAccess.file_exists(path):
		var img := Image.load_from_file(ProjectSettings.globalize_path(path))
		if img != null:
			return ImageTexture.create_from_image(img)
	return null


func setup(choose: bool, opts: Array) -> void:
	choose_mode = choose
	options = opts


func _ready() -> void:
	size = Vector2(480, 270)
	mouse_filter = Control.MOUSE_FILTER_STOP
	theme = Game.theme
	var reg_tex := load_tex("res://assets/map/map_regions.png")
	if reg_tex != null:
		land_img = reg_tex.get_image()
	# clipped viewport onto the big map
	var clip := Control.new()
	clip.position = VIEW.position
	clip.size = VIEW.size
	clip.clip_contents = true
	clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(clip)
	map_rect = TextureRect.new()
	map_rect.texture = load_tex("res://assets/map/map_base.png")
	map_rect.size = Vector2(MW, MH)
	map_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sea_mat = ShaderMaterial.new()
	sea_mat.shader = load("res://shaders/map_sea.gdshader")
	sea_mat.set_shader_parameter("shore_tex", load_tex("res://assets/map/map_shore.png"))
	map_rect.material = sea_mat
	clip.add_child(map_rect)
	fog_rect = TextureRect.new()
	fog_rect.texture = map_rect.texture
	fog_rect.size = Vector2(MW, MH)
	fog_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fog_mat = ShaderMaterial.new()
	fog_mat.shader = load("res://shaders/map_fog.gdshader")
	fog_mat.set_shader_parameter("region_tex", reg_tex)
	fog_rect.material = fog_mat
	clip.add_child(fog_rect)
	layer_over = Control.new()
	layer_over.size = Vector2(MW, MH)
	layer_over.mouse_filter = Control.MOUSE_FILTER_IGNORE
	clip.add_child(layer_over)
	layer_over.draw.connect(_draw_map)
	# what the column has seen: realms already marched through start revealed; this visit burns the veil back
	var seen := {}
	for r in Game.route_log:
		seen[str(r)] = true
	var order := ["north", "east", "south", "west"]
	var target := Vector4.ZERO
	for i in 4:
		var v := 1.0 if seen.has(order[i]) else 0.0
		if choose_mode and options.has(order[i]):
			v = max(v, 0.45)         # scouts have seen the edge of the realms you could march into
		target[i] = v
	reveal = target
	var last := str(Game.route_log.back()) if not Game.route_log.is_empty() else "south"
	var newest := order.find(last)
	if newest >= 0 and Game.route_log.count(last) == 1:
		reveal[newest] = 0.0
		var tw := create_tween()
		tw.tween_method(_set_reveal.bind(newest), 0.0, 1.0, 2.2).set_delay(0.4)
	fog_mat.set_shader_parameter("reveal", reveal)
	# sea traffic, sky, and weather
	var lanes := [[Vector2(360, 200), Vector2(150, 70), 0.035, "red"], [Vector2(360, 205), Vector2(205, 95), -0.022, "white"],
		[Vector2(520, 205), Vector2(60, 40), 0.05, "violet"], [Vector2(330, 150), Vector2(110, 40), -0.03, "grey"], [Vector2(400, 290), Vector2(120, 22), 0.04, "white"], [Vector2(250, 250), Vector2(70, 30), -0.045, "red"]]
	for l in lanes:
		ships.append({"c": l[0], "r": l[1], "w": l[2], "a": randf() * TAU, "sail": l[3]})
	for i in 4:
		cloud_tex.append(load_tex("res://assets/map/cloud%d.png" % i))
	for n in ["red", "white", "violet", "grey"]:
		ship_tex[n] = load_tex("res://assets/map/ship_%s.png" % n)
	for i in 6:
		clouds.append([randf() * MW, randf_range(20, MH - 40), randf_range(5.0, 9.0), 1.0, i % 4])
	for i in 4:
		birds.append([randf() * MW, randf_range(30, MH - 30), randf_range(14, 22), randf() * TAU])
	# open on the column's current position
	pan = _clamp_pan(_current_pos() - VIEW.size * 0.5)
	pan_target = pan
	Game.sfx("ui_open", -3.0, 0.9)
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, 0.25)


func _set_reveal(v: float, i: int) -> void:
	reveal[i] = v
	fog_mat.set_shader_parameter("reveal", reveal)


# ------------------------------------------------------------------ geography of the march
func _stop_for(region: String, nth: int) -> Vector2:
	var arr: Array = STOPS[region]
	return arr[nth % arr.size()]


func _route_points() -> Array:
	## fort, then one stop per leg marched (the nth visit to a realm uses its nth stop)
	var pts: Array = [FORT]
	var counts := {}
	for r in Game.route_log:
		var k := str(r)
		var n: int = counts.get(k, 0)
		pts.append(_stop_for(k, n))
		counts[k] = n + 1
	return pts


func _option_point(o: String) -> Vector2:
	if o == "altar":
		return ALTAR
	return _stop_for(o, Game.route_log.count(o))


func _current_pos() -> Vector2:
	var pts := _route_points()
	return pts.back()


func _is_land(p: Vector2) -> bool:
	if land_img == null:
		return false
	var x := clampi(int(p.x), 0, int(MW) - 1)
	var y := clampi(int(p.y), 0, int(MH) - 1)
	return land_img.get_pixel(x, y).g > 0.5


func _clamp_pan(p: Vector2) -> Vector2:
	return Vector2(clamp(p.x, 0.0, MW - VIEW.size.x), clamp(p.y, 0.0, MH - VIEW.size.y))


# ------------------------------------------------------------------ frame loop
func _process(delta: float) -> void:
	t += delta
	var mv := Vector2.ZERO
	if card == null:
		if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
			mv.x -= 1
		if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
			mv.x += 1
		if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
			mv.y -= 1
		if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
			mv.y += 1
	if mv != Vector2.ZERO:
		pan_target = _clamp_pan(pan_target + mv * 160.0 * delta)
	pan = pan.lerp(pan_target, min(1.0, delta * 10.0))
	var pr := pan.round()
	map_rect.position = -pr
	fog_rect.position = -pr
	layer_over.position = -pr
	sea_mat.set_shader_parameter("t", t)
	fog_mat.set_shader_parameter("t", t)
	# ships sail their lanes, hiding behind headlands
	for s in ships:
		s["a"] = float(s["a"]) + float(s["w"]) * delta
	# the serpent surfaces now and then somewhere in open water
	serpent["t"] = float(serpent["t"]) + delta
	if float(serpent["t"]) > 7.0:
		for k in 20:
			var p := Vector2(randf_range(200, 540), randf_range(120, 290))
			if not _is_land(p) and not _is_land(p + Vector2(18, 0)) and not _is_land(p - Vector2(18, 0)) and p.distance_to(ALTAR) > 40.0:
				serpent = {"t": 0.0, "p": p, "dir": 1.0 if randf() < 0.5 else -1.0}
				break
	for c in clouds:
		c[0] = fmod(float(c[0]) + float(c[2]) * delta, MW + 120.0)
	for b in birds:
		b[0] = fmod(float(b[0]) + float(b[2]) * delta, MW + 40.0)
	_spawn_weather(delta)
	for q in parts:
		q["life"] = float(q["life"]) - delta
		q["p"] = Vector2(q["p"]) + Vector2(q["v"]) * delta
	parts = parts.filter(func(q): return float(q["life"]) > 0.0)
	# hover over a choosable stop
	hover = ""
	if choose_mode and card == null:
		var mp := get_local_mouse_position()
		if VIEW.has_point(mp):
			var mm := mp - VIEW.position + pan
			for o in options:
				if mm.distance_to(_option_point(str(o))) < 10.0:
					hover = str(o)
	layer_over.queue_redraw()
	queue_redraw()


func _spawn_weather(delta: float) -> void:
	var view := Rect2(pan - Vector2(20, 20), VIEW.size + Vector2(40, 40))
	var p := Vector2(randf_range(view.position.x, view.end.x), randf_range(view.position.y, view.end.y))
	if not _is_land(p) or land_img == null:
		return
	var id := int(round(land_img.get_pixel(int(p.x), int(p.y)).r * 255.0 / 50.0))
	if randf() > delta * 60.0:
		return
	match id:
		1:
			parts.append({"k": "snow", "p": p, "v": Vector2(-4, 9), "life": 2.5, "max": 2.5})
		4:
			parts.append({"k": "fly", "p": p, "v": Vector2(randf_range(-2, 2), randf_range(-2, 2)), "life": 2.0, "max": 2.0})
		2:
			parts.append({"k": "mote", "p": p, "v": Vector2(0, -4), "life": 2.0, "max": 2.0})
		3:
			if randf() < 0.3:
				parts.append({"k": "dust", "p": p, "v": Vector2(6, -1), "life": 1.6, "max": 1.6})


# ------------------------------------------------------------------ drawing (map space)
func _draw_map() -> void:
	var o := layer_over
	# cloud shadows on land and sea
	for c in clouds:
		_cloud(o, Vector2(float(c[0]) - 60.0 + 12.0, float(c[1]) + 18.0), float(c[3]), int(c[4]), Color(0.0, 0.03, 0.08, 0.22))
	# weather
	for q in parts:
		var al: float = clamp(float(q["life"]) / float(q["max"]) * 1.6, 0.0, 1.0)
		var pp: Vector2 = Vector2(q["p"]).round()
		match str(q["k"]):
			"snow":
				o.draw_rect(Rect2(pp, Vector2(1, 1)), Color(1, 1, 1, 0.9 * al))
			"fly":
				o.draw_rect(Rect2(pp, Vector2(1, 1)), Color(0.9, 1.0, 0.55, al * (0.5 + 0.5 * sin(t * 6.0 + pp.x))))
			"mote":
				o.draw_rect(Rect2(pp, Vector2(1, 1)), Color(0.9, 0.7, 1.0, al))
			"dust":
				o.draw_rect(Rect2(pp, Vector2(2, 1)), Color(0.95, 0.85, 0.6, 0.6 * al))
	# ships with a wake; hidden while their lane crosses land
	for s in ships:
		var a: float = s["a"]
		var c0: Vector2 = s["c"]
		var r: Vector2 = s["r"]
		var p := c0 + Vector2(cos(a) * r.x, sin(a) * r.y)
		if _is_land(p) or _is_land(p + Vector2(0, 3)):
			continue
		var dirx := -sin(a) * r.x * float(s["w"])
		_ship(o, p.round(), 1.0 if dirx >= 0.0 else -1.0, s["sail"])
	# the serpent: three coils rising and sinking, a splash where it breaks the surface
	var st: float = serpent["t"]
	if st >= 0.0 and st < 5.0:
		var sp: Vector2 = serpent["p"]
		var up: float = sin(clamp(st / 5.0, 0.0, 1.0) * PI)
		for k in 3:
			var cx := sp.x + (k * 9.0 - 9.0 + st * 3.0) * float(serpent["dir"])
			var h := roundf((2.0 + k % 2) * up)
			for dx in range(-3, 4):
				var hh := roundf(h * cos(dx / 3.0 * PI * 0.5))
				if hh >= 1.0:
					o.draw_rect(Rect2(cx + dx, sp.y - hh, 1, hh), Color(0.42, 0.22, 0.45) if dx < 1 else Color(0.3, 0.14, 0.34))
			o.draw_rect(Rect2(cx - 4, sp.y, 9, 1), Color(0.85, 0.95, 0.95, 0.7 * up))
		var hx := sp.x + (18.0 + st * 3.0) * float(serpent["dir"])
		if up > 0.4:
			o.draw_rect(Rect2(hx - 1, sp.y - 5, 3, 5), Color(0.42, 0.22, 0.45))
			o.draw_rect(Rect2(hx + float(serpent["dir"]), sp.y - 5, 1, 1), Color(1.0, 0.85, 0.3))
	# Great Altar on its island: stepped stone, fire, a column of smoke
	_altar(o)
	# Cassius' fort
	_fort(o, FORT)
	# the road marched: a gold line with marching dashes; sea crossings dashed blue
	var pts := _route_points()
	for i in range(pts.size() - 1):
		_route_seg(o, pts[i], pts[i + 1], true)
	# every stop of every realm: faint markers; visited ones get a bronze stud
	var visited := {}
	for p in pts:
		visited[p] = true
	for k in STOPS:
		for sp2 in STOPS[k]:
			var v: Vector2 = sp2
			if not visited.has(v):
				o.draw_rect(Rect2(v - Vector2(1, 1), Vector2(3, 3)), Color(0.15, 0.1, 0.08, 0.6))
				o.draw_rect(Rect2(v, Vector2(1, 1)), Color(0.85, 0.78, 0.6, 0.6))
	for i in range(1, pts.size() - 1):
		_stud(o, pts[i])
	# the roads you could take now
	if choose_mode:
		var cur: Vector2 = pts.back()
		for op in options:
			var dst := _option_point(str(op))
			_route_seg(o, cur, dst, false)
			var pulse := 0.5 + 0.5 * sin(t * 4.0)
			var rc: Color = REGION_COL.get(str(op), GOLD)
			var big := 7.0 + pulse * 2.0 + (2.0 if hover == str(op) or sel == str(op) else 0.0)
			o.draw_arc(dst, big, 0, TAU, 20, Color(rc.r, rc.g, rc.b, 0.85), 1.0)
			o.draw_arc(dst, big + 3.0, 0, TAU, 20, Color(rc.r, rc.g, rc.b, 0.35 * pulse), 1.0)
			_stud(o, dst, rc)
	# where the column is: the eagle standard, bobbing
	_standard(o, pts.back())
	# birds and clouds over everything
	for b in birds:
		var bp := Vector2(float(b[0]) - 20.0, float(b[1]) + sin(t * 0.8 + float(b[3])) * 4.0).round()
		var flap := int(t * 6.0 + float(b[3])) % 2
		var bc := Color(0.12, 0.1, 0.12)
		o.draw_rect(Rect2(bp, Vector2(1, 1)), bc)
		o.draw_rect(Rect2(bp + Vector2(-2, -1 + flap), Vector2(2, 1)), bc)
		o.draw_rect(Rect2(bp + Vector2(1, -1 + flap), Vector2(2, 1)), bc)
	for c in clouds:
		_cloud(o, Vector2(float(c[0]) - 60.0, float(c[1])), float(c[3]), int(c[4]), Color(1, 1, 1, 0.85))
	# realm names
	for k in LABEL_AT:
		_plate(o, LABEL_AT[k], Game.L(str(Game.REGIONS[k]["name"])), REGION_COL[k])
	_plate(o, ALTAR + Vector2(0, -26), Game.L("The Great Altar"), GOLD)


func _cloud(o: Control, p: Vector2, sc: float, idx: int, col: Color) -> void:
	var tx: Texture2D = cloud_tex[idx % cloud_tex.size()] if not cloud_tex.is_empty() else null
	if tx != null:
		o.draw_texture(tx, (p - tx.get_size() * 0.5).round(), col)


func _ship(o: Control, p: Vector2, dir: float, sail) -> void:
	var bob := roundf(sin(t * 3.0 + p.x) * 0.5)
	p.y += bob
	var tx: Texture2D = ship_tex.get(str(sail))
	if tx != null:
		var sz := tx.get_size()
		var r := Rect2((p - Vector2(sz.x * 0.5, sz.y - 2)).round(), sz)
		if dir < 0.0:
			r.position.x += sz.x
			r.size.x = -sz.x
		o.draw_texture_rect(tx, r, false)
	for k in 5:
		o.draw_rect(Rect2(p + Vector2(-dir * (10 + k * 2), 1 + (k % 2)), Vector2(2, 1)), Color(0.85, 0.95, 0.95, 0.6 - k * 0.1))


func _altar(o: Control) -> void:
	var a := ALTAR
	for i in 3:
		o.draw_rect(Rect2(a + Vector2(-8 + i * 2, -2 - i * 2), Vector2(16 - i * 4, 2)), Color(0.78, 0.74, 0.64) if i % 2 == 0 else Color(0.66, 0.62, 0.54))
	o.draw_rect(Rect2(a + Vector2(-3, -9), Vector2(6, 3)), Color(0.5, 0.42, 0.32))
	for k in 5:
		var fx := float(k - 2)
		var fh := 3.0 + 2.0 * absf(sin(t * 10.0 + k * 1.7)) - absf(fx) * 0.8
		o.draw_rect(Rect2(a + Vector2(fx, -9 - fh), Vector2(1, fh)), Color(1, 0.85, 0.4) if absf(fx) < 1.5 else Color(1, 0.5, 0.15))
	for k in 9:
		var ph := fmod(t * 0.6 + k * 0.11, 1.0)
		var sp := a + Vector2(sin(ph * 5.0 + k) * 2.0 + ph * 10.0, -14.0 - ph * 40.0)
		var sz := 2.0 + ph * 5.0
		o.draw_rect(Rect2((sp - Vector2(sz, sz) * 0.5).round(), Vector2(sz, sz).round()), Color(0.55, 0.52, 0.5, 0.45 * (1.0 - ph)))


func _fort(o: Control, p: Vector2) -> void:
	o.draw_rect(Rect2(p + Vector2(-7, -6), Vector2(14, 6)), Color(0.55, 0.5, 0.44))
	o.draw_rect(Rect2(p + Vector2(-7, -6), Vector2(14, 1)), Color(0.75, 0.7, 0.62))
	for k in range(-7, 8, 3):
		o.draw_rect(Rect2(p + Vector2(k, -8), Vector2(2, 2)), Color(0.55, 0.5, 0.44))
	o.draw_rect(Rect2(p + Vector2(-2, -4), Vector2(4, 4)), Color(0.15, 0.1, 0.08))
	o.draw_rect(Rect2(p + Vector2(0, -14), Vector2(1, 6)), Color(0.3, 0.2, 0.12))
	o.draw_rect(Rect2(p + Vector2(1, -14), Vector2(4, 3)), Color(0.75, 0.2, 0.15))
	_plate(o, p + Vector2(0, 12), Game.L("The fort"), Color(0.9, 0.85, 0.75))


func _route_seg(o: Control, a: Vector2, b: Vector2, done: bool) -> void:
	## a road between two stops, bowed slightly; dashed where it crosses water
	var n := int(a.distance_to(b) / 2.0) + 1
	var mid := (a + b) * 0.5 + (b - a).orthogonal().normalized() * a.distance_to(b) * 0.12
	var march := t * 8.0
	for i in n:
		var u := float(i) / float(n)
		var p := a.lerp(mid, u).lerp(mid.lerp(b, u), u)
		var water := not _is_land(p)
		var k := int(i + (march if not done else march * 0.5)) % 4
		if done:
			if water and k >= 2:
				continue
			o.draw_rect(Rect2(p.round() - Vector2(0.5, 0.5), Vector2(2, 2)), INK)
			o.draw_rect(Rect2(p.round(), Vector2(1, 1)), Color(0.55, 0.8, 0.95) if water else GOLD)
		else:
			if k >= 2:
				continue
			o.draw_rect(Rect2(p.round(), Vector2(1, 1)), Color(1, 1, 1, 0.85))


func _stud(o: Control, p: Vector2, col := Color(0.82, 0.62, 0.3)) -> void:
	o.draw_rect(Rect2(p - Vector2(2, 2), Vector2(5, 5)), INK)
	o.draw_rect(Rect2(p - Vector2(1, 1), Vector2(3, 3)), col)
	o.draw_rect(Rect2(p - Vector2(1, 1), Vector2(1, 1)), col.lightened(0.4))


func _standard(o: Control, p: Vector2) -> void:
	var bob := roundf(sin(t * 3.0) * 1.0)
	var q := p + Vector2(0, bob)
	o.draw_rect(Rect2(q + Vector2(0, -16), Vector2(1, 16)), Color(0.3, 0.2, 0.12))
	o.draw_rect(Rect2(q + Vector2(-3, -15), Vector2(7, 1)), Color(0.85, 0.65, 0.25))
	for yy in 6:
		var sh := roundf(sin(t * 4.0 - yy * 0.6) * 0.8)
		o.draw_rect(Rect2(q + Vector2(-2 + sh, -14 + yy), Vector2(5, 1)), Color(0.72, 0.15, 0.12) if yy < 5 else Color(0.9, 0.7, 0.3))
	o.draw_rect(Rect2(q + Vector2(-1, -19), Vector2(3, 3)), GOLD)
	o.draw_rect(Rect2(q + Vector2(-2, -18), Vector2(1, 1)), GOLD)
	o.draw_rect(Rect2(q + Vector2(2, -18), Vector2(1, 1)), GOLD)
	o.draw_arc(p, 5.0 + fmod(t * 6.0, 6.0), 0, TAU, 16, Color(1, 0.9, 0.6, 0.6 * (1.0 - fmod(t * 6.0, 6.0) / 6.0)), 1.0)


func _plate(o: CanvasItem, center: Vector2, text: String, col: Color) -> void:
	## a name on the red swallow-tailed banner the menus use for their titles
	var w: float = Game.font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x + 12.0
	var hgt: float = Game.font.get_height(8) + 4.0
	var r := Rect2((center - Vector2(w * 0.5, hgt * 0.5)).round(), Vector2(w, hgt))
	var sb: StyleBox = Game.theme.get_stylebox("panel", "TitlePlate") if Game.theme.has_stylebox("panel", "TitlePlate") else null
	if sb != null:
		o.draw_style_box(sb, r)
	else:
		o.draw_rect(r, Color(0.5, 0.12, 0.1, 0.9))
	o.draw_string(Game.font, r.position + Vector2(6, Game.font.get_ascent(8) + 2.0), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1.0, 0.93, 0.75))


# ------------------------------------------------------------------ screen-space frame, HUD
func _draw() -> void:
	# the same gold-meander frame as every window in the game
	var sb: StyleBox = Game.theme.get_stylebox("panel", "PanelContainer")
	if sb != null:
		draw_style_box(sb, Rect2(0, 0, 480, 270))
	else:
		draw_rect(Rect2(0, 0, 480, 270), Color(0.16, 0.09, 0.1))
	draw_rect(VIEW.grow(1), INK, false, 1.0)
	# title on a red banner, day and leg on the right
	_plate(self, Vector2(14, 12) + Vector2(Game.font.get_string_size(Game.L("The four realms"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x * 0.5 + 6.0, 8.0), Game.L("The four realms"), GOLD)
	var info := Game.L("Day %d   Leg %d of %d") % [Game.day, Game.leg + 1, Game.TOTAL_LEGS]
	var iw: float = Game.font.get_string_size(info, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
	draw_string(Game.font, Vector2(466 - iw, 25), info, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.89, 0.66, 0.29))
	# hint bar along the foot of the chart
	var hint := Game.L("Choose the next road: click a glowing stop") if choose_mode else Game.L("solid: marched   dashed: by sea   [WASD / drag] look   [M / Esc] close")
	draw_rect(Rect2(VIEW.position.x, VIEW.end.y + 2, VIEW.size.x, 12), Color(0.08, 0.05, 0.05))
	draw_string(Game.font, Vector2(VIEW.position.x + 4, VIEW.end.y + 11), hint, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.84, 0.78, 0.63))
	# compass rose in the corner of the chart
	var cp := VIEW.position + Vector2(VIEW.size.x - 18, 16)
	draw_circle(cp, 9.0, Color(0.08, 0.06, 0.06, 0.8))
	draw_arc(cp, 9.0, 0, TAU, 20, Color(0.89, 0.66, 0.29), 1.0)
	draw_colored_polygon(PackedVector2Array([cp + Vector2(0, -8), cp + Vector2(2, 0), cp + Vector2(-2, 0)]), Color(0.85, 0.2, 0.15))
	draw_colored_polygon(PackedVector2Array([cp + Vector2(0, 8), cp + Vector2(2, 0), cp + Vector2(-2, 0)]), Color(0.9, 0.85, 0.75))


# ------------------------------------------------------------------ input
func _gui_input(event: InputEvent) -> void:
	if card != null:
		return
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			if choose_mode and hover != "":
				_open_card(hover)
				return
			dragging = true
			drag_from = event.position
		elif event.button_index == MOUSE_BUTTON_LEFT and not event.pressed:
			dragging = false
		elif event.button_index == MOUSE_BUTTON_RIGHT and event.pressed and not choose_mode:
			_close()
	elif event is InputEventMouseMotion and dragging:
		pan_target = _clamp_pan(pan_target - event.relative)
		pan = pan_target
	accept_event()


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or not event.pressed or event.echo:
		return
	if card != null:
		if event.keycode == KEY_ESCAPE:
			_close_card()
		get_viewport().set_input_as_handled()
		return
	if event.keycode == KEY_ESCAPE or event.keycode == KEY_M:
		_close()
	elif choose_mode and (event.keycode == KEY_1 or event.keycode == KEY_2) and options.size() >= event.keycode - KEY_0:
		_open_card(str(options[event.keycode - KEY_1]))
	get_viewport().set_input_as_handled()


func _close() -> void:
	Game.sfx("ui_close", -5.0)
	closed.emit()
	queue_free()


# ------------------------------------------------------------------ a road's card
func _open_card(o: String) -> void:
	sel = o
	Game.sfx("ui_press", -4.0)
	pan_target = _clamp_pan(_option_point(o) - VIEW.size * 0.5)
	card = PanelContainer.new()
	card.theme = Game.theme
	add_child(card)
	var vb := VBoxContainer.new()
	card.add_child(vb)
	if o == "altar":
		vb.add_child(Game.label(Game.L("The Great Altar"), GOLD))
		vb.add_child(Game.label(Game.L("There is only one road left. Torches on the hill ahead: the Great Altar, and the Emperor's auditors."), null, 220))
		vb.add_child(Game.button(Game.L("Go up to the Great Altar"), _pick.bind(o)))
	else:
		var rg: Dictionary = Game.REGIONS[o]
		vb.add_child(Game.label(Game.L(str(rg["name"])), REGION_COL[o]))
		vb.add_child(Game.label(Game.L(str(rg["blurb"])), null, 220))
		vb.add_child(Game.label(Game.L("Altars here answer to %s.") % Game.L(str(rg["values_text"])), Color(0.62, 0.57, 0.5), 220))
		var est := 0
		var fb: Dictionary = Game.make_battle(o, Game.leg + 1)
		for g in fb["main"]:
			est += int(g[1])
		vb.add_child(Game.label(Game.L("Scouts: about %d hold that road, not counting what hides. Recruits there: %d.") % [est, 22 if o == "south" else 12], Color(0.62, 0.57, 0.5), 220))
		vb.add_child(Game.button(Game.L("March  (%s)") % Game.L(str(rg["road"])), _pick.bind(o)))
	vb.add_child(Game.button(Game.L("Back"), _close_card))
	card.position = Vector2(240 - 120, 60)
	_place_card.call_deferred()
	Game.enable_keys.call_deferred(card)


func _place_card() -> void:
	if card != null:
		card.position = ((Vector2(480, 270) - card.size) * 0.5).round() + Vector2(0, 10)


func _close_card() -> void:
	if card != null:
		card.queue_free()
		card = null
	sel = ""


func _pick(o: String) -> void:
	Game.sfx("horn", -6.0)
	chosen.emit(o)
	queue_free()
