extends Node2D
## Regiment battle in the spirit of Sword & Banner: you command banners, not men.
## Each soldier has his own health, attack timer and target; stats and orders belong to the regiment.

const FIELD := Rect2(0, 20, 480, 214)
const DEPLOY := Rect2(24, 150, 432, 78)
const TYPE_IDX := {"spear": 0, "shield": 1, "archer": 2, "cavalry": 3}
const FACTION_ROW := {"south": 0, "north": 1, "west": 2, "east": 3, "bandit": 4}
const RANKS := [8, 20, 40]
const RANGE := 122.0
const SWITCH_TIME := 3.0
const SWITCH_CD := 10.0
const FORM_MODS := {
	"line": {},
	"wedge": {"speed": 1.1, "charge": 0.5},
	"ring": {"speed": 0.35, "m_armor": 0.8, "dmg": 0.3, "leash": 4.0},
	"loose": {"speed": 1.2, "armor": -0.2, "dodge": 0.6, "leash": 40.0},
	"testudo": {"speed": 0.4, "m_armor": 1.5, "r_armor": 3.0, "dmg": -0.2, "leash": 3.0},
	"dense": {"ranged": -0.3, "volley": 0.5, "leash": 8.0},
}


class Soldier:
	var pos := Vector2.ZERO
	var hp := 1.0
	var reg = null
	var slot := 0
	var cd := 0.0
	var rcd := 0.0
	var target = null
	var think := 0.0
	var walk := 0.0
	var atk_t := 0.0
	var alive := true
	var face := 1
	var debuff := 0.0
	var moving := false
	var burn := 0.0
	var burn_acc := 0.0
	var burn_by = null


class Regiment:
	var team := 0
	var type := "spear"
	var faction := "south"
	var title := ""
	var soldiers: Array = []
	var start_men := 0
	var center := Vector2.ZERO
	var dest := Vector2.ZERO
	var facing := Vector2.UP
	var final_facing := Vector2.ZERO
	var formation := "line"
	var forms: Array = []
	var switch_t := 0.0
	var switch_cd := 0.0
	var hp := 30.0
	var atk := 5.0
	var r_atk := 0.0
	var m_arm := 0.0
	var r_arm := 0.0
	var cd := 1.0
	var speed := 20.0
	var reach := 10.0
	var kills := 0
	var rank := 0
	var retreating := false
	var resting := false
	var order_target = null
	var move_order := false
	var volley_cd := 6.0
	var hidden := false
	var routed := false
	var dead := false
	var elite := false
	var data = null
	var slots: Array = []
	var need_reslot := true
	var is_moving := false
	var move_time := 0.0
	var charge_t := 0.0
	var curse_t := 0.0
	var ranged_hit_t := 0.0
	var ai_t := 0.0
	var ranged_target = null
	var is_flank := false

	func right() -> Vector2:
		return Vector2(-facing.y, facing.x)

	func slot_pos(i: int) -> Vector2:
		var o: Vector2 = slots[min(i, slots.size() - 1)]
		return center + right() * o.x - facing * o.y


var regs: Array = []
var selected: Array = []
var projectiles: Array = []
var corpses: Array = []
var fx: Array = []
var texts: Array = []
var grid: Array = [{}, {}]
var phase := "deploy"
var paused := false
var time := 0.0
var cfg: Dictionary
var omen_flank := false
var flank_arrived := false
var clash_cd := 0.0
var arrow_cd := 0.0

var tex_units: Texture2D
var tex_ground: Texture2D
var tex_obst: Texture2D
var tex_banner: Texture2D
var decor: Array = []

var drag_start := Vector2.ZERO
var dragging := false
var rdrag_start := Vector2.ZERO
var rdragging := false
var drag_reg = null
var volley_mode := false

var ui_root: Control
var top_label: Label
var info_label: Label
var btn_row: HBoxContainer
var begin_btn: Button
var info_t := 0.0
var result_open := false


func _ready() -> void:
	cfg = Game.next_battle
	omen_flank = Game.omen.has("flank")
	glow = Node2D.new()
	var gm := CanvasItemMaterial.new()
	gm.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	glow.material = gm
	add_child(glow)
	glow.draw.connect(_draw_glow)
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	tex_units = load("res://assets/battle/units.png")
	tex_ground = load("res://assets/battle/%s.png" % str(Game.REGIONS[cfg["region"]]["ground"]))
	tex_obst = load("res://assets/battle/obstacles.png")
	tex_banner = load("res://assets/battle/banners.png")
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(str(cfg["name"]))
	for i in 22:
		decor.append([Vector2(rng.randf_range(4, 470), rng.randf_range(24, 226)), rng.randi() % 3])
	_spawn_armies()
	_build_ui()
	Game.music("drums")
	_refresh_panel()


# ------------------------------------------------------------------ setup
func _make_reg(team: int, type: String, men: int, faction: String, mult: float, data = null) -> Regiment:
	var r := Regiment.new()
	var base: Dictionary = Game.UNITS[type]
	var fs: Dictionary = Game.FACTION_STATS[faction]
	r.team = team
	r.type = type
	r.faction = faction
	r.data = data
	r.start_men = men
	r.hp = float(base["hp"]) * float(fs["hp"]) * mult
	r.atk = float(base["atk"]) * float(fs["atk"]) * mult
	r.r_atk = float(base["r_atk"]) * float(fs["atk"])
	r.m_arm = float(base["m_arm"])
	r.r_arm = float(base["r_arm"])
	r.cd = float(base["cd"])
	r.speed = float(base["speed"]) * float(fs["speed"])
	r.reach = float(base["reach"])
	r.forms = Game.FORMS_BY_TYPE[type]
	r.title = Game.L(str(base["name"]))
	r.facing = Vector2.UP if team == 0 else Vector2.DOWN
	if data != null:
		r.title = Game.L(str(data["name"]))
		r.kills = int(data["kills"])
		r.rank = int(data["rank"])
		r.elite = bool(data["elite"])
		r.atk += float(data["atk_bonus"])
		r.r_atk += float(data["r_atk_bonus"])
		r.formation = str(data["formation"])
		if team == 0:
			var L: int = Game.lvl(type)
			match type:
				"spear":
					r.hp *= 1.0 + 0.06 * L
					r.atk *= 1.0 + 0.06 * L
				"shield":
					r.hp *= 1.0 + 0.08 * L
					r.m_arm += 0.4 * L
					r.r_arm += 0.4 * L
				"archer":
					r.r_atk += 0.8 * L
				"cavalry":
					r.atk *= 1.0 + 0.06 * L
					r.speed *= 1.0 + 0.04 * L
			r.hp *= 1.0 + 0.03 * Game.lvl("eagle")
			var lv := func(k): return Game.lvl(k) > 0
			if type == "spear" and lv.call("triarii"):
				r.hp *= 1.4
				r.m_arm += 2.0
				r.r_arm += 2.0
				r.speed *= 0.85
			if type == "spear" and lv.call("velites"):
				r.speed *= 1.3
			if type == "shield" and lv.call("praetor"):
				r.m_arm += 3.0
				r.r_arm += 3.0
				r.atk *= 1.15
			if type == "archer" and lv.call("longbow"):
				r.r_atk += 1.0
			if type == "archer" and lv.call("skirm"):
				r.speed *= 1.4
			if type == "cavalry" and lv.call("cata"):
				r.hp *= 1.5
				r.m_arm += 2.0
				r.r_arm += 2.0
				r.speed *= 0.85
			if type == "cavalry" and lv.call("raider"):
				r.speed *= 1.25
			if lv.call("aeterna"):
				r.hp *= 1.1
			if lv.call("bloodstd"):
				r.hp *= 1.25
			if (type == "spear" or type == "shield") and lv.call("lore_south"):
				r.hp *= 1.15
			if type == "shield" and lv.call("lore_north"):
				r.m_arm += 2.0
				r.r_arm += 2.0
	for i in men:
		var s := Soldier.new()
		s.reg = r
		s.hp = r.hp
		s.face = 1 if team == 0 else -1
		s.rcd = randf() * 2.0
		s.think = randf() * 0.3
		r.soldiers.append(s)
	regs.append(r)
	return r


func _place(r: Regiment, at: Vector2) -> void:
	r.center = at
	r.dest = at
	_reslot(r)
	for s in r.soldiers:
		s.pos = r.slot_pos(s.slot)


func _spawn_armies() -> void:
	# yours: melee in front, archers behind, horse on the wings
	var front: Array = []
	var back: Array = []
	var wings: Array = []
	for d in Game.regiments:
		var fac := "north" if (str(d["name"]).begins_with("Frostbay") or str(d["name"]).begins_with("霜湾")) else "south"
		var r := _make_reg(0, str(d["type"]), int(d["men"]), fac, float(d["mult"]), d)
		if r.type == "archer":
			back.append(r)
		elif r.type == "cavalry":
			wings.append(r)
		else:
			front.append(r)
	for i in front.size():
		_place(front[i], Vector2(240 + (i - (front.size() - 1) / 2.0) * 62, 172))
	for i in back.size():
		_place(back[i], Vector2(240 + (i - (back.size() - 1) / 2.0) * 70, 208))
	for i in wings.size():
		_place(wings[i], Vector2(60 if i % 2 == 0 else 420, 196 - (i / 2) * 26))
	# theirs
	var faction: String = cfg["faction"]
	var main: Array = cfg["main"]
	var melee_i := 0
	var arch_i := 0
	var n_melee := 0
	for g in main:
		if g[0] != "archer":
			n_melee += 1
	for g in main:
		var r := _make_reg(1, str(g[0]), int(g[1]), faction, 1.0)
		if r.type == "archer":
			_place(r, Vector2(150 + arch_i * 170, 44))
			arch_i += 1
			if faction == "west":
				r.formation = "loose"
				r.need_reslot = true
		else:
			_place(r, Vector2(240 + (melee_i - (n_melee - 1) / 2.0) * 66, 78))
			melee_i += 1
	var side: float = -30.0 if cfg["flank_side"] == "left" else 510.0
	var fi := 0
	for g in cfg["flank"]:
		var r := _make_reg(1, str(g[0]), int(g[1]), faction, 1.0)
		r.hidden = true
		r.is_flank = true
		r.facing = Vector2.RIGHT if side < 0.0 else Vector2.LEFT
		if r.type == "cavalry":
			r.formation = "wedge"
		_place(r, Vector2(side, 150 + fi * 34))
		fi += 1


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 5
	add_child(layer)
	ui_root = Control.new()
	ui_root.theme = Game.theme
	ui_root.size = Vector2(480, 270)
	ui_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(ui_root)
	for rc in [Rect2(0, 0, 480, 20), Rect2(0, 234, 480, 36)]:
		var bar := ColorRect.new()
		bar.color = Color.BLACK
		bar.position = rc.position
		bar.size = rc.size
		bar.mouse_filter = Control.MOUSE_FILTER_STOP
		ui_root.add_child(bar)
	top_label = Game.label("")
	top_label.position = Vector2(6, 1)
	top_label.size = Vector2(468, 18)
	ui_root.add_child(top_label)
	info_label = Game.label("", Color(0.75, 0.7, 0.62))
	info_label.position = Vector2(6, 236)
	info_label.size = Vector2(468, 10)
	info_label.clip_text = true
	ui_root.add_child(info_label)
	btn_row = HBoxContainer.new()
	btn_row.position = Vector2(6, 249)
	btn_row.add_theme_constant_override("separation", 3)
	ui_root.add_child(btn_row)
	begin_btn = Game.button(Game.L("BEGIN  [Enter]"), _begin)
	begin_btn.position = Vector2(398, 249)
	ui_root.add_child(begin_btn)


func _refresh_panel() -> void:
	for c in btn_row.get_children():
		c.queue_free()
	if result_open:
		return
	if selected.is_empty():
		btn_row.add_child(Game.label(Game.L("Left-click or drag: select.  Right-click: move / attack (drag to set facing).  Space: pause."), Color(0.6, 0.56, 0.5)))
		return
	var first: Regiment = selected[0]
	var i := 1
	for f in first.forms:
		var b := Game.button("%d %s" % [i, Game.L(str(Game.FORMATIONS[f]["name"]))], _order_formation.bind(str(f)))
		if first.formation == f:
			b.add_theme_color_override("font_color", Color(1, 0.85, 0.4))
		b.tooltip_text = Game.L(str(Game.FORMATIONS[f]["desc"]))
		btn_row.add_child(b)
		i += 1
	if phase == "fight":
		btn_row.add_child(Game.button(Game.L("R Retreat"), _order_retreat))
		btn_row.add_child(Game.button(Game.L("H Halt"), _order_halt))
		if first.type == "archer":
			btn_row.add_child(Game.button(Game.L("V Volley"), _arm_volley))


func _update_labels() -> void:
	var mine := 0
	var theirs := 0
	for r in regs:
		if r.dead:
			continue
		if r.team == 0:
			mine += r.soldiers.size()
		elif not r.hidden:
			theirs += r.soldiers.size()
	var line := Game.L("%s     yours %d   theirs %d in sight") % [Game.L(str(cfg["name"])), mine, theirs]
	if phase == "deploy":
		line += Game.L("\nDEPLOY: drag banners inside the marked ground, pick formations, then begin.")
	elif not flank_arrived:
		if omen_flank:
			line += Game.L("\nOMEN: their hidden force comes from the %s at about %d.  now %d") % [Game.L("LEFT") if cfg["flank_side"] == "left" else Game.L("RIGHT"), int(cfg["flank_time"]), int(time)]
		else:
			line += Game.L("\nSomething is moving beyond the flanks. You do not know which one.   %d") % int(time)
	elif paused:
		line += Game.L("\nPAUSED - orders can still be given.")
	top_label.text = line
	if selected.is_empty():
		info_label.text = ""
	else:
		var r: Regiment = selected[0]
		var st := ""
		if r.switch_t > 0.0:
			st = Game.L("  REFORMING %.1fs (cannot attack)") % r.switch_t
		elif r.switch_cd > 0.0:
			st = Game.L("  formation change ready in %ds") % int(ceil(r.switch_cd))
		if r.retreating:
			st += Game.L("  RESTING - healing") if r.resting else Game.L("  RETREATING")
		if r.type == "archer":
			st += Game.L("  volley %s") % (Game.L("READY") if r.volley_cd <= 0.0 else Game.L("%ds") % int(ceil(r.volley_cd)))
		info_label.text = Game.L("%s%s  %d/%d men  kills %d  [%s: %s]%s") % [r.title, ["", " *", " **", " ***"][r.rank], r.soldiers.size(), r.start_men, r.kills, Game.L(str(Game.FORMATIONS[r.formation]["name"])), Game.L(str(Game.FORMATIONS[r.formation]["desc"])), st]


# ------------------------------------------------------------------ formations
func fm(r: Regiment, key: String) -> float:
	var m: Dictionary = FORM_MODS[r.formation]
	var v: float = float(m.get(key, 1.0 if key == "speed" else 0.0))
	if r.team == 0:
		if key == "charge" and r.formation == "wedge" and Game.lvl("spear") >= 3:
			v = 1.0
		if r.formation == "ring" and Game.lvl("spear") >= 5:
			if key == "m_armor":
				v += 0.4
			elif key == "speed":
				v = 0.55
		if key == "speed" and r.formation == "testudo" and Game.lvl("shield") >= 3:
			v = 0.6
	return v


func _range(r: Regiment) -> float:
	return RANGE * (1.3 if r.team == 0 and r.type == "archer" and Game.lvl("longbow") > 0 else 1.0)


func _reslot(r: Regiment) -> void:
	## Slots are local: x = sideways, y = depth behind the front. Filled left-to-right, front rank first.
	r.need_reslot = false
	var n: int = r.soldiers.size()
	var sx := 10.0 if r.type == "cavalry" else 7.0
	var sy := 9.0 if r.type == "cavalry" else 6.0
	var out: Array = []
	match r.formation:
		"wedge":
			var row := 0
			var placed := 0
			while placed < n:
				var in_row: int = min(row * 2 + 1, n - placed)
				for c in in_row:
					out.append(Vector2((c - (in_row - 1) / 2.0) * sx, row * sy))
				placed += in_row
				row += 1
		"ring":
			var outer: int = n if n <= 22 else int(ceil(n * 0.62))
			var rad: float = max(9.0, outer * sx / TAU * 0.9)
			for i in n:
				if i < outer:
					var a := TAU * i / float(max(1, outer))
					out.append(Vector2(cos(a) * rad, sin(a) * rad * 0.8 + rad))
				else:
					var a2 := TAU * (i - outer) / float(max(1, n - outer))
					out.append(Vector2(cos(a2) * rad * 0.55, sin(a2) * rad * 0.44 + rad))
		_:
			var width := 7
			if r.formation == "loose":
				sx *= 1.7
				sy *= 1.7
			elif r.formation == "testudo":
				sx = 5.0
				sy = 4.5
			elif r.formation == "dense":
				sx = 5.0
				sy = 5.0
				width = 9
			for i in n:
				var row2: int = i / width
				var in_row2: int = min(width, n - row2 * width)
				var col: int = i % width
				out.append(Vector2((col - (in_row2 - 1) / 2.0) * sx, row2 * sy))
	if out.is_empty():
		out.append(Vector2.ZERO)
	r.slots = out
	for i in n:
		r.soldiers[i].slot = i


func _set_formation(r: Regiment, f: String, forced := false) -> bool:
	if r.formation == f or not r.forms.has(f):
		return false
	if phase == "deploy":
		r.formation = f
		_reslot(r)
		for s in r.soldiers:
			s.pos = r.slot_pos(s.slot)
		return true
	if not forced and (r.switch_cd > 0.0 or r.switch_t > 0.0):
		return false
	r.formation = f
	r.switch_t = SWITCH_TIME
	r.switch_cd = SWITCH_TIME + SWITCH_CD
	r.need_reslot = true
	return true


# ------------------------------------------------------------------ orders
func _order_formation(f: String) -> void:
	var any := false
	for r in selected:
		if _set_formation(r, f):
			any = true
	if any:
		Game.sfx("thud", -4.0)
	_refresh_panel()


func _order_retreat() -> void:
	for r in selected:
		r.retreating = true
		r.resting = false
		r.order_target = null
		r.move_order = true
		r.dest = Vector2(clamp(r.center.x, 30.0, 450.0), 224.0)
		r.final_facing = Vector2.UP
	Game.sfx("horn", -10.0, 1.4)


func _order_halt() -> void:
	for r in selected:
		r.order_target = null
		r.dest = r.center
		r.move_order = true
		r.retreating = false
		r.resting = false


func _arm_volley() -> void:
	volley_mode = true


func _begin() -> void:
	if phase != "deploy":
		paused = not paused
		begin_btn.text = Game.L("RESUME [Space]") if paused else Game.L("PAUSE  [Space]")
		return
	phase = "fight"
	begin_btn.text = Game.L("PAUSE  [Space]")
	Game.sfx("horn", -3.0)
	for r in regs:
		if r.team == 0 and r.data != null:
			r.data["formation"] = r.formation
	_refresh_panel()


func _reg_at(p: Vector2, team: int):
	var best = null
	var bd := 12.0 * 12.0
	for r in regs:
		if r.team != team or r.dead or r.hidden:
			continue
		if Rect2(r.center.x - 7, r.center.y - 34, 14, 16).has_point(p):
			return r
		for s in r.soldiers:
			var d: float = p.distance_squared_to(s.pos + Vector2(0, -6))
			if d < bd:
				bd = d
				best = r
	return best


func _unhandled_input(event: InputEvent) -> void:
	if result_open:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_SPACE:
				if phase == "fight":
					_begin()
			KEY_ENTER, KEY_KP_ENTER:
				if phase == "deploy":
					_begin()
			KEY_R:
				if phase == "fight":
					_order_retreat()
			KEY_H:
				_order_halt()
			KEY_V:
				if phase == "fight" and not selected.is_empty() and selected[0].type == "archer":
					volley_mode = true
			KEY_1, KEY_2, KEY_3, KEY_4, KEY_5:
				var idx: int = event.keycode - KEY_1
				if not selected.is_empty() and idx < selected[0].forms.size():
					_order_formation(str(selected[0].forms[idx]))
			KEY_ESCAPE:
				volley_mode = false
				selected = []
				_refresh_panel()
		return
	var mp := get_global_mouse_position()
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				if volley_mode:
					_fire_volleys(mp)
					volley_mode = false
					return
				drag_start = mp
				dragging = true
				drag_reg = null
				if phase == "deploy":
					drag_reg = _reg_at(mp, 0)
					if drag_reg != null:
						selected = [drag_reg]
						_refresh_panel()
			else:
				if dragging and drag_reg == null:
					_finish_select(mp, event.shift_pressed)
				dragging = false
				drag_reg = null
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			if event.pressed:
				rdrag_start = mp
				rdragging = true
				volley_mode = false
			elif rdragging:
				rdragging = false
				_finish_order(mp)
	elif event is InputEventMouseMotion and drag_reg != null and phase == "deploy":
		var c := Vector2(clamp(mp.x, DEPLOY.position.x + 20, DEPLOY.end.x - 20), clamp(mp.y, DEPLOY.position.y + 8, DEPLOY.end.y - 28))
		_place(drag_reg, c)


func _finish_select(mp: Vector2, add: bool) -> void:
	var picked: Array = []
	if drag_start.distance_to(mp) > 6.0:
		var box := Rect2(drag_start, mp - drag_start).abs()
		for r in regs:
			if r.team == 0 and not r.dead and box.has_point(r.center):
				picked.append(r)
	else:
		var r2 = _reg_at(mp, 0)
		if r2 != null:
			picked.append(r2)
	if add:
		for r in picked:
			if not selected.has(r):
				selected.append(r)
	else:
		selected = picked
	if not picked.is_empty():
		Game.sfx("click", -8.0)
	_refresh_panel()


func _finish_order(mp: Vector2) -> void:
	if selected.is_empty():
		return
	var drag := mp - rdrag_start
	if phase == "deploy":
		for r in selected:
			if drag.length() > 10.0:
				r.facing = drag.normalized()
				_place(r, r.center)
		return
	var enemy = _reg_at(rdrag_start, 1)
	var mid := Vector2.ZERO
	for r in selected:
		mid += r.center
	mid /= float(selected.size())
	for r in selected:
		r.retreating = false
		r.resting = false
		if enemy != null:
			r.order_target = enemy
			r.move_order = false
			r.final_facing = Vector2.ZERO
		else:
			r.order_target = null
			r.move_order = true
			var off: Vector2 = (r.center - mid) if selected.size() > 1 else Vector2.ZERO
			r.dest = (rdrag_start + off).clamp(FIELD.position + Vector2(10, 10), FIELD.end - Vector2(10, 6))
			r.final_facing = drag.normalized() if drag.length() > 10.0 else Vector2.ZERO
	fx.append({"p": rdrag_start, "t": 0.5, "kind": "order", "c": Color(1, 0.3, 0.2) if enemy != null else Color(1, 0.9, 0.5)})
	Game.sfx("click", -8.0, 0.8)


# ------------------------------------------------------------------ simulation
func _process(delta: float) -> void:
	delta = min(delta, 0.05)
	info_t -= delta
	if info_t <= 0.0:
		info_t = 0.2
		_update_labels()
	clash_cd -= delta
	arrow_cd -= delta
	if phase == "fight" and not paused and not result_open:
		time += delta
		_rebuild_grid()
		for r in regs:
			if not r.dead:
				_update_reg(r, delta)
		_update_projectiles(delta)
		_tick_burns(delta)
		_check_end()
	_update_parts(delta)
	if glow != null:
		glow.queue_redraw()
	for i in range(fx.size() - 1, -1, -1):
		fx[i]["t"] -= delta
		if fx[i]["t"] <= 0.0:
			fx.remove_at(i)
	for i in range(texts.size() - 1, -1, -1):
		texts[i]["t"] -= delta
		texts[i]["p"] += Vector2(0, -8.0 * delta)
		if texts[i]["t"] <= 0.0:
			texts.remove_at(i)
	queue_redraw()


func _rebuild_grid() -> void:
	grid[0].clear()
	grid[1].clear()
	for r in regs:
		if r.dead or r.hidden:
			continue
		var g: Dictionary = grid[r.team]
		for s in r.soldiers:
			var k: int = int(s.pos.x) / 16 + (int(s.pos.y) / 16) * 64
			if g.has(k):
				g[k].append(s)
			else:
				g[k] = [s]


func _nearest(pos: Vector2, enemy_team: int, radius: float):
	var g: Dictionary = grid[enemy_team]
	var cx: int = int(pos.x) / 16
	var cy: int = int(pos.y) / 16
	var rr: int = int(ceil(radius / 16.0))
	var best = null
	var bd: float = radius * radius
	for yy in range(cy - rr, cy + rr + 1):
		for xx in range(cx - rr, cx + rr + 1):
			var k: int = xx + yy * 64
			if g.has(k):
				for s in g[k]:
					if s.alive:
						var d: float = pos.distance_squared_to(s.pos)
						if d < bd:
							bd = d
							best = s
	return best


func _nearest_reg(r: Regiment, max_d: float, prefer_archers := false):
	var best = null
	var bd := max_d
	for o in regs:
		if o.team == r.team or o.dead or o.hidden:
			continue
		var d: float = r.center.distance_to(o.center)
		if prefer_archers and o.type == "archer":
			d -= 110.0
		if o.retreating:
			d += 50.0
		if d < bd:
			bd = d
			best = o
	return best


func _update_reg(r: Regiment, delta: float) -> void:
	if r.hidden:
		if time >= float(cfg["flank_time"]):
			_reveal_flank()
		return
	r.switch_t = max(0.0, r.switch_t - delta)
	r.switch_cd = max(0.0, r.switch_cd - delta)
	r.volley_cd = max(0.0, r.volley_cd - delta)
	r.charge_t = max(0.0, r.charge_t - delta)
	r.curse_t = max(0.0, r.curse_t - delta)
	r.ranged_hit_t = max(0.0, r.ranged_hit_t - delta)
	if r.need_reslot:
		_reslot(r)
	r.ai_t -= delta
	if r.routed:
		r.order_target = null
		r.dest = Vector2(r.center.x, -40.0)
	elif r.team == 1:
		if r.ai_t <= 0.0:
			r.ai_t = 0.8 + randf() * 0.4
			_ai(r)
	elif r.ai_t <= 0.0:
		r.ai_t = 0.5
		# your regiments defend themselves, but only chase when you have not told them to go somewhere
		if not r.move_order and not r.retreating and r.order_target == null and r.type != "archer":
			r.order_target = _nearest_reg(r, 46.0)
		if r.type == "archer":
			r.ranged_target = _nearest_reg(r, _range(r) + 12.0)
	# pursue target
	if r.order_target != null:
		var t: Regiment = r.order_target
		if t.dead or t.hidden:
			r.order_target = null
			r.dest = r.center
		else:
			var d: float = r.center.distance_to(t.center)
			var stop: float = _range(r) * 0.8 if r.type == "archer" else 16.0
			var dir: Vector2 = (t.center - r.center) / max(d, 0.01)
			r.dest = t.center - dir * stop if d > stop else r.center
			if r.formation != "ring":
				r.facing = dir
			if r.type == "archer":
				r.ranged_target = t
	# move the banner
	var dv: Vector2 = r.dest - r.center
	var dist: float = dv.length()
	if dist > 1.0:
		var sp: float = r.speed * fm(r, "speed") * (1.25 if r.retreating or r.routed else 1.0)
		r.center += dv / dist * min(dist, sp * delta)
		if r.order_target == null and dist > 8.0 and r.formation != "ring":
			r.facing = r.facing.lerp(dv / dist, min(1.0, delta * 6.0)).normalized()
		r.is_moving = true
		r.move_time += delta
	else:
		if r.is_moving and r.final_facing != Vector2.ZERO:
			r.facing = r.final_facing
		r.is_moving = false
		r.move_time = max(0.0, r.move_time - delta)
		r.move_order = false
		if r.retreating:
			r.resting = true
	if r.resting:
		var heal: float = 1.2 * delta
		for s in r.soldiers:
			s.hp = min(r.hp, s.hp + heal)
	if r.routed and r.center.y < 6.0:
		r.soldiers.clear()
		r.dead = true
		selected.erase(r)
		return
	for s in r.soldiers.duplicate():
		if s.alive:
			_update_soldier(s, r, delta)


func _update_soldier(s: Soldier, r: Regiment, delta: float) -> void:
	s.cd -= delta
	s.rcd -= delta
	s.atk_t -= delta
	s.debuff -= delta
	var home: Vector2 = r.slot_pos(s.slot)
	var want: Vector2 = home
	var can_fight: bool = not r.retreating and not r.routed and r.switch_t <= 0.0
	if can_fight:
		s.think -= delta
		if s.target != null and not s.target.alive:
			s.target = null
		if s.think <= 0.0:
			s.think = 0.22 + randf() * 0.12
			var aggro := 22.0
			if r.type == "cavalry":
				aggro = 28.0
			elif r.type == "archer":
				aggro = 12.0
			s.target = _nearest(s.pos, 1 - r.team, aggro)
		if s.target != null:
			var tp: Vector2 = s.target.pos
			var d: float = s.pos.distance_to(tp)
			if d <= r.reach:
				want = s.pos
				s.face = 1 if tp.x >= s.pos.x else -1
				if s.cd <= 0.0:
					_melee(s, s.target)
			else:
				var leash: float = float(FORM_MODS[r.formation].get("leash", 26.0))
				var off: Vector2 = tp - home
				if off.length() > leash:
					tp = home + off.normalized() * leash
				want = tp
		elif r.r_atk > 0.0 and s.rcd <= 0.0 and not r.is_moving and r.ranged_target != null:
			_shoot(s, r)
	var dv: Vector2 = want - s.pos
	var dist: float = dv.length()
	if dist > 0.7:
		var sp: float = r.speed * 1.35 * max(0.5, fm(r, "speed")) * (0.8 if s.debuff > 0.0 else 1.0)
		if r.switch_t > 0.0:
			sp = max(sp, 26.0)
		s.pos += dv / dist * min(dist, sp * delta)
		s.moving = true
		s.walk += delta
		if abs(dv.x) > 0.4 and s.atk_t <= 0.0:
			s.face = 1 if dv.x > 0.0 else -1
	else:
		s.moving = false


func _damage(a: Regiment, t: Soldier, ranged: bool, base: float, extra: float) -> float:
	## design-doc formula:  atk x (1 + sum of damage bonuses) x (1 - reduction)  -  armour x (1 + sum of armour bonuses)
	var d: Regiment = t.reg
	var bonus: float = 1.0 + a.rank * 0.1 + fm(a, "dmg") + extra
	var arm_b: float = d.rank * 0.1 + fm(d, "armor") + fm(d, "r_armor" if ranged else "m_armor")
	if a.team == 0:
		bonus += float(Game.battle_buff["dmg"]) + 0.05 * Game.lvl("whet")
		bonus += 0.1 * Game.lvl("aeterna") + 0.2 * Game.lvl("decim") + 0.3 * Game.lvl("shieldsdown")
		if Game.lvl("lore_west") > 0 and time < 12.0:
			bonus += 0.4
		if Game.syn("wellfed") and Game.grain >= Game.daily_need() * 5:
			bonus += 0.12
	if d.team == 0:
		arm_b += float(Game.battle_buff["armor"]) + 0.07 * Game.lvl("iron") + (0.1 if Game.lvl("eagle") >= 5 else 0.0) - 0.3 * Game.lvl("shieldsdown")
	if d.curse_t > 0.0:
		arm_b -= 0.5
	var armor: float = (d.r_arm if ranged else d.m_arm) * max(0.0, 1.0 + arm_b)
	var raw: float = base * max(0.1, bonus)
	# subtractive armour would let heavy troops take zero; a 15% floor keeps every hit meaningful
	return max(raw - armor, raw * 0.15)


func _melee(s: Soldier, t: Soldier) -> void:
	var r: Regiment = s.reg
	var tr: Regiment = t.reg
	s.cd = r.cd * (1.25 if s.debuff > 0.0 else 1.0) * randf_range(0.9, 1.1)
	s.atk_t = 0.25
	var extra := 0.0
	if r.type == "spear" and tr.type == "cavalry":
		extra += 0.6
	if r.type == "cavalry" and (tr.type == "archer" or tr.type == "shield"):
		extra += 0.4
	if s.debuff > 0.0:
		extra -= 0.2
	if tr.formation != "ring" and tr.facing.dot(s.pos - tr.center) < -5.0:
		extra += 0.5 if r.type == "cavalry" else 0.3      # struck from behind
	var velites: bool = r.team == 0 and r.type == "spear" and Game.lvl("velites") > 0
	var can_charge: bool = r.type == "cavalry" or r.formation == "wedge" or velites
	if can_charge and r.move_time > 1.2 and r.charge_t <= 0.0:
		r.charge_t = 1.6
		r.move_time = 0.0
		texts.append({"p": r.center + Vector2(-14, -30), "t": 1.0, "s": Game.L("CHARGE"), "c": Color(1, 0.85, 0.4)})
	if r.charge_t > 0.0:
		extra += (1.0 if r.type == "cavalry" else (0.6 if velites else 0.0)) + fm(r, "charge")
		if r.type == "cavalry" and r.team == 0 and Game.lvl("raider") > 0:
			extra += 0.5
		if r.type == "cavalry" and r.team == 0 and Game.lvl("cavalry") >= 3:
			extra += 0.5
		if r.formation == "wedge" or (r.type == "cavalry" and r.team == 0 and Game.lvl("cavalry") >= 5):
			t.debuff = 4.0
		if r.type == "cavalry" and tr.formation == "testudo" and not tr.elite and not (tr.team == 0 and Game.lvl("shield") >= 5):
			_set_formation(tr, "line", true)
			texts.append({"p": tr.center + Vector2(-20, -30), "t": 1.2, "s": Game.L("TESTUDO BROKEN"), "c": Color(1, 0.5, 0.4)})
	_strike(t, _damage(r, t, false, r.atk, extra), r, s)
	if clash_cd <= 0.0:
		clash_cd = 0.09
		Game.sfx("clash", -14.0, randf_range(0.85, 1.25))


func _shoot(s: Soldier, r: Regiment) -> void:
	var tr: Regiment = r.ranged_target
	if tr.dead or tr.hidden or tr.soldiers.is_empty():
		r.ranged_target = null
		return
	var t: Soldier = tr.soldiers[randi() % tr.soldiers.size()]
	var d: float = s.pos.distance_to(t.pos)
	if d > _range(r):
		s.rcd = 0.4
		return
	s.rcd = (2.3 + randf() * 0.7) * (0.75 if r.team == 0 and Game.lvl("skirm") > 0 else 1.0)
	s.atk_t = 0.3
	s.face = 1 if t.pos.x >= s.pos.x else -1
	projectiles.append({"a": s.pos + Vector2(0, -8), "b": t.pos + Vector2(0, -5), "k": 0.0, "dur": max(0.25, d / 170.0), "reg": r, "t": t, "volley": false,
		"base": r.r_atk * (1.0 + fm(r, "ranged")) * (1.25 if r.team == 0 and Game.lvl("archer") >= 5 else 1.0)})
	if arrow_cd <= 0.0:
		arrow_cd = 0.25
		Game.sfx("arrow", -16.0, randf_range(0.9, 1.2))


func _volley(r: Regiment, at: Vector2) -> bool:
	if r.volley_cd > 0.0 or r.r_atk <= 0.0 or r.retreating or r.switch_t > 0.0:
		return false
	if r.center.distance_to(at) > _range(r) * 1.25:
		if r.team == 0:
			texts.append({"p": r.center + Vector2(-20, -30), "t": 1.0, "s": Game.L("OUT OF RANGE"), "c": Color(1, 0.6, 0.5)})
		return false
	r.volley_cd = 18.0 * (0.65 if (r.team == 0 and Game.lvl("archer") >= 3) else 1.0) * (0.7 if (r.team == 0 and Game.lvl("lore_east") > 0) else 1.0)
	for s in r.soldiers:
		var land: Vector2 = at + Vector2(randf_range(-22, 22), randf_range(-16, 16))
		s.atk_t = 0.4
		s.rcd = 1.5
		projectiles.append({"a": s.pos + Vector2(0, -8), "b": land, "k": -randf() * 0.25, "dur": max(0.5, s.pos.distance_to(land) / 150.0), "reg": r, "t": null, "volley": true,
			"base": r.r_atk * 1.4 * (1.0 + fm(r, "volley")) * (1.25 if r.team == 0 and Game.lvl("archer") >= 5 else 1.0)})
	Game.sfx("arrow", -4.0, 0.7)
	return true


func _fire_volleys(at: Vector2) -> void:
	for r in selected:
		if r.type == "archer":
			_volley(r, at)


func _update_projectiles(delta: float) -> void:
	for i in range(projectiles.size() - 1, -1, -1):
		var p: Dictionary = projectiles[i]
		p["k"] += delta / float(p["dur"])
		if p["k"] < 1.0:
			continue
		projectiles.remove_at(i)
		var a: Regiment = p["reg"]
		var hit = null
		if p["volley"]:
			hit = _nearest(p["b"] + Vector2(0, 5), 1 - a.team, 7.5)
			if hit != null and randf() < fm(hit.reg, "dodge"):
				hit = null
		else:
			var t = p["t"]
			if t != null and t.alive and t.pos.distance_to(p["b"] + Vector2(0, 5)) < 9.0 and randf() < 0.85:
				hit = t
		if hit != null:
			hit.reg.ranged_hit_t = 4.0
			if a.faction == "east":
				hit.reg.curse_t = 5.0     # Duskviolet hexes rot armour
			_strike(hit, _damage(a, hit, true, float(p["base"]), 0.0), a)
		else:
			fx.append({"p": p["b"] + Vector2(0, 5), "t": 0.3, "kind": "dust", "c": Color(0.5, 0.45, 0.4)})


func _strike(t: Soldier, dmg: float, r: Regiment, s = null) -> void:
	## your doctrines turn some hits into crits, spells and combos; enemy hits pass straight through
	if r.team == 1 and s != null and t.reg.team == 0 and Game.syn("glacier") and randf() < 0.1:
		s.debuff = max(s.debuff, 2.5)
		_fx_frost(s.pos + Vector2(0, -6))
	if r.team == 0 and t.alive:
		var crit := false
		if randf() < 0.05 * Game.lvl("crit"):
			crit = true
			dmg *= 1.8
			_fx_crit(t.pos + Vector2(0, -7))
		if randf() < 0.05 * Game.lvl("fire"):
			if t.burn <= 0.0:
				_emit(t.pos + Vector2(0, -6), 6, Color(1, 0.6, 0.2), 30.0, "ember")
			t.burn = 3.0
			t.burn_by = r
		if randf() < 0.05 * Game.lvl("frost") + (0.1 if Game.lvl("lore_north") > 0 and Game.lvl("frost") > 0 else 0.0):
			t.debuff = max(t.debuff, 2.5)
			_fx_frost(t.pos + Vector2(0, -6))
		if randf() < 0.06 * Game.lvl("hex"):
			t.reg.curse_t = 4.0
			fx.append({"p": t.reg.center + Vector2(0, -10), "t": 0.8, "kind": "hex", "c": Color(0.78, 0.5, 1.0)})
			_emit(t.reg.center + Vector2(0, -8), 10, Color(0.75, 0.45, 1.0), 26.0, "mote")
		if randf() < 0.04 * Game.lvl("bolt"):
			_lightning(t, r)
		if r.type == "shield" and s != null and Game.lvl("bash") > 0 and randf() < 0.2:
			t.debuff = max(t.debuff, 1.5)
			fx.append({"p": t.pos + Vector2(0, -12), "t": 0.8, "kind": "stun", "c": Color(1, 0.95, 0.6)})
		var bl: int = Game.lvl("blood")
		if bl > 0:
			var heal: float = dmg * 0.06 * bl * (3.0 if crit and Game.syn("bloodlust") else 1.0)
			var who = s
			if who == null and Game.syn("surgeons") and not r.soldiers.is_empty():
				who = r.soldiers[randi() % r.soldiers.size()]
			if who != null and who.hp < r.hp:
				who.hp = min(r.hp, who.hp + heal)
				if randf() < 0.3:
					_emit(t.pos + Vector2(0, -6), 3, Color(1, 0.2, 0.25), 18.0, "drop", who.pos + Vector2(0, -8))
	_hurt(t, dmg, r)


func _lightning(t: Soldier, r: Regiment) -> void:
	var from: Vector2 = t.pos + Vector2(0, -6)
	# the first strike comes down from the sky
	fx.append({"p": from + Vector2(randf_range(-10, 10), -70), "q": from, "t": 0.28, "kind": "bolt", "c": Color(1, 1, 0.8), "seed": randi()})
	_emit(from, 10, Color(1, 1, 0.7), 60.0, "spark")
	flash_a = max(flash_a, 0.12)
	var shatter: bool = Game.syn("shatter")
	if shatter and t.debuff > 0.0:
		_hurt(t, 6.0, r)
		_emit(from, 14, Color(0.75, 0.95, 1.0), 70.0, "shard")
	var jumped := 0
	for o in t.reg.soldiers.duplicate():
		if jumped >= 2:
			break
		if o != t and o.alive and o.pos.distance_to(t.pos) < 30.0:
			var to: Vector2 = o.pos + Vector2(0, -6)
			fx.append({"p": from, "q": to, "t": 0.24, "kind": "bolt", "c": Color(0.85, 0.95, 1), "seed": randi()})
			_emit(to, 6, Color(1, 1, 0.7), 40.0, "spark")
			var dmg: float = 5.0 * (1.0 + 0.05 * Game.lvl("whet"))
			if shatter and o.debuff > 0.0:
				dmg *= 2.0
				_emit(to, 12, Color(0.75, 0.95, 1.0), 60.0, "shard")
				texts.append({"p": to + Vector2(-12, -14), "t": 0.6, "s": Game.L("SHATTER"), "c": Color(0.7, 0.95, 1)})
			from = to
			_hurt(o, dmg, r)
			jumped += 1
	Game.sfx("clash", -8.0, 1.9)


func _fx_crit(p: Vector2) -> void:
	fx.append({"p": p, "t": 0.35, "kind": "crit", "c": Color(1, 0.9, 0.4)})
	_emit(p, 8, Color(1, 0.88, 0.45), 55.0, "spark")
	if randf() < 0.25:
		texts.append({"p": p + Vector2(-8, -12), "t": 0.6, "s": Game.L("CRIT"), "c": Color(1, 0.88, 0.4)})


func _fx_frost(p: Vector2) -> void:
	fx.append({"p": p, "t": 0.5, "kind": "frost", "c": Color(0.6, 0.95, 1.0)})
	_emit(p, 7, Color(0.7, 0.95, 1.0), 34.0, "shard")


func _tick_burns(delta: float) -> void:
	for r in regs:
		if r.team != 1 or r.dead:
			continue
		for s in r.soldiers.duplicate():
			if s.burn <= 0.0 or not s.alive:
				continue
			s.burn -= delta
			s.burn_acc += 2.5 * delta * (1.5 if Game.syn("wildfire") and r.curse_t > 0.0 else 1.0)
			if randf() < delta * 14.0:
				_emit(s.pos + Vector2(randf_range(-2, 2), -5), 1, Color(1, 0.55, 0.15), 8.0, "ember")
			if s.burn_acc >= 1.0 and s.burn_by != null:
				var dmg: float = s.burn_acc
				s.burn_acc = 0.0
				var by = s.burn_by
				_hurt(s, dmg, by)
				if not s.alive and Game.syn("wildfire"):
					var spread := 0
					for o in r.soldiers:
						if spread >= 2:
							break
						if o.alive and o.burn <= 0.0 and o.pos.distance_to(s.pos) < 22.0:
							o.burn = 3.0
							o.burn_by = by
							spread += 1
							fx.append({"p": s.pos + Vector2(0, -6), "q": o.pos + Vector2(0, -6), "t": 0.4, "kind": "jump", "c": Color(0.8, 0.45, 1.0)})
					_emit(s.pos + Vector2(0, -6), 12, Color(0.85, 0.45, 1.0), 40.0, "ember")


# ------------------------------------------------------------------ particles
var parts: Array = []
var flash_a := 0.0
var glow: Node2D


func _emit(p: Vector2, n: int, c: Color, spd: float, kind: String, target = null) -> void:
	if parts.size() > 700:
		return
	for i in n:
		var v := Vector2.from_angle(randf() * TAU) * spd * randf_range(0.35, 1.0)
		var life := randf_range(0.3, 0.6)
		match kind:
			"ember":
				v = Vector2(randf_range(-8, 8), randf_range(-26, -10)) * (spd / 20.0)
				life = randf_range(0.5, 1.0)
			"mote":
				life = randf_range(0.6, 1.0)
			"shard":
				v.y -= spd * 0.4
				life = randf_range(0.4, 0.7)
			"drop":
				life = randf_range(0.35, 0.55)
		parts.append({"p": p, "o": p, "v": v, "life": life, "max": life, "c": c, "k": kind, "to": target, "spin": randf() * TAU})


func _update_parts(delta: float) -> void:
	flash_a = max(0.0, flash_a - delta * 1.6)
	for i in range(parts.size() - 1, -1, -1):
		var q: Dictionary = parts[i]
		q["life"] -= delta
		if q["life"] <= 0.0:
			parts.remove_at(i)
			continue
		q["o"] = q["p"]
		match q["k"]:
			"spark":
				q["v"] *= 1.0 - delta * 4.0
				q["v"] += Vector2(0, 60) * delta
			"ember":
				q["v"] += Vector2(sin(time * 6.0 + q["spin"]) * 20.0, -6.0) * delta
			"shard":
				q["v"] += Vector2(0, 120) * delta
				q["spin"] += delta * 12.0
			"mote":
				q["v"] *= 1.0 - delta * 2.5
				q["v"] += Vector2(0, -8) * delta
			"drop":
				if q["to"] != null:
					q["v"] = q["v"].lerp((q["to"] - q["p"]) * 5.0, min(1.0, delta * 8.0))
		q["p"] += q["v"] * delta


func _draw_parts() -> void:
	for q in parts:
		var a: float = clamp(float(q["life"]) / float(q["max"]) * 1.6, 0.0, 1.0)
		var c: Color = q["c"]
		var p: Vector2 = q["p"]
		match q["k"]:
			"spark":
				draw_line(q["o"], p, Color(c.r, c.g, c.b, a), 1.0)
			"shard":
				var d := Vector2.from_angle(q["spin"]) * 1.5
				draw_line(p - d, p + d, Color(c.r, c.g, c.b, a), 1.0)
			"ember":
				var hot: float = float(q["life"]) / float(q["max"])
				draw_rect(Rect2(p.round(), Vector2.ONE), Color(1, 0.4 + 0.5 * hot, 0.15 + 0.4 * hot * hot, a) if c.r > c.b else Color(c.r, c.g, c.b, a))
			_:
				draw_rect(Rect2(p.round(), Vector2.ONE), Color(c.r, c.g, c.b, a))


func _draw_glow() -> void:
	## additive layer: soft light for fire, lightning, frost and every bright particle
	var g := glow
	for q in parts:
		var a: float = clamp(float(q["life"]) / float(q["max"]), 0.0, 1.0)
		var c: Color = q["c"]
		g.draw_circle(q["p"], 2.5, Color(c.r, c.g, c.b, 0.18 * a))
	for f in fx:
		var c2: Color = f["c"]
		var fp: Vector2 = f["p"]
		match f["kind"]:
			"bolt":
				var a2: float = float(f["t"]) / 0.28
				g.draw_circle(f["q"], 10.0, Color(c2.r, c2.g, c2.b, 0.35 * a2))
				g.draw_line(fp, f["q"], Color(c2.r, c2.g, c2.b, 0.25 * a2), 4.0)
			"crit":
				g.draw_circle(fp, 7.0, Color(1, 0.85, 0.4, 0.4 * float(f["t"]) / 0.35))
			"frost":
				g.draw_circle(fp, 6.0, Color(0.5, 0.85, 1.0, 0.35 * float(f["t"]) / 0.5))
			"hex":
				g.draw_circle(fp, 14.0, Color(0.6, 0.3, 1.0, 0.12 * float(f["t"]) / 0.8))
	for r in regs:
		if r.dead or r.team != 1:
			continue
		for s in r.soldiers:
			if s.burn > 0.0:
				var fl := 0.7 + 0.3 * sin(time * 20.0 + s.pos.x)
				g.draw_circle(s.pos + Vector2(0, -5), 4.0, Color(1, 0.45, 0.1, 0.22 * fl))
	if flash_a > 0.0:
		g.draw_rect(Rect2(0, 0, 480, 270), Color(0.8, 0.85, 1.0, flash_a))


func _hurt(t: Soldier, dmg: float, by: Regiment) -> void:
	if not t.alive:
		return
	t.hp -= dmg
	if fx.size() < 120:
		fx.append({"p": t.pos + Vector2(randf_range(-2, 2), -7), "t": 0.18, "kind": "spark", "c": Color(1, 0.95, 0.7)})
	if t.hp > 0.0:
		return
	t.alive = false
	var r: Regiment = t.reg
	r.soldiers.erase(t)
	r.need_reslot = true
	corpses.append([t.pos, FACTION_ROW[r.faction], TYPE_IDX[r.type], t.face])
	if corpses.size() > 420:
		corpses.pop_front()
	by.kills += 1
	if by.rank < 3 and by.kills >= RANKS[by.rank]:
		by.rank += 1
		texts.append({"p": by.center + Vector2(-22, -34), "t": 2.0, "s": Game.L("PROMOTED"), "c": Color(1, 0.85, 0.3)})
		if by.team == 0:
			Game.sfx("upgrade", -8.0)
	if r.soldiers.is_empty():
		r.dead = true
		selected.erase(r)
		texts.append({"p": r.center + Vector2(-24, -20), "t": 2.2, "s": Game.L("DESTROYED"), "c": Color(1, 0.4, 0.35)})
		Game.sfx("thud", -2.0, 0.7)
		_refresh_panel()
	elif r.team == 1 and not r.routed and r.soldiers.size() <= int(r.start_men * 0.22):
		r.routed = true
		texts.append({"p": r.center + Vector2(-16, -20), "t": 2.0, "s": Game.L("ROUTED"), "c": Color(0.9, 0.9, 0.6)})


func _reveal_flank() -> void:
	if flank_arrived:
		return
	flank_arrived = true
	var where := Vector2(20 if cfg["flank_side"] == "left" else 400, 120)
	for r in regs:
		if r.hidden:
			r.hidden = false
			r.dest = Vector2(60 if cfg["flank_side"] == "left" else 420, r.center.y)
	texts.append({"p": where, "t": 3.0, "s": Game.L("AMBUSH!"), "c": Color(1, 0.35, 0.3)})
	Game.sfx("horn", -2.0, 0.75)


func _ai(r: Regiment) -> void:
	var t = _nearest_reg(r, 9999.0, r.type == "cavalry")
	if t == null:
		return
	r.order_target = t
	if r.type == "archer":
		if r.volley_cd <= 0.0 and r.center.distance_to(t.center) < RANGE * 1.1:
			_volley(r, t.center)
	elif r.type == "shield":
		var near = _nearest_reg(r, 60.0)
		if r.ranged_hit_t > 0.0 and near == null:
			_set_formation(r, "testudo")
		elif near != null and r.formation == "testudo":
			_set_formation(r, "line")
	elif r.type == "spear":
		if t.type == "cavalry" and r.center.distance_to(t.center) < 70.0:
			_set_formation(r, "ring")
		elif r.formation == "ring" and t.type != "cavalry":
			_set_formation(r, "line")


func _check_end() -> void:
	var mine := 0
	var theirs := 0
	var hidden_left := 0
	for r in regs:
		if r.dead:
			continue
		if r.team == 0:
			mine += 1
		elif r.hidden:
			hidden_left += 1
		elif not r.routed:
			theirs += 1
	if theirs == 0 and hidden_left > 0:
		_reveal_flank()
		return
	if mine == 0:
		_finish(false)
	elif theirs == 0 and hidden_left == 0:
		_finish(true)


# ------------------------------------------------------------------ aftermath
func _finish(won: bool) -> void:
	result_open = true
	begin_btn.visible = false
	_refresh_panel()
	var lines: Array = []
	var lost_total := 0
	var decimated := 0
	var destroyed: Array = []
	var keep: Array = []
	for r in regs:
		if r.team != 0 or r.data == null:
			continue
		var alive: int = r.soldiers.size()
		var lost: int = r.start_men - alive
		var back := 0
		if won and alive > 0 and Game.lvl("medici") > 0 and Game.lvl("bloodstd") == 0:
			back = int(lost * (0.12 * Game.lvl("medici") + (0.1 if Game.syn("surgeons") else 0.0)))
		if Game.lvl("decim") > 0 and alive + back > 1:
			alive -= 1
			decimated += 1
		lost -= back
		lost_total += lost
		var promo := ""
		if r.rank > int(r.data["rank"]):
			promo = Game.L("   PROMOTED")
		r.data["men"] = alive + back
		r.data["kills"] = r.kills
		r.data["rank"] = r.rank
		if alive + back <= 0:
			destroyed.append(r.title)
			lines.append(Game.L("%s - destroyed") % r.title)
		else:
			keep.append(r.data)
			lines.append(Game.L("%s - %d stand, %d fell%s%s") % [r.title, alive + back, lost, (Game.L("  (%d carried back by the medici)") % back) if back > 0 else "", promo])
	Game.regiments = keep
	Game.fallen += lost_total
	Game.battle_buff = {"dmg": 0.0, "armor": 0.0}
	var title := Game.L("The field is yours") if won else Game.L("The standard has fallen")
	var body := "\n".join(PackedStringArray(lines))
	if won:
		Game.denarii += int(cfg["reward_denarii"])
		Game.sfx_coin_pickup(-8.0)       # quiet: the same screen counts the dead
		Game.grain += int(cfg["reward_grain"])
		Game.add_item(str(cfg["loot"]))
		Game.leg_state["won"] = true
		Game.write(Game.L("Held %s. %d of ours did not get up.") % [Game.L(str(Game.REGIONS[cfg["region"]]["road"])), lost_total])
		for d in destroyed:
			Game.write(Game.L("The %s were destroyed to a man.") % str(d))
		body += Game.L("\n\nTaken from the field: %d denarii, %d grain, %s.") % [int(cfg["reward_denarii"]), int(cfg["reward_grain"]), Game.L(str(Game.ITEMS[cfg["loot"]]["name"]))]
		if Game.lvl("scorch") > 0:
			Game.grain += 15
			body += Game.L("\nTheir stores burned for us: +15 grain.")
		body += Game.L("\nRegiments that still stand will be whole again by morning. The dead stay in the ledger.")
	if decimated > 0:
		body += Game.L("\nDecimation: %d of our own, chosen by lot.") % decimated
		Game.sfx("horn", -4.0, 1.2)
	else:
		Game.write(Game.L("The standard fell on %s.") % Game.L(str(Game.REGIONS[cfg["region"]]["road"])))
		Game.game_over_reason = Game.L("The standard fell on %s, day %d. No grain went home.") % [Game.L(str(Game.REGIONS[cfg["region"]]["road"])), Game.day]
		body += Game.L("\n\nNobody is left to carry the grain.")
	Game.changed.emit()
	var center := CenterContainer.new()
	center.size = Vector2(480, 270)
	ui_root.add_child(center)
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(320, 0)
	center.add_child(panel)
	var vb := VBoxContainer.new()
	panel.add_child(vb)
	vb.add_child(Game.label(title, Color(0.96, 0.8, 0.42)))
	vb.add_child(HSeparator.new())
	vb.add_child(Game.label(body, null, 306))
	vb.add_child(Game.button(Game.L("Return to the column") if won else Game.L("The ledger closes"), _leave.bind(won)))


func _leave(won: bool) -> void:
	Game.go("expedition" if won else "ending")


# ------------------------------------------------------------------ drawing
func _by_y(a, b) -> bool:
	return a.pos.y < b.pos.y


func _draw() -> void:
	draw_texture_rect(tex_ground, FIELD, true)
	for d in decor:
		draw_texture_rect_region(tex_obst, Rect2(d[0], Vector2(16, 16)), Rect2(int(d[1]) * 16, 0, 16, 16), Color(1, 1, 1, 0.9))
	# far tree line and edge shade give the tilted-ground feel
	for i in 6:
		draw_rect(Rect2(0, 20 + i * 2, 480, 2), Color(0, 0, 0, 0.5 - i * 0.08))
	if phase == "deploy":
		draw_rect(DEPLOY, Color(1, 0.85, 0.4, 0.08))
		draw_rect(DEPLOY, Color(1, 0.85, 0.4, 0.7), false, 1.0)
	if (phase == "deploy" or not flank_arrived) and omen_flank:
		var left: bool = cfg["flank_side"] == "left"
		var ax := 4.0 if left else 476.0
		var dirx := 1.0 if left else -1.0
		var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 200.0)
		for k in 3:
			var x0 := ax + dirx * (k * 9 + pulse * 4.0)
			draw_colored_polygon(PackedVector2Array([Vector2(x0, 140), Vector2(x0 + dirx * 8, 150), Vector2(x0, 160)]), Color(1, 0.3, 0.25, 0.85 - k * 0.2))
		draw_string(Game.font, Vector2(8 if left else 392, 134), Game.L("OMEN: FLANK"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1, 0.6, 0.5))
	for c in corpses:
		var p: Vector2 = c[0]
		var src := Rect2((int(c[2]) * 4 + 3) * 16, int(c[1]) * 16, 16, 16)
		draw_texture_rect_region(tex_units, Rect2(p.x - 8, p.y - 14, 16, 16), src, Color(0.8, 0.75, 0.75, 0.9))
	# orders and selection
	for r in selected:
		if r.dead:
			continue
		if r.order_target != null:
			draw_dashed_line(r.center, r.order_target.center, Color(1, 0.35, 0.25, 0.8), 1.0, 4.0)
		elif r.center.distance_to(r.dest) > 4.0:
			draw_dashed_line(r.center, r.dest, Color(1, 0.9, 0.5, 0.8), 1.0, 4.0)
			draw_arc(r.dest, 4.0, 0, TAU, 10, Color(1, 0.9, 0.5), 1.0)
		for s in r.soldiers:
			draw_rect(Rect2(s.pos.x - 3, s.pos.y, 6, 1), Color(1, 0.9, 0.4, 0.9))
		draw_line(r.center, r.center + r.facing * 12.0, Color(1, 0.9, 0.4, 0.6), 1.0)
		if r.type == "archer":
			draw_arc(r.center, _range(r), 0, TAU, 48, Color(1, 1, 1, 0.12), 1.0)
	# soldiers, painter-sorted
	var all: Array = []
	for r in regs:
		if r.dead or r.hidden:
			continue
		all.append_array(r.soldiers)
	all.sort_custom(_by_y)
	for s in all:
		var r2: Regiment = s.reg
		var frame := 0
		if s.atk_t > 0.0:
			frame = 2
		elif s.moving and int(s.walk * 8.0) % 2 == 1:
			frame = 1
		var src2 := Rect2((int(TYPE_IDX[r2.type]) * 4 + frame) * 16, int(FACTION_ROW[r2.faction]) * 16, 16, 16)
		var col := Color.WHITE
		if s.hp < r2.hp * 0.35:
			col = Color(1, 0.72, 0.72)
		if r2.curse_t > 0.0:
			col = col * Color(0.8, 0.6, 1.0)
		if r2.switch_t > 0.0:
			col = col * Color(0.8, 0.8, 0.8)
		if s.face < 0:
			src2.position.x += 256.0      # mirrored half of the sheet
		draw_texture_rect_region(tex_units, Rect2(s.pos.x - 8, s.pos.y - 14, 16, 16), src2, col)
	for p in projectiles:
		var k: float = clamp(float(p["k"]), 0.0, 1.0)
		if float(p["k"]) < 0.0:
			continue
		var a: Vector2 = p["a"]
		var b: Vector2 = p["b"]
		var h: float = a.distance_to(b) * (0.32 if p["volley"] else 0.16)
		var pos: Vector2 = a.lerp(b, k) + Vector2(0, -sin(PI * k) * h)
		var k2: float = min(1.0, k + 0.06)
		var nxt: Vector2 = a.lerp(b, k2) + Vector2(0, -sin(PI * k2) * h)
		var dirv: Vector2 = (nxt - pos).normalized()
		draw_line(pos - dirv * 4.0, pos, Color(0.93, 0.9, 0.8), 1.0)
	for f in fx:
		var fp: Vector2 = f["p"]
		var c: Color = f["c"]
		match f["kind"]:
			"spark":
				var e: float = (0.18 - float(f["t"])) * 30.0
				draw_rect(Rect2(fp.x - e, fp.y, 1, 1), c)
				draw_rect(Rect2(fp.x + e, fp.y - 1, 1, 1), c)
				draw_rect(Rect2(fp.x, fp.y - e, 1, 1), c)
			"dust":
				draw_rect(Rect2(fp.x - 1, fp.y - 1, 2, 1), c)
				draw_rect(Rect2(fp.x - 2 - (0.3 - float(f["t"])) * 8.0, fp.y - 2, 1, 1), c)
				draw_rect(Rect2(fp.x + 2 + (0.3 - float(f["t"])) * 8.0, fp.y - 2, 1, 1), c)
			"order":
				draw_arc(fp, 3.0 + (0.5 - float(f["t"])) * 14.0, 0, TAU, 12, Color(c.r, c.g, c.b, float(f["t"]) * 2.0), 1.0)
			"crit":
				var k0: float = 1.0 - float(f["t"]) / 0.35
				var e2: float = 2.0 + k0 * 9.0
				for k in 8:
					var dv := Vector2.from_angle(k * PI / 4.0 + PI / 8.0) * e2 * (1.0 if k % 2 == 0 else 0.55)
					draw_line(fp + dv * 0.35, fp + dv, Color(c.r, c.g, c.b, 1.0 - k0), 1.0)
				draw_rect(Rect2(fp - Vector2.ONE, Vector2(2, 2)), Color(1, 1, 0.9, 1.0 - k0))
			"frost":
				var k1: float = 1.0 - float(f["t"]) / 0.5
				var e3: float = 2.0 + k1 * 6.0
				for k in 6:
					var dv2 := Vector2.from_angle(k * PI / 3.0) * e3
					draw_line(fp, fp + dv2, Color(c.r, c.g, c.b, 1.0 - k1), 1.0)
					draw_rect(Rect2((fp + dv2 * 0.6 + Vector2.from_angle(k * PI / 3.0 + 1.2) * 1.5).round(), Vector2.ONE), Color(1, 1, 1, 1.0 - k1))
			"hex":
				var k2: float = 1.0 - float(f["t"]) / 0.8
				var rr: float = 6.0 + k2 * 12.0
				draw_arc(fp, rr, 0, TAU, 20, Color(c.r, c.g, c.b, (1.0 - k2) * 0.9), 1.0)
				for k in 6:                       # runes riding the circle
					var ap := time * 3.0 + k * TAU / 6.0
					var rp: Vector2 = fp + Vector2.from_angle(ap) * rr
					draw_rect(Rect2(rp.round() - Vector2(1, 1), Vector2(2, 2)), Color(0.95, 0.75, 1.0, 1.0 - k2))
			"bolt":
				var q: Vector2 = f["q"]
				var rng := RandomNumberGenerator.new()
				rng.seed = int(f["seed"]) + int(f["t"] * 30.0)        # re-jag a few times while it lives
				var prev := fp
				var steps := 6
				for k in range(1, steps + 1):
					var nx: Vector2 = fp.lerp(q, float(k) / steps)
					if k < steps:
						nx += Vector2(rng.randf_range(-4, 4), rng.randf_range(-2, 2))
						if rng.randf() < 0.3:                          # a little side branch
							draw_line(nx, nx + Vector2(rng.randf_range(-6, 6), rng.randf_range(2, 7)), Color(c.r, c.g, c.b, 0.7), 1.0)
					draw_line(prev, nx, Color(1, 1, 1), 1.0)
					prev = nx
			"jump":
				var k3: float = 1.0 - float(f["t"]) / 0.4
				var mid: Vector2 = fp.lerp(f["q"], k3) + Vector2(0, -sin(PI * k3) * 8.0)
				draw_rect(Rect2(mid.round() - Vector2.ONE, Vector2(2, 2)), c)
			"stun":
				for k in 3:
					var ap2 := time * 6.0 + k * TAU / 3.0
					draw_rect(Rect2((fp + Vector2(cos(ap2) * 5.0, sin(ap2) * 2.0)).round(), Vector2.ONE), c)
			"flame":
				pass
	_draw_parts()
	# banners
	for r in regs:
		if r.dead or r.hidden:
			continue
		var bp: Vector2 = r.center + Vector2(0, -20)
		var sel: bool = selected.has(r)
		var flag := Color(0.86, 0.2, 0.16) if r.team == 0 else Color(0.2, 0.2, 0.24)
		if sel:
			flag = Color(1.0, 0.72, 0.2)
		if r.routed:
			flag = Color(0.6, 0.6, 0.55)
		draw_rect(Rect2(bp.x - 1, bp.y - 14, 1, 16), Color(0.25, 0.18, 0.12))
		draw_texture_rect_region(tex_banner, Rect2(bp.x, bp.y - 14, 12, 14), Rect2(int(TYPE_IDX[r.type]) * 12, 0, 12, 14), flag)
		var cnt := str(r.soldiers.size())
		draw_string(Game.font, Vector2(bp.x + 14, bp.y - 5), cnt, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0, 0, 0))
		draw_string(Game.font, Vector2(bp.x + 13, bp.y - 6), cnt, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1, 0.95, 0.85) if r.team == 0 else Color(0.85, 0.85, 0.9))
		for k in r.rank:
			draw_rect(Rect2(bp.x + 1 + k * 4, bp.y - 17, 3, 2), Color(1, 0.85, 0.3))
		if r.switch_t > 0.0:
			draw_rect(Rect2(bp.x - 8, bp.y + 3, 28, 2), Color(0, 0, 0, 0.7))
			draw_rect(Rect2(bp.x - 8, bp.y + 3, 28 * (1.0 - r.switch_t / SWITCH_TIME), 2), Color(0.6, 0.8, 1.0))
		if r.resting:
			draw_string(Game.font, Vector2(bp.x - 8, bp.y - 18), "+", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.5, 1, 0.5))
		if r.team == 0 and r.type == "archer" and r.volley_cd <= 0.0 and phase == "fight":
			draw_rect(Rect2(bp.x + 13, bp.y - 15, 3, 3), Color(0.5, 0.9, 1.0))
	for t in texts:
		var tp: Vector2 = t["p"]
		draw_string(Game.font, tp + Vector2(1, 1), str(t["s"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0, 0, 0, 0.8))
		draw_string(Game.font, tp, str(t["s"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, t["c"])
	var mp := get_global_mouse_position()
	if dragging and drag_reg == null and drag_start.distance_to(mp) > 6.0 and phase == "fight":
		draw_rect(Rect2(drag_start, mp - drag_start).abs(), Color(1, 0.9, 0.5, 0.9), false, 1.0)
	if rdragging and rdrag_start.distance_to(mp) > 10.0:
		draw_line(rdrag_start, mp, Color(1, 0.9, 0.5), 1.0)
	if volley_mode:
		draw_arc(mp, 22.0, 0, TAU, 20, Color(0.5, 0.9, 1.0), 1.0)
		draw_string(Game.font, mp + Vector2(-20, -26), Game.L("VOLLEY"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.5, 0.9, 1.0))
