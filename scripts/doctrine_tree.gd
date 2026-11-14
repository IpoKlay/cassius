extends Control
## The doctrine wheel, four rings deep.
##   ring 0  five corps, 5 drills each (every drill fills 20% of the circle)
##   ring 1  ten arts, 3 levels each, opened by the corps beside them
##   ring 2  ten specialisations - each corps chooses one of two, the other is sealed for the run
##   ring 3  five war-orders (strong, each with a price, at most two) and four lore nodes the road unlocks
## Arts learned together light the synergy threads between them.
## The wheel renders at full screen resolution while open, with an additive light layer for the particles.

const CENTER := Vector2(158, 141)
const RX: Array[float] = [40.0, 75.0, 110.0, 146.0]
const RY: Array[float] = [32.0, 60.0, 88.0, 114.0]
const NR: Array[float] = [11.0, 8.0, 8.0, 9.0]
const PANEL := Rect2(316, 22, 158, 240)
const GOLD := Color(0.96, 0.8, 0.42)
const DIM := Color(0.62, 0.57, 0.5)
const BAD := Color(0.95, 0.45, 0.38)
const LOCKED := Color(0.3, 0.27, 0.25)
const TEAL := Color(0.45, 0.95, 0.85)

var host = null
var ids: Array = []
var syn_ids: Array = []
var pos: Dictionary = {}
var anim: Dictionary = {}
var sel := "spear"
var hover := ""
var t := 0.0
var shake := 0.0
var flash := Color(0, 0, 0, 0)
var purse_shown := 0.0
var purse_pop := 0.0
var parts: Array = []
var rings: Array = []
var coins: Array = []
var floats: Array = []
var pulses: Array = []
var rays: Array = []
var dust: Array = []
var glow: Node2D
var syn_was: Dictionary = {}
var fx = preload("res://scripts/tree_fx.gd").new()
var TX := {}                      # the bronze-shield art: scene, frames, icons, coin, laurel, eagle, wax tablet
var wax_box: StyleBoxTexture
const LAMP := Vector2(26, 244)
## each doctrine's own effect: a burst when learned, a living effect once mastered
const THEME := {
	"spear": "spears", "shield": "dome", "archer": "arrows", "cavalry": "hooves", "eagle": "feathers",
	"whet": "grind", "crit": "glint", "iron": "brackets", "frost": "frost", "fire": "fire",
	"hex": "runes", "bolt": "lightning", "blood": "blood", "forage": "harvest", "medici": "heal",
	"triarii": "wall", "velites": "javelins", "praetor": "laurel", "bash": "impact", "longbow": "beam",
	"skirm": "wind", "cata": "clang", "raider": "dust", "aeterna": "crown", "auxilia": "coins",
	"decim": "skull", "scorch": "wildfire", "forced": "speed", "bloodstd": "bloodbanner", "shieldsdown": "shatter",
	"lore_south": "sun", "lore_north": "aurora", "lore_west": "leaves", "lore_east": "stars",
}


func _ready() -> void:
	size = Vector2(480, 270)
	mouse_filter = Control.MOUSE_FILTER_STOP
	focus_mode = Control.FOCUS_ALL
	theme = Game.theme
	for id in Game.TREE:
		ids.append(id)
		var d: Dictionary = Game.TREE[id]
		var ring := int(d["ring"])
		var a := deg_to_rad(float(d["ang"]))
		pos[id] = CENTER + Vector2(cos(a) * RX[ring], sin(a) * RY[ring])
		anim[id] = {"s": 0.0, "ts": 1.0, "fill": float(Game.lvl(id)) / float(d["max"]), "flash": 0.0, "shake": 0.0, "punch": 0.0, "pop": 0.0}
	for sid in Game.SYNERGIES:
		syn_ids.append(sid)
		syn_was[sid] = Game.syn(sid)
		anim["syn:" + sid] = {"flow": 1.0 if Game.syn(sid) else 0.0}
	purse_shown = Game.denarii
	for i in 90:
		dust.append([Vector2(randf() * 310, randf() * 270), randf_range(0.2, 1.0), randf() * TAU])
	for k in ["tree_bg", "corps_bronze", "corps_gold", "art_bronze", "art_gold", "spec_bronze", "spec_gold", "order_bronze", "order_gold",
			"lore_bronze", "lore_gold", "coin_head", "coin_eagle", "laurel", "eagle", "wax_panel"]:
		TX[k] = Game.load_tex("res://assets/tree/%s.png" % k)
	for id in Game.TREE:
		TX["i_" + str(id)] = Game.load_tex("res://assets/tree/icons/%s.png" % id)
	if TX["wax_panel"] != null:
		wax_box = StyleBoxTexture.new()
		wax_box.texture = TX["wax_panel"]
		for side in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP, SIDE_BOTTOM]:
			wax_box.set_texture_margin(side, 8)
	glow = Node2D.new()
	var gm := CanvasItemMaterial.new()
	gm.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	glow.material = gm
	add_child(glow)
	glow.draw.connect(_draw_glow)
	# open with a flourish: the rings bloom outward one after another
	for id in ids:
		var ring := int(Game.TREE[id]["ring"])
		var tw := create_tween()
		tw.tween_interval(0.05 + ring * 0.09 + randf() * 0.05)
		tw.tween_method(func(v): anim[id]["s"] = v, 0.0, 1.0, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	for r in 4:
		rings.append({"p": CENTER, "r": 4.0, "v": 160.0 + r * 40.0, "life": 0.5, "max": 0.5, "c": GOLD, "w": 0.7, "delay": r * 0.09})
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, 0.18)
	grab_focus.call_deferred()


# ------------------------------------------------------------------ helpers
func _ring(id: String) -> int:
	return int(Game.TREE[id]["ring"])


func _kind(id: String) -> String:
	var d: Dictionary = Game.TREE[id]
	if d.has("lore"):
		return "lore"
	if d.get("order", false):
		return "order"
	return ["corps", "art", "spec", "order"][int(d["ring"])]


func _known(id: String) -> bool:
	## lore stays a silhouette until the road has given it
	var d: Dictionary = Game.TREE[id]
	return not d.has("lore") or Game.flags.has(str(d["lore"])) or Game.lvl(id) > 0


func _sealed(id: String) -> bool:
	var d: Dictionary = Game.TREE[id]
	return d.has("rival") and Game.lvl(str(d["rival"])) > 0


func _bez(a: Vector2, b: Vector2, k: float) -> Vector2:
	var c := ((a + b) * 0.5).lerp(CENTER, 0.42)
	return a.lerp(c, k).lerp(c.lerp(b, k), k)


func _syn_mid(sid: String) -> Vector2:
	var sy: Dictionary = Game.SYNERGIES[sid]
	return _bez(pos[sy["a"]], pos[sy["b"]], 0.5)


func _node_at(p: Vector2) -> String:
	for id in ids:
		if p.distance_to(pos[id]) <= NR[_ring(id)] + 2.5:
			return id
	for sid in syn_ids:
		if p.distance_to(_syn_mid(sid)) <= 4.5:
			return "syn:" + sid
	return ""


# ------------------------------------------------------------------ input
func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var h := _node_at(event.position)
		if h != hover:
			hover = h
			if h != "":
				sel = h
				Game.sfx("click", -21.0, 1.8)
				if not h.begins_with("syn:"):
					_emit(pos[h], 4, Game.TREE[h]["col"], 18.0, "mote")
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			var h := _node_at(event.position)
			if h != "":
				sel = h
				if not h.begins_with("syn:"):
					_try_buy(h)
			elif Rect2(PANEL.position.x + 8, PANEL.end.y - 18, 60, 14).has_point(event.position):
				_back()
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			_back()
		accept_event()


func _input(event: InputEvent) -> void:
	if not (event is InputEventKey) or not event.pressed:
		return
	var handled := true
	match event.keycode:
		KEY_ESCAPE, KEY_BACKSPACE:
			if not event.echo:
				_back()
		KEY_ENTER, KEY_KP_ENTER, KEY_SPACE:
			if not sel.begins_with("syn:"):
				_try_buy(sel)
		KEY_LEFT, KEY_A:
			_step(-1)
		KEY_RIGHT, KEY_D:
			_step(1)
		KEY_UP, KEY_W:
			_jump(1)
		KEY_DOWN, KEY_S:
			_jump(-1)
		_:
			handled = false
	if handled:
		get_viewport().set_input_as_handled()


func _ring_ids(ring: int) -> Array:
	var a: Array = ids.filter(func(i): return _ring(i) == ring)
	a.sort_custom(func(x, y): return float(Game.TREE[x]["ang"]) < float(Game.TREE[y]["ang"]))
	return a


func _step(dir: int) -> void:
	if sel.begins_with("syn:"):
		sel = "spear"
	var r: Array = _ring_ids(_ring(sel))
	sel = r[(r.find(sel) + dir + r.size()) % r.size()]
	Game.sfx("click", -19.0, 1.5)


func _jump(dir: int) -> void:
	if sel.begins_with("syn:"):
		sel = "spear"
	var ring: int = clamp(_ring(sel) + dir, 0, 3)
	if ring == _ring(sel):
		return
	var a := float(Game.TREE[sel]["ang"])
	var best := ""
	var bd := 999.0
	for id in _ring_ids(ring):
		var d: float = abs(wrapf(float(Game.TREE[id]["ang"]) - a, -180.0, 180.0))
		if d < bd:
			bd = d
			best = id
	sel = best
	Game.sfx("click", -19.0, 1.3)


func _back() -> void:
	Game.sfx("click", -12.0, 0.8)
	if host != null:
		host.open_camp()


# ------------------------------------------------------------------ buying
func _try_buy(id: String) -> void:
	var d: Dictionary = Game.TREE[id]
	var cost := Game.tree_cost(id)
	if cost < 0:
		_fail(id, Game.L("MASTERED") if int(d["max"]) > 1 else Game.L("LEARNED"), GOLD)
		return
	var why := Game.tree_block(id)
	if why != "":
		_fail(id, why.split(" - ")[0].to_upper(), BAD)
		return
	if Game.denarii < cost:
		_fail(id, Game.L("NEED %d d") % cost, BAD)
		return
	Game.denarii -= cost
	var lv := Game.lvl(id) + 1
	Game.upgrades[id] = lv
	Game.write(Game.L("Paid %d denarii: %s%s.") % [cost, Game.L(str(d["name"])), (Game.L(", level %d") % lv) if int(d["max"]) > 1 else ""])
	Game.changed.emit()
	Game.sfx("coin_pay", -3.0, 1.0 + 0.03 * lv)       # every purchase: the purse empties
	Game.sfx("coin", -8.0, 1.0 + 0.05 * lv)
	anim[id]["punch"] = -0.35
	purse_pop = 1.0
	var n := 5 + lv * 2 + (6 if _ring(id) >= 2 else 0)
	for i in n:
		coins.append({"a": CENTER + Vector2(0, -2), "b": pos[id], "k": -0.035 * i, "dur": 0.28,
			"h": randf_range(16, 40), "side": randf_range(-24, 24), "id": id if i == n - 1 else ""})


func _impact(id: String) -> void:
	var d: Dictionary = Game.TREE[id]
	var lv := Game.lvl(id)
	var mx := int(d["max"])
	var c: Color = d["col"]
	var a: Dictionary = anim[id]
	var p: Vector2 = pos[id]
	var kind := _kind(id)
	a["flash"] = 1.0
	a["punch"] = 0.6
	var big: bool = (d.has("mile") and d["mile"].has(lv)) or lv == mx or kind in ["spec", "order", "lore"]
	shake = 4.5 if kind == "order" else (3.5 if big else 2.0)
	fx.burst(str(THEME.get(id, "")), p, NR[_ring(id)], lv, mx)
	shake = max(shake, fx.shake)
	_emit(p, 12, GOLD, 70.0, "spark")
	rings.append({"p": p, "r": NR[_ring(id)], "v": 80.0, "life": 0.45, "max": 0.45, "c": c, "w": 1.2})
	if big:
		rings.append({"p": p, "r": 3.0, "v": 150.0, "life": 0.7, "max": 0.7, "c": GOLD, "w": 0.7})
		rays.append({"p": p, "life": 0.9, "max": 0.9, "c": c, "rot": randf() * TAU, "n": 12})
	# each doctrine has its own voice: thunder for the bolt, a chanted blessing for the medici...
	var snd := "up_" + str(THEME.get(id, ""))
	if Game._sfx.has(snd) or ResourceLoader.exists("res://assets/audio/%s.wav" % snd) or FileAccess.file_exists("res://assets/audio/%s.wav" % snd):
		Game.sfx(snd, -1.0 if big else -3.5, 1.0 + 0.025 * (lv - 1))
	else:
		Game.sfx("upgrade", -4.0 if big else -7.0, 0.85 + 0.07 * lv)
	var txt := _roman(lv)
	if d.has("mile") and d["mile"].has(lv):
		txt = Game.L(str(d["mile"][lv])).split(" - ")[0].to_upper()
	elif kind == "spec" or kind == "lore":
		txt = Game.L(str(d["name"])).to_upper()
	elif kind == "order":
		txt = Game.L("ORDER GIVEN")
	elif lv == mx:
		txt = Game.L("MASTERED")
	floats.append({"p": p + Vector2(0, -NR[_ring(id)] - 6), "s": txt, "c": GOLD if big else Color(1, 0.95, 0.85), "life": 1.2, "max": 1.2})
	if kind == "order":
		flash = Color(0.9, 0.15, 0.1, 0.32)
		Game.sfx("horn", -8.0, 0.9)
		for k in 3:
			rings.append({"p": p, "r": 4.0, "v": 120.0 + k * 70.0, "life": 0.8, "max": 0.8, "c": Color(1, 0.3, 0.2), "w": 1.0, "delay": k * 0.08})
	elif lv == mx and kind == "corps":
		flash = Color(1, 0.85, 0.5, 0.18)
		Game.sfx("ritual", -12.0, 1.4)
	if kind == "spec":
		var rv: String = str(d["rival"])
		var rt := create_tween()
		rt.tween_interval(0.25)
		rt.tween_callback(func(): _seal(rv))
	# a corps drill can open arts and specialisations: light runs down every link that just woke
	if kind == "corps":
		for o in ids:
			var od: Dictionary = Game.TREE[o]
			if str(od.get("parent", "")) != id or Game.lvl(o) > 0:
				continue
			var opened: bool = (int(od["ring"]) == 1 and Game.tree_need(o) == lv) or (int(od["ring"]) == 2 and lv == 5)
			if opened:
				pulses.append({"a": p, "b": pos[o], "k": 0.0, "c": od["col"], "id": o, "kind": "unlock"})
	# synergies that just came alive run their thread in from both ends
	for sid in syn_ids:
		if Game.syn(sid) and not syn_was[sid]:
			syn_was[sid] = true
			var sy: Dictionary = Game.SYNERGIES[sid]
			pulses.append({"a": pos[sy["a"]], "b": _syn_mid(sid), "k": 0.0, "c": sy["col"], "id": sid, "kind": "syn", "from": sy["a"]})
			pulses.append({"a": pos[sy["b"]], "b": _syn_mid(sid), "k": 0.0, "c": sy["col"], "id": "", "kind": "syn", "from": sy["b"]})


func _seal(id: String) -> void:
	anim[id]["shake"] = 0.3
	_emit(pos[id], 16, Color(0.6, 0.55, 0.5), 50.0, "shard")
	floats.append({"p": pos[id] + Vector2(0, -14), "s": Game.L("SEALED"), "c": DIM, "life": 1.0, "max": 1.0})
	Game.sfx("thud", -6.0, 0.8)


func _theme_burst(id: String, p: Vector2, k: float) -> void:
	var c: Color = Game.TREE[id]["col"]
	match str(Game.TREE[id]["icon"]):
		"flame":
			_emit(p, int(26 * k), Color(1, 0.6, 0.2), 30.0, "ember")
		"snow":
			_emit(p, int(22 * k), Color(0.75, 0.95, 1), 70.0, "shard")
		"bolt":
			for i in int(4 * k):
				pulses.append({"a": p, "b": p + Vector2.from_angle(randf() * TAU) * randf_range(16, 30), "k": 0.0, "c": c, "id": "", "kind": "arc"})
			_emit(p, int(14 * k), c, 80.0, "spark")
		"eye":
			_emit(p, int(20 * k), c, 30.0, "mote")
		"drop":
			_emit(p, int(18 * k), Color(1, 0.2, 0.25), 50.0, "drop")
		_:
			_emit(p, int(24 * k), c, 60.0, "spark")


func _fail(id: String, why: String, col: Color) -> void:
	anim[id]["shake"] = 0.35
	anim[id]["flash"] = -0.8
	floats.append({"p": pos[id] + Vector2(0, -NR[_ring(id)] - 6), "s": why, "c": col, "life": 1.0, "max": 1.0})
	Game.sfx("thud", -8.0, 1.5)


func _emit(p: Vector2, n: int, c: Color, spd: float, kind: String) -> void:
	fx.emit(kind, p, n, c, spd)


# ------------------------------------------------------------------ simulation
func _process(delta: float) -> void:
	t += delta
	shake = max(0.0, shake - delta * 14.0)
	flash.a = max(0.0, flash.a - delta * 0.9)
	purse_pop = max(0.0, purse_pop - delta * 4.0)
	purse_shown = lerp(purse_shown, float(Game.denarii), min(1.0, delta * 9.0))
	for id in ids:
		var a: Dictionary = anim[id]
		var d: Dictionary = Game.TREE[id]
		var want := float(Game.lvl(id)) / float(d["max"])
		if not _coin_pending(id):
			a["fill"] = lerp(float(a["fill"]), want, min(1.0, delta * 10.0))
		a["ts"] = lerp(float(a["ts"]), 1.2 if id == sel else 1.0, min(1.0, delta * 14.0))
		a["flash"] = move_toward(float(a["flash"]), 0.0, delta * 2.6)
		a["shake"] = max(0.0, float(a["shake"]) - delta)
		a["punch"] = lerp(float(a["punch"]), 0.0, min(1.0, delta * 9.0))
		a["pop"] = max(0.0, float(a["pop"]) - delta * 2.5)
		_ambient(id, delta)
	for sid in syn_ids:
		var sa: Dictionary = anim["syn:" + sid]
		sa["flow"] = move_toward(float(sa["flow"]), 1.0 if (Game.syn(sid) and not _syn_pending(sid)) else 0.0, delta * 2.0)
		if float(sa["flow"]) > 0.5 and randf() < delta * 5.0:
			var sy: Dictionary = Game.SYNERGIES[sid]
			_emit(_bez(pos[sy["a"]], pos[sy["b"]], randf()), 1, sy["col"], 6.0, "mote")
	for q in dust:
		q[0] += Vector2(sin(t * 0.4 + q[2]) * 3.0, -4.0 * q[1]) * delta
		if q[0].y < 0:
			q[0] = Vector2(randf() * 310, 270)
	fx.update(delta)
	for i in range(rings.size() - 1, -1, -1):
		var q: Dictionary = rings[i]
		if float(q.get("delay", 0.0)) > 0.0:
			q["delay"] -= delta
			continue
		q["life"] -= delta
		q["r"] += q["v"] * delta
		if q["life"] <= 0.0:
			rings.remove_at(i)
	for i in range(rays.size() - 1, -1, -1):
		rays[i]["life"] -= delta
		if rays[i]["life"] <= 0.0:
			rays.remove_at(i)
	for i in range(coins.size() - 1, -1, -1):
		var q: Dictionary = coins[i]
		q["k"] += delta / float(q["dur"])
		if q["k"] >= 1.0:
			coins.remove_at(i)
			_emit(q["b"], 3, GOLD, 34.0, "spark")
			Game.sfx("coin", -17.0, randf_range(1.3, 1.8))
			if q["id"] != "":
				_impact(q["id"])
	for i in range(floats.size() - 1, -1, -1):
		var q: Dictionary = floats[i]
		q["life"] -= delta
		q["p"] += Vector2(0, -14.0 * delta)
		if q["life"] <= 0.0:
			floats.remove_at(i)
	for i in range(pulses.size() - 1, -1, -1):
		var q: Dictionary = pulses[i]
		q["k"] += delta * (6.0 if q["kind"] == "arc" else 3.0)
		if q["k"] < 1.0:
			if q["kind"] != "arc" and randf() < 0.6:
				_emit(q["a"].lerp(q["b"], q["k"]), 1, q["c"], 10.0, "mote")
			continue
		pulses.remove_at(i)
		match q["kind"]:
			"unlock":
				anim[q["id"]]["pop"] = 1.0
				anim[q["id"]]["flash"] = 0.8
				_emit(q["b"], 16, q["c"], 46.0, "spark")
				rings.append({"p": q["b"], "r": 5.0, "v": 70.0, "life": 0.4, "max": 0.4, "c": q["c"], "w": 0.8})
				floats.append({"p": q["b"] + Vector2(0, -14), "s": Game.L("UNLOCKED"), "c": q["c"], "life": 0.9, "max": 0.9})
				Game.sfx("upgrade", -13.0, 1.6)
			"syn":
				if q["id"] != "":
					var sy: Dictionary = Game.SYNERGIES[q["id"]]
					var m := _syn_mid(q["id"])
					_emit(m, 30, sy["col"], 70.0, "spark")
					_emit(m, 12, Color(1, 1, 1), 40.0, "mote")
					rings.append({"p": m, "r": 3.0, "v": 110.0, "life": 0.6, "max": 0.6, "c": sy["col"], "w": 1.0})
					rays.append({"p": m, "life": 1.0, "max": 1.0, "c": sy["col"], "rot": randf() * TAU, "n": 10})
					floats.append({"p": m + Vector2(0, -10), "s": Game.L("SYNERGY: ") + Game.L(str(sy["name"])).to_upper(), "c": sy["col"], "life": 1.6, "max": 1.6})
					shake = 3.0
					Game.sfx("ritual", -10.0, 1.7)
	queue_redraw()
	glow.queue_redraw()


func _ambient(id: String, delta: float) -> void:
	var lv := Game.lvl(id)
	if lv <= 0:
		return
	fx.ambient(str(THEME.get(id, "")), id, pos[id], NR[_ring(id)], lv, int(Game.TREE[id]["max"]), delta)


func _coin_pending(id: String) -> bool:
	for q in coins:
		if q["id"] == id:
			return true
	return false


func _syn_pending(sid: String) -> bool:
	var sy: Dictionary = Game.SYNERGIES[sid]
	for q in pulses:
		if q["kind"] == "syn" and (q["id"] == sid or q["from"] == sy["a"] or q["from"] == sy["b"]):
			return true
	return false


# ------------------------------------------------------------------ drawing
func _draw() -> void:
	var off := Vector2(randf_range(-1, 1), randf_range(-1, 1)) * shake * 0.6
	draw_rect(Rect2(0, 0, 480, 270), Color(0.06, 0.04, 0.03))
	if TX.get("tree_bg") != null:
		# the lamp breathes: the whole table brightens and dims a touch
		var fl := 0.93 + 0.05 * sin(t * 7.0) + 0.03 * sin(t * 17.3)
		draw_texture(TX["tree_bg"], Vector2.ZERO, Color(fl, fl * 0.98, fl * 0.95))
	for q in dust:
		draw_rect(Rect2(Vector2(q[0]).round(), Vector2.ONE), Color(1, 0.85, 0.6, 0.15 + 0.3 * q[1] * (0.6 + 0.4 * sin(t * 2.0 + q[2]))))
	draw_set_transform(off)
	if _all_corps_mastered():
		var eg: Texture2D = TX.get("eagle")
		if eg != null:
			draw_texture(eg, (CENTER - Vector2(32, 30)).round(), Color(1, 1, 1, 0.85))
	# synergy threads
	for sid in syn_ids:
		var sy: Dictionary = Game.SYNERGIES[sid]
		var on: float = anim["syn:" + sid]["flow"]
		var sc: Color = sy["col"]
		var n := 18
		var prev: Vector2 = pos[sy["a"]]
		for k in range(1, n + 1):
			var nx := _bez(pos[sy["a"]], pos[sy["b"]], float(k) / n)
			if on > 0.01:
				draw_line(prev, nx, Color(sc.r, sc.g, sc.b, 0.25 + 0.5 * on), 1.0)
			elif k % 2 == 0:
				draw_line(prev, nx, Color(0.4, 0.36, 0.33, 0.35), 1.0)
			prev = nx
		var m := _syn_mid(sid)
		var dm := PackedVector2Array([m + Vector2(0, -3.5), m + Vector2(3.5, 0), m + Vector2(0, 3.5), m + Vector2(-3.5, 0)])
		draw_colored_polygon(dm, Color(0.08, 0.06, 0.05))
		dm.append(dm[0])
		draw_polyline(dm, sc if on > 0.5 else Color(0.45, 0.4, 0.36), 1.4 if sel == "syn:" + sid else 0.8)
		if on > 0.5:
			draw_rect(Rect2(m.floor(), Vector2.ONE), sc.lightened(0.5))
			for j in 2:                                     # two pixel sparks chase each other along the thread
				var k1 := fmod(t * 0.4 + j * 0.5, 1.0)
				for tr in 4:
					var q1 := _bez(pos[sy["a"]], pos[sy["b"]], clamp(k1 - tr * 0.012, 0.0, 1.0))
					var q2 := _bez(pos[sy["a"]], pos[sy["b"]], clamp(1.0 - k1 + tr * 0.012, 0.0, 1.0))
					var ca := Color(sc.r, sc.g, sc.b, on * (1.0 - tr * 0.25)).lightened(0.3 if tr == 0 else 0.0)
					draw_rect(Rect2(q1.floor(), Vector2.ONE), ca)
					draw_rect(Rect2(q2.floor(), Vector2.ONE), ca)
	# links
	for id in ids:
		var d: Dictionary = Game.TREE[id]
		var p: Vector2 = pos[id]
		var ring := int(d["ring"])
		if ring == 0:
			var lv := Game.lvl(id)
			_groove(CENTER + (p - CENTER).normalized() * 17.0, p - (p - CENTER).normalized() * 12.0, lv > 0)
		elif d.has("parent"):
			var par: Vector2 = pos[d["parent"]]
			var a := par + (p - par).normalized() * (NR[0] + 1.0)
			var b := p - (p - par).normalized() * (NR[ring] + 1.0)
			if _sealed(id):
				_dash(a, b, Color(0.35, 0.12, 0.1, 0.8))
			else:
				_groove(a, b, Game.lvl(id) > 0)
		if d.has("rival") and str(d["rival"]) > id:          # the either/or bridge between two specialisations
			var o: Vector2 = pos[d["rival"]]
			var mid := (p + o) * 0.5 + (((p + o) * 0.5) - CENTER).normalized() * 6.0
			draw_line(p.lerp(mid, 0.45), mid, Color(0.6, 0.5, 0.4, 0.5), 1.0)
			draw_line(o.lerp(mid, 0.45), mid, Color(0.6, 0.5, 0.4, 0.5), 1.0)
			draw_string(Game.font, mid + Vector2(-4, 3), Game.L("or"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.75, 0.65, 0.5, 0.8))
	for q in pulses:
		if q["kind"] == "arc":
			continue
		var hp: Vector2 = q["a"].lerp(q["b"], q["k"])
		draw_line(q["a"], hp, q["c"], 1.2)
		draw_rect(Rect2(hp.floor() - Vector2.ONE, Vector2(2, 2)), Color(1, 1, 0.92))
	# the purse at the heart
	# the Emperor's denarius in the boss: it flips when you spend
	var flip := cos(purse_pop * PI * 3.0) if purse_pop > 0.01 else 1.0
	var face: Texture2D = TX.get("coin_head") if flip >= 0.0 else TX.get("coin_eagle")
	if face != null:
		var cw := maxf(2.0, 30.0 * absf(flip)) * (1.0 + purse_pop * 0.15)
		draw_texture_rect(face, Rect2((CENTER - Vector2(cw * 0.5, 15)).round(), Vector2(roundf(cw), 30)), false)
	var ns := str(int(round(purse_shown)))
	var nw: float = Game.font.get_string_size(ns, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
	draw_rect(Rect2((CENTER + Vector2(-nw * 0.5 - 3, 16)).round(), Vector2(nw + 6, Game.font.get_height(8))), Color(0.08, 0.05, 0.03, 0.85))
	draw_string(Game.font, (CENTER + Vector2(-nw * 0.5, 16 + Game.font.get_ascent(8))).round(), ns, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, GOLD)
	for id in ids:                                      # mastered doctrines keep their effect alive, behind the wheel
		if Game.lvl(id) > 0 and Game.tree_cost(id) < 0:
			fx.draw_ambient(self, str(THEME.get(id, "")), id, pos[id], NR[_ring(id)])
	fx.draw_shapes(self, true)
	fx.draw_parts(self, false)
	for id in ids:
		_draw_node(id)
	fx.draw_shapes(self, false)
	fx.draw_parts(self, true)
	for q in coins:
		if q["k"] < 0.0:
			continue
		var k2: float = clamp(q["k"], 0.0, 1.0)
		var cp: Vector2 = q["a"].lerp(q["b"], k2) + Vector2(sin(PI * k2) * q["side"], -sin(PI * k2) * q["h"])
		draw_texture_rect(Game.tex_coin, Rect2(cp - Vector2(2.5, 2.5), Vector2(5, 5)), false)
	for q in pulses:
		if q["kind"] != "arc":
			continue
		var rng := RandomNumberGenerator.new()
		rng.seed = int(q["a"].x * 100.0) + int(q["k"] * 8.0)
		var prev2: Vector2 = q["a"]
		for k in range(1, 5):
			var nx2: Vector2 = q["a"].lerp(q["b"], k / 4.0) + (Vector2(rng.randf_range(-2, 2), rng.randf_range(-2, 2)) if k < 4 else Vector2.ZERO)
			draw_line(prev2, nx2, Color(1, 1, 0.85, 1.0 - q["k"]), 1.0)
			prev2 = nx2
	for q in floats:
		var al2: float = clamp(float(q["life"]) / float(q["max"]) * 2.0, 0.0, 1.0)
		var w: float = Game.font.get_string_size(str(q["s"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
		var fp: Vector2 = q["p"] - Vector2(w / 2.0, 0)
		draw_string(Game.font, fp + Vector2(0.6, 0.6), q["s"], HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0, 0, 0, al2))
		draw_string(Game.font, fp, q["s"], HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(q["c"].r, q["c"].g, q["c"].b, al2))
	draw_set_transform(Vector2.ZERO)
	_draw_panel()
	draw_string(Game.font, Vector2(8, 12), Game.L("DRILL AND DOCTRINE"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, GOLD)
	draw_string(Game.font, Vector2(8, 22), Game.L("%d drills learned   war-orders %d/%d") % [Game.total_drills(), Game.orders_given(), Game.MAX_ORDERS], HORIZONTAL_ALIGNMENT_LEFT, -1, 8, DIM)
	if flash.a > 0.0:
		draw_rect(Rect2(0, 0, 480, 270), flash)


func _shape(kind: String, p: Vector2, r: float, col: Color) -> void:
	match kind:
		"order":
			draw_colored_polygon(PackedVector2Array([p + Vector2(0, -r * 1.15), p + Vector2(r * 1.15, 0), p + Vector2(0, r * 1.15), p + Vector2(-r * 1.15, 0)]), col)
		"lore":
			var pts := PackedVector2Array()
			for k in 6:
				pts.append(p + Vector2.from_angle(k * PI / 3.0 + PI / 6.0) * r * 1.08)
			draw_colored_polygon(pts, col)
		"spec":
			var pts2 := PackedVector2Array()
			for k in 8:
				pts2.append(p + Vector2.from_angle(k * PI / 4.0 + PI / 8.0) * r * 1.04)
			draw_colored_polygon(pts2, col)
		_:
			draw_circle(p, r, col, true, -1.0, false)


func _outline(kind: String, p: Vector2, r: float, col: Color, w: float) -> void:
	match kind:
		"order":
			draw_polyline(PackedVector2Array([p + Vector2(0, -r * 1.15), p + Vector2(r * 1.15, 0), p + Vector2(0, r * 1.15), p + Vector2(-r * 1.15, 0), p + Vector2(0, -r * 1.15)]), col, w)
		"lore":
			var pts := PackedVector2Array()
			for k in 7:
				pts.append(p + Vector2.from_angle(k * PI / 3.0 + PI / 6.0) * r * 1.08)
			draw_polyline(pts, col, w)
		"spec":
			var pts2 := PackedVector2Array()
			for k in 9:
				pts2.append(p + Vector2.from_angle(k * PI / 4.0 + PI / 8.0) * r * 1.04)
			draw_polyline(pts2, col, w)
		_:
			draw_arc(p, r, 0, TAU, 40, col, w)


func _draw_node(id: String) -> void:
	var d: Dictionary = Game.TREE[id]
	var a: Dictionary = anim[id]
	var ring := int(d["ring"])
	var kind := _kind(id)
	var lv := Game.lvl(id)
	var mx := int(d["max"])
	var known := _known(id)
	var sealed := _sealed(id)
	var open_ := Game.tree_open(id)
	var cost := Game.tree_cost(id)
	var can := open_ and cost >= 0 and Game.denarii >= cost
	var c: Color = d["col"] if ((open_ or lv > 0) and not sealed) else LOCKED
	var sc: float = float(a["s"]) * float(a["ts"]) * (1.0 + float(a["punch"]) + float(a["pop"]) * 0.3)
	if sc < 0.08:
		return
	var p: Vector2 = pos[id] + Vector2(sin(t * 60.0) * 3.0 * float(a["shake"]) / 0.35, 0)
	var r: float = NR[ring] * sc
	var mastered := lv >= mx
	var frame_key := kind + ("_gold" if mastered or (kind != "corps" and kind != "art" and lv > 0) else "_bronze")
	var fr: Texture2D = TX.get(frame_key)
	# state: locked pieces are dull, sealed ones near black, learnable ones breathe
	var tint := Color.WHITE
	if sealed:
		tint = Color(0.3, 0.26, 0.26)
	elif lv == 0 and not open_:
		tint = Color(0.36, 0.33, 0.3)
	if can:
		var br := 0.5 + 0.5 * sin(t * 4.0 + ids.find(id))
		draw_arc(p, r + 3.0 + br, 0, TAU, 32, Color(1.0, 0.9, 0.6, 0.55 + 0.4 * br), 1.0)
	# a dark seat under every piece lifts it off the bronze
	draw_circle(p + Vector2(1, 2), r + 2.0, Color(0.03, 0.015, 0.0, 0.55))
	draw_circle(p, r + 1.0, Color(0.05, 0.03, 0.01, 0.6))
	if mastered and kind == "corps" and TX.get("laurel") != null:
		var ls := 36.0 * sc
		draw_texture_rect(TX["laurel"], Rect2((p - Vector2(ls, ls) * 0.5).round(), Vector2(ls, ls).round()), false)
	if fr != null:
		var fs := fr.get_size() * sc
		draw_texture_rect(fr, Rect2((p - fs * 0.5).round(), fs.round()), false, tint)
	else:
		draw_circle(p, r, Color(0.3, 0.2, 0.1))
	# drills: corps fill five slots cut in the rim with molten gold; arts show three pips
	if kind == "corps":
		for k in mx:
			var ang := -PI / 2.0 + TAU * k / mx
			var col := Color(1.0, 0.86, 0.4) if k < lv else Color(0.12, 0.07, 0.04)
			draw_arc(p, 9.9 * sc, ang - 0.2, ang + 0.2, 4, col, 2.0)
	elif kind == "art":
		for k in mx:
			var pp2 := p + Vector2((k - (mx - 1) * 0.5) * 4.0, 10.0) * sc
			draw_rect(Rect2(pp2.round() - Vector2(1, 1), Vector2(3, 3)), Color(0.1, 0.06, 0.04))
			draw_rect(Rect2(pp2.round(), Vector2(1, 1)), Color(1.0, 0.86, 0.4) if k < lv else Color(0.35, 0.28, 0.2))
	var fl: float = a["flash"]
	if fl > 0.0:
		draw_circle(p, r, Color(1, 1, 0.92, fl * 0.6))
	elif fl < 0.0:
		draw_circle(p, r, Color(1, 0.2, 0.15, -fl * 0.45))
	var ic: Texture2D = TX.get("i_" + id)
	if not known:
		draw_string(Game.font, p + Vector2(-2.5, 3), "?", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.25, 0.2, 0.16))
	elif ic != null:
		var isz := 12.0 * sc
		var itint := Color.WHITE if (open_ or lv > 0) and not sealed else Color(0.3, 0.28, 0.26, 0.9)
		draw_texture_rect(ic, Rect2((p - Vector2(isz, isz) * 0.5 - Vector2(0, 1 if kind == "art" else 0)).round(), Vector2(isz, isz).round()), false, itint)
	if sealed:
		draw_line(p + Vector2(-r * 0.6, -r * 0.6), p + Vector2(r * 0.6, r * 0.6), Color(0.75, 0.2, 0.15, 0.9), 1.0)
		draw_line(p + Vector2(r * 0.6, -r * 0.6), p + Vector2(-r * 0.6, r * 0.6), Color(0.75, 0.2, 0.15, 0.9), 1.0)
	if id == sel:
		for k in 4:
			var ang2 := t * 2.0 + k * PI / 2.0
			draw_line(p + Vector2.from_angle(ang2) * (r + 3.0), p + Vector2.from_angle(ang2) * (r + 6.0), Color(1, 0.95, 0.8), 1.0)
	if not open_ and lv == 0 and not sealed and known:
		var lp := p + Vector2(r * 0.45, r * 0.35)
		draw_rect(Rect2(lp, Vector2(3.4, 2.6)), Color(0.3, 0.26, 0.22))
		draw_arc(lp + Vector2(1.7, 0), 1.1, PI, TAU, 8, Color(0.3, 0.26, 0.22), 1.0)


func _groove(a: Vector2, b: Vector2, lit: bool) -> void:
	## a channel cut in the bronze; once a drill is learned, molten gold runs down it
	# unlearned paths stay a faint scratch so the eye goes to what is learned
	if not lit:
		draw_line(a, b, Color(0.08, 0.04, 0.02, 0.5), 1.0)
		return
	draw_line(a, b, Color(0.1, 0.05, 0.02, 0.9), 3.0)
	draw_line(a, b, Color(1.0, 0.78, 0.3), 1.0)
	var k := fmod(t * 0.6 + a.x * 0.01, 1.0)
	draw_rect(Rect2(a.lerp(b, k).round(), Vector2.ONE), Color(1, 1, 0.85))


func _all_corps_mastered() -> bool:
	for id in ids:
		if _kind(id) == "corps" and Game.lvl(id) < int(Game.TREE[id]["max"]):
			return false
	return true


func _roman(n: int) -> String:
	return ["0", "I", "II", "III", "IV", "V", "VI"][clampi(n, 0, 6)]


func _draw_glow() -> void:
	var g := glow
	for id in ids:
		var lv := Game.lvl(id)
		var d: Dictionary = Game.TREE[id]
		var p: Vector2 = pos[id]
		var r: float = NR[int(d["ring"])] * float(anim[id]["s"])
		var c: Color = d["col"]
		if float(anim[id]["flash"]) > 0.0:
			g.draw_circle(p, r * 2.6, Color(c.r, c.g, c.b, 0.3 * float(anim[id]["flash"])), true, -1.0, false)
	g.draw_circle(CENTER, 22.0, Color(1, 0.75, 0.35, 0.05 + 0.03 * sin(t * 1.5)), true, -1.0, false)
	var lf := 0.9 + 0.1 * sin(t * 7.0) + 0.05 * sin(t * 17.3)
	g.draw_circle(LAMP + Vector2(0, -6), 60.0 * lf, Color(1.0, 0.6, 0.25, 0.05), true, -1.0, false)
	g.draw_circle(LAMP + Vector2(0, -6), 26.0 * lf, Color(1.0, 0.7, 0.3, 0.08), true, -1.0, false)
	g.draw_rect(Rect2(LAMP + Vector2(-2, -12 - sin(t * 13.0)), Vector2(3, 4)), Color(1.0, 0.85, 0.4, 0.9))
	# every few seconds a glint of lamplight slides across the shield
	var sw := fmod(t, 7.0) / 1.4
	if sw < 1.0:
		var bx := CENTER.x - 170.0 + sw * 340.0
		for yy in range(int(CENTER.y - 126.0), int(CENTER.y + 126.0), 1):
			var dy := (yy - CENTER.y) / 126.0
			var half := 162.0 * sqrt(maxf(0.0, 1.0 - dy * dy))
			var x0 := bx + (yy - CENTER.y) * 0.5
			if x0 > CENTER.x - half and x0 < CENTER.x + half:
				g.draw_rect(Rect2(x0, yy, 4, 1), Color(1.0, 0.85, 0.55, 0.07 * sin(sw * PI)))
	for id in ids:
		if Game.lvl(id) > 0 and Game.tree_cost(id) < 0:
			fx.draw_ambient_glow(g, str(THEME.get(id, "")), pos[id], NR[_ring(id)])
	fx.draw_glow(g)
	for q in rings:
		if float(q.get("delay", 0.0)) > 0.0:
			continue
		var al: float = float(q["life"]) / float(q["max"])
		var c3: Color = q["c"]
		g.draw_arc(q["p"], q["r"], 0, TAU, 64, Color(c3.r, c3.g, c3.b, al * 0.9), q["w"])
		g.draw_arc(q["p"], q["r"] * 0.92, 0, TAU, 64, Color(c3.r, c3.g, c3.b, al * 0.25), float(q["w"]) * 3.0)
	for q in rays:
		var al3: float = float(q["life"]) / float(q["max"])
		var c5: Color = q["c"]
		var n: int = q["n"]
		var p0: Vector2 = q["p"]
		for k in n:
			var ang: float = float(q["rot"]) + k * TAU / n + (1.0 - al3) * 0.6
			var L: float = 30.0 + (1.0 - al3) * 40.0
			g.draw_colored_polygon(PackedVector2Array([p0, p0 + Vector2.from_angle(ang - 0.06) * L, p0 + Vector2.from_angle(ang + 0.06) * L]), Color(c5.r, c5.g, c5.b, 0.22 * al3))


func _draw_panel() -> void:
	if wax_box != null:
		draw_style_box(wax_box, PANEL.grow(2))
	else:
		draw_rect(PANEL, Color(0.075, 0.055, 0.045, 0.97))
	var x := PANEL.position.x + 8
	var y := PANEL.position.y + 13
	if sel.begins_with("syn:"):
		var sid := sel.substr(4)
		var sy: Dictionary = Game.SYNERGIES[sid]
		var sc: Color = sy["col"]
		draw_rect(PANEL.grow(-6), Color(sc.r, sc.g, sc.b, 0.35), false, 1.0)
		draw_string(Game.font, Vector2(x, y), Game.L(str(sy["name"])).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, sc)
		y += 1 + Game.LH
		draw_string(Game.font, Vector2(x, y), Game.L("SYNERGY   ") + (Game.L("ACTIVE") if Game.syn(sid) else Game.L("dormant")), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, GOLD if Game.syn(sid) else DIM)
		y = _wrap(Game.L(str(sy["desc"])), x, y + 7 + Game.LH, Color(0.92, 0.88, 0.8))
		y += 8
		for k in ["a", "b"]:
			var aid: String = sy[k]
			var have := Game.lvl(aid) > 0
			draw_string(Game.font, Vector2(x, y + Game.LH - 1), ("[x] " if have else "[ ] ") + Game.L(str(Game.TREE[aid]["name"])), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, GOLD if have else DIM)
			y += 1 + Game.LH
		_panel_footer()
		return
	var id := sel
	var d: Dictionary = Game.TREE[id]
	var lv := Game.lvl(id)
	var mx := int(d["max"])
	var kind := _kind(id)
	var known := _known(id)
	var c: Color = d["col"] if known else DIM
	draw_rect(PANEL.grow(-6), Color(c.r, c.g, c.b, 0.35), false, 1.0)
	draw_string(Game.font, Vector2(x, y), Game.L(str(d["name"])).to_upper() if known else "? ? ?", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, c.lightened(0.2))
	y += 1 + Game.LH
	var tags := {"corps": Game.L("CORPS"), "art": Game.L("ART"), "spec": Game.L("SPECIALISATION"), "order": Game.L("WAR-ORDER"), "lore": Game.L("LORE")}
	var head: String = tags[kind]
	if mx > 1:
		head += "   %s / %s" % [_roman(lv), _roman(mx)]
	elif lv > 0:
		head += Game.L("   LEARNED")
	draw_string(Game.font, Vector2(x, y), head, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, DIM)
	y += 5
	if mx > 1:
		for k in mx:
			draw_rect(Rect2(x + k * 14, y, 12, 3), c if k < lv else Color(0.2, 0.18, 0.16))
		y += 6
	if not known:
		y = _wrap(Game.L("The road has not given this yet."), x, y + 3 + Game.LH, DIM)
		y = _wrap(Game.L("Hint: ") + Game.L(str(d["hint"])), x, y + 3 + Game.LH, TEAL)
	else:
		y = _wrap((Game.L("each level: ") if mx > 1 else "") + Game.L(str(d["per"])), x, y + 3 + Game.LH, Color(0.92, 0.88, 0.8))
		if d.has("cost_txt"):
			y = _wrap(Game.L("PRICE: ") + Game.L(str(d["cost_txt"])), x, y + 3 + Game.LH, BAD)
		if d.has("mile"):
			y += 3
			for m in d["mile"]:
				y = _wrap((_roman(int(m)) + "  ") + Game.L(str(d["mile"][m])), x, y + 1 + Game.LH, GOLD if lv >= int(m) else Color(0.55, 0.5, 0.45))
		if d.has("rival"):
			var rn := Game.L(str(Game.TREE[d["rival"]]["name"]))
			y = _wrap((Game.L("SEALED: you chose %s") % rn) if _sealed(id) else (Game.L("Choosing this seals %s for the run") % rn), x, y + 3 + Game.LH, BAD if _sealed(id) else DIM)
		for sid in syn_ids:
			var sy2: Dictionary = Game.SYNERGIES[sid]
			if sy2["a"] == id or sy2["b"] == id:
				var other: String = sy2["b"] if sy2["a"] == id else sy2["a"]
				y = _wrap("+ %s: %s" % [Game.L(str(Game.TREE[other]["name"])), Game.L(str(sy2["name"]))], x, y + 1 + Game.LH, sy2["col"] if Game.syn(sid) else Color(0.5, 0.46, 0.42))
		var why := Game.tree_block(id)
		if lv < mx and why != "":
			y = _wrap(why, x, y + 3 + Game.LH, BAD)
	var cost := Game.tree_cost(id)
	var cy := PANEL.end.y - 40
	if cost < 0:
		draw_string(Game.font, Vector2(x, cy), Game.L("LEARNED") if mx == 1 else Game.L("MASTERED"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, GOLD)
	elif known:
		draw_texture_rect(Game.tex_coin, Rect2(Vector2(x, cy - 7), Vector2(7, 7)), false)
		var ok := Game.denarii >= cost and Game.tree_open(id)
		draw_string(Game.font, Vector2(x + 11, cy), Game.L("%d   (you hold %d)") % [cost, Game.denarii], HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1, 0.95, 0.8) if ok else BAD)
	_panel_footer()


func _panel_footer() -> void:
	var bx := Rect2(PANEL.position.x + 8, PANEL.end.y - 18, 60, 14)
	draw_rect(bx, Color(0.16, 0.12, 0.09))
	draw_rect(bx, Color(0.6, 0.48, 0.3), false, 1.0)
	draw_string(Game.font, bx.position + Vector2(6, 10), Game.L("< BACK"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.92, 0.86, 0.72))
	draw_string(Game.font, Vector2(PANEL.position.x + 74, PANEL.end.y - 20), Game.L("click/Enter: learn"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.45, 0.42, 0.38))
	draw_string(Game.font, Vector2(PANEL.position.x + 74, PANEL.end.y - 9), Game.L("arrows: move"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.45, 0.42, 0.38))


func _wrap(text: String, x: float, y: float, col: Color) -> float:
	var zh := Game.lang != "en"
	var words: PackedStringArray = text.split(" ")
	if zh:
		# Chinese wraps between any two characters; keep ASCII runs together
		words = PackedStringArray()
		var run := ""
		for ch in text:
			if ch.unicode_at(0) < 128 and ch != " ":
				run += ch
			else:
				if run != "":
					words.append(run)
					run = ""
				words.append(ch)
		if run != "":
			words.append(run)
	var sep := "" if zh else " "
	var line := ""
	var maxw := PANEL.size.x - 16
	for w in words:
		var tryl := (line + sep + w).strip_edges() if not zh else line + w
		if Game.font.get_string_size(tryl, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x > maxw and line != "":
			draw_string(Game.font, Vector2(x, y), line, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, col)
			y += Game.LH
			line = w.strip_edges() if zh else w
		else:
			line = tryl
	if line != "":
		draw_string(Game.font, Vector2(x, y), line, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, col)
	return y


func _dash_ellipse(ring: int, n: int, rot: float, col: Color) -> void:
	for i in n:
		if i % 2 == 0:
			var a0 := rot + TAU * i / n
			var a1 := rot + TAU * (i + 1) / n
			draw_line(CENTER + Vector2(cos(a0) * RX[ring], sin(a0) * RY[ring]), CENTER + Vector2(cos(a1) * RX[ring], sin(a1) * RY[ring]), col, 1.0)


func _dash(a: Vector2, b: Vector2, col: Color) -> void:
	var n := int(a.distance_to(b) / 2.5)
	for i in n:
		if i % 2 == 0:
			draw_line(a.lerp(b, float(i) / n), a.lerp(b, float(i + 1) / n), col, 1.0)


# ------------------------------------------------------------------ icons
func _icon(kind: String, p: Vector2, s: float, c: Color) -> void:
	var w := 0.9
	match kind:
		"spear":
			draw_line(p + Vector2(-s, s), p + Vector2(s * 0.6, -s * 0.6), c, w)
			draw_colored_polygon(PackedVector2Array([p + Vector2(s, -s), p + Vector2(s * 0.2, -s * 0.6), p + Vector2(s * 0.6, -s * 0.2)]), c)
		"javelin":
			for k in 2:
				var o := Vector2(k * s * 0.5 - s * 0.25, 0)
				draw_line(p + o + Vector2(-s * 0.6, s), p + o + Vector2(s * 0.4, -s * 0.8), c, w)
		"shield", "shield2":
			var pts := PackedVector2Array([p + Vector2(-s * 0.8, -s), p + Vector2(s * 0.8, -s), p + Vector2(s * 0.8, s * 0.2), p + Vector2(0, s), p + Vector2(-s * 0.8, s * 0.2)])
			if kind == "shield":
				draw_colored_polygon(pts, c)
				draw_circle(p + Vector2(0, -s * 0.15), max(0.6, s * 0.25), c.darkened(0.5), true, -1.0, false)
			else:
				pts.append(pts[0])
				draw_polyline(pts, c, w)
				draw_line(p + Vector2(0, -s), p + Vector2(0, s), c, w)
		"wall":
			for k in 3:
				draw_rect(Rect2(p + Vector2(-s + k * s * 0.7, -s * 0.8), Vector2(s * 0.55, s * 1.6)), c)
		"helm":
			draw_arc(p + Vector2(0, s * 0.2), s * 0.8, PI, TAU, 12, c, w * 1.5)
			draw_rect(Rect2(p + Vector2(-s * 0.8, s * 0.2), Vector2(s * 0.5, s * 0.6)), c)
			draw_rect(Rect2(p + Vector2(s * 0.3, s * 0.2), Vector2(s * 0.5, s * 0.6)), c)
			draw_colored_polygon(PackedVector2Array([p + Vector2(-s * 0.2, -s * 0.6), p + Vector2(s * 0.2, -s * 0.6), p + Vector2(0, -s * 1.1)]), c)
		"fist":
			draw_rect(Rect2(p + Vector2(-s * 0.7, -s * 0.5), Vector2(s * 1.4, s * 1.1)), c)
			for k in 3:
				draw_line(p + Vector2(-s * 0.7 + k * s * 0.47, -s * 0.5), p + Vector2(-s * 0.7 + k * s * 0.47, s * 0.1), c.darkened(0.5), 1.0)
		"bow", "bow2":
			draw_arc(p + Vector2(-s * 0.4, 0), s, -PI / 2.6, PI / 2.6, 12, c, w)
			draw_line(p + Vector2(-s * 0.4, 0) + Vector2.from_angle(-PI / 2.6) * s, p + Vector2(-s * 0.4, 0) + Vector2.from_angle(PI / 2.6) * s, c, 1.0)
			draw_line(p + Vector2(-s * 0.6, 0), p + Vector2(s * (1.3 if kind == "bow2" else 1.0), 0), c, w)
		"feet":
			draw_line(p + Vector2(-s, s * 0.6), p + Vector2(s, -s * 0.6), c, w)
			draw_line(p + Vector2(-s, s * 0.1), p + Vector2(s * 0.4, -s * 0.8), c, w)
			draw_line(p + Vector2(-s * 0.4, s * 0.9), p + Vector2(s, -s * 0.1), c, w)
		"horse":
			draw_arc(p + Vector2(0, s * 0.1), s * 0.8, -PI * 0.3, PI * 1.3, 18, c, w * 1.6)
		"eagle":
			draw_polyline(PackedVector2Array([p + Vector2(-s, -s * 0.5), p + Vector2(-s * 0.4, 0), p + Vector2(0, -s * 0.2), p + Vector2(s * 0.4, 0), p + Vector2(s, -s * 0.5)]), c, w)
			draw_line(p + Vector2(0, -s * 0.2), p + Vector2(0, s * 0.8), c, w)
			draw_circle(p + Vector2(0, -s * 0.55), max(0.6, s * 0.22), c, true, -1.0, false)
		"laurel":
			draw_arc(p, s * 0.85, PI * 0.55, PI * 1.45, 10, c, w)
			draw_arc(p, s * 0.85, -PI * 0.45, PI * 0.45, 10, c, w)
			for k in 4:
				var a := PI * 0.6 + k * 0.25
				draw_circle(p + Vector2.from_angle(a) * s * 0.85, s * 0.18, c, true, -1.0, false)
				draw_circle(p + Vector2.from_angle(PI - a) * s * 0.85, s * 0.18, c, true, -1.0, false)
		"coin":
			draw_arc(p, s * 0.8, 0, TAU, 16, c, w)
			draw_line(p + Vector2(0, -s * 0.5), p + Vector2(0, s * 0.5), c, w)
		"skull":
			draw_circle(p + Vector2(0, -s * 0.15), s * 0.7, c, true, -1.0, false)
			draw_rect(Rect2(p + Vector2(-s * 0.4, s * 0.3), Vector2(s * 0.8, s * 0.5)), c)
			draw_circle(p + Vector2(-s * 0.28, -s * 0.15), s * 0.18, Color(0.05, 0.03, 0.03), true, -1.0, false)
			draw_circle(p + Vector2(s * 0.28, -s * 0.15), s * 0.18, Color(0.05, 0.03, 0.03), true, -1.0, false)
		"leaf":
			draw_colored_polygon(PackedVector2Array([p + Vector2(0, -s), p + Vector2(s * 0.6, 0), p + Vector2(0, s), p + Vector2(-s * 0.6, 0)]), c)
			draw_line(p + Vector2(0, -s), p + Vector2(0, s), c.darkened(0.5), 1.0)
		"swords":
			draw_line(p + Vector2(-s, -s), p + Vector2(s, s), c, w)
			draw_line(p + Vector2(s, -s), p + Vector2(-s, s), c, w)
			draw_line(p + Vector2(-s, s * 0.4), p + Vector2(-s * 0.4, s), c, w)
			draw_line(p + Vector2(s, s * 0.4), p + Vector2(s * 0.4, s), c, w)
		"star":
			draw_colored_polygon(PackedVector2Array([p + Vector2(0, -s), p + Vector2(s * 0.25, -s * 0.25), p + Vector2(s, 0), p + Vector2(s * 0.25, s * 0.25), p + Vector2(0, s), p + Vector2(-s * 0.25, s * 0.25), p + Vector2(-s, 0), p + Vector2(-s * 0.25, -s * 0.25)]), c)
		"snow":
			for k in 3:
				var v := Vector2.from_angle(k * PI / 3.0) * s
				draw_line(p - v, p + v, c, w)
		"flame":
			var fl := sin(t * 9.0) * s * 0.12
			draw_colored_polygon(PackedVector2Array([p + Vector2(fl, -s), p + Vector2(s * 0.7, s * 0.2), p + Vector2(s * 0.4, s * 0.8), p + Vector2(-s * 0.4, s * 0.8), p + Vector2(-s * 0.7, s * 0.2)]), c)
			draw_colored_polygon(PackedVector2Array([p + Vector2(fl * 0.5, -s * 0.2), p + Vector2(s * 0.3, s * 0.5), p + Vector2(-s * 0.3, s * 0.5)]), Color(1, 0.95, 0.7))
		"eye":
			draw_arc(p + Vector2(0, s * 0.7), s * 1.1, -PI * 0.82, -PI * 0.18, 10, c, w)
			draw_arc(p + Vector2(0, -s * 0.7), s * 1.1, PI * 0.18, PI * 0.82, 10, c, w)
			draw_circle(p, max(0.6, s * 0.3), c, true, -1.0, false)
		"bolt":
			draw_colored_polygon(PackedVector2Array([p + Vector2(s * 0.3, -s), p + Vector2(-s * 0.5, s * 0.1), p + Vector2(0, s * 0.1), p + Vector2(-s * 0.3, s), p + Vector2(s * 0.5, -s * 0.1), p + Vector2(0, -s * 0.1)]), c)
		"drop":
			draw_circle(p + Vector2(0, s * 0.3), s * 0.6, c, true, -1.0, false)
			draw_colored_polygon(PackedVector2Array([p + Vector2(0, -s), p + Vector2(s * 0.55, s * 0.1), p + Vector2(-s * 0.55, s * 0.1)]), c)
		"wheat":
			draw_line(p + Vector2(0, s), p + Vector2(0, -s), c, w)
			for k in 3:
				var yy := -s * 0.7 + k * s * 0.5
				draw_line(p + Vector2(0, yy + 1), p + Vector2(-s * 0.5, yy - 1), c, w)
				draw_line(p + Vector2(0, yy + 1), p + Vector2(s * 0.5, yy - 1), c, w)
		"cross":
			draw_rect(Rect2(p + Vector2(-s * 0.25, -s), Vector2(s * 0.5, s * 2.0)), c)
			draw_rect(Rect2(p + Vector2(-s, -s * 0.25), Vector2(s * 2.0, s * 0.5)), c)
