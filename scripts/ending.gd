extends Node2D
## The Great Altar. No good or bad ending - only a settlement of what was promised against what was done.
## A painted scene plays first (the altar fire, the road home in the snow, or the fallen standard),
## then the account is read out line by line on a framed card.

const UI_FX = preload("res://scripts/ui_fx.gd")
var t := 0.0
var tex := {}
var root: Control
var lines: Array = []
var shown := 0.0
var settled := false
var image_line := ""
var scene := "altar"
var fire_power := 1.0
var fog := false
var cine := 0.0               # seconds since the settlement; the card fades in after CINE
const CINE := 2.6
var last_line := -1
var parts: Array = []
var glow: Node2D
var card: Node2D
var runner_x := 300.0


func _ready() -> void:
	for k in ["altar", "home", "fallen"]:
		tex[k] = Game.load_tex("res://assets/ending/end_%s.png" % k)
	Game.music("ambient")
	glow = Node2D.new()
	var gm := CanvasItemMaterial.new()
	gm.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	glow.material = gm
	add_child(glow)
	glow.draw.connect(_draw_glow)
	card = Node2D.new()
	card.modulate.a = 0.0
	add_child(card)
	card.draw.connect(_draw_card)
	var layer := CanvasLayer.new()
	layer.layer = 5
	add_child(layer)
	root = Control.new()
	root.theme = Game.theme
	root.size = Vector2(480, 270)
	layer.add_child(root)
	if Game.game_over_reason != "":
		_settle("lost")
	else:
		_ask()


func _clear() -> void:
	for c in root.get_children():
		c.queue_free()


func _panel(width: int) -> VBoxContainer:
	_clear()
	var center := CenterContainer.new()
	center.size = Vector2(480, 270)
	root.add_child(center)
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(width, 0)
	center.add_child(panel)
	var vb := VBoxContainer.new()
	panel.add_child(vb)
	Game.sfx("ui_open", -5.0)
	_sparkle.call_deferred(panel)
	return vb


func _sparkle(panel: Control) -> void:
	await get_tree().process_frame
	if is_instance_valid(panel):
		var fx = UI_FX.new()
		fx.mode = "border"
		fx.rect = Rect2(panel.global_position + Vector2(2, 2), panel.size - Vector2(4, 4))
		root.add_child(fx)


func _ask() -> void:
	var vb := _panel(380)
	vb.add_child(Game.label(Game.L("The Great Altar"), Color(0.96, 0.8, 0.42)))
	vb.add_child(HSeparator.new())
	var txt := Game.L("Auditors with wax tablets wait at the foot of the steps. Behind them, more cattle than you have ever seen in one place.\n\nThe ledger demands %d grain and %d offerings. Your carts hold %d grain and %d offerings. Meet it, and the fort is granted a season's ration.") % [Game.QUOTA, Game.TRIBUTE_NEEDED, Game.grain, Game.tribute_count()]
	if Game.has_promise("horn") and Game.inventory.has("relic_horn"):
		txt += Game.L("\n\nA Frostbay runner stands apart from the crowd, watching your baggage. You swore on their stone.")
	vb.add_child(Game.label(txt, null, 366))
	vb.add_child(Game.button(Game.L("Deliver everything the ledger asks for."), _settle.bind("deliver")))
	if Game.inventory.has("relic_horn"):
		vb.add_child(Game.button(Game.L("Deliver the rest - but put the horn in the Frostbay runner's hands first."), _settle.bind("horn")))
	vb.add_child(Game.button(Game.L("Turn the carts around. The grain goes home; the Emperor gets nothing."), _settle.bind("home")))
	Game.enable_keys.call_deferred(root)


func _settle(choice: String) -> void:
	settled = true
	cine = 0.0
	last_line = -1
	lines = []
	scene = "fallen" if choice == "lost" else ("home" if choice == "home" else "altar")
	fog = choice == "horn"
	match scene:
		"altar":
			Game.sfx("end_fire", -2.0)
			if fog:
				Game.sfx("end_horn", -4.0)
		"home":
			Game.sfx("end_wind", -3.0)
		"fallen":
			Game.sfx("end_wind", -4.0)
			Game.sfx("end_thud", -3.0, 0.8)
	lines.append(Game.L("Day %d. %d men marched behind the standard. %d did not come back.") % [Game.day, Game.marched, Game.fallen])
	var empire_ok := false
	var home := "broken"
	if choice == "lost":
		lines.append(Game.game_over_reason)
		lines.append(Game.L("The Emperor's ledger records the column as 'not delivered'."))
		image_line = Game.L("A horn, somewhere in fog.")
	else:
		var offerings := Game.tribute_count()
		if choice == "horn":
			Game.remove_item("relic_horn")
			offerings -= 1
			if Game.has_promise("horn"):
				Game.set_promise("horn", "kept")
			else:
				Game.promise("horn", Game.L("Frostbay: the Ancestral Horn returned."))
				Game.set_promise("horn", "kept")
			lines.append(Game.L("The runner took the horn without a word and was gone before the auditors looked up."))
		elif Game.has_promise("horn"):
			Game.set_promise("horn", "broken")
		if choice == "home":
			lines.append(Game.L("You delivered nothing. %d measures of grain went north in your own carts.") % Game.grain)
			lines.append(Game.L("The Emperor's ledger records you as a deserter with a baggage train."))
			home = "kept" if Game.grain >= 60 else "broken"
			if home == "kept":
				lines.append(Game.L("The fort ate thin bread until spring. Most of them lived."))
			else:
				lines.append(Game.L("It was not enough grain for that many people. The gates were opened anyway."))
			image_line = Game.L("A shield wall at a ford, facing south.")
		else:
			empire_ok = Game.grain >= Game.QUOTA and offerings >= Game.TRIBUTE_NEEDED
			fire_power = 1.0 if empire_ok else 0.45
			lines.append(Game.L("Delivered: %d of %d grain, %d of %d offerings.") % [min(Game.grain, Game.QUOTA), Game.QUOTA, offerings, Game.TRIBUTE_NEEDED])
			if empire_ok:
				home = "kept"
				lines.append(Game.L("The auditors pressed their seal. A season's ration was sent to the fort."))
				if Game.flags.has("falsified") or Game.flags.has("treason"):
					lines.append(Game.L("Nobody looks closely at the books of an officer who met his quota."))
			else:
				lines.append(Game.L("The auditors accepted what there was and granted nothing. Short is short."))
				if Game.flags.has("falsified"):
					lines.append(Game.L("One of them set two ledgers side by side for a long time."))
				if Game.flags.has("treason"):
					lines.append(Game.L("One of them turned your orders over and looked at the seal."))
			lines.append(Game.L("The Great Sacrifice was held. Whether it worked, the next harvest will say."))
			image_line = Game.L("A wet red cord in a priest's hands.")
	Game.set_promise("home", home)
	lines.append("")
	for p in Game.promises:
		var state := str(p["state"])
		if state == "open":
			state = "unanswered"
		lines.append("%s  -  %s" % [str(p["text"]), Game.L(state)])
	lines.append("")
	lines.append(Game.L("The ledger has %d entries in your hand. Nobody asks to read it.") % Game.ledger.size())
	lines.append(image_line)
	lines.append("")
	lines.append(Game.L("What you promised to protect - did you protect it?"))
	_clear()
	shown = 0.0


func _process(delta: float) -> void:
	t += delta
	if settled:
		cine += delta
		if cine > CINE:
			card.modulate.a = min(1.0, card.modulate.a + delta * 2.5)
			shown += delta * 0.9
			var cur := int(shown)
			if cur != last_line and cur < lines.size():
				last_line = cur
				_line_sound(cur)
	_spawn(delta)
	for q in parts:
		q["life"] = float(q["life"]) - delta
		q["p"] = Vector2(q["p"]) + Vector2(q["v"]) * delta
		if q["k"] == "crow":
			q["a"] = float(q["a"]) + delta * float(q["w"])
	parts = parts.filter(func(q): return float(q["life"]) > 0.0)
	if fog:
		runner_x -= delta * 9.0
	queue_redraw()
	glow.queue_redraw()
	card.queue_redraw()


func _line_sound(i: int) -> void:
	var s := str(lines[i])
	if s == "":
		return
	if i == lines.size() - 1:
		Game.sfx("end_gong", -3.0)
	elif s.ends_with(Game.L("kept")):
		Game.sfx("end_bell", -4.0)
	elif s.ends_with(Game.L("broken")):
		Game.sfx("end_thud", -4.0)
	else:
		Game.sfx("end_drum", -9.0, randf_range(0.9, 1.1))


func _spawn(delta: float) -> void:
	match scene:
		"altar":
			# a column of smoke from the great bowl; gold when the sacrifice was met
			if randf() < delta * 10.0:
				parts.append({"k": "smoke", "p": Vector2(240 + randf_range(-14, 14), 92), "v": Vector2(randf_range(2, 7), -randf_range(10, 18)), "life": 7.0, "max": 7.0})
			if randf() < delta * 30.0 * fire_power:
				parts.append({"k": "ember", "p": Vector2(240 + randf_range(-26, 26), 96), "v": Vector2(randf_range(-10, 10), -randf_range(20, 50)), "life": 2.2, "max": 2.2, "c": Color(1.0, 0.75, 0.3)})
		"home":
			if randf() < delta * 60.0:
				parts.append({"k": "snow", "p": Vector2(randf() * 520.0 - 20.0, -4), "v": Vector2(randf_range(-6, 2), randf_range(10, 22)), "life": 16.0, "max": 16.0})
			if randf() < delta * 4.0:
				parts.append({"k": "smoke", "p": Vector2(206 + randf_range(-2, 2), 118), "v": Vector2(randf_range(3, 6), -randf_range(5, 9)), "life": 5.0, "max": 5.0})
		"fallen":
			for sx in [60, 140, 380, 440]:
				if randf() < delta * 3.0:
					parts.append({"k": "dsmoke", "p": Vector2(sx + randf_range(-3, 3), 186), "v": Vector2(randf_range(3, 8), -randf_range(7, 13)), "life": 9.0, "max": 9.0})
			if randf() < delta * 6.0:
				parts.append({"k": "ember", "p": Vector2(randf() * 480.0, 272), "v": Vector2(randf_range(-4, 10), -randf_range(10, 24)), "life": 5.0, "max": 5.0, "c": Color(1.0, 0.5, 0.2)})
			var crows := 0
			for q in parts:
				if q["k"] == "crow":
					crows += 1
			if crows < 4:
				parts.append({"k": "crow", "p": Vector2.ZERO, "v": Vector2.ZERO, "life": 999.0, "max": 999.0, "a": randf() * TAU, "w": randf_range(0.5, 0.9), "r": randf_range(30, 70), "c0": Vector2(300 + randf_range(-30, 30), 120 + randf_range(-20, 20))})


func _unhandled_input(event: InputEvent) -> void:
	if not settled:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if cine < CINE:
			cine = CINE
			return
		if shown < lines.size():
			shown = float(lines.size()) + 1.0
		elif event.keycode == KEY_ENTER or event.keycode == KEY_SPACE:
			set_process_unhandled_input(false)
			Game.go("title")
		elif event.keycode == KEY_L:
			_show_ledger()


func _show_ledger() -> void:
	var vb := _panel(380)
	vb.add_child(Game.label(Game.L("The ledger"), Color(0.96, 0.8, 0.42)))
	var sc := ScrollContainer.new()
	sc.custom_minimum_size = Vector2(0, 170)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vb.add_child(sc)
	var inner := VBoxContainer.new()
	sc.add_child(inner)
	for e in Game.ledger:
		inner.add_child(Game.label(Game.L("Day %d.  %s") % [int(e["day"]), str(e["text"])], null, 360))
	vb.add_child(Game.button(Game.L("Close"), _clear))


func _draw() -> void:
	draw_rect(Rect2(0, 0, 480, 270), Color(0.02, 0.02, 0.05))
	var bg: Texture2D = tex.get(scene)
	if bg != null:
		draw_texture(bg, Vector2.ZERO)
	match scene:
		"altar":
			_draw_altar()
		"home":
			_draw_home()
		"fallen":
			_draw_fallen()
	for q in parts:
		var al: float = clamp(float(q["life"]) / float(q["max"]) * 1.4, 0.0, 1.0)
		var pp: Vector2 = Vector2(q["p"]).round()
		match str(q["k"]):
			"smoke":
				var k: float = 1.0 - float(q["life"]) / float(q["max"])
				var sc := Color(0.75, 0.62, 0.42) if (scene == "altar" and fire_power > 0.9) else Color(0.5, 0.48, 0.52)
				var sz: float = 3.0 + k * 9.0
				draw_rect(Rect2(pp - Vector2(sz, sz) * 0.5, Vector2(sz, sz)), Color(sc.r, sc.g, sc.b, 0.22 * al))
			"dsmoke":
				var k2: float = 1.0 - float(q["life"]) / float(q["max"])
				var sz2: float = 3.0 + k2 * 12.0
				draw_rect(Rect2(pp - Vector2(sz2, sz2) * 0.5, Vector2(sz2, sz2)), Color(0.12, 0.07, 0.08, 0.35 * al))
			"ember":
				draw_rect(Rect2(pp, Vector2(1, 1)), Color(q["c"].r, q["c"].g, q["c"].b, al))
			"snow":
				draw_rect(Rect2(pp, Vector2(1, 1)), Color(1, 1, 1, 0.85))
			"crow":
				var cp: Vector2 = Vector2(q["c0"]) + Vector2(cos(float(q["a"])), sin(float(q["a"])) * 0.4) * float(q["r"])
				var flap := int(t * 7.0 + float(q["r"])) % 2
				var cc := Color(0.05, 0.02, 0.03)
				cp = cp.round()
				draw_rect(Rect2(cp, Vector2(2, 1)), cc)
				draw_rect(Rect2(cp + Vector2(-3, -1 + flap), Vector2(3, 1)), cc)
				draw_rect(Rect2(cp + Vector2(2, -1 + flap), Vector2(3, 1)), cc)
	if fog:
		for i in 5:
			var fy := 200.0 + i * 13.0
			var fx := fmod(t * (6.0 + i * 2.0) + i * 97.0, 560.0) - 80.0
			draw_rect(Rect2(fx - 160, fy, 320, 7), Color(0.75, 0.75, 0.85, 0.10))
			draw_rect(Rect2(fx - 260 + 560, fy + 3, 260, 5), Color(0.75, 0.75, 0.85, 0.08))
		# the Frostbay runner, slipping away into the fog with the horn
		var rx := roundf(runner_x)
		if rx > -10.0:
			draw_rect(Rect2(rx, 222, 4, 12), Color(0.08, 0.06, 0.1))
			draw_rect(Rect2(rx, 218, 4, 4), Color(0.08, 0.06, 0.1))
			draw_rect(Rect2(rx + (int(t * 6.0) % 2) - 1, 234, 2, 4), Color(0.08, 0.06, 0.1))
			draw_rect(Rect2(rx + 4, 224, 4, 2), Color(0.9, 0.85, 0.7))
	# the opening caption, typed under the picture before the account is read
	if settled and cine < CINE + 0.6:
		var a: float = clamp(min(cine * 2.0, (CINE + 0.6 - cine) * 2.0), 0.0, 1.0)
		var cap := image_line.substr(0, int(cine * 30.0))
		var cw: float = Game.font.get_string_size(image_line, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
		draw_rect(Rect2(0, 236, 480, 22), Color(0, 0, 0, 0.55 * a))
		draw_string(Game.font, Vector2((480.0 - cw) * 0.5, 251), cap, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1.0, 0.9, 0.7, a))


func _flames(base: Vector2, width: int, height: float, power: float, hot := Color(1.0, 0.9, 0.5), mid := Color(1.0, 0.55, 0.18), cool := Color(0.75, 0.2, 0.1)) -> void:
	for k in width:
		var fx := float(k) - width * 0.5
		var edge: float = 1.0 - absf(fx) / (width * 0.5)
		var h: float = height * power * edge * (0.65 + 0.35 * absf(sin(t * 9.0 + k * 1.37) * cos(t * 5.3 + k * 0.71)))
		if h < 1.0:
			continue
		draw_rect(Rect2(base + Vector2(fx, -h), Vector2(1, h)), cool)
		draw_rect(Rect2(base + Vector2(fx, -h * 0.7), Vector2(1, h * 0.7)), mid)
		if edge > 0.45:
			draw_rect(Rect2(base + Vector2(fx, -h * 0.4), Vector2(1, h * 0.4)), hot)


func _draw_altar() -> void:
	_flames(Vector2(240, 101), 60, 46.0, fire_power)
	for x in [120, 360]:
		_flames(Vector2(x, 147), 12, 12.0, 0.6 + 0.4 * fire_power)


func _draw_home() -> void:
	# the fort's open gate glows; lamps flicker along the wall
	var a := 0.75 + 0.25 * sin(t * 2.0)
	draw_rect(Rect2(233, 138, 14, 16), Color(1.0, 0.8, 0.45, a))
	for i in 5:
		if sin(t * 3.0 + i * 1.7) > 0.0:
			draw_rect(Rect2(208 + i * 16, 136, 1, 1), Color(1, 0.85, 0.5))


func _draw_fallen() -> void:
	# the torn vexillum still stirs in the wind
	for yy in 18:
		var sh := roundf(sin(t * 3.0 - yy * 0.4) * 1.5)
		draw_rect(Rect2(296 + sh, 202 + yy, 18 - int(yy * 0.3), 1), Color(0.56, 0.14, 0.13))


func _draw_glow() -> void:
	var pulse := 0.9 + 0.1 * sin(t * 7.0) + 0.04 * sin(t * 19.0)
	match scene:
		"altar":
			var r := 90.0 * fire_power * pulse
			glow.draw_circle(Vector2(240, 80), r, Color(1.0, 0.45, 0.15, 0.07))
			glow.draw_circle(Vector2(240, 88), r * 0.55, Color(1.0, 0.6, 0.25, 0.10))
			for x in [120, 360]:
				glow.draw_circle(Vector2(x, 140), 22.0 * pulse, Color(1.0, 0.5, 0.2, 0.08))
		"home":
			glow.draw_circle(Vector2(240, 146), 26.0 * pulse, Color(1.0, 0.7, 0.35, 0.10))
			glow.draw_circle(Vector2(320, 160), 60.0, Color(1.0, 0.8, 0.5, 0.06))
		"fallen":
			glow.draw_circle(Vector2(224, 146), 70.0 * pulse, Color(1.0, 0.45, 0.15, 0.08))


func _draw_card() -> void:
	if not settled:
		return
	var box := Rect2(34, 22, 412, 226)
	var sb: StyleBox = Game.theme.get_stylebox("panel", "PanelContainer")
	card.draw_rect(box, Color(0.04, 0.02, 0.03, 0.55))
	if sb != null:
		card.draw_style_box(sb, box)
	# measure every revealed line; scroll the card so the newest line is always in view
	var n: int = min(int(shown), lines.size())
	var hs: Array = []
	var total := 0.0
	for i in n:
		var hh: float = max(Game.font.get_height(8), Game.font.get_multiline_string_size(str(lines[i]), HORIZONTAL_ALIGNMENT_LEFT, 380, 8).y)
		hs.append(hh)
		total += hh
	var top := 48.0
	var bottom := 236.0
	var y: float = top - max(0.0, total - (bottom - top))
	for i in n:
		var s := str(lines[i])
		var col := Color(0.91, 0.84, 0.66)
		if i == lines.size() - 1:
			col = Color(1.0, 0.86, 0.5)
		elif s.ends_with(Game.L("kept")):
			col = Color(0.6, 0.85, 0.55)
		elif s.ends_with(Game.L("broken")):
			col = Color(0.95, 0.45, 0.38)
		if y >= top - 2.0:
			var fade: float = clamp(shown - i, 0.0, 1.0)
			card.draw_multiline_string(Game.font, Vector2(50, y), s, HORIZONTAL_ALIGNMENT_LEFT, 380, 8, -1, Color(col.r, col.g, col.b, fade))
		y += hs[i]
	if shown >= lines.size():
		var foot := Game.L("[Enter] march again     [L] read the ledger")
		var fw: float = Game.font.get_string_size(foot, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
		card.draw_rect(Rect2(0, 252, 480, 18), Color(0, 0, 0, 0.6))
		card.draw_string(Game.font, Vector2((480.0 - fw) * 0.5, 264), foot, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.75, 0.68, 0.58))
