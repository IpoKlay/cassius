extends Node
## The march, Hades-style: a real 3D world seen through a tilted orthographic camera and rendered
## at 480x270 so every mesh comes out as pixels. Free 8-way movement; every stop is a decision.

const U := 1.0                  # leg data (Game.leg_state) is in road pixels, and so is the 2D world
const GROUND_Y := 176.0          # where feet stand (top of the grass on the stone ledge)
const WATER_Y := 204.0           # foot of the ledge; below it the river mirrors the world (Kingdom-style)
const SKY := {"south": [Color8(88, 180, 192), Color8(207, 230, 200)], "west": [Color8(106, 158, 200), Color8(214, 226, 208)],
	"north": [Color8(122, 144, 170), Color8(223, 228, 232)], "east": [Color8(74, 58, 120), Color8(232, 180, 168)]}
const WATER := {"south": Vector3(0.22, 0.52, 0.5), "west": Vector3(0.2, 0.3, 0.28), "north": Vector3(0.24, 0.32, 0.4), "east": Vector3(0.26, 0.2, 0.36)}
const WALK := 70.0               # pixels per second
const GALLOP := 124.0
const GOLDC := Color(0.96, 0.8, 0.42)
const DIM := Color(0.62, 0.57, 0.5)
const BAD := Color(0.95, 0.45, 0.38)
const GOOD := Color(0.6, 0.85, 0.55)
const WOODC := Color(0.43, 0.3, 0.18)
const WOOD_D := Color(0.27, 0.18, 0.12)
const STONE := Color(0.59, 0.57, 0.55)
const STONE_D := Color(0.36, 0.35, 0.36)
const REDC := Color(0.67, 0.16, 0.12)
const CREAM := Color(0.68, 0.6, 0.44)
const TAN := Color(0.59, 0.46, 0.33)

var keys_label: Label
var art_hint := ""
const VIGNETTE = preload("res://scripts/vignette.gd")
const UI_FX = preload("res://scripts/ui_fx.gd")
const WORLD_MAP = preload("res://scripts/world_map.gd")
var PAL := {
	"south": {"grass": Color8(84, 92, 44), "grass_hi": Color8(150, 140, 62), "dirt": Color8(104, 80, 60), "leaf": Color8(52, 66, 36), "leaf_hi": Color8(140, 120, 56), "trunk": Color8(62, 44, 36)},
	"west": {"grass": Color8(56, 104, 50), "grass_hi": Color8(130, 176, 80), "dirt": Color8(92, 82, 52), "leaf": Color8(30, 76, 44), "leaf_hi": Color8(96, 150, 74), "trunk": Color8(52, 42, 30)},
	"north": {"grass": Color8(196, 212, 230), "grass_hi": Color8(240, 246, 252), "dirt": Color8(104, 116, 142), "leaf": Color8(48, 76, 96), "leaf_hi": Color8(214, 228, 240), "trunk": Color8(50, 46, 56)},
	"east": {"grass": Color8(60, 50, 84), "grass_hi": Color8(170, 140, 196), "dirt": Color8(88, 72, 100), "leaf": Color8(64, 36, 90), "leaf_hi": Color8(170, 110, 180), "trunk": Color8(42, 28, 52)},
}

var st: Dictionary
var region := "south"
var length := 80.0              # world units
var pos := Vector2.ZERO
var facing := 1
var anim_t := 0.0
var busy := false
var near = null
var wall_toast_cd := 0.0

var world: Node2D                # everything at road depth (parallax 1.0)
var cam_x := 0.0                 # left edge of the screen, in road pixels
var layers: Array = []           # [Sprite2D, parallax factor]
var sky_mat: ShaderMaterial
var water_mat: ShaderMaterial
var fog_mat: ShaderMaterial
var tint_mod: CanvasModulate
var torch: PointLight2D
var player: Sprite2D
var followers: Array = []
var anims: Array = []
var poi_nodes: Array = []
var fire_lights: Array = []
var priest_spr: Sprite2D = null
var wfx: Node2D                  # weather, embers, hoof dust (world space)
var fg: Node2D                   # dark foreground grass in front of the column
var birds: Array = []
var parts: Array = []
var fg_bits: Array = []
var night_k := 0.0
var rays: Node2D
var ray_k := 0.0
var rain := false
var tufts: Array = []
var falls: Array = []
var hud_box: Control
var idle_t := 0.0
var show_t := 3.0
var keys_t := 0.0
var ui: CanvasLayer
var menu_layer: CanvasLayer
var fx_layer: CanvasLayer
var menu_root: Control = null
var menu_closable := true
var hud: Dictionary = {}
var prompt: Label
var toast: Label
var flash: ColorRect
var ledger_note: Label
var leg_title: Label
var last_denarii := -1
var last_grain := -1
var hoof_t := 0.0


func _ready() -> void:
	st = Game.leg_state
	region = Game.region
	length = float(st["length"]) / U
	pos = Vector2(float(st["x"]) / U, GROUND_Y)
	Game.music("ambient")
	_build_world()
	_build_overlays()
	_build_ui()
	Game.changed.connect(_refresh_hud)
	Game.ledger_written.connect(_on_ledger)
	_refresh_hud()
	_apply_time()
	if Game.flags.has("toast"):
		say(str(Game.flags["toast"]), 5.0)
		Game.flags.erase("toast")
	if pos.x < 90.0 and not st["won"]:
		_show_leg_title()
	if Game.leg == 0 and pos.x < 90.0 and not st["won"]:
		say(Game.L("The north road. Ride east. Make camp at the standard."), 5.0)


# ------------------------------------------------------------------ 2D kit (side view, Kingdom-style)
func _tex(path: String) -> Texture2D:
	return Game.load_tex("res://assets/%s.png" % path)


func _sprite(path: String, hframes: int, at: Vector2, parent: Node = null) -> Sprite2D:
	## a pixel sprite standing on the road: feet on `at`
	var s := Sprite2D.new()
	s.texture = _tex(path)
	s.hframes = hframes
	s.centered = false
	if s.texture != null:
		s.offset = Vector2(-s.texture.get_width() / float(hframes) / 2.0, -s.texture.get_height())
	s.position = at.round()
	(parent if parent != null else world).add_child(s)
	return s


func _light(at: Vector2, scale_: float, energy: float, col := Color(1.0, 0.62, 0.3), parent: Node = null) -> PointLight2D:
	var l := PointLight2D.new()
	l.texture = _tex("props/glow")
	l.texture_scale = scale_
	l.energy = energy
	l.color = col
	l.position = at
	l.set_meta("base", energy)
	(parent if parent != null else world).add_child(l)
	return l


func _fire(at: Vector2, size_ := 1.0) -> void:
	anims.append([_sprite("props/campfire", 4, at), 4, 9.0, 0])
	fire_lights.append(_light(at + Vector2(0, -8), 1.6 * size_, 1.0))
	parts_src.append(at + Vector2(0, -10))


var parts_src: Array = []        # places embers rise from


func _tile_layer(path: String, y: float, factor: float, z: int, haze := 0.0, drift := 0.0) -> void:
	## a horizontally repeating backdrop strip that scrolls at `factor` of the road speed
	var tx := _tex(path)
	if tx == null:
		return
	var s := Sprite2D.new()
	s.texture = tx
	s.centered = false
	s.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	s.region_enabled = true
	s.region_rect = Rect2(0, 0, 480.0 + tx.get_width() * 2.0, tx.get_height())
	s.position = Vector2(0, y)
	s.z_index = z
	var hm: ShaderMaterial = null
	if haze > 0.0:
		hm = ShaderMaterial.new()
		hm.shader = load("res://shaders/haze.gdshader")
		hm.set_shader_parameter("amount", haze)
		s.material = hm
	add_child(s)
	layers.append([s, factor, hm, haze, float(tx.get_width()), drift])


func _near_poi(x: float, margin: float) -> bool:
	for p in st["pois"]:
		if absf(float(p["x"]) / U - x) < margin:
			return true
	return false


# ------------------------------------------------------------------ construction
func _build_world() -> void:
	var pal: Dictionary = PAL[region]
	var rt: Color = Game.REGIONS[region]["tint"]
	# sky lives on its own layer so the day/night tint does not darken it twice
	var sky_layer := CanvasLayer.new()
	sky_layer.layer = -1
	add_child(sky_layer)
	var sky := ColorRect.new()
	sky.position = Vector2(0, 0)
	sky.size = Vector2(480, WATER_Y)
	sky_mat = ShaderMaterial.new()
	sky_mat.shader = load("res://shaders/sky.gdshader")
	sky.material = sky_mat
	sky_layer.add_child(sky)
	# parallax backdrops, far to near (painted per region: clouds, distant ridge, the range, the near wood)
	_tile_layer("road/%s_clouds" % region, 4, 0.04, -50, 0.0, 2.5)
	_tile_layer("road/%s_ridge" % region, GROUND_Y - 120.0, 0.08, -45, 0.5)
	_tile_layer("road/%s_mountains" % region, GROUND_Y - 142.0, 0.15, -40, 0.25)
	_tile_layer("road/%s_mid" % region, GROUND_Y - 148.0, 0.45, -20, 0.1)
	_tile_layer("road/%s_ledge" % region, GROUND_Y - 6.0, 1.0, -3)
	rays = Node2D.new()
	rays.z_index = -22
	add_child(rays)
	rays.draw.connect(_draw_rays)
	# the road world
	world = Node2D.new()
	add_child(world)
	tint_mod = CanvasModulate.new()
	add_child(tint_mod)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash("%s-%d" % [region, Game.leg])
	rain = (region == "west" and rng.randf() < 0.5) or (region == "south" and rng.randf() < 0.25) or (region == "east" and rng.randf() < 0.3)
	# trees behind the road, thinned out around stops so they stay readable
	var x := -60.0
	while x < length + 80.0:
		x += rng.randf_range(40.0, 110.0)
		if _near_poi(x, 70.0):
			continue
		var tr := _sprite("road/%s_tree%d" % [region, rng.randi() % 4], 1, Vector2(x, GROUND_Y + 1.0))
		tr.z_index = -4
		tr.flip_h = rng.randf() < 0.5
	# Roman things left along the road: broken columns, milestones, amphorae, a statue, a fallen capital
	var dx := 0.0
	while dx < length:
		dx += rng.randf_range(90.0, 210.0)
		if _near_poi(dx, 60.0):
			continue
		var dk: int = [0, 1, 2, 4, 5, 1][rng.randi() % 6]
		var dc := _sprite("road/r_deco%d" % dk, 1, Vector2(dx, GROUND_Y + 1.0))
		dc.z_index = -2
	# bright grass clumps hanging over the ledge face, and plants on the verge in front of the column
	var px := -10.0
	while px < length + 20.0:
		px += rng.randf_range(40.0, 120.0)
		var cl := _sprite("road/%s_plant3" % region, 1, Vector2(px, GROUND_Y + 14.0))
		cl.z_index = -2
	px = -10.0
	while px < length + 20.0:
		px += rng.randf_range(50.0, 140.0)
		var kind := rng.randi() % 3
		var pl := _sprite("road/%s_plant%d" % [region, kind], 1, Vector2(px, GROUND_Y + 5.0))
		pl.z_index = 6
		pl.flip_h = rng.randf() < 0.5
		if kind == 2:
			tufts.append(pl)
	# little streams spilling off the ledge into the river
	var fx2 := 80.0
	while fx2 < length:
		fx2 += rng.randf_range(220.0, 420.0)
		falls.append(fx2)
	for p in st["pois"]:
		_build_poi(p, pal)
	# the column: each one follows the one in front
	var defs := [["sprites/soldier0", 10, 4, 4, 6, 24.0], ["sprites/soldier1", 10, 4, 4, 6, 18.0], ["sprites/soldier2", 10, 4, 4, 6, 18.0],
		["sprites/ox", 10, 4, 4, 6, 26.0], ["sprites/cart", 5, 1, 1, 4, 33.0]]
	var back := 0.0
	for dd in defs:
		if dd[0] == "sprites/ox" and not Game.inventory.has("white_ox"):
			continue
		back += float(dd[5])
		var s := _sprite(str(dd[0]), int(dd[1]), Vector2(pos.x - back, GROUND_Y))
		s.z_index = 2
		followers.append({"spr": s, "idle_n": dd[3], "walk_at": dd[2], "walk_n": dd[4], "gap": float(dd[5]), "t": randf() * 3.0, "x": pos.x - back})
	player = _sprite("sprites/cassius", 12, pos)
	player.z_index = 3
	torch = _light(Vector2(6, -22), 2.4, 0.0, Color(1.0, 0.72, 0.42), player)
	# weather, embers and dust; and a dark band of foreground grass for depth
	wfx = Node2D.new()
	wfx.z_index = 8
	world.add_child(wfx)
	wfx.draw.connect(_draw_wfx)
	fg = Node2D.new()
	fg.z_index = 20
	add_child(fg)
	var fx := -40.0
	while fx < length * 1.35 + 600.0:
		fx += rng.randf_range(30.0, 110.0)
		fg_bits.append([fx, rng.randf_range(6, 16), rng.randi() % 3, rng.randf() * TAU])
	for i in 3:
		birds.append([randf() * 600.0, randf_range(40, 110), randf_range(14, 24), randf() * TAU])
	# the river: mirrors everything above the waterline
	var wl := CanvasLayer.new()
	wl.layer = 1
	add_child(wl)
	var water := ColorRect.new()
	water.position = Vector2(0, WATER_Y)
	water.size = Vector2(480, 270.0 - WATER_Y)
	water_mat = ShaderMaterial.new()
	water_mat.shader = load("res://shaders/water.gdshader")
	water_mat.set_shader_parameter("line_v", WATER_Y / 270.0)
	water_mat.set_shader_parameter("stretch", 1.0)
	water.material = water_mat
	water.mouse_filter = Control.MOUSE_FILTER_IGNORE
	wl.add_child(water)
	cam_x = clamp(pos.x - 200.0, 0.0, max(0.0, length - 480.0))


func _build_poi(p: Dictionary, pal: Dictionary) -> void:
	var x := float(p["x"]) / U
	var node := {"poi": p, "x": x, "top": GROUND_Y - 40.0}
	var g := GROUND_Y
	match p["type"]:
		"camp":
			var t1 := _sprite("road/r_tent", 1, Vector2(x - 46, g))
			t1.z_index = -1
			var t2 := _sprite("road/r_tent", 1, Vector2(x - 18, g - 3))
			t2.z_index = -2
			t2.modulate = Color(0.85, 0.85, 0.85)
			anims.append([_sprite("props/banner", 4, Vector2(x, g)), 4, 4.0, 0])
			_fire(Vector2(x + 30, g + 1))
			_sprite("road/r_deco3", 1, Vector2(x + 54, g + 1))
			node["top"] = g - 46.0
		"shop":
			var shp := _sprite("road/r_shop", 1, Vector2(x, g + 1))
			shp.z_index = -1
			anims.append([_sprite("sprites/merchant", 4, Vector2(x + 50, g)), 4, 3.0, 0])
			fire_lights.append(_light(Vector2(x, g - 40), 1.4, 0.9, Color(1.0, 0.78, 0.45)))
			node["top"] = g - 62.0
		"altar":
			var al := _sprite("road/r_altar", 1, Vector2(x, g + 1))
			al.z_index = -1
			anims.append([_sprite("props/campfire", 4, Vector2(x, g - 38)), 4, 9.0, 0])
			fire_lights.append(_light(Vector2(x, g - 44), 2.0, 1.1))
			parts_src.append(Vector2(x, g - 48))
			priest_spr = _sprite("sprites/priest", 12, Vector2(x + 40, g))
			anims.append([priest_spr, 4, 3.0, 0])
			node["top"] = g - 50.0
		"event":
			anims.append([_sprite("sprites/villager", 4, Vector2(x - 8, g)), 4, 3.0, 0])
			var v2 := _sprite("sprites/villager", 4, Vector2(x + 10, g))
			v2.flip_h = true
			v2.modulate = Color(0.85, 0.8, 0.9)
			anims.append([v2, 4, 2.6, 1])
			var cart := _sprite("sprites/cart", 5, Vector2(x + 40, g))
			cart.modulate = Color(0.8, 0.75, 0.7)
			node["top"] = g - 30.0
		"warning":
			var w := _sprite("road/r_hostile", 1, Vector2(x, g + 1))
			node["spr"] = w
			var barrier := Node2D.new()
			world.add_child(barrier)
			for k in 7:
				var stake := Line2D.new()
				stake.width = 2.0
				stake.default_color = WOOD_D if k % 2 else WOODC
				var bx := x + 34.0 + k * 5.0
				stake.points = PackedVector2Array([Vector2(bx - 6, g + 2), Vector2(bx + 4, g - 20)]) if k % 2 else PackedVector2Array([Vector2(bx + 6, g + 2), Vector2(bx - 4, g - 20)])
				barrier.add_child(stake)
			node["barrier"] = barrier
			if st["won"]:
				barrier.visible = false
				w.modulate = Color(0.45, 0.45, 0.45)
			node["top"] = g - 34.0
		"crossroads":
			_sprite("road/r_signpost", 1, Vector2(x, g + 1))
			_fire(Vector2(x - 28, g + 1), 1.2)
			node["top"] = g - 38.0
	poi_nodes.append(node)


func _build_overlays() -> void:
	var fl := CanvasLayer.new()
	fl.layer = 2
	add_child(fl)
	var fog := ColorRect.new()
	fog.size = Vector2(480, 270)
	fog.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fog_mat = ShaderMaterial.new()
	fog_mat.shader = load("res://shaders/fog.gdshader")
	fog.material = fog_mat
	fl.add_child(fog)
	# the "old fresco" grade: earthy limited palette, warm and a little faded, darker corners
	var gl := CanvasLayer.new()
	gl.layer = 3
	add_child(gl)
	var grade := ColorRect.new()
	grade.size = Vector2(480, 270)
	grade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var gm := ShaderMaterial.new()
	gm.shader = load("res://shaders/retro.gdshader")
	gm.set_shader_parameter("strength", 0.22)
	gm.set_shader_parameter("warmth", 0.12)
	gm.set_shader_parameter("vignette", 0.3)
	grade.material = gm
	gl.add_child(grade)


func _build_ui() -> void:
	ui = CanvasLayer.new()
	ui.layer = 5
	add_child(ui)
	var root := Control.new()
	root.theme = Game.theme
	root.size = Vector2(480, 270)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(root)
	# Kingdom keeps the screen clean: the purse and the count fade in only when you stop or something changes
	hud_box = Control.new()
	hud_box.size = Vector2(480, 24)
	hud_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(hud_box)
	var shade := ColorRect.new()
	shade.size = Vector2(480, 20)
	shade.color = Color(0, 0, 0, 0.35)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud_box.add_child(shade)
	var row := HBoxContainer.new()
	row.position = Vector2(8, 3)
	row.add_theme_constant_override("separation", 3)
	hud_box.add_child(row)
	row.add_child(Game.icon_rect(Game.tex_coin))
	hud["denarii"] = Game.label("0", GOLDC)
	row.add_child(hud["denarii"])
	row.add_child(_spacer(8))
	row.add_child(Game.icon_rect(_grain_icon()))
	hud["grain"] = Game.label("0")
	row.add_child(hud["grain"])
	row.add_child(_spacer(8))
	hud["men"] = Game.label("")
	row.add_child(hud["men"])
	row.add_child(_spacer(8))
	hud["tribute"] = Game.label("")
	row.add_child(hud["tribute"])
	hud["day"] = Game.label("", DIM)
	hud["day"].position = Vector2(300, 6)
	hud["day"].size = Vector2(172, 10)
	hud["day"].horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	hud_box.add_child(hud["day"])
	for k in ["denarii", "grain", "men", "tribute", "day"]:
		_shadow(hud[k])
	keys_label = Game.label(Game.L("WASD ride    Shift gallop    F interact    I pack    L ledger    M map"), DIM)
	keys_label.position = Vector2(8, 256)
	_shadow(keys_label)
	root.add_child(keys_label)
	Game.lang_changed.connect(_on_lang_changed)
	prompt = Game.label("", Color(1, 0.95, 0.8))
	prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt.size = Vector2(200, 10)
	prompt.visible = false
	root.add_child(prompt)
	toast = Game.label("", Color(1, 0.95, 0.85))
	toast.position = Vector2(40, 28)
	toast.size = Vector2(400, 30)
	toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	toast.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	toast.modulate.a = 0.0
	root.add_child(toast)
	ledger_note = Game.label("", Color(0.78, 0.72, 0.6))
	ledger_note.position = Vector2(150, 224)
	ledger_note.size = Vector2(322, 24)
	ledger_note.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	ledger_note.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
	ledger_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	ledger_note.modulate.a = 0.0
	_shadow(ledger_note)
	leg_title = Game.label("", Color(0.98, 0.9, 0.72))
	leg_title.scale = Vector2(2, 2)
	leg_title.position = Vector2(0, 74)
	leg_title.size = Vector2(240, 12)
	leg_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	leg_title.modulate.a = 0.0
	_shadow(leg_title)
	root.add_child(leg_title)
	_shadow(prompt)
	_shadow(toast)
	menu_layer = CanvasLayer.new()
	menu_layer.layer = 10
	add_child(menu_layer)
	fx_layer = CanvasLayer.new()
	fx_layer.layer = 20
	add_child(fx_layer)
	flash = ColorRect.new()
	flash.size = Vector2(480, 270)
	flash.color = Color(1, 0.95, 0.85, 0.0)
	flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fx_layer.add_child(flash)
	ledger_note.theme = Game.theme
	fx_layer.add_child(ledger_note)


func _on_lang_changed() -> void:
	if is_instance_valid(keys_label):
		keys_label.text = Game.L("WASD ride    Shift gallop    F interact    I pack    L ledger    M map")


func _grain_icon() -> AtlasTexture:
	var a := AtlasTexture.new()
	a.atlas = Game.tex_items
	a.region = Rect2(5 * 16, 0, 16, 16)
	return a


func _spacer(w: int) -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(w, 1)
	return c


func _refresh_hud() -> void:
	if hud.is_empty():
		return
	hud["denarii"].text = str(Game.denarii)
	if last_denarii >= 0 and Game.denarii != last_denarii:
		_pop(hud["denarii"], Game.denarii > last_denarii)
	if last_grain >= 0 and Game.grain != last_grain:
		_pop(hud["grain"], Game.grain > last_grain)
	if last_denarii >= 0 and (Game.denarii != last_denarii or Game.grain != last_grain):
		show_t = 2.5          # a change always shows the purse
	last_denarii = Game.denarii
	last_grain = Game.grain
	hud["grain"].text = Game.L("%d / %d grain  (-%d a day)") % [Game.grain, Game.QUOTA, Game.daily_need()]
	hud["grain"].add_theme_color_override("font_color", BAD if Game.grain < Game.daily_need() * 2 else Color(0.91, 0.84, 0.66))
	hud["men"].text = Game.L("%d men") % Game.total_men()
	hud["tribute"].text = Game.L("offerings %d/%d") % [Game.tribute_count(), Game.TRIBUTE_NEEDED]
	hud["day"].text = Game.L("Day %d   Leg %d of %d   %s") % [Game.day, Game.leg + 1, Game.TOTAL_LEGS, Game.REGIONS[region]["name"]]


func _shadow(l: Label) -> void:
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.85))
	l.add_theme_constant_override("shadow_offset_x", 1)
	l.add_theme_constant_override("shadow_offset_y", 1)


func _hint(b: Button, info: Label, text: String) -> void:
	## show a line of explanation while a button is hovered or keyboard-focused
	var cb := func():
		info.text = text
	b.mouse_entered.connect(cb)
	b.focus_entered.connect(cb)


func _focus_later(b: Button) -> void:
	await get_tree().process_frame
	if is_instance_valid(b) and b.is_inside_tree():
		b.grab_focus()


func _pop(l: Label, up: bool) -> void:
	## a number just changed: flash it green or red and let it settle
	l.modulate = Color(0.5, 1.0, 0.5) if up else Color(1.0, 0.4, 0.35)
	var tw := create_tween()
	tw.tween_property(l, "modulate", Color.WHITE, 0.9)


func _on_ledger(text: String) -> void:
	## every ledger entry is shown being written, so the player feels the book filling up
	if ledger_note == null:
		return
	ledger_note.text = Game.L("written in the ledger:  ") + text
	ledger_note.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(ledger_note, "modulate:a", 1.0, 0.25)
	tw.tween_interval(4.0)
	tw.tween_property(ledger_note, "modulate:a", 0.0, 1.2)


func _show_leg_title() -> void:
	leg_title.text = Game.L(str(Game.REGIONS[region]["road"])).to_upper()
	var tw := create_tween()
	tw.tween_interval(0.5)
	tw.tween_property(leg_title, "modulate:a", 1.0, 0.7)
	tw.tween_interval(2.4)
	tw.tween_property(leg_title, "modulate:a", 0.0, 1.2)


func say(text: String, secs := 3.5) -> void:
	toast.text = text
	var tw := create_tween()
	tw.tween_property(toast, "modulate:a", 1.0, 0.3)
	tw.tween_interval(secs)
	tw.tween_property(toast, "modulate:a", 0.0, 0.8)


# ------------------------------------------------------------------ frame loop
func _process(delta: float) -> void:
	anim_t += delta
	wall_toast_cd -= delta
	var dir := 0.0
	if not busy and not Game.settings_open:
		if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
			dir += 1.0
		if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
			dir -= 1.0
	var galloping := Input.is_key_pressed(KEY_SHIFT)
	var speed := GALLOP if galloping else WALK
	if Game.lvl("forced") > 0:
		speed *= 1.4
	var moving: bool = dir != 0.0
	if moving:
		pos.x += dir * speed * delta
		facing = 1 if dir > 0.0 else -1
		var max_x := length - 30.0
		if not st["won"]:
			for n in poi_nodes:
				if n["poi"]["type"] == "warning":
					max_x = float(n["x"]) + 22.0
			if pos.x > max_x and wall_toast_cd <= 0.0:
				wall_toast_cd = 6.0
				say(Game.L("The road ahead is held. Give battle at the marker - or prepare first."))
		pos.x = clamp(pos.x, 30.0, max_x)
		hoof_t -= delta
		if hoof_t <= 0.0:
			hoof_t = 0.16 if galloping else 0.3
			Game.sfx("thud", -24.0, randf_range(1.5, 1.9))
			if galloping:
				for k in 3:
					parts.append({"k": "dust", "p": Vector2(pos.x - facing * 8.0, GROUND_Y - 1.0), "v": Vector2(-facing * randf_range(10, 30), -randf_range(4, 14)), "life": 0.7, "max": 0.7})
	st["x"] = pos.x * U
	player.position = pos.round()
	player.flip_h = facing < 0
	if moving:
		player.frame = 4 + int(anim_t * (14.0 if galloping else 9.0)) % 8
	else:
		player.frame = int(anim_t * 3.0) % 4
	# the column: a chain, each keeps its distance from whoever is in front
	var lead := pos.x
	for f in followers:
		var spr: Sprite2D = f["spr"]
		var fx: float = f["x"]
		var gap: float = f["gap"]
		var d := lead - fx
		if absf(d) > gap + 1.0:
			var stp: float = min(absf(d) - gap, speed * 1.15 * delta)
			fx += signf(d) * stp
			spr.flip_h = d < 0.0
			f["t"] = float(f["t"]) + delta
			spr.frame = int(f["walk_at"]) + int(float(f["t"]) * 9.0) % int(f["walk_n"])
		else:
			spr.frame = int(anim_t * 3.0 + gap * 0.3) % int(f["idle_n"])
		f["x"] = fx
		spr.position = Vector2(roundf(fx), GROUND_Y)
		lead = fx
	for a in anims:
		var sp: Sprite2D = a[0]
		if sp == priest_spr and busy and ritual_playing:
			continue
		sp.frame = (int(a[3]) + int(anim_t * float(a[2]))) % int(a[1])
	# camera leads the rider a little; whole pixels only
	var want: float = clamp(pos.x + facing * 50.0 - 240.0, 0.0, max(0.0, length - 480.0))
	cam_x = lerp(cam_x, want, min(1.0, delta * 2.6))
	var cx := roundf(cam_x)
	world.position.x = -cx
	for l in layers:
		var spr2: Sprite2D = l[0]
		spr2.position.x = -roundf(fmod(cx * float(l[1]) + anim_t * float(l[5]), float(l[4])))
	idle_t = 0.0 if moving else idle_t + delta
	show_t -= delta
	hud_box.modulate.a = move_toward(hud_box.modulate.a, 1.0 if (idle_t > 0.8 or show_t > 0.0 or busy) else 0.15, delta * 2.5)
	keys_t += delta
	keys_label.modulate.a = move_toward(keys_label.modulate.a, 0.0 if keys_t > 8.0 and not busy else 0.85, delta * 0.8)
	for tf in tufts:
		var sx: float = tf.position.x - cx
		if sx > -20.0 and sx < 500.0:
			tf.skew = sin(anim_t * 1.6 + tf.position.x * 0.045) * 0.18 + (0.08 if rain else 0.0)
	_update_parts(delta)
	rays.queue_redraw()
	wfx.queue_redraw()
	fg.queue_redraw()
	fog_mat.set_shader_parameter("scroll", cx)
	water_mat.set_shader_parameter("scroll", cx)
	_apply_time()
	_update_prompt()


func _update_parts(delta: float) -> void:
	var view := Rect2(cam_x - 20.0, 0, 520, 270)
	# region weather, spawned across the visible stretch of road
	var wx := cam_x + randf() * 480.0
	match region:
		"north":
			if randf() < delta * 50.0:
				parts.append({"k": "snow", "p": Vector2(wx, 16), "v": Vector2(randf_range(-10, -2), randf_range(14, 26)), "life": 12.0, "max": 12.0})
		"west":
			if randf() < delta * 3.0:
				parts.append({"k": "leaf", "p": Vector2(wx, 60 + randf() * 60), "v": Vector2(randf_range(-14, -6), randf_range(8, 14)), "life": 9.0, "max": 9.0, "ph": randf() * TAU})
		"east":
			if randf() < delta * 6.0:
				parts.append({"k": "mote", "p": Vector2(wx, 120 + randf() * 80), "v": Vector2(randf_range(-3, 3), -randf_range(3, 8)), "life": 5.0, "max": 5.0, "c": Color(0.78, 0.66, 0.84)})
		_:
			if randf() < delta * 3.0:
				parts.append({"k": "mote", "p": Vector2(wx, 150 + randf() * 50), "v": Vector2(randf_range(-4, 4), -randf_range(1, 4)), "life": 5.0, "max": 5.0, "c": Color(1.0, 0.9, 0.65)})
	if rain:
		for k in int(delta * 260.0) + (1 if randf() < fmod(delta * 260.0, 1.0) else 0):
			parts.append({"k": "rain", "p": Vector2(cam_x + randf() * 560.0 - 40.0, 10), "v": Vector2(-40, 260), "life": 1.0, "max": 1.0})
	# fireflies after dusk
	if night_k > 0.3 and randf() < delta * 4.0 * night_k:
		parts.append({"k": "firefly", "p": Vector2(wx, GROUND_Y - randf_range(6, 40)), "v": Vector2(randf_range(-4, 4), randf_range(-3, 3)), "life": 4.0, "max": 4.0, "ph": randf() * TAU})
	# embers from every fire in view
	for src in parts_src:
		var sp: Vector2 = src
		if view.has_point(Vector2(sp.x, 100)) and randf() < delta * 7.0:
			parts.append({"k": "ember", "p": sp + Vector2(randf_range(-3, 3), 0), "v": Vector2(randf_range(-5, 5), -randf_range(14, 30)), "life": 1.4, "max": 1.4})
	for q in parts:
		q["life"] = float(q["life"]) - delta
		var v: Vector2 = q["v"]
		if q["k"] == "leaf":
			v.x += sin(anim_t * 2.0 + float(q["ph"])) * 10.0 * delta
			q["v"] = v
		if q["k"] == "dust":
			q["v"] = v * 0.92
		q["p"] = Vector2(q["p"]) + v * delta
		if q["k"] == "firefly":
			q["p"] = Vector2(q["p"]) + Vector2(sin(anim_t * 1.7 + float(q["ph"])), cos(anim_t * 1.3 + float(q["ph"]))) * delta * 8.0
	parts = parts.filter(func(q): return float(q["life"]) > 0.0 and Vector2(q["p"]).y < (GROUND_Y + 2.0 if q["k"] == "rain" else WATER_Y + 2.0))
	for b in birds:
		b[0] = fmod(float(b[0]) + float(b[2]) * delta, 700.0)


func _draw_wfx() -> void:
	for q in parts:
		var al: float = clamp(float(q["life"]) / float(q["max"]) * 1.5, 0.0, 1.0)
		var pp: Vector2 = Vector2(q["p"]).round()
		match str(q["k"]):
			"snow":
				wfx.draw_rect(Rect2(pp, Vector2(1, 1)), Color(1, 1, 1, 0.9 * al))
			"leaf":
				var lc := Color(0.75, 0.55, 0.2, al) if int(pp.x) % 3 != 0 else Color(0.55, 0.65, 0.25, al)
				wfx.draw_rect(Rect2(pp, Vector2(2, 1)), lc)
			"mote":
				var tw: float = 0.5 + 0.5 * sin(anim_t * 4.0 + pp.x)
				wfx.draw_rect(Rect2(pp, Vector2(1, 1)), Color(q["c"].r, q["c"].g, q["c"].b, al * tw))
			"firefly":
				var tw2: float = 0.5 + 0.5 * sin(anim_t * 6.0 + float(q["ph"]))
				wfx.draw_rect(Rect2(pp, Vector2(1, 1)), Color(0.95, 0.85, 0.5, al * tw2 * night_k))
			"ember":
				wfx.draw_rect(Rect2(pp, Vector2(1, 1)), Color(1.0, 0.7, 0.3, al))
			"dust":
				wfx.draw_rect(Rect2(pp, Vector2(2, 2)), Color(0.75, 0.66, 0.52, 0.5 * al))
			"rain":
				wfx.draw_line(pp, pp + Vector2(-2, 6), Color(0.7, 0.75, 0.85, 0.45), 1.0)
				if pp.y > GROUND_Y - 4.0:
					wfx.draw_rect(Rect2(pp + Vector2(-1, 0), Vector2(3, 1)), Color(0.8, 0.85, 0.9, 0.5))
	# streams off the ledge: a column of falling water with moving highlights, and a splash ring
	for fx3 in falls:
		var wx: float = fx3
		if wx < cam_x - 10.0 or wx > cam_x + 490.0:
			continue
		for yy in range(int(GROUND_Y + 8.0), int(WATER_Y)):
			var ph := fmod(anim_t * 40.0 - yy, 8.0)
			var c := Color(0.85, 0.92, 0.95, 0.85) if ph < 2.0 else Color(0.55, 0.7, 0.78, 0.7)
			wfx.draw_rect(Rect2(wx, yy, 2, 1), c)
		var sp := int(anim_t * 6.0) % 3
		wfx.draw_rect(Rect2(wx - 2 - sp, WATER_Y - 1, 6 + sp * 2, 1), Color(0.9, 0.95, 1.0, 0.6))
	# birds drifting high over the road (in world space, but slow, so they read as far away)
	for b in birds:
		var bp := Vector2(cam_x + float(b[0]) - 100.0, float(b[1]) + sin(anim_t * 0.8 + float(b[3])) * 5.0).round()
		var flap := int(anim_t * 6.0 + float(b[3])) % 2
		var bc := Color(0.1, 0.08, 0.12, 0.85)
		wfx.draw_rect(Rect2(bp, Vector2(1, 1)), bc)
		wfx.draw_rect(Rect2(bp + Vector2(-2, -1 + flap), Vector2(2, 1)), bc)
		wfx.draw_rect(Rect2(bp + Vector2(1, -1 + flap), Vector2(2, 1)), bc)


func _draw_rays() -> void:
	## low sun through the trees at dawn and late afternoon: soft slanted shafts behind the near wood
	if ray_k <= 0.01:
		return
	var off := fmod(cam_x * 0.5, 160.0)
	for i in 6:
		var x0 := 40.0 + i * 160.0 * 0.5 + 23.0 * sin(i * 2.3) - off
		var w := 10.0 + 8.0 * absf(sin(i * 1.7))
		var a := ray_k * (0.05 + 0.03 * sin(anim_t * 0.6 + i))
		var pts := PackedVector2Array([Vector2(x0, 40), Vector2(x0 + w, 40), Vector2(x0 + w + 70, GROUND_Y), Vector2(x0 + 70, GROUND_Y)])
		rays.draw_colored_polygon(pts, Color(1.0, 0.9, 0.65, a))


func _draw_fg() -> void:
	## dark grass and bushes passing in front of the column, faster than the road, for depth
	var pal: Dictionary = PAL[region]
	var c: Color = pal["leaf"].darkened(0.55)
	var cx := roundf(cam_x * 1.35)
	for b in fg_bits:
		var x: float = float(b[0]) - cx
		if x < -40.0 or x > 520.0:
			continue
		var h: float = b[1]
		var sway := sin(anim_t * 1.5 + float(b[3])) * 1.5
		match int(b[2]):
			0:      # tuft of tall grass
				for k in 7:
					var gx := x + k * 2.0
					var gh := h * (0.6 + 0.4 * sin(k * 1.9 + float(b[3])))
					fg.draw_line(Vector2(gx, WATER_Y + 1), Vector2(gx + sway * (gh / h), WATER_Y + 1 - gh), c, 1.0)
			1:      # round bush
				fg.draw_circle(Vector2(x + 6, WATER_Y - h * 0.4), h * 0.6, c)
				fg.draw_circle(Vector2(x + 14, WATER_Y - h * 0.3), h * 0.45, c)
			_:      # reeds
				for k in 4:
					var rx := x + k * 3.0
					fg.draw_line(Vector2(rx, WATER_Y + 1), Vector2(rx + sway, WATER_Y - h - k), c, 1.0)
					fg.draw_rect(Rect2(Vector2(rx + sway - 1, WATER_Y - h - k - 3).round(), Vector2(2, 4)), c)


func _mix3(keys: Array, p: float) -> Color:
	for i in range(keys.size() - 1):
		if p <= keys[i + 1][0]:
			var a: Color = keys[i][1]
			var b: Color = keys[i + 1][1]
			var k: float = (p - keys[i][0]) / max(0.001, keys[i + 1][0] - keys[i][0])
			return a.lerp(b, clamp(k, 0.0, 1.0))
	return keys[keys.size() - 1][1]


func _apply_time() -> void:
	## Distance along the leg IS the time of day: dawn at the camp, night at the crossroads.
	var p: float = clamp(pos.x / length, 0.0, 1.0)
	var rt := Color.WHITE        # the painted strips already carry each region's colour
	var dt: Color = SKY[region][0]
	var db: Color = SKY[region][1]
	var top := _mix3([[0.0, dt.lerp(Color(0.42, 0.36, 0.5), 0.55)], [0.25, dt], [0.5, dt], [0.66, dt.lerp(Color(0.36, 0.26, 0.42), 0.6)], [0.86, Color(0.07, 0.08, 0.15)], [1.0, Color(0.05, 0.06, 0.12)]], p)
	var bot := _mix3([[0.0, db.lerp(Color(0.98, 0.76, 0.6), 0.55)], [0.25, db], [0.5, db], [0.66, db.lerp(Color(0.98, 0.62, 0.4), 0.6)], [0.86, Color(0.22, 0.22, 0.32)], [1.0, Color(0.16, 0.17, 0.26)]], p)
	var tint := _mix3([[0.0, Color(1.0, 0.88, 0.84)], [0.25, Color(1, 1, 1)], [0.5, Color(1, 1, 1)], [0.66, Color(1.0, 0.8, 0.66)], [0.86, Color(0.42, 0.46, 0.7)], [1.0, Color(0.36, 0.4, 0.64)]], p)
	night_k = clamp((p - 0.62) / 0.24, 0.0, 1.0)
	sky_mat.set_shader_parameter("top_col", Vector3(top.r, top.g, top.b) * Vector3(rt.r, rt.g, rt.b))
	sky_mat.set_shader_parameter("bot_col", Vector3(bot.r, bot.g, bot.b) * Vector3(rt.r, rt.g, rt.b))
	sky_mat.set_shader_parameter("night", night_k)
	# the sun climbs and sinks across the leg; the moon rises after dusk
	var orb := Vector2(0.15 + p * 0.8, 0.75 - sin(clamp(p / 0.8, 0.0, 1.0) * PI) * 0.55) if night_k < 0.5 else Vector2(0.25 + p * 0.3, 0.25)
	sky_mat.set_shader_parameter("orb_pos", orb)
	sky_mat.set_shader_parameter("orb_col", Vector3(1.0, 0.92, 0.7) if night_k < 0.5 else Vector3(0.9, 0.92, 1.0))
	if rain:
		tint = tint * Color(0.78, 0.8, 0.86)
		top = top.lerp(Color(0.36, 0.38, 0.44), 0.6)
		bot = bot.lerp(Color(0.6, 0.62, 0.66), 0.6)
		sky_mat.set_shader_parameter("top_col", Vector3(top.r, top.g, top.b) * Vector3(rt.r, rt.g, rt.b))
		sky_mat.set_shader_parameter("bot_col", Vector3(bot.r, bot.g, bot.b) * Vector3(rt.r, rt.g, rt.b))
	tint = tint.lerp(Color(0.26, 0.28, 0.44), night_k * 0.55)      # Kingdom nights: only the fires carry colour
	tint_mod.color = tint * rt
	# aerial perspective: far strips fade into the horizon colour (divided by the tint the world will get)
	var hz := bot * rt
	var tw := tint * rt
	var fogc := Vector3(hz.r / max(tw.r, 0.25), hz.g / max(tw.g, 0.25), hz.b / max(tw.b, 0.25)).clamp(Vector3.ZERO, Vector3(1.4, 1.4, 1.4))
	for l in layers:
		if l[2] != null:
			var m: ShaderMaterial = l[2]
			m.set_shader_parameter("fog_col", fogc)
			m.set_shader_parameter("amount", float(l[3]) * (1.0 - night_k * 0.5) * (1.25 if rain else 1.0))
	ray_k = (0.0 if rain else 1.0) * (clamp(1.0 - absf(p - 0.12) / 0.14, 0.0, 1.0) * 0.9 + clamp(1.0 - absf(p - 0.58) / 0.1, 0.0, 1.0) * 0.7)
	torch.energy = 0.9 * night_k
	for l in fire_lights:
		var base: float = l.get_meta("base")
		l.energy = base * (0.2 + 1.1 * night_k) * (0.9 + 0.1 * sin(anim_t * 11.0 + l.position.x))
	water_mat.set_shader_parameter("tint", (WATER[region] as Vector3).lerp(Vector3(0.03, 0.05, 0.12), night_k))
	var fc := Color(0.86, 0.86, 0.94).lerp(Color(0.4, 0.46, 0.7), night_k) * rt
	fog_mat.set_shader_parameter("fog_col", Vector3(fc.r, fc.g, fc.b))
	fog_mat.set_shader_parameter("density", 0.12 + 0.2 * night_k + (0.2 if p < 0.12 else 0.0))


func _prompt_text(p: Dictionary) -> String:
	match p["type"]:
		"camp":
			return Game.L("[F] Make camp")
		"shop":
			return Game.L("[F] Trade")
		"altar":
			return Game.L("[F] The altar") if not p["used"] else Game.L("The altar is cold")
		"event":
			return Game.L("[F] Speak") if not p["used"] else ""
		"warning":
			return Game.L("[F] Give battle") if not st["won"] else ""
		"crossroads":
			return Game.L("[F] Choose the road") if st["won"] else ""
	return ""


func _update_prompt() -> void:
	near = null
	var best := 46.0
	for n in poi_nodes:
		var d: float = absf(float(n["x"]) - pos.x)
		if d < best and _prompt_text(n["poi"]) != "":
			best = d
			near = n
	if near == null or busy:
		prompt.visible = false
		return
	prompt.visible = true
	prompt.text = _prompt_text(near["poi"])
	var sx := roundf(float(near["x"]) - cam_x)
	prompt.position = Vector2(sx - 100.0, clamp(float(near["top"]) - 14.0, 24.0, 236.0) + roundf(sin(anim_t * 3.0) * 2.0))


func _unhandled_input(event: InputEvent) -> void:
	if Game.settings_open:
		return
	if not (event is InputEventKey) or not event.pressed or event.echo:
		return
	if busy:
		if event.keycode == KEY_ESCAPE and menu_closable:
			close_menu()
		return
	if event.keycode == KEY_HOME and OS.is_debug_build():      # debug: straight to the doctrine wheel with a fat purse
		Game.denarii = max(Game.denarii, 400)
		open_tree()
		return
	if (event.keycode == KEY_BRACKETRIGHT or event.keycode == KEY_PAGEDOWN) and OS.is_debug_build():
		_debug_next_stop()
		return
	match event.keycode:
		KEY_F, KEY_E, KEY_ENTER:
			if near != null:
				_interact(near["poi"])
		KEY_I:
			open_pack()
		KEY_L:
			open_ledger()
		KEY_M:
			open_map()


func _debug_next_stop() -> void:
	## dev shortcut (debug builds only): "]" jumps the column to the next stop on the road
	var best := length - 30.0
	for n in poi_nodes:
		var nx: float = n["x"]
		if nx > pos.x + 12.0 and nx < best:
			best = nx
	if not st["won"]:
		for n in poi_nodes:
			if n["poi"]["type"] == "warning":
				best = min(best, float(n["x"]))
	pos.x = best
	var back := 0.0
	for f in followers:
		back += float(f["gap"])
		f["x"] = pos.x - back
	cam_x = clamp(pos.x - 240.0, 0.0, max(0.0, length - 480.0))


func _interact(p: Dictionary) -> void:
	match p["type"]:
		"camp":
			open_camp()
		"shop":
			open_shop(p)
		"altar":
			if not p["used"]:
				open_altar(p)
		"event":
			if not p["used"]:
				open_event(p)
		"warning":
			if not st["won"]:
				open_battle_brief()
		"crossroads":
			if st["won"]:
				open_crossroads()


# ------------------------------------------------------------------ window kit
func close_menu() -> void:
	if menu_root != null:
		Game.sfx("ui_close", -6.0)
		menu_root.queue_free()
		menu_root = null
	busy = false
	menu_closable = true


func window(title: String, width := 300, closable := true) -> VBoxContainer:
	var fresh: bool = menu_root == null
	if menu_root != null:
		menu_root.queue_free()
	busy = true
	menu_closable = closable
	menu_root = Control.new()
	menu_root.theme = Game.theme
	menu_root.size = Vector2(480, 270)
	menu_layer.add_child(menu_root)
	Game.enable_keys.call_deferred(menu_root)
	if fresh:
		menu_root.modulate.a = 0.0
		create_tween().tween_property(menu_root, "modulate:a", 1.0, 0.14)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.5)
	dim.size = Vector2(480, 270)
	menu_root.add_child(dim)
	var center := CenterContainer.new()
	center.size = Vector2(480, 270)
	menu_root.add_child(center)
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(width, 0)
	center.add_child(panel)
	var vb := VBoxContainer.new()
	panel.add_child(vb)
	var head := HBoxContainer.new()
	vb.add_child(head)
	var plate := PanelContainer.new()
	plate.theme_type_variation = "TitlePlate"
	plate.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	plate.add_child(Game.label(title, Color(1.0, 0.9, 0.62)))
	head.add_child(plate)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(spacer)
	if closable:
		head.add_child(Game.button("x", close_menu))
	# a small animated painting heads the window
	var art := art_hint
	art_hint = ""
	if art == "":
		art = _art_for(title)
	var vig = null
	if art != "":
		vig = VIGNETTE.new()
		vig.setup(art)
		vb.add_child(vig)
	vb.add_child(HSeparator.new())
	if fresh:
		Game.sfx("ui_open", -5.0)
		panel.pivot_offset = Vector2(width * 0.5, 60)
		panel.scale = Vector2(0.94, 0.94)
		create_tween().tween_property(panel, "scale", Vector2.ONE, 0.18).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	_settle_window.call_deferred(panel, vig, fresh)
	return vb


func _art_for(title: String) -> String:
	var table := {"Camp": "camp", "Muster": "muster", "The baggage train": "pack", "The ledger": "ledger",
		"The four realms": "map", "A roadside stall": "stall", "A river altar": "altar", "The road is held": "brief",
		"The road divides": "cross", "The omen": "omen", "The toll": "brief"}
	for k in table:
		if title == Game.L(k):
			return table[k]
	return ""


func _settle_window(panel: Control, vig, fresh: bool) -> void:
	## after layout: shrink the painting if the window would run off screen, then run the gold sparks round the frame
	if not is_instance_valid(panel):
		return
	await get_tree().process_frame
	if not is_instance_valid(panel):
		return
	var over := panel.get_combined_minimum_size().y - 262.0
	if is_instance_valid(vig) and over > 0.0:
		var hgt: float = max(0.0, vig.custom_minimum_size.y - over)
		if hgt < 22.0:
			vig.queue_free()
		else:
			vig.custom_minimum_size.y = hgt
		await get_tree().process_frame
	if fresh and is_instance_valid(panel):
		var fx = UI_FX.new()
		fx.mode = "border"
		fx.rect = Rect2(panel.global_position + Vector2(2, 2), panel.size - Vector2(4, 4))
		menu_layer.add_child(fx)


func stamp(at: Vector2) -> void:
	## a wax seal pressed where a decision was made
	var fx = UI_FX.new()
	fx.mode = "seal"
	fx.at = at
	fx_layer.add_child(fx)
	Game.sfx("ui_choice", -3.0)


func _scroll(vb: VBoxContainer, height: int) -> VBoxContainer:
	var sc := ScrollContainer.new()
	sc.custom_minimum_size = Vector2(0, height)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vb.add_child(sc)
	var inner := VBoxContainer.new()
	inner.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(inner)
	return inner


func _item_row(id: String, right_text: String, cb = null, enabled := true) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_child(Game.icon_rect(Game.item_icon(id)))
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 0)
	var it: Dictionary = Game.ITEMS[id]
	var nm := Game.L(str(it["name"]))
	if it.get("tribute", false):
		nm += Game.L("  [offering]")
	col.add_child(Game.label(nm))
	col.add_child(Game.label(Game.L(str(it["desc"])), DIM, 190))
	row.add_child(col)
	if cb != null:
		row.add_child(Game.button(right_text, cb, enabled))
	elif right_text != "":
		row.add_child(Game.label(right_text, DIM))
	return row


func result(title: String, text: String, then = null) -> void:
	var vb := window(title, 300, false)
	vb.add_child(Game.label(text, null, 288))
	var cb := func():
		close_menu()
		if then != null:
			then.call()
	vb.add_child(Game.button(Game.L("Continue"), cb))


# ------------------------------------------------------------------ pack / ledger / map
func open_pack() -> void:
	var vb := window(Game.L("The baggage train"), 320)
	vb.add_child(Game.label(Game.L("Everything here can be sold, equipped, sacrificed - or delivered. Not all four."), DIM, 300))
	var inner := _scroll(vb, 150)
	if Game.inventory.is_empty():
		inner.add_child(Game.label(Game.L("Nothing but dust and rope."), DIM))
	for id in Game.inventory:
		inner.add_child(_item_row(id, Game.L("worth %d") % int(Game.ITEMS[id]["value"])))


func open_ledger() -> void:
	var vb := window(Game.L("The ledger"), 340)
	vb.add_child(Game.label(Game.L("Written in your own hand. It is not shown to anyone until the end."), DIM, 320))
	var inner := _scroll(vb, 120)
	for e in Game.ledger:
		inner.add_child(Game.label(Game.L("Day %d.  %s") % [int(e["day"]), str(e["text"])], null, 318))
	vb.add_child(HSeparator.new())
	vb.add_child(Game.label(Game.L("Promises"), GOLDC))
	for p in Game.promises:
		var c = null
		if p["state"] == "kept":
			c = GOOD
		elif p["state"] == "broken":
			c = BAD
		vb.add_child(Game.label("%s  (%s)" % [str(p["text"]), Game.L(str(p["state"]))], c, 318))


func open_map(choose := false) -> void:
	## the living map of the four realms; at a crossroads it is where the next road is chosen
	busy = true
	var layer := CanvasLayer.new()
	layer.layer = 30
	add_child(layer)
	var m = WORLD_MAP.new()
	m.setup(choose, st["options"] if choose else [])
	layer.add_child(m)
	m.closed.connect(_on_map_closed.bind(layer, choose))
	m.chosen.connect(_on_map_chosen.bind(layer))


func _on_map_closed(layer: CanvasLayer, choose: bool) -> void:
	layer.queue_free()
	busy = false
	if choose:
		open_crossroads()


func _on_map_chosen(o: String, layer: CanvasLayer) -> void:
	layer.queue_free()
	if o == "altar":
		_to_altar()
	else:
		_march(o)


# ------------------------------------------------------------------ shop
func open_shop(p: Dictionary) -> void:
	var vb := window(Game.L("A roadside stall"), 404)
	vb.add_child(Game.label(Game.L("Worn boards, a faded awning. Everything has a price in the King's coin.   You hold %d denarii.") % Game.denarii, DIM, 390))
	var info := Game.label("", null, 390)
	info.custom_minimum_size = Vector2(390, 22)
	var cols := HBoxContainer.new()
	vb.add_child(cols)
	var left := VBoxContainer.new()
	left.custom_minimum_size = Vector2(192, 0)
	cols.add_child(left)
	cols.add_child(VSeparator.new())
	var right := VBoxContainer.new()
	right.custom_minimum_size = Vector2(190, 0)
	cols.add_child(right)
	left.add_child(Game.label(Game.L("BUY"), GOLDC))
	var buy_grain := func():
		Game.denarii -= 12
		Game.grain += 10
		Game.sfx("coin_spend", -6.0)
		Game.sfx("grain", -4.0)
		Game.changed.emit()
		open_shop(p)
	var bg := Game.button(Game.L("10 grain  -  12 d"), buy_grain, Game.denarii >= 12)
	_hint(bg, info, Game.L("Ten measures of grain. The column eats %d a day, and the ledger wants %d.") % [Game.daily_need(), Game.QUOTA])
	left.add_child(bg)
	var stock: Array = p["stock"]
	for id in stock:
		var it: Dictionary = Game.ITEMS[id]
		var price := int(ceil(int(it["value"]) * 1.4))
		var buy := func():
			Game.denarii -= price
			Game.add_item(id)
			stock.erase(id)
			Game.sfx("coin_spend", -4.0)
			open_shop(p)
		var b := Game.button("%s  -  %d d" % [Game.L(str(it["name"])), price], buy, Game.denarii >= price)
		b.icon = Game.item_icon(id)
		_hint(b, info, Game.L(str(it["desc"])) + (Game.L("  [counts as an offering]") if it.get("tribute", false) else ""))
		left.add_child(b)
	right.add_child(Game.label(Game.L("SELL"), GOLDC))
	var inner := _scroll(right, 96)
	var any := false
	for id in Game.inventory:
		var it2: Dictionary = Game.ITEMS[id]
		var val := int(it2["value"])
		if val <= 0:
			continue
		any = true
		var sell := func():
			Game.remove_item(id)
			Game.denarii += val
			Game.sfx("sell", -3.0)
			if id == "white_ox":
				Game.write(Game.L("Sold the white ox for %d denarii.") % val)
			elif id == "relic_horn":
				Game.write(Game.L("Sold the Ancestral Horn of Frostbay to a stallkeeper."))
				if Game.has_promise("horn"):
					Game.set_promise("horn", "broken")
			Game.changed.emit()
			open_shop(p)
		var b2 := Game.button("%s  +%d d" % [Game.L(str(it2["name"])), val], sell)
		b2.icon = Game.item_icon(id)
		_hint(b2, info, Game.L(str(it2["desc"])) + (Game.L("  [the ledger lists this as an offering]") if it2.get("tribute", false) else ""))
		inner.add_child(b2)
	if not any:
		inner.add_child(Game.label(Game.L("Nothing he wants."), DIM))
	vb.add_child(HSeparator.new())
	vb.add_child(info)


# ------------------------------------------------------------------ camp
func open_camp() -> void:
	var vb := window(Game.L("Camp"), 250)
	vb.add_child(Game.label(Game.L("Tents, a fire, the standard. %d men, %d grain, %d days of food at this strength.") % [Game.total_men(), Game.grain, int(Game.grain / max(1, Game.daily_need()))], DIM, 236))
	vb.add_child(Game.button(Game.L("Drill and doctrine  (upgrade tree)"), open_tree))
	vb.add_child(Game.button(Game.L("Muster the regiments  (recruit, equip)"), open_muster))
	vb.add_child(Game.button(Game.L("The ledger"), open_ledger))
	vb.add_child(Game.button(Game.L("Settings  (language)"), Game.open_settings.bind(open_camp)))
	vb.add_child(Game.button(Game.L("Break camp"), close_menu))


func open_muster() -> void:
	var vb := window(Game.L("Muster"), 400)
	if not st.has("levy"):
		st["levy"] = int((22 if region == "south" else 12) * (1.5 if Game.lvl("auxilia") > 0 else 1.0) * (0.5 if Game.lvl("scorch") > 0 else 1.0))
	vb.add_child(Game.label(Game.L("Men willing to follow the standard here: %d.   Each regiment holds %d at most; you may field %d regiments.") % [int(st["levy"]), Game.MAX_MEN, Game.MAX_REGS], DIM, 386))
	var inner := _scroll(vb, 78)
	var ranks := ["", " *", " **", " ***"]
	for r in Game.regiments:
		var row := HBoxContainer.new()
		inner.add_child(row)
		var rank_txt: String = ranks[int(r["rank"])]
		var l := Game.label(Game.L("%s%s   %d/%d   kills %d") % [Game.L(str(r["name"])), rank_txt, int(r["men"]), Game.MAX_MEN, int(r["kills"])])
		l.custom_minimum_size = Vector2(170, 0)
		row.add_child(l)
		var cost := Game.recruit_cost(str(r["type"]))
		var n: int = max(0, min(5, min(Game.MAX_MEN - int(r["men"]), int(st["levy"]))))
		var add_men := func():
			Game.denarii -= cost * n
			r["men"] += n
			st["levy"] -= n
			Game.marched += n
			Game.sfx("coin_spend", -4.0)
			Game.changed.emit()
			open_muster()
		row.add_child(Game.button(Game.L("+%d men  %d d") % [n, cost * n], add_men, n > 0 and Game.denarii >= cost * n and not r["elite"]))
		var seen := {}
		for id in Game.inventory:
			var eq = Game.ITEMS[id].get("equip", "")
			if seen.has(id) or not (eq == "any" or eq == r["type"]):
				continue
			seen[id] = true
			var equip := func():
				Game.remove_item(id)
				if id == "bowstrings":
					r["r_atk_bonus"] += 2.0
				elif id == "spearheads":
					r["atk_bonus"] += 2.0
				else:
					r["atk_bonus"] += 1.0
				Game.sfx("upgrade", -6.0)
				open_muster()
			var b := Game.button("", equip)
			b.icon = Game.item_icon(id)
			b.tooltip_text = Game.L("Equip ") + Game.L(str(Game.ITEMS[id]["name"]))
			row.add_child(b)
	vb.add_child(HSeparator.new())
	vb.add_child(Game.label(Game.L("Raise a new regiment of 10"), GOLDC))
	var row2 := HBoxContainer.new()
	vb.add_child(row2)
	for t in ["spear", "shield", "archer", "cavalry"]:
		var c := Game.recruit_cost(t) * 10 + 8
		var ok: bool = Game.regiments.size() < Game.MAX_REGS and int(st["levy"]) >= 10 and Game.denarii >= c
		var raise := func():
			Game.denarii -= c
			st["levy"] -= 10
			Game.marched += 10
			Game.add_regiment(t, 10)
			Game.sfx("coin_spend", -4.0)
			open_muster()
		row2.add_child(Game.button("%s  %d d" % [Game.L(str(Game.UNITS[t]["name"])), c], raise, ok))
	vb.add_child(Game.label(Game.L("Hastati hold lines and kill horses.  Scutarii soak arrows.  Sagittarii shred light armour.  Equites flank."), DIM, 386))
	vb.add_child(Game.button(Game.L("Back"), open_camp))


func open_tree() -> void:
	## the doctrine wheel is its own full-screen control (scripts/doctrine_tree.gd)
	if menu_root != null:
		menu_root.queue_free()
	busy = true
	menu_closable = true
	var t = load("res://scripts/doctrine_tree.gd").new()
	t.host = self
	menu_root = t
	menu_layer.add_child(t)


func _coin_burst(at: Vector2) -> void:
	## the satisfying part: coins fly from the purse into the doctrine and it pops
	for i in 9:
		var c := Sprite2D.new()
		c.texture = Game.tex_coin
		c.position = Vector2(18, 10)
		c.z_index = 100
		fx_layer.add_child(c)
		var tw := create_tween()
		tw.tween_interval(i * 0.03)
		var mid := at + Vector2(randf_range(-30, 30), randf_range(-36, -8))
		tw.tween_property(c, "position", mid, 0.18).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.tween_property(c, "position", at, 0.14).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		tw.tween_property(c, "scale", Vector2(2.2, 2.2), 0.08)
		tw.parallel().tween_property(c, "modulate:a", 0.0, 0.08)
		tw.tween_callback(c.queue_free)
	flash.color = Color(1, 0.9, 0.6, 0.0)
	var ft := create_tween()
	ft.tween_interval(0.3)
	ft.tween_property(flash, "color:a", 0.22, 0.05)
	ft.tween_property(flash, "color:a", 0.0, 0.35)


# ------------------------------------------------------------------ altar & omens
var ritual_playing := false


func _omen_power(kind: String, value: int) -> int:
	var valued: Array = Game.REGIONS[region]["values"]
	return value * (2 if valued.has(kind) else 1)


func _tier_name(power: int) -> String:
	if power >= 70:
		return Game.L("blazing")
	if power >= 30:
		return Game.L("clear")
	return Game.L("faint")


func open_altar(p: Dictionary) -> void:
	var vb := window(Game.L("A river altar"), 360)
	vb.add_child(Game.label(Game.L("A priest with a wet red cord at his waist. \"Men before a battle do not ask to be stronger. They ask: will I die today? Where will they come from?\"\nThe gods of this country answer loudest to %s. What is burned is gone - it cannot be sold, eaten, or delivered.") % Game.L(str(Game.REGIONS[region]["values_text"])), DIM, 346))
	var inner := _scroll(vb, 118)
	var seen := {}
	for id in Game.inventory:
		if seen.has(id):
			continue
		seen[id] = true
		var it: Dictionary = Game.ITEMS[id]
		var power := 999 if id == "family_portrait" else _omen_power(str(it["kind"]), int(it["value"]))
		var b := Game.button(Game.L("%s  -  a %s omen") % [Game.L(str(it["name"])), _tier_name(power)], _sacrifice.bind(p, id, power))
		b.icon = Game.item_icon(id)
		inner.add_child(b)
	var mp := _omen_power("life", 22)
	inner.add_child(Game.button(Game.L("Three volunteers  -  a %s omen") % _tier_name(mp), _sacrifice.bind(p, "men", mp), Game.total_men() > 6))
	inner.add_child(Game.button(Game.L("Ten measures of grain  -  a faint omen"), _sacrifice.bind(p, "grain", 10), Game.grain >= 10))
	vb.add_child(Game.label(Game.L("faint: their numbers.   clear: also where the flank attack comes from.   blazing: also steadies your men (+15% armour)."), DIM, 346))
	var leave := Game.button(Game.L("Leave the altar cold"), close_menu)
	vb.add_child(leave)
	_focus_later(leave)          # never let a stray Enter burn the portrait


func _ritual_frame(v: float) -> void:
	priest_spr.frame = 4 + int(v) % 8


func _ritual_done(power: int) -> void:
	ritual_playing = false
	_reveal_omen(power)


func _sacrifice(p: Dictionary, what: String, power: int) -> void:
	p["used"] = true
	close_menu()
	busy = true
	menu_closable = false
	ritual_playing = true
	if what == "men":
		Game.lose_men(3)
		Game.write(Game.L("Three men walked to the altar at %s. I did not stop them.") % Game.L(str(Game.REGIONS[region]["road"])))
	elif what == "grain":
		Game.grain -= 10
		Game.write(Game.L("Burned ten measures of grain for a faint omen."))
	else:
		Game.remove_item(what)
		if what == "family_portrait":
			Game.write(Game.L("Burned the portrait of Livia and the child. The cedar caught quickly."))
		elif what == "relic_horn":
			Game.write(Game.L("Burned Frostbay's Ancestral Horn on a foreign altar."))
			if Game.has_promise("horn"):
				Game.set_promise("horn", "broken")
		else:
			Game.write(Game.L("Gave %s to the fire at %s.") % [Game.L(str(Game.ITEMS[what]["name"])), Game.L(str(Game.REGIONS[region]["road"]))])
	Game.changed.emit()
	Game.sfx("ritual")
	flash.color = Color(1, 0.9, 0.75, 0.0)
	var tw := create_tween()
	tw.tween_method(_ritual_frame, 0.0, 15.9, 2.4)
	tw.tween_property(flash, "color:a", 0.85, 0.25)
	tw.tween_property(flash, "color:a", 0.0, 0.9)
	tw.tween_callback(_ritual_done.bind(power))


func _reveal_omen(power: int) -> void:
	var b: Dictionary = Game.next_battle
	var lines: Array = []
	Game.omen["count"] = true
	var groups := {}
	for g in b["main"]:
		groups[g[0]] = int(groups.get(g[0], 0)) + int(g[1])
	var parts: Array = []
	for k in groups:
		parts.append("%d %s" % [int(groups[k]), Game.L(str(k))])
	lines.append(Game.L("\"%s hold the road. I count %s before you, and more that I cannot see.\"") % [Game.L(str(Game.REGIONS[region]["enemy"])), Game.L(", ").join(PackedStringArray(parts))])
	if power >= 30:
		Game.omen["flank"] = true
		var side := Game.L("WEST (your left)") if b["flank_side"] == "left" else Game.L("EAST (your right)")
		var fl: Array = []
		for g in b["flank"]:
			fl.append("%d %s" % [int(g[1]), Game.L(str(g[0]))])
		lines.append(Game.L("\"The ones you cannot see - %s - will come out of the %s, when the drums have beaten about %d times.\"") % [Game.L(", ").join(PackedStringArray(fl)), side, int(b["flank_time"])])
	if power >= 70:
		Game.battle_buff["armor"] = 0.15
		lines.append(Game.L("\"Tell your men what I told you. Men who know where death stands hold their shields higher.\""))
	# the gods also say things you cannot change
	var days_left: int = Game.TOTAL_LEGS - Game.leg
	var short: int = Game.QUOTA - (Game.grain - Game.daily_need() * days_left)
	if short > 0:
		lines.append(Game.L("He looks at the carts. \"At this pace you reach the Great Altar %d measures short. That is not an omen. That is arithmetic.\"") % short)
	if Game.flags.has("west_hostile") and b["faction"] == "west":
		lines.append(Game.L("\"The forest remembers the seeds. A third warband waits in the trees. It was always going to.\""))
	result(Game.L("The omen"), "\n\n".join(PackedStringArray(lines)))


# ------------------------------------------------------------------ battle briefing
func open_battle_brief() -> void:
	var b: Dictionary = Game.next_battle
	var vb := window(Game.L("The road is held"), 320)
	var txt := Game.L("%s bar the way.") % Game.L(str(Game.REGIONS[region]["enemy"]))
	if Game.omen.has("count") or Game.lvl("eagle") >= 3 or Game.lvl("lore_east") > 0:
		txt += Game.L(" About %d of them in all.") % Game.battle_enemy_men()
	else:
		txt += Game.L(" You cannot tell how many. The altar might have told you.")
	if Game.omen.has("flank"):
		txt += Game.L(" Their hidden force will strike from your %s.") % (Game.L("LEFT") if b["flank_side"] == "left" else Game.L("RIGHT"))
	else:
		txt += Game.L(" Scouts report movement on the flanks, but not which one.")
	txt += Game.L("\n\nYou have %d men in %d regiments. Regiments that survive are whole again tomorrow; the dead are not.") % [Game.total_men(), Game.regiments.size()]
	vb.add_child(Game.label(txt, null, 306))
	var fight := func():
		Game.sfx("horn", -3.0)
		Game.go("battle")
	vb.add_child(Game.button(Game.L("Raise the standard  (fight)"), fight))
	var lose: int = int(Game.grain / 2)
	var toll := func():
		Game.grain -= lose
		st["won"] = true
		Game.write(Game.L("Left %d measures of grain on the road rather than fight for it.") % lose)
		Game.changed.emit()
		for n in poi_nodes:
			if n.has("spr"):
				n["spr"].modulate = Color(0.45, 0.45, 0.45)
			if n.has("barrier"):
				n["barrier"].visible = false
		result(Game.L("The toll"), Game.L("They let the column through between two lines of spears. Nobody on either side says anything."))
	vb.add_child(Game.button(Game.L("Abandon half the grain as a toll and slip past  (-%d grain)") % lose, toll))
	vb.add_child(Game.button(Game.L("Not yet"), close_menu))


# ------------------------------------------------------------------ events
func _finish_event(p: Dictionary, title: String, text: String) -> void:
	art_hint = _event_art(p)
	p["used"] = true
	Game.flags["event_" + str(p["event"])] = true
	Game.changed.emit()
	result(title, text)


func _skip_event(p: Dictionary, title: String) -> void:
	p["used"] = true
	Game.flags["event_" + str(p["event"])] = true
	Game.write(Game.L("Rode past %s without a word.") % title)
	close_menu()


func _event_art(p: Dictionary) -> String:
	return {"south": "village", "west": "seed", "north": "oath", "east": "envoy", "deserters": "deserters"}.get(str(p.get("event", "")), "refugees")


func _show_event(p: Dictionary, title: String, text: String, choices: Array) -> void:
	art_hint = _event_art(p)
	var vb := window(title, 372, false)
	vb.add_child(Game.label(text, null, 358))
	vb.add_child(HSeparator.new())
	for c in choices:
		var b := Game.button(str(c[0]), c[2], c[1])
		b.pressed.connect(func(): stamp(b.get_global_rect().get_center() if is_instance_valid(b) else Vector2(240, 135)))
		b.set("autowrap_mode", TextServer.AUTOWRAP_WORD_SMART)   # Godot 4.3+; ignored on older 4.x
		b.custom_minimum_size = Vector2(358, 0)
		vb.add_child(b)
	vb.add_child(Game.button(Game.L("Ride on without answering  (they will be gone when you return)"), _skip_event.bind(p, title)))


func open_event(p: Dictionary) -> void:
	match str(p["event"]):
		"south":
			_event_south(p)
		"west":
			_event_west(p)
		"north":
			_event_north(p)
		"east":
			_event_east(p)
		"deserters":
			_event_deserters(p)
		_:
			_event_refugees(p)


func _event_south(p: Dictionary) -> void:
	var title := Game.L("Vicus Aquila")
	var a := func():
		Game.grain += 35
		Game.denarii += 10
		Game.flags["village_taken"] = true
		Game.write(Game.L("Collected Vicus Aquila's arrears in full under lawful writ. Sixty people, five measures left."))
		_finish_event(p, title, Game.L("It is done before noon. It is entirely legal. A child follows the carts as far as the milestone."))
	var b := func():
		Game.grain += 17
		Game.flags["falsified"] = true
		Game.write(Game.L("Took half from Vicus Aquila. Wrote that it was paid in full. That is a capital crime."))
		_finish_event(p, title, Game.L("The headman watches you write the lie and says nothing. If an auditor ever compares the ledgers, it is your neck."))
	var c := func():
		Game.grain -= 8
		var r = Game.regiments[0]
		r["men"] = min(Game.MAX_MEN, int(r["men"]) + 6)
		Game.marched += 6
		Game.flags["lore_south"] = true
		Game.write(Game.L("Gave Vicus Aquila eight measures of the Emperor's grain. Six of their sons joined the column."))
		_finish_event(p, title, Game.L("Six young men fall in behind the standard. Now they are yours to feed, and yours to bring back."))
	_show_event(p, title, Game.L("An imperial village, on your own side of the border. The ledger says they owe 35 measures. The headman shows you the granary: it holds perhaps 40, and there are sixty people.\n\"You have the writ,\" he says. \"I can read.\""), [
		[Game.L("Collect in full.  +35 grain, +10 denarii"), true, a],
		[Game.L("Take half and write 'paid in full'.  +17 grain"), true, b],
		[Game.L("Leave them a tithe of yours.  -8 grain, 6 villagers enlist"), Game.grain >= 8, c],
	])


func _event_west(p: Dictionary) -> void:
	var title := Game.L("The Thorncrown seed-keepers")
	var a := func():
		Game.grain += 45
		Game.add_item("seed_pouch")
		Game.flags["west_hostile"] = true
		Game.rebuild_battle()
		Game.write(Game.L("Took the Thorncrown's last seed as tax. There will be no planting there in spring."))
		_finish_event(p, title, Game.L("They do not resist. As the carts roll, horns sound from three directions in the trees - not an attack. A count."))
	var has_salt: bool = Game.inventory.has("salt")
	var b := func():
		if not Game.remove_item("salt"):
			Game.denarii -= 20
		Game.omen["flank"] = true
		Game.omen["count"] = true
		Game.add_item("leather")
		Game.flags["lore_west"] = true
		Game.promise("west", Game.L("Thorncrown: their seed was left in the ground."))
		Game.set_promise("west", "kept")
		Game.write(Game.L("Left the Thorncrown seed untouched and paid for passage. The Emperor's ledger is 45 measures short for it."))
		_finish_event(p, title, Game.L("The matron sends a boy to walk with your scouts. He shows them exactly where the next warband waits, and from which side. You receive cured hides, and no grain at all."))
	var c := func():
		Game.grain += 15
		Game.write(Game.L("Took a third of the Thorncrown seed. Told myself it was a compromise."))
		_finish_event(p, title, Game.L("Enough left to plant a thin field. Enough taken that they will remember your face."))
	_show_event(p, title, Game.L("The ledger lists 45 measures of 'grain tax' from the forest tribes. What they bring out, on a bark tray, is seed. All of it. A matron in a bone mask sets it down and steps back.\n\"If you take it, we eat this winter's bark and plant nothing in spring.\""), [
		[Game.L("Seize the seed.  +45 grain, +Seed Grain offering; the forest turns hostile"), true, a],
		[Game.L("Leave the seed; pay for passage.  ") + (Game.L("-Salt Cone") if has_salt else Game.L("-20 denarii")) + Game.L("; their scouts reveal the next battle"), has_salt or Game.denarii >= 20, b],
		[Game.L("Take a third and call it the tax.  +15 grain"), true, c],
	])


func _event_north(p: Dictionary) -> void:
	var title := Game.L("The Frostbay oath-stone")
	var have: bool = Game.inventory.has("relic_horn")
	var a := func():
		Game.remove_item("relic_horn")
		Game.grain += 20
		Game.add_regiment("shield", 16, Game.L("Frostbay Oathshields"), 1.4)
		Game.flags["lore_north"] = true
		Game.promise("horn", Game.L("Frostbay: the Ancestral Horn returned."))
		Game.set_promise("horn", "kept")
		Game.write(Game.L("Gave the Emperor's offering back to the people it was taken from. The ledger is one offering short."))
		_finish_event(p, title, Game.L("They carry it away wrapped in a cloak, like a child. Sixteen huge men fall in at the rear of your column with dried fish for twenty."))
	var b := func():
		Game.add_regiment("shield", 16, Game.L("Frostbay Oathshields"), 1.4)
		Game.flags["lore_north"] = true
		Game.promise("horn", Game.L("Frostbay: return the Ancestral Horn at journey's end."))
		Game.write(Game.L("Swore on the Frostbay stone to return the horn. I still carry it, and it is still on the Emperor's list."))
		_finish_event(p, title, Game.L("You get the regiment today and keep the offering - until the Great Altar, where one of the two promises you have made about this horn will have to break."))
	var c := func():
		Game.flags["north_hostile"] = true
		Game.rebuild_battle()
		Game.write(Game.L("Refused Frostbay their horn."))
		_finish_event(p, title, Game.L("The speaker nods slowly, as if you had confirmed something. The shield-wall opens. There are more of them further up the road now."))
	var room: bool = Game.regiments.size() < Game.MAX_REGS
	_show_event(p, title, Game.L("A shield-wall waits across the road, not hostile yet. Their speaker is a head taller than your horse.\n\"You carry our fathers' horn in your baggage, listed as 'offering'. Return it and our oathshields march with you. Burn it in the south and we will not forget which officer carried it there.\""), [
		[Game.L("Hand it over now.  -Ancestral Horn; an Oathshield regiment and 20 grain"), have and room, a],
		[Game.L("Swear on the stone to return it at journey's end.  Oathshields join now"), have and room, b],
		[Game.L("Refuse. The horn is imperial property.  More of them will hold the road"), true, c],
	])


func _event_east(p: Dictionary) -> void:
	var title := Game.L("A veiled envoy")
	var ups: Array = Game.upgrades.keys().filter(func(k): return Game.lvl(k) > 0)
	var a := func():
		Game.flags["free_omens"] = true
		Game.flags["lore_east"] = true
		Game.flags["treason"] = true
		Game.omen["count"] = true
		Game.omen["flank"] = true
		Game.write(Game.L("Broke the Emperor's seal for the Duskviolet Court. That is treason. I can now see what is coming."))
		_finish_event(p, title, Game.L("The clerk copies quickly. In return the astrologer gives you a marked calendar: where and when each enemy on your road will strike. The wax will not go back on."))
	var b := func():
		var lost: String = str(ups[0])
		for id in ups:           # an art first, so no art is left above its corps
			if int(Game.TREE[id]["ring"]) == 1:
				lost = str(id)
		Game.upgrades[lost] = Game.lvl(lost) - 1
		Game.add_item("codex")
		Game.flags["lore_east"] = true
		var nm := Game.L(str(Game.TREE[lost]["name"]))
		Game.write(Game.L("Let the Duskviolet seal away what the men knew of %s, for a codex.") % nm)
		_finish_event(p, title, Game.L("The astrologer touches brazier smoke to your centurions' foreheads. By evening nobody in camp can remember how %s was drilled. You hold a codex the Empire will accept as an offering.") % nm)
	var c := func():
		Game.write(Game.L("Refused the Duskviolet envoy."))
		_finish_event(p, title, Game.L("\"Then walk blind,\" she says, without malice. The brazier goes out by itself."))
	_show_event(p, title, Game.L("A Duskviolet astrologer waits by the road with a brazier and a clerk. \"We keep the calendar. We know what this year's omen was, and why your King forbade its reading. You carry sealed orders with the Emperor's mark. Let my clerk copy them - or pay in the other coin we take.\""), [
		[Game.L("Break the imperial seal.  Every future battle is fully foretold"), true, a],
		[Game.L("Pay in memory.  Lose a learned doctrine; gain the Sealed Codex (offering)"), ups.size() > 0, b],
		[Game.L("Refuse both."), true, c],
	])


func _event_deserters(p: Dictionary) -> void:
	var title := Game.L("Three men in the grain cart")
	var a := func():
		Game.lose_men(3)
		Game.battle_buff["dmg"] = 0.15
		Game.write(Game.L("Had three deserters killed in front of the column. One was the signifer's brother."))
		_finish_event(p, title, Game.L("It takes less time than striking a tent. The drill is very sharp the next morning."))
	var b := func():
		Game.grain = max(0, Game.grain - 6)
		Game.write(Game.L("Pardoned three deserters."))
		_finish_event(p, title, Game.L("They go back to their files. Some men look relieved. Some are doing arithmetic about sacks and boots."))
	var c := func():
		Game.lose_men(3)
		Game.fallen -= 3
		Game.write(Game.L("Sent three men home with letters. Called it a courier detail."))
		_finish_event(p, title, Game.L("You write to the fort that grain is coming. You write it as if you knew."))
	_show_event(p, title, Game.L("The night watch drags three of your own out of the baggage: a sack of grain each, boots packed for the road home. One of them is the standard-bearer's brother. The column is watching to see what a promise from you is worth."), [
		[Game.L("Execute them before the standard.  -3 men; +15% damage next battle"), true, a],
		[Game.L("Pardon them. The grain is already eaten.  -6 grain"), true, b],
		[Game.L("Send them home with letters for the fort.  -3 men"), true, c],
	])


func _event_refugees(p: Dictionary) -> void:
	var title := Game.L("Refugees on the road")
	var a := func():
		Game.grain -= 8
		var r = Game.regiments[Game.regiments.size() - 1]
		r["men"] = min(Game.MAX_MEN, int(r["men"]) + 4)
		Game.marched += 4
		Game.write(Game.L("Fed forty strangers with grain that belongs to the Emperor and the fort."))
		_finish_event(p, title, Game.L("Four of the younger ones ask for spears. The old woman keeps her amber."))
	var b := func():
		Game.grain -= 3
		Game.add_item("amber")
		Game.write(Game.L("Bought a village's whole wealth for three measures of grain."))
		_finish_event(p, title, Game.L("A fair price, in a famine. She counts the loaves twice."))
	var c := func():
		Game.write(Game.L("Had the rear guard turn refugees away with spear-butts."))
		_finish_event(p, title, Game.L("They stop following by nightfall. The column moves faster."))
	_show_event(p, title, Game.L("Forty people with handcarts have been following the dust of your column for a day, because soldiers mean food. An old woman holds up a lump of amber the size of a fist - everything her village owned."), [
		[Game.L("Feed them.  -8 grain; four of them take the oath"), Game.grain >= 8, a],
		[Game.L("Take the amber for a day's bread.  -3 grain, +Amber"), Game.grain >= 3, b],
		[Game.L("Drive them off the road."), true, c],
	])


# ------------------------------------------------------------------ crossroads
func _march(o: String) -> void:
	var msg := Game.pass_day()
	if Game.total_men() <= 0:
		Game.game_over_reason = Game.L("The column starved on the road. Nobody reached the Great Altar.")
		Game.go("ending")
		return
	Game.leg += 1
	Game.flags["toast"] = msg
	Game.start_leg(o)
	if Game.flags.has("free_omens"):
		Game.omen["count"] = true
		Game.omen["flank"] = true
	Game.go("expedition")


func _to_altar() -> void:
	Game.pass_day()
	Game.go("ending")


func open_crossroads() -> void:
	var vb := window(Game.L("The road divides"), 400)
	var need := Game.daily_need()
	var warn := ""
	if Game.grain < need:
		warn = Game.L("You have only %d - men will die on the march.") % Game.grain
	vb.add_child(Game.label(Game.L("Night. A day's march either way; the column will eat %d grain. %s") % [need, warn], DIM, 386))
	var opts: Array = st["options"]
	vb.add_child(Game.button(Game.L("Choose on the map"), _cross_map))
	if opts[0] == "altar":
		vb.add_child(Game.label(Game.L("There is only one road left. Torches on the hill ahead: the Great Altar, and the Emperor's auditors."), null, 386))
		vb.add_child(Game.button(Game.L("Go up to the Great Altar"), _to_altar))
		return
	var row := HBoxContainer.new()
	vb.add_child(row)
	for o in opts:
		var rg: Dictionary = Game.REGIONS[o]
		var card := VBoxContainer.new()
		card.custom_minimum_size = Vector2(190, 0)
		row.add_child(card)
		card.add_child(Game.label(Game.L(str(rg["name"])), GOLDC))
		card.add_child(Game.label(Game.L(str(rg["blurb"])), null, 186))
		card.add_child(Game.label(Game.L("Altars here answer to %s.") % Game.L(str(rg["values_text"])), DIM, 186))
		var visited: bool = Game.flags.has("event_" + str(o))
		card.add_child(Game.label(Game.L("You have dealt with them before.") if visited else Game.L("They have something the ledger wants."), DIM, 186))
		var est := 0
		var fb: Dictionary = Game.make_battle(str(o), Game.leg + 1)
		for g in fb["main"]:
			est += int(g[1])
		card.add_child(Game.label(Game.L("Scouts: about %d hold that road, not counting what hides. Recruits there: %d.") % [est, 22 if o == "south" else 12], DIM, 186))
		card.add_child(Game.button(Game.L("March  (%s)") % Game.L(str(rg["road"])), _march.bind(str(o))))


func _cross_map() -> void:
	close_menu()
	open_map(true)
