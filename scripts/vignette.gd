extends Control
## A small animated pixel painting that heads a window: the camp fire flickers, banners stir,
## snow falls on the oath stone. The picture is 224x56; the control may be shorter (it crops to the middle).

const FX := {
	"camp": {"fire": [[126, 44, 1.0]], "smoke": [[126, 34]], "stars": 1},
	"muster": {"banners": [[54, 10, 13, 14], [144, 10, 13, 14]], "motes": "#ffd9a0"},
	"pack": {"motes": "#f2d098", "dust": 1},
	"ledger": {"candle": [[23, 23]], "motes": "#ffcf8a"},
	"map": {"glint": [[112, 28]]},
	"stall": {"lantern": [[172, 22]], "motes": "#ffd9a0"},
	"altar": {"fire": [[112, 28, 1.2]], "smoke": [[112, 18]], "water": [[0, 38, 224, 56]]},
	"brief": {"embers": 1, "smoke": [[30, 20], [190, 24]]},
	"village": {"smoke": [[33, 22], [195, 20]], "motes": "#ffe0b0"},
	"seed": {"fireflies": "#d8f07a"},
	"oath": {"snow": 1, "runes": [[112, 12, 28]]},
	"envoy": {"fire": [[123, 38, 0.8, "violet"]], "motes": "#c890ff"},
	"deserters": {"lantern": [[188, 24]]},
	"refugees": {"dust": 1, "motes": "#ffd0a0"},
	"cross": {"stars": 1, "torches": [[200, 28], [206, 28], [212, 28]]},
	"omen": {"fire": [[112, 34, 1.4]], "smoke": [[112, 24]], "embers": 1},
}

const IW := 224
const IH := 56
var key := ""
var tex: Texture2D
var t := 0.0
var parts: Array = []
var glow: Node2D


static func load_tex(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path)
	if FileAccess.file_exists(path):
		var img := Image.load_from_file(ProjectSettings.globalize_path(path))
		if img != null:
			return ImageTexture.create_from_image(img)
	return null


func setup(k: String) -> void:
	key = k
	tex = load_tex("res://assets/ui/vignettes/v_%s.png" % k)
	custom_minimum_size = Vector2(IW + 4, IH + 4)
	clip_contents = true
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	glow = Node2D.new()
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	glow.material = m
	add_child(glow)
	glow.draw.connect(_draw_glow)


func _fx() -> Dictionary:
	return FX.get(key, {})


func _origin() -> Vector2:
	## where the 224x56 picture's top-left sits inside this control (centred, cropped vertically)
	return Vector2(floor((size.x - IW) * 0.5), floor((size.y - IH) * 0.5))


func _process(delta: float) -> void:
	t += delta
	var f := _fx()
	var o := _origin()
	# spawn particles in picture coordinates
	if f.has("smoke"):
		for s in f["smoke"]:
			if randf() < delta * 5.0:
				parts.append({"k": "smoke", "p": Vector2(s[0] + randf_range(-2, 2), s[1]), "v": Vector2(randf_range(1, 4), -randf_range(5, 9)), "life": 2.6, "max": 2.6})
	if f.has("fire"):
		for s in f["fire"]:
			if randf() < delta * 14.0:
				parts.append({"k": "ember", "p": Vector2(s[0] + randf_range(-3, 3), s[1] - 4), "v": Vector2(randf_range(-4, 4), -randf_range(10, 22)), "life": 1.0, "max": 1.0, "c": Color(0.85, 0.55, 1.0) if s.size() > 3 else Color(1.0, 0.7, 0.3)})
	if f.has("embers") and randf() < delta * 10.0:
		parts.append({"k": "ember", "p": Vector2(randf() * IW, IH + 2), "v": Vector2(randf_range(-3, 6), -randf_range(8, 18)), "life": 3.0, "max": 3.0, "c": Color(1.0, 0.55, 0.25)})
	if f.has("snow") and randf() < delta * 30.0:
		parts.append({"k": "snow", "p": Vector2(randf() * IW, -2), "v": Vector2(randf_range(-3, 1), randf_range(6, 12)), "life": 8.0, "max": 8.0})
	if f.has("motes") and randf() < delta * 6.0:
		parts.append({"k": "mote", "p": Vector2(randf() * IW, randf_range(10, IH - 6)), "v": Vector2(randf_range(-2, 2), -randf_range(0.5, 2)), "life": 3.0, "max": 3.0, "c": Color(str(f["motes"]))})
	if f.has("fireflies") and randf() < delta * 5.0:
		parts.append({"k": "firefly", "p": Vector2(randf() * IW, randf_range(20, IH - 6)), "v": Vector2(randf_range(-3, 3), randf_range(-2, 2)), "life": 3.5, "max": 3.5, "c": Color(str(f["fireflies"])), "ph": randf() * TAU})
	if f.has("dust") and randf() < delta * 8.0:
		parts.append({"k": "dust", "p": Vector2(-2, randf_range(IH - 18, IH - 4)), "v": Vector2(randf_range(8, 16), -randf_range(0, 2)), "life": 4.0, "max": 4.0})
	for q in parts:
		q["life"] = float(q["life"]) - delta
		q["p"] = Vector2(q["p"]) + Vector2(q["v"]) * delta
		if q["k"] == "firefly":
			q["p"] = Vector2(q["p"]) + Vector2(sin(t * 2.0 + float(q["ph"])), cos(t * 1.6 + float(q["ph"]))) * delta * 6.0
	parts = parts.filter(func(q): return float(q["life"]) > 0.0)
	queue_redraw()
	glow.queue_redraw()


func _draw() -> void:
	var o := _origin()
	draw_rect(Rect2(o - Vector2(2, 2), Vector2(IW + 4, IH + 4)), Color(0.08, 0.04, 0.05))
	if tex != null:
		draw_texture(tex, o)
	var f := _fx()
	# twinkling stars: a deterministic scatter of bright pixels in the sky
	if f.has("stars"):
		for i in 14:
			var h := hash(i * 92821 + key.length())
			var sp := o + Vector2(h % IW, (h / 251) % 26)
			if sin(t * (1.5 + (h % 7) * 0.4) + i) > 0.55:
				draw_rect(Rect2(sp, Vector2(1, 1)), Color(1, 1, 1, 0.9))
	# banners stirring (redraw the cloth over the static one, shifted per row)
	if f.has("banners"):
		for b in f["banners"]:
			for yy in int(b[3]):
				var sh := roundf(sin(t * 3.0 - yy * 0.5) * (yy / float(b[3])) * 1.5)
				draw_rect(Rect2(o + Vector2(b[0] + sh, b[1] + yy), Vector2(b[2], 1)), Color(0.56, 0.14, 0.13).darkened(0.12 * (0.5 + 0.5 * sin(t * 3.0 - yy * 0.5))))
	# fires: a flickering column of pixels
	if f.has("fire"):
		for s in f["fire"]:
			var sc: float = float(s[2])
			var violet: bool = s.size() > 3
			for k in 9:
				var fx := float(k - 4)
				var fh: float = (7.0 + 5.0 * absf(sin(t * 12.0 + k * 1.9)) - absf(fx) * 1.4) * sc
				if fh <= 0.0:
					continue
				var hot := absf(fx) < 2.0
				var c := (Color(0.95, 0.8, 1.0) if hot else Color(0.7, 0.35, 1.0)) if violet else (Color(1.0, 0.88, 0.45) if hot else Color(0.98, 0.42, 0.14))
				draw_rect(Rect2(o + Vector2(s[0] + fx, s[1] - fh), Vector2(1, fh)), c)
	if f.has("candle"):
		for s in f["candle"]:
			var ch := 3.0 + sin(t * 17.0) * 1.0
			draw_rect(Rect2(o + Vector2(s[0], s[1] - ch), Vector2(1, ch)), Color(1, 0.85, 0.45))
	for lt in f.get("lantern", []) + f.get("torches", []):
		draw_rect(Rect2(o + Vector2(lt[0] - 1, lt[1] - 1), Vector2(2, 2)), Color(1, 0.8, 0.4, 0.75 + 0.25 * sin(t * 9.0 + lt[0])))
	if f.has("runes"):
		for r in f["runes"]:
			var a: float = 0.5 + 0.5 * sin(t * 2.2)
			for yy in range(int(r[1]), int(r[1]) + int(r[2]), 6):
				draw_rect(Rect2(o + Vector2(r[0] - 2, yy), Vector2(5, 2)), Color(0.6, 0.95, 1.0, 0.35 + 0.65 * a))
	if f.has("water"):
		for i in 10:
			var h2 := hash(i * 7717)
			var wp := o + Vector2(h2 % IW, 40 + (h2 / 97) % 15)
			if sin(t * 3.0 + i * 1.3) > 0.6:
				draw_rect(Rect2(wp, Vector2(2, 1)), Color(0.75, 0.9, 1.0, 0.9))
	if f.has("glint"):
		for g in f["glint"]:
			var a2 := 0.5 + 0.5 * sin(t * 4.0)
			draw_rect(Rect2(o + Vector2(g[0] - 2, g[1]), Vector2(5, 1)), Color(1, 0.95, 0.6, a2))
			draw_rect(Rect2(o + Vector2(g[0], g[1] - 2), Vector2(1, 5)), Color(1, 0.95, 0.6, a2))
	for q in parts:
		var al: float = clamp(float(q["life"]) / float(q["max"]) * 1.5, 0.0, 1.0)
		var pp: Vector2 = (o + Vector2(q["p"])).round()
		match str(q["k"]):
			"smoke":
				var k2: float = 1.0 - float(q["life"]) / float(q["max"])
				draw_rect(Rect2(pp, Vector2(2, 2) + Vector2(2, 2) * k2), Color(0.55, 0.5, 0.55, 0.35 * al))
			"ember":
				draw_rect(Rect2(pp, Vector2(1, 1)), Color(q["c"].r, q["c"].g, q["c"].b, al))
			"snow":
				draw_rect(Rect2(pp, Vector2(1, 1)), Color(1, 1, 1, 0.9))
			"mote", "firefly":
				var tw: float = 0.5 + 0.5 * sin(t * 5.0 + pp.x)
				draw_rect(Rect2(pp, Vector2(1, 1)), Color(q["c"].r, q["c"].g, q["c"].b, al * tw))
			"dust":
				draw_rect(Rect2(pp, Vector2(2, 1)), Color(0.85, 0.72, 0.55, 0.35 * al))
	# gold frame around the painting
	draw_rect(Rect2(o - Vector2(1, 1), Vector2(IW + 2, IH + 2)), Color(0.89, 0.66, 0.29), false, 1.0)


func _draw_glow() -> void:
	var o := _origin()
	var f := _fx()
	var pulse := 0.85 + 0.15 * sin(t * 9.0) + 0.05 * sin(t * 23.0)
	for s in f.get("fire", []):
		var c := Color(0.6, 0.25, 0.9) if s.size() > 3 else Color(0.95, 0.45, 0.15)
		var r: float = 16.0 * float(s[2]) * pulse
		glow.draw_circle(o + Vector2(s[0], s[1] - 4), r, Color(c.r, c.g, c.b, 0.10))
		glow.draw_circle(o + Vector2(s[0], s[1] - 4), r * 0.55, Color(c.r, c.g, c.b, 0.14))
	for s in f.get("candle", []) + f.get("lantern", []):
		glow.draw_circle(o + Vector2(s[0], s[1]), 12.0 * pulse, Color(1.0, 0.6, 0.25, 0.10))
		glow.draw_circle(o + Vector2(s[0], s[1]), 5.0 * pulse, Color(1.0, 0.7, 0.3, 0.15))
	for r in f.get("runes", []):
		glow.draw_circle(o + Vector2(r[0], r[1] + r[2] * 0.5), 16.0, Color(0.3, 0.8, 1.0, 0.08 + 0.06 * sin(t * 2.2)))
	if key == "omen":
		glow.draw_circle(o + Vector2(112, 15), 14.0 + 2.0 * sin(t * 2.0), Color(1.0, 0.75, 0.3, 0.12))
