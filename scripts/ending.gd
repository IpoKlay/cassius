extends Node2D
## The Great Altar. No good or bad ending - only a settlement of what was promised against what was done.

var t := 0.0
var tex := {}
var root: Control
var lines: Array = []
var shown := 0.0
var settled := false
var image_line := ""


func _ready() -> void:
	for k in ["props/altar", "sprites/priest", "sprites/cassius", "sprites/soldier1", "bg/south_mountains", "bg/south_ground", "props/banner"]:
		tex[k] = load("res://assets/%s.png" % k)
	Game.music("ambient")
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
	return vb


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
	lines = []
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
		shown += delta * 0.9
	queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
	if not settled:
		return
	if event is InputEventKey and event.pressed and not event.echo:
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
	for i in 12:
		draw_rect(Rect2(0, 20 + i * 14, 480, 15), Color(0.07, 0.06, 0.16).lerp(Color(0.62, 0.28, 0.2), i / 11.0))
	var m: Texture2D = tex["bg/south_mountains"]
	draw_texture(m, Vector2(0, 80), Color(0.42, 0.33, 0.46))
	var g: Texture2D = tex["bg/south_ground"]
	for i in 6:
		draw_texture(g, Vector2(i * 96, 196), Color(0.6, 0.54, 0.62))
	var f4 := int(t * 6.0) % 4
	var a: Texture2D = tex["props/altar"]
	draw_texture_rect_region(a, Rect2(184, 108, 112, 88), Rect2(f4 * 56, 0, 56, 44))
	var pr: Texture2D = tex["sprites/priest"]
	draw_texture_rect_region(pr, Rect2(306, 144, 40, 52), Rect2((4 + int(t * 3.0) % 8) * 20, 0, 20, 26), Color(0.8, 0.75, 0.8))
	var c: Texture2D = tex["sprites/cassius"]
	draw_texture_rect_region(c, Rect2(70, 134, 64, 64), Rect2((int(t * 2.0) % 4) * 32, 0, 32, 32), Color(0.7, 0.65, 0.75))
	draw_rect(Rect2(0, 0, 480, 20), Color.BLACK)
	draw_rect(Rect2(0, 236, 480, 34), Color.BLACK)
	if not settled:
		return
	draw_rect(Rect2(0, 20, 480, 216), Color(0, 0, 0, 0.6))
	var y := 40.0
	var n: int = min(int(shown), lines.size())
	for i in n:
		var s := str(lines[i])
		var col := Color(0.91, 0.84, 0.66)
		if i == lines.size() - 1:
			col = Color(1.0, 0.86, 0.5)
		elif s.ends_with(Game.L("kept")):
			col = Color(0.6, 0.85, 0.55)
		elif s.ends_with(Game.L("broken")):
			col = Color(0.95, 0.45, 0.38)
		draw_multiline_string(Game.font, Vector2(50, y), s, HORIZONTAL_ALIGNMENT_LEFT, 380, 8, -1, col)
		y += max(Game.font.get_height(8), Game.font.get_multiline_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, 380, 8).y)
	if shown >= lines.size():
		draw_string(Game.font, Vector2(50, 256), Game.L("[Enter] march again     [L] read the ledger"), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.55, 0.5, 0.46))
