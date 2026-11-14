extends Node2D
## Title card + five illustrated slides that set up the expedition.

const SLIDES := [
	"Four powers ring the inner sea. Each believes the gods are owed something different - and that the others are paying it wrong.",
	"The harvests failed three years running. The King called a Great Sacrifice, and sent his ledgers out to collect for it: grain, herds, and holy things.",
	"The north says the Empire carried off its ancestors' horn. The western forest is being cut for altars. The east keeps the calendar and will not publish this year's omen. And miners say the ground under the old altar rings hollow.",
	"Cassius commands a border fort. When the refugees came he opened the gates and promised: while the standard stands, you may stay.",
	"The granary is nearly empty. The Empire's answer was a writ: reopen the north road, collect what the provinces owe, deliver it to the Great Altar - and your fort will be fed.\n\nSeventy men. Forty-five measures of grain. Go.",
]

## the story illustrations (painted, 1920x816) and the pixel map; swap STORY_DIR to "res://assets/story/pixel" for the pixel set
const STORY_DIR := "res://assets/story"
const PIC := Rect2(0, 16, 480, 204)          # 2.35:1 picture between black bars
const MOTES := [   # per-slide drifting particles: colour, count, fall speed, sideways drift, size
	[Color(1, 1, 1, 0.8), 70, 9.0, 4.0, 1.0],
	[Color(1, 0.65, 0.3, 0.9), 60, -10.0, 3.0, 1.0],
	[Color(0.9, 0.95, 1, 0.7), 60, 6.0, 2.0, 1.0],
	[Color(0.7, 0.8, 1, 0.55), 140, 160.0, -40.0, 0.0],
	[Color(1, 0.9, 0.65, 0.8), 70, -5.0, 6.0, 1.0],
]

var slide := -1
var menu_sel := 0
var menu_hover := -1
var title_tex := {}
var birds: Array = []
var embers: Array = []
const MENU := ["New campaign", "Settings", "Quit"]
const BRAZIERS := [Vector2(150, 208), Vector2(330, 208)]
var pics: Array = []
var frame_a: TextureRect
var frame_b: TextureRect
var clip: Control
var overlay: Node2D
var slide_t := 0.0
var motes: Array = []
var chars := 0.0
var t := 0.0
var tex := {}


func _ready() -> void:
	for k in ["ui/map", "ui/coin_big", "sprites/cassius", "sprites/soldier0", "sprites/soldier1", "sprites/ox", "props/altar", "props/campfire", "props/tent",
			"bg/south_mountains", "bg/south_forest_mid", "bg/north_mountains", "bg/west_forest_mid", "bg/east_mountains", "bg/south_ground", "props/banner", "sprites/priest"]:
		tex[k] = load("res://assets/%s.png" % k)
	Game.music("ambient")
	for k in ["sky", "clouds", "far", "city", "mid", "fore"]:
		title_tex[k] = _load_pic("res://assets/title/title_%s.png" % k)
	for i in 5:
		birds.append([randf() * 480.0, randf_range(30, 120), randf_range(10, 18), randf() * TAU])
	for i in 5:
		pics.append(_load_pic("%s/slide%d.png" % [STORY_DIR if i > 0 else "res://assets/story", i + 1]))
	clip = Control.new()
	clip.position = PIC.position
	clip.size = PIC.size
	clip.clip_contents = true
	clip.visible = false
	add_child(clip)
	frame_b = TextureRect.new()
	frame_a = TextureRect.new()
	for fr in [frame_b, frame_a]:
		fr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		fr.stretch_mode = TextureRect.STRETCH_SCALE
		fr.size = PIC.size
		clip.add_child(fr)
	overlay = Node2D.new()
	add_child(overlay)
	overlay.draw.connect(_draw_overlay)
	for i in 160:
		motes.append([randf() * 480.0, randf() * 204.0, randf_range(0.5, 1.0), randf() * TAU])


func _load_pic(path: String) -> Texture2D:
	## imported texture when the editor has seen the file; otherwise read the png straight from disk
	if ResourceLoader.exists(path):
		return load(path)
	var img := Image.load_from_file(ProjectSettings.globalize_path(path))
	return ImageTexture.create_from_image(img) if img != null else null


func _exit_tree() -> void:
	get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
	get_viewport().snap_2d_transforms_to_pixel = true


func _show_slide(i: int) -> void:
	## crossfade to the next illustration, rendered at full screen resolution
	get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	get_viewport().snap_2d_transforms_to_pixel = false
	clip.visible = true
	slide_t = 0.0
	frame_b.texture = frame_a.texture
	frame_b.modulate.a = 1.0 if frame_b.texture != null else 0.0
	frame_b.size = frame_a.size
	frame_b.position = frame_a.position
	frame_a.texture = pics[i]
	# the map is pixel art: keep it crisp; the paintings are filtered smoothly
	frame_a.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST if i == 0 else CanvasItem.TEXTURE_FILTER_LINEAR
	frame_a.modulate.a = 0.0
	create_tween().tween_property(frame_a, "modulate:a", 1.0, 0.6)


func _process(delta: float) -> void:
	t += delta
	slide_t += delta
	chars += delta * 45.0
	if slide >= 0 and slide < pics.size():
		# slow Ken Burns push-in, alternating direction per slide
		if slide == 0:
			frame_a.size = PIC.size
			frame_a.position = Vector2.ZERO
		else:
			var k: float = smoothstep(0.0, 1.0, min(1.0, slide_t / 20.0))
			var sc := 1.02 + 0.04 * k
			var dir := 1.0 if slide % 2 == 0 else -1.0
			frame_a.size = PIC.size * sc
			frame_a.position = Vector2(-(PIC.size.x * (sc - 1.0)) * (0.5 + 0.35 * dir * (k - 0.5)), -(PIC.size.y * (sc - 1.0)) * 0.5)
		var m: Array = MOTES[slide]
		for q in motes:
			q[1] += float(m[2]) * delta * q[2]
			q[0] += (float(m[3]) * q[2] + sin(t + q[3]) * 3.0) * delta
			q[0] = fposmod(q[0], 480.0)
			q[1] = fposmod(q[1], 204.0)
	queue_redraw()
	overlay.queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
	## forward: any key / left click / right arrow.  back: left arrow, A, Backspace, right click.  Esc: skip.
	var step := 0
	if Game.settings_open:
		return
	if slide < 0:
		_menu_input(event)
		return
	if event is InputEventKey and event.pressed:
		match event.keycode:
			KEY_ESCAPE:
				if slide >= 0 and not event.echo:
					_start()
				return
			KEY_LEFT, KEY_A, KEY_BACKSPACE, KEY_PAGEUP:
				step = -1
			_:
				if event.echo and event.keycode != KEY_RIGHT:
					return
				step = 1
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			step = 1
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			step = -1
	if step == 0:
		return
	if step > 0 and slide >= 0 and chars < Game.L(SLIDES[slide]).length():
		chars = 9999.0                 # first press finishes the sentence
		return
	if step < 0 and slide <= 0:
		return
	slide += step
	Game.sfx("click", -6.0, 1.0 if step > 0 else 0.85)
	if slide >= SLIDES.size():
		_start()
		return
	chars = 0.0 if step > 0 else 9999.0     # going back shows the line already read
	_show_slide(slide)


func _start() -> void:
	set_process_unhandled_input(false)
	Game.new_run()
	Game.start_leg("south")
	Game.sfx("horn", -4.0)
	Game.go("expedition")


func _sky(top: Color, bot: Color, h := 170) -> void:
	var bands := 12
	for i in bands:
		var c := top.lerp(bot, float(i) / float(bands - 1))
		draw_rect(Rect2(0, 20 + i * h / bands, 480, h / bands + 1), c)


func _strip(key: String, y: float, off: float, mod := Color.WHITE) -> void:
	var tx: Texture2D = tex[key]
	var w := tx.get_width()
	var x := -fmod(off, float(w))
	while x < 480.0:
		draw_texture(tx, Vector2(x, y), mod)
		x += w


func _frame(key: String, frame: int, fw: int, pos: Vector2, sc := 1.0, mod := Color.WHITE) -> void:
	var tx: Texture2D = tex[key]
	var h := tx.get_height()
	draw_texture_rect_region(tx, Rect2(pos, Vector2(fw, h) * sc), Rect2(frame * fw, 0, fw, h), mod)


func _text(s: String, pos: Vector2, width: float, col := Color(0.91, 0.84, 0.66)) -> void:
	draw_multiline_string(Game.font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, width, 8, -1, col)


func _draw() -> void:
	draw_rect(Rect2(0, 0, 480, 270), Color(0.03, 0.02, 0.04))
	var f4 := int(t * 5.0) % 4
	if slide < 0:
		_draw_title()
		return


func _draw_overlay() -> void:
	if slide < 0 or slide >= SLIDES.size():
		return
	var o := overlay
	var m: Array = MOTES[slide]
	var c: Color = m[0]
	for i in int(m[1]):
		var q: Array = motes[i]
		var p := Vector2(q[0], q[1] + PIC.position.y)
		var tw: float = 0.55 + 0.45 * sin(t * 2.0 + q[3])
		if float(m[4]) <= 0.0:          # rain: short slanted streaks
			o.draw_line(p, p + Vector2(-2.0, 6.0), Color(c.r, c.g, c.b, c.a * tw), 0.6)
		else:
			o.draw_circle(p, 0.35 + 0.45 * q[2], Color(c.r, c.g, c.b, c.a * tw))
			o.draw_circle(p, 1.4 * q[2], Color(c.r, c.g, c.b, 0.12 * tw))
	o.draw_rect(Rect2(0, 0, 480, PIC.position.y), Color.BLACK)
	o.draw_rect(Rect2(0, PIC.end.y, 480, 270 - PIC.end.y), Color.BLACK)
	for i in SLIDES.size():                     # progress dots
		var dc := Color(0.89, 0.77, 0.55) if i == slide else Color(0.35, 0.31, 0.27)
		o.draw_circle(Vector2(240 + (i - 2) * 10, 8), 1.6 if i == slide else 1.0, dc)
	var full := Game.L(SLIDES[slide])
	var shown: String = full.substr(0, int(chars))
	var tw_ := 380.0 if Game.lang == "en" else 400.0
	var tx_ := 50.0 if Game.lang == "en" else 40.0
	var ty := PIC.end.y + 14.0
	if Game.lang != "en":
		# Chinese runs taller: lift the caption so it ends above the footer, on a dark band over the picture
		var hh: float = Game.font.get_multiline_string_size(full, HORIZONTAL_ALIGNMENT_LEFT, tw_, 8).y
		ty = min(ty, 258.0 - hh + Game.font.get_ascent(8))
		if ty < PIC.end.y + 12.0:
			o.draw_rect(Rect2(0, ty - Game.font.get_ascent(8) - 4.0, 480, PIC.end.y - ty + Game.font.get_ascent(8) + 4.0), Color(0, 0, 0, 0.72))
	o.draw_multiline_string(Game.font, Vector2(tx_, ty), shown, HORIZONTAL_ALIGNMENT_LEFT, tw_, 8, -1, Color(0.91, 0.84, 0.66))
	var foot := Game.L("[<- ->] back / next   [Esc] skip")
	o.draw_string(Game.font, Vector2(472.0 - Game.font.get_string_size(foot, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x, 266), foot, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.45, 0.41, 0.37))


# ---------------------------------------------------------------- title: dusk over Rome + menu
func _menu_rect(i: int) -> Rect2:
	return Rect2(180, 205 + i * 15, 120, 13)


func _menu_pick(i: int) -> void:
	Game.sfx("click", -4.0, 1.0)
	match i:
		0:
			slide = 0
			chars = 0.0
			Game.sfx("horn", -10.0, 1.1)
			_show_slide(0)
		1:
			Game.open_settings()
		2:
			get_tree().quit()


func _menu_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		match event.keycode:
			KEY_UP, KEY_W:
				menu_sel = (menu_sel + MENU.size() - 1) % MENU.size()
				Game.sfx("click", -14.0, 1.4)
			KEY_DOWN, KEY_S, KEY_TAB:
				menu_sel = (menu_sel + 1) % MENU.size()
				Game.sfx("click", -14.0, 1.4)
			KEY_ENTER, KEY_KP_ENTER, KEY_SPACE:
				if not event.echo:
					_menu_pick(menu_sel)
	elif event is InputEventMouseMotion:
		var mp: Vector2 = get_local_mouse_position()
		menu_hover = -1
		for i in MENU.size():
			if _menu_rect(i).grow(2).has_point(mp):
				menu_hover = i
				if menu_sel != i:
					menu_sel = i
					Game.sfx("click", -16.0, 1.5)
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var mp2: Vector2 = get_local_mouse_position()
		for i in MENU.size():
			if _menu_rect(i).grow(2).has_point(mp2):
				_menu_pick(i)


func _tex_draw(k: String, pos := Vector2.ZERO) -> void:
	var tx: Texture2D = title_tex.get(k)
	if tx != null:
		draw_texture(tx, pos)


func _draw_title() -> void:
	_tex_draw("sky")
	var cl: Texture2D = title_tex.get("clouds")
	if cl != null:
		var off := fmod(t * 3.0, float(cl.get_width()))
		draw_texture(cl, Vector2(-off, 18))
		draw_texture(cl, Vector2(cl.get_width() - off, 18))
	# birds wheeling over the city
	for b in birds:
		b[0] = fmod(b[0] + b[2] * get_process_delta_time() + 480.0, 520.0)
		var bp := Vector2(b[0] - 20.0, b[1] + sin(t * 0.7 + b[3]) * 6.0)
		var flap := int(t * 6.0 + b[3]) % 2
		var bc := Color(0.16, 0.1, 0.16)
		draw_rect(Rect2(bp.round(), Vector2(1, 1)), bc)
		draw_rect(Rect2((bp + Vector2(-2, -1 + flap)).round(), Vector2(2, 1)), bc)
		draw_rect(Rect2((bp + Vector2(1, -1 + flap)).round(), Vector2(2, 1)), bc)
	_tex_draw("far")
	_tex_draw("city")
	# lamps in the lower town flicker on as dusk falls
	for i in 26:
		var h := hash(i * 7919)
		var lp := Vector2(8 + (h % 140) + (300 if i % 2 == 0 else 0), 194 + (h / 7) % 40)
		if sin(t * (0.8 + (h % 5) * 0.3) + i) > 0.2:
			draw_rect(Rect2(lp, Vector2(1, 1)), Color(1.0, 0.8, 0.45, 0.85))
	_tex_draw("mid")
	_tex_draw("fore")
	# braziers: fire, glow, rising embers
	for bz in BRAZIERS:
		var p: Vector2 = bz
		draw_circle(p + Vector2(0, -6), 14.0 + sin(t * 9.0) * 1.5, Color(1.0, 0.55, 0.2, 0.07))
		draw_circle(p + Vector2(0, -5), 7.0 + sin(t * 13.0) * 1.0, Color(1.0, 0.65, 0.25, 0.12))
		for k in 7:
			var fx := float(k - 3)
			var fh: float = 6.0 + 4.0 * abs(sin(t * 11.0 + k * 1.7)) - abs(fx) * 1.2
			var fc := Color(1.0, 0.85, 0.4) if abs(fx) < 1.5 else Color(0.98, 0.45, 0.15)
			draw_rect(Rect2(p + Vector2(fx, -fh), Vector2(1, fh)), fc)
		draw_rect(Rect2(p + Vector2(-1, -4), Vector2(2, 3)), Color(1, 0.97, 0.8))
		if randf() < 0.25:
			embers.append([p + Vector2(randf_range(-3, 3), -8), randf_range(1.0, 2.2), randf_range(-4, 4)])
	for e in embers:
		e[1] -= get_process_delta_time()
		e[0] += Vector2(e[2] + sin(t * 3.0 + e[2]) * 3.0, -16.0) * get_process_delta_time()
		draw_rect(Rect2(Vector2(e[0]).round(), Vector2(1, 1)), Color(1, 0.7, 0.3, clamp(float(e[1]), 0.0, 1.0)))
	embers = embers.filter(func(e): return float(e[1]) > 0.0)
	# two crimson standards hanging from the great columns, stirring in the wind
	for side in [0, 1]:
		var x0 := 6.0 if side == 0 else 452.0
		var w := 22.0
		var top := 22.0
		var length := 92.0
		for yy in int(length):
			var k := float(yy) / length
			var sway := sin(t * 1.6 - yy * 0.08 + side) * 2.5 * k
			var shade := 0.85 + 0.15 * sin(t * 1.6 - yy * 0.08 + side + 1.2)
			var c := Color(0.64 * shade, 0.15 * shade, 0.17 * shade)
			var wl := w
			if yy > length - 10:
				wl = w * (1.0 - float(yy - (length - 10)) / 10.0 * 0.5)    # swallowtail
			var xo := (w - wl) * 0.5 if yy > length - 10 else 0.0
			draw_rect(Rect2(Vector2(x0 + sway, top + yy).round(), Vector2(xo, 1)), c)
			draw_rect(Rect2(Vector2(x0 + sway + w - xo, top + yy).round(), Vector2(xo, 1)), c)
			if yy <= length - 10:
				draw_rect(Rect2(Vector2(x0 + sway, top + yy).round(), Vector2(w, 1)), c)
			if yy == 6 or yy == int(length) - 14:
				draw_rect(Rect2(Vector2(x0 + sway, top + yy).round(), Vector2(w, 1)), Color(1, 0.8, 0.35))
		# gold crossbar + a little gold wreath on each banner
		draw_rect(Rect2(x0 - 3, top - 2, w + 6, 2), Color(0.85, 0.62, 0.22))
		var ec := Vector2(x0 + w * 0.5 + sin(t * 1.6 - 3.0 + side) * 1.2, top + 30)
		draw_arc(ec.round(), 6.0, 0.4, TAU - 0.4, 16, Color(1, 0.82, 0.38), 1.0)
		draw_rect(Rect2(ec.round() + Vector2(-1, -2), Vector2(2, 4)), Color(1, 0.82, 0.38))
	# title
	var title_w: float = Game.font_en.get_string_size("CASSIUS", HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x * 4.0
	var tx0 := (480.0 - title_w) * 0.5
	draw_set_transform(Vector2(tx0, 24), 0.0, Vector2(4, 4))
	draw_string(Game.font_en, Vector2(0.5, 9.5), "CASSIUS", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.12, 0.05, 0.08))
	draw_string(Game.font_en, Vector2(0, 8.75), "CASSIUS", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.62, 0.36, 0.12))
	draw_string(Game.font_en, Vector2(0, 8), "CASSIUS", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1.0, 0.86, 0.5))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var sub := Game.L("What you promised to protect - did you protect it?")
	var sw: float = Game.font.get_string_size(sub, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
	draw_string(Game.font, Vector2((480.0 - sw) * 0.5 + 1, 66), sub, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.1, 0.04, 0.08, 0.8))
	draw_string(Game.font, Vector2((480.0 - sw) * 0.5, 65), sub, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.99, 0.9, 0.74))
	# menu
	draw_rect(Rect2(172, 200, 136, 50), Color(0.06, 0.03, 0.07, 0.72))
	draw_rect(Rect2(172, 200, 136, 50), Color(0.78, 0.58, 0.3, 0.8), false, 1.0)
	for i in MENU.size():
		var r := _menu_rect(i)
		var label := Game.L(MENU[i])
		var lw: float = Game.font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
		var on := i == menu_sel
		if on:
			draw_rect(r, Color(0.55, 0.16, 0.14, 0.75))
			var bob := int(t * 4.0) % 2
			draw_string(Game.font, Vector2(r.position.x + 4 + bob, r.position.y + 10), ">", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1, 0.86, 0.5))
			draw_string(Game.font, Vector2(r.end.x - 9 - bob, r.position.y + 10), "<", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1, 0.86, 0.5))
		draw_string(Game.font, Vector2(r.position.x + (r.size.x - lw) * 0.5, r.position.y + 10), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(1, 0.9, 0.62) if on else Color(0.78, 0.7, 0.6))
	var hint := Game.L("arrows / mouse  -  Enter")
	var hw: float = Game.font.get_string_size(hint, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
	draw_string(Game.font, Vector2((480.0 - hw) * 0.5, 262), hint, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0.55, 0.48, 0.44))
