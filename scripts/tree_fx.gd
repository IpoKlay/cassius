extends RefCounted
## Pixel particle and shape effects for the doctrine wheel.
## Every doctrine has a theme: a burst when it is learned (bigger with each level, much bigger at the top)
## and, once mastered, a living effect that keeps playing *behind* the wheel so it never hides a node.

const FIRE := [Color(0.35, 0.1, 0.07), Color(0.75, 0.2, 0.08), Color(1.0, 0.45, 0.12), Color(1.0, 0.75, 0.25), Color(1.0, 0.95, 0.7)]
const GOLD := Color(0.96, 0.8, 0.42)

var parts: Array = []
var shapes: Array = []
var t := 0.0
var flash := Color(0, 0, 0, 0)
var shake := 0.0
var _clock: Dictionary = {}          # per-node timers for periodic ambient events


# ------------------------------------------------------------------ spawning
func emit(kind: String, p: Vector2, n: int, c: Color, spd: float, front := true, extra := {}) -> void:
	if parts.size() > 1400:
		return
	for i in n:
		var v := Vector2.from_angle(randf() * TAU) * spd * randf_range(0.3, 1.0)
		var life := randf_range(0.4, 0.8)
		match kind:
			"flame":
				v = Vector2(randf_range(-0.35, 0.35) * spd, -randf_range(0.6, 1.0) * spd)
				life = randf_range(0.35, 0.7)
			"ember":
				v = Vector2(randf_range(-8, 8), -randf_range(14, 30)) * (spd / 24.0)
				life = randf_range(0.6, 1.2)
			"smoke":
				v = Vector2(randf_range(-6, 6), -randf_range(8, 16))
				life = randf_range(0.8, 1.4)
			"mote", "glint", "star":
				life = randf_range(0.6, 1.2)
			"feather", "leaf":
				v = Vector2(randf_range(-1, 1), randf_range(-1.2, 0.2)) * spd
				life = randf_range(1.0, 1.8)
			"coin":
				v = Vector2(randf_range(-0.5, 0.5) * spd, -randf_range(0.7, 1.0) * spd * 1.6)
				life = randf_range(0.7, 1.0)
			"drop":
				v = Vector2(randf_range(-1, 1) * spd * 0.6, -randf_range(0.3, 1.0) * spd)
				life = randf_range(0.6, 1.0)
			"cross":
				v = Vector2(randf_range(-4, 4), -randf_range(10, 20))
				life = randf_range(0.8, 1.3)
			"snow":
				v = Vector2(randf_range(-4, 4), randf_range(6, 14))
				life = randf_range(1.0, 1.8)
			"arrow":
				v = Vector2(randf_range(-0.5, 0.5) * spd, -spd)
				life = randf_range(0.8, 1.0)
			"dust":
				life = randf_range(0.5, 0.9)
		var q := {"k": kind, "p": p, "o": p, "v": v, "life": life, "max": life, "c": c, "front": front, "spin": randf() * TAU, "sz": randf_range(0.6, 1.4)}
		for key in extra:
			q[key] = extra[key]
		if kind in ["rune", "grain", "orbit"]:
			q["ang"] = randf() * TAU
			q["rad"] = float(extra.get("rad", 10.0)) * randf_range(0.8, 1.2)
			q["cx"] = p
		parts.append(q)


func shape(kind: String, p: Vector2, life: float, data := {}) -> void:
	var s := {"k": kind, "p": p, "life": life, "max": life, "seed": randi(), "delay": float(data.get("delay", 0.0))}
	for key in data:
		s[key] = data[key]
	shapes.append(s)


# ------------------------------------------------------------------ bursts, one per theme
## fire, lightning and the shield dome set the bar: each doctrine gets one big readable picture
func burst(theme: String, p: Vector2, r: float, lv: int, mx: int) -> void:
	var k := float(lv) / float(mx)
	var full := lv >= mx
	var m := 0.6 + k
	match theme:
		"fire":
			emit("flame", p + Vector2(0, r * 0.3), int(26 * m), FIRE[4], 46.0 * m)
			emit("ember", p, int(12 * m), FIRE[3], 30.0)
			if full:
				for i in 60:
					emit("flame", p + Vector2(randf_range(-r * 1.6, r * 1.6), r * 0.6), 1, FIRE[4], randf_range(50, 90))
				emit("smoke", p + Vector2(0, -r), 18, Color(0.2, 0.14, 0.12), 10.0)
				shape("ring", p, 0.5, {"c": FIRE[3], "v": 120.0, "r": r})
				flash = Color(1, 0.4, 0.1, 0.18)
		"lightning":
			shape("bolt", p, 0.32, {"from": Vector2(p.x + randf_range(-30, 30), -10)})
			emit("spark", p, int(14 * m), Color(1, 1, 0.75), 70.0)
			flash = Color(0.85, 0.9, 1.0, 0.12 + 0.12 * k)
			if full:
				for i in 3:
					shape("bolt", p, 0.32, {"from": Vector2(p.x + randf_range(-80, 80), -10), "delay": 0.08 * (i + 1)})
				shape("ring", p, 0.45, {"c": Color(1, 1, 0.7), "v": 140.0, "r": r})
				shake = 4.0
		"dome":
			shape("hexdome", p, 0.8, {"R": r + 6.0 + 4.0 * k, "c": Color(0.5, 0.7, 1)})
			emit("mote", p, int(10 * m), Color(0.6, 0.8, 1), 30.0)
			if full:
				shape("hexdome", p, 1.2, {"R": r + 18.0, "c": Color(0.75, 0.9, 1), "delay": 0.1})
		"spears":
			# spears hurled down from the sky, slamming in around the node
			var n := 2 + lv + (6 if full else 0)
			for i in n:
				var land := p + Vector2.from_angle(-PI / 2.0 + (i - (n - 1) / 2.0) * 0.55) * (r + 4.0) * (1.0 if not full else 1.6)
				var from := land + Vector2(randf_range(-40, 40), -90)
				shape("fall", land, 1.1, {"what": "spear", "from": from, "hit_t": 0.18 + i * 0.05, "onhit": "thud", "c": Color(0.95, 0.5, 0.35)})
		"arrows":
			# a volley blots out the sky and comes down around the node
			var n2 := 8 + lv * 5 + (24 if full else 0)
			for i in n2:
				var land2 := p + Vector2(randf_range(-30, 30), randf_range(-14, 18))
				shape("fall", land2, 1.4, {"what": "arrow", "from": land2 + Vector2(-70, -110) + Vector2(randf_range(-20, 20), 0), "hit_t": 0.35 + randf() * 0.25, "onhit": "tick"})
		"hooves":
			# a horse gallops right through the wheel, dust boiling behind it
			var n3 := 1 + (2 if full else 0)
			for i in n3:
				var yy := p.y + r - 2.0 + i * 7.0
				shape("runner", Vector2(p.x, yy), 1.0, {"x0": p.x - 80.0, "x1": p.x + 90.0, "delay": i * 0.18, "scale": 2.0 if i == 0 else 1.0})
			shake = 2.5
		"feathers":
			# the eagle stoops onto the standard, wings flung wide
			shape("swoop", p, 1.3, {"from": p + Vector2(70, -80), "scale": 2.0, "full": full})
			if full:
				shape("rays", p, 1.2, {"n": 10, "c": GOLD, "delay": 0.4})
		"grind":
			shape("wheel", p + Vector2(-r - 7, 2), 1.0, {"R": 7.0 + 2.0 * k})
			for i in int(40 * m):
				var v := Vector2.from_angle(-PI * 0.3 + randf_range(-0.45, 0.45)) * randf_range(50, 150)
				parts.append({"k": "spark", "p": p + Vector2(-r - 2, 4), "o": p, "v": v, "life": randf_range(0.3, 0.7), "max": 0.7, "c": Color(1, randf_range(0.6, 0.95), 0.35), "front": true, "spin": 0.0, "sz": 1.0})
		"glint":
			# a critical cut: blades cross the node, then a star bursts out of it
			shape("slash", p, 0.5, {"L": 40.0 + 20.0 * k, "ang": -0.6})
			if lv >= 2 or full:
				shape("slash", p, 0.5, {"L": 40.0 + 20.0 * k, "ang": 0.6, "delay": 0.1})
			shape("star", p, 0.5, {"L": r + 12.0 + 10.0 * k, "c": Color(1, 0.95, 0.6), "delay": 0.15})
			emit("spark", p, 18, Color(1, 0.3, 0.25), 90.0)
			flash = Color(1, 1, 1, 0.12)
			if full:
				shape("slash", p, 0.5, {"L": 70.0, "ang": 0.0, "delay": 0.22})
				shape("slash", p, 0.5, {"L": 70.0, "ang": PI / 2.0, "delay": 0.28})
				shake = 4.0
		"brackets":
			# an anvil drops out of the sky onto the node
			shape("fall", p, 1.0, {"what": "anvil", "from": p + Vector2(0, -120), "hit_t": 0.28, "onhit": "anvil", "scale": 2.0 if full else 1.0})
		"frost":
			# ice spears erupt from the ground in a ring
			var n4 := 6 + lv * 2 + (8 if full else 0)
			for i in n4:
				var ang := i * TAU / n4 + randf_range(-0.1, 0.1)
				shape("spike", p + Vector2(cos(ang) * (r + 3), sin(ang) * (r + 3) * 0.7), 1.0, {"H": randf_range(8, 14) + 6.0 * k, "lean": cos(ang) * 0.5, "delay": i * 0.02})
			emit("shard", p, int(14 * m), Color(0.75, 0.95, 1), 60.0)
			if full:
				shape("crystal", p, 1.2, {"L": r + 24.0, "c": Color(0.85, 1, 1), "rot": PI / 6.0})
				for i in 50:
					emit("snow", p + Vector2(randf_range(-50, 50), randf_range(-50, -10)), 1, Color(0.9, 0.97, 1), 0.0)
				flash = Color(0.6, 0.9, 1, 0.15)
		"runes":
			# an eye opens over the node and stares a beam down into it
			shape("eye", p + Vector2(0, -r - 14), 1.4, {"scale": 2.0 if full else 1.0})
			shape("runecircle", p, 1.2, {"R": r + 6.0, "c": Color(0.78, 0.5, 1.0), "delay": 0.2})
			if full:
				shape("runecircle", p, 1.5, {"R": r + 16.0, "c": Color(0.95, 0.75, 1.0), "dir": -1.0, "delay": 0.3})
				flash = Color(0.5, 0.2, 0.9, 0.16)
		"blood":
			shape("splat", p, 1.6, {"R": 8.0 + 6.0 * k})
			shape("heart", p + Vector2(0, -r - 8), 1.2, {"scale": 2.0 if full else 1.0})
			emit("drop", p, int(20 * m), Color(0.85, 0.08, 0.15), 60.0)
			flash = Color(0.6, 0.0, 0.05, 0.12 + 0.1 * k)
		"harvest":
			# a field of wheat springs up and bows in the wind
			var n5 := 6 + lv * 3 + (10 if full else 0)
			for i in n5:
				shape("stalk", p + Vector2((i - (n5 - 1) / 2.0) * 3.0, r + 2), 1.6, {"H": randf_range(10, 18) + 4.0 * k, "delay": abs(i - (n5 - 1) / 2.0) * 0.03})
			emit("grain", p + Vector2(0, r), int(14 * m), Color(0.95, 0.82, 0.4), 0.0, true, {"rad": r + 4.0})
		"heal":
			shape("pillar", p, 1.2, {"W": 6.0 + 4.0 * k, "c": Color(0.55, 1, 0.7)})
			emit("cross", p, int(10 * m), Color(0.6, 1, 0.75), 0.0)
			if full:
				shape("pillar", p, 1.5, {"W": 18.0, "c": Color(0.75, 1, 0.85), "delay": 0.15})
		"wall":
			for i in 5:
				shape("rise", p + Vector2((i - 2) * 6.0, r + 3), 1.4, {"what": "tower", "delay": i * 0.06})
			emit("dust", p + Vector2(0, r), 18, Color(0.6, 0.45, 0.35), 50.0)
			shake = 3.0
		"javelins":
			for i in 7:
				var to := p + Vector2.from_angle(randf() * TAU) * randf_range(26, 44)
				shape("fall", to, 1.0, {"what": "javelin", "from": p, "hit_t": 0.35, "arc": 22.0, "onhit": "tick"})
		"laurel":
			shape("wreath", p, 1.4, {"R": r + 4.0})
			emit("glint", p, 10, GOLD, 30.0)
		"impact":
			shape("bash", p, 0.6, {"R": r})
			emit("spark", p + Vector2(r + 6, 0), 26, Color(0.85, 0.95, 1), 100.0)
			shake = 5.0
		"beam":
			shape("beam", p, 0.7, {"c": Color(0.6, 1, 0.6)})
			emit("spark", p, 14, Color(0.8, 1, 0.7), 50.0)
			flash = Color(0.5, 1, 0.5, 0.1)
		"wind":
			shape("tornado", p, 1.4, {"R": r + 6.0})
			for i in 16:
				emit("streak", p + Vector2(randf_range(-30, 0), randf_range(-r, r)), 1, Color(0.8, 1, 0.7), 0.0, true, {"wind": true})
		"clang":
			shape("fall", p + Vector2(0, -2), 0.9, {"what": "helm", "from": p + Vector2(0, -100), "hit_t": 0.25, "onhit": "anvil", "scale": 2.0})
		"dust":
			shape("comet", p, 1.0, {"R": r + 8.0})
		"crown":
			shape("pillar", p, 1.2, {"W": 10.0, "c": Color(0.95, 0.55, 0.9)})
			shape("fall", p + Vector2(0, -r - 4), 1.4, {"what": "crown", "from": p + Vector2(0, -60), "hit_t": 0.4, "onhit": "glint", "scale": 2.0})
		"coins":
			for i in 34:
				var land3 := p + Vector2(randf_range(-26, 26), randf_range(-4, 8))
				shape("fall", land3, 0.9, {"what": "coin", "from": land3 + Vector2(randf_range(-6, 6), -randf_range(80, 140)), "hit_t": randf_range(0.2, 0.5), "onhit": "coin"})
		"skull":
			shape("sprite", p + Vector2(0, -r - 12), 1.6, {"what": "skull", "scale": 2.0, "rise": 8.0})
			shape("tally", p + Vector2(-14, r + 8), 1.6, {})
			emit("smoke", p, 26, Color(0.3, 0.05, 0.05), 12.0)
			flash = Color(0.5, 0.0, 0.0, 0.28)
			shake = 4.0
		"wildfire":
			for i in 70:
				var a := randf() * TAU
				emit("flame", p + Vector2(cos(a) * (r + 7), sin(a) * (r + 7) * 0.6), 1, FIRE[4], randf_range(50, 90))
			shape("ring", p, 0.6, {"c": FIRE[2], "v": 160.0, "r": r})
			flash = Color(1, 0.35, 0.05, 0.25)
		"speed":
			shape("steps", p, 1.4, {})
			shape("speedlines", p, 0.8, {"R": r})
		"bloodbanner":
			shape("fall", p + Vector2(0, r), 1.6, {"what": "flag", "from": p + Vector2(0, -90), "hit_t": 0.3, "onhit": "thud", "scale": 2.0})
			for i in 26:
				emit("drop", p + Vector2(randf_range(-r * 1.4, r * 1.4), -r - randf_range(4, 24)), 1, Color(0.8, 0.08, 0.15), 0.0)
			flash = Color(0.6, 0.0, 0.05, 0.22)
		"shatter":
			shape("shieldbreak", p, 1.0, {"R": r * 2.0})
			emit("shard", p, 34, Color(0.75, 0.75, 0.8), 90.0)
			shake = 5.0
		"sun":
			for i in 5:
				shape("sunbeam", p, 1.6, {"x": p.x + (i - 2) * 9.0, "delay": i * 0.05})
			shape("rays", p, 1.2, {"n": 12, "c": Color(1, 0.88, 0.55)})
		"aurora":
			shape("aurora", Vector2(p.x, 40), 2.6, {"R": r, "wide": true})
			emit("mote", p, 16, Color(0.5, 1, 0.8), 25.0)
		"leaves":
			emit("orbit", p, 50, Color(0.5, 0.9, 0.4), 0.0, true, {"rad": r + 6.0, "leafy": true})
			emit("leaf", p, 30, Color(0.65, 0.85, 0.3), 50.0)
			emit("leaf", p, 14, Color(0.9, 0.55, 0.2), 50.0)
		"stars":
			shape("shooting", p, 0.8, {"from": p + Vector2(-90, -70)})
			shape("constellation", p, 2.0, {"R": r + 18.0, "delay": 0.3})
		_:
			emit("spark", p, int(20 * m), GOLD, 60.0)


func _on_hit(s: Dictionary) -> void:
	## what happens the instant a falling thing lands
	var p: Vector2 = s["p"]
	match str(s.get("onhit", "")):
		"thud":
			emit("dust", p, 10, Color(0.65, 0.52, 0.38), 40.0)
			emit("spark", p, 6, Color(1, 0.85, 0.6), 50.0)
			shape("ring", p, 0.3, {"c": Color(1, 0.85, 0.6), "v": 90.0, "r": 2.0})
			shake = max(shake, 2.5)
		"anvil":
			emit("spark", p, 34, Color(1, 0.9, 0.6), 120.0)
			emit("dust", p + Vector2(0, 6), 16, Color(0.55, 0.5, 0.48), 60.0)
			shape("ring", p, 0.4, {"c": Color(0.9, 0.9, 1), "v": 170.0, "r": 4.0})
			shape("ring", p, 0.5, {"c": Color(0.7, 0.75, 0.9), "v": 110.0, "r": 4.0, "delay": 0.08})
			shake = 6.0
			flash = Color(1, 1, 1, 0.12)
		"tick":
			if randf() < 0.4:
				emit("dust", p, 2, Color(0.6, 0.5, 0.4), 16.0)
		"coin":
			emit("spark", p, 2, GOLD, 30.0)
		"glint":
			emit("glint", p, 12, Color(1, 0.8, 1), 40.0)
			shape("ring", p, 0.4, {"c": Color(1, 0.7, 1), "v": 90.0, "r": 4.0})


# ------------------------------------------------------------------ ambient: partly learned = a hint, mastered = the full effect
func ambient(theme: String, key: String, p: Vector2, r: float, lv: int, mx: int, delta: float) -> void:
	var full := lv >= mx
	if not full:
		if randf() < delta * (0.7 + lv * 0.4):
			match theme:
				"fire", "wildfire":
					emit("flame", p + Vector2(randf_range(-r, r) * 0.5, -r * 0.3), 1, FIRE[3], 22.0, false)
				"frost":
					emit("snow", p + Vector2(randf_range(-r, r), -r), 1, Color(0.9, 0.97, 1), 0.0, false)
				"blood", "bloodbanner":
					emit("drop", p + Vector2(randf_range(-2, 2), r * 0.5), 1, Color(0.85, 0.1, 0.15), 4.0, false)
				"runes":
					emit("rune", p, 1, Color(0.85, 0.6, 1), 0.0, false, {"rad": r + 5.0})
				"heal":
					emit("cross", p, 1, Color(0.5, 1, 0.65), 0.0, false)
				"lightning":
					shape("arc", p, 0.12, {"R": r, "back": true})
				_:
					emit("mote", p + Vector2.from_angle(randf() * TAU) * r, 1, GOLD, 6.0, false)
		return
	var c0: float = _clock.get(key, randf() * 2.0)
	c0 -= delta
	match theme:
		"fire":
			for i in int(delta * 70.0 + randf()):
				emit("flame", p + Vector2(randf_range(-r * 1.5, r * 1.5), r * 0.5), 1, FIRE[4], randf_range(26, 46), false)
			if randf() < delta * 6.0:
				emit("smoke", p + Vector2(randf_range(-r, r), -r * 1.2), 1, Color(0.18, 0.13, 0.12), 8.0, false)
			if randf() < delta * 8.0:
				emit("ember", p, 1, FIRE[3], 30.0, false)
		"wildfire":
			for i in int(delta * 40.0 + randf()):
				var a := randf() * TAU
				emit("flame", p + Vector2(cos(a) * (r + 5), sin(a) * (r + 5) * 0.6), 1, FIRE[4], randf_range(16, 30), false)
		"lightning":
			if c0 <= 0.0:
				c0 = randf_range(1.2, 2.6)
				shape("bolt", p, 0.25, {"from": p + Vector2(randf_range(-14, 14), -46), "small": true, "back": true})
				emit("spark", p, 6, Color(1, 1, 0.75), 40.0, false)
			if randf() < delta * 3.0:
				shape("arc", p, 0.12, {"R": r, "back": true})
		"frost":
			if randf() < delta * 10.0:
				emit("snow", p + Vector2(randf_range(-28, 28), randf_range(-34, -10)), 1, Color(0.92, 0.98, 1), 0.0, false)
		"blood", "bloodbanner":
			if randf() < delta * 3.0:
				emit("drop", p + Vector2(randf_range(-r, r) * 0.6, r * 0.6), 1, Color(0.8, 0.08, 0.15), 3.0, false)
		"glint":
			if c0 <= 0.0:
				c0 = randf_range(1.5, 3.0)
				shape("slash", p + Vector2(randf_range(-4, 4), randf_range(-4, 4)), 0.35, {"L": 18.0, "ang": randf_range(-1.2, 1.2), "back": true})
		"grind":
			if randf() < delta * 14.0:
				parts.append({"k": "spark", "p": p + Vector2(-r - 2, 4), "o": p, "v": Vector2.from_angle(-PI * 0.3 + randf_range(-0.4, 0.4)) * randf_range(30, 70), "life": 0.35, "max": 0.35, "c": Color(1, 0.8, 0.4), "front": false, "spin": 0.0, "sz": 1.0})
		"harvest":
			if randf() < delta * 3.0:
				emit("grain", p + Vector2(0, r), 1, Color(0.95, 0.85, 0.45), 0.0, false, {"rad": r + 5.0})
		"heal":
			if randf() < delta * 2.0:
				emit("cross", p + Vector2(randf_range(-r, r), 0), 1, Color(0.5, 1, 0.65), 0.0, false)
		"arrows":
			if c0 <= 0.0:
				c0 = randf_range(2.0, 3.5)
				for i in 5:
					var land := p + Vector2(randf_range(-24, 24), randf_range(-8, 14))
					shape("fall", land, 1.0, {"what": "arrow", "from": land + Vector2(-60, -90), "hit_t": 0.3 + randf() * 0.2, "onhit": "tick", "back": true})
		"hooves", "dust":
			if randf() < delta * 6.0:
				emit("orbit", p, 1, Color(0.8, 0.68, 0.45), 0.0, false, {"rad": r + 6.0})
		"feathers":
			if randf() < delta * 1.2:
				emit("feather", p, 1, Color(1, 0.9, 0.65), 20.0, false)
		"javelins", "speed", "wind":
			if randf() < delta * 4.0:
				emit("streak", p + Vector2(randf_range(-20, 0), randf_range(-r, r)), 1, Color(1, 0.9, 0.6), 0.0, false, {"wind": true})
		"impact", "clang", "brackets":
			if randf() < delta * 2.0:
				emit("spark", p + Vector2.from_angle(randf() * TAU) * r, 3, Color(0.9, 0.95, 1), 30.0, false)
		"coins":
			if c0 <= 0.0:
				c0 = randf_range(0.8, 1.5)
				emit("coin", p, 1, GOLD, 26.0, false)
		"skull":
			if randf() < delta * 5.0:
				emit("smoke", p + Vector2(randf_range(-r, r) * 0.6, -r * 0.4), 1, Color(0.28, 0.07, 0.07), 6.0, false)
		"shatter":
			if randf() < delta * 1.5:
				emit("shard", p + Vector2(randf_range(-r, r), 0), 1, Color(0.7, 0.7, 0.75), 20.0, false)
		"leaves":
			if randf() < delta * 4.0:
				emit("orbit", p, 1, Color(0.5, 0.9, 0.4) if randf() < 0.7 else Color(0.9, 0.55, 0.2), 0.0, false, {"rad": r + 6.0, "leafy": true})
		"runes":
			if randf() < delta * 2.0:
				emit("mote", p + Vector2.from_angle(randf() * TAU) * (r + 6), 1, Color(0.8, 0.5, 1), 5.0, false)
	_clock[key] = c0


func draw_ambient(ci: CanvasItem, theme: String, key: String, p: Vector2, r: float) -> void:
	## the standing picture of a mastered doctrine, always drawn behind the nodes
	var seed := key.hash()
	match theme:
		"dome":
			var R := r + 6.0
			var pts := PackedVector2Array()
			for j in 7:
				pts.append((p + Vector2.from_angle(j * PI / 3.0 + PI / 6.0) * R).floor())
			ci.draw_polyline(pts, Color(0.55, 0.75, 1, 0.35 + 0.2 * sin(t * 2.0)), 1.0)
		"spears":
			for j in 7:
				var ang := -PI / 2.0 + (j - 3) * 0.42
				var base := p + Vector2.from_angle(ang) * (r + 3.0)
				_spear(ci, base + Vector2(0, 4), base + Vector2(sin(ang) * 2.0, -12.0), 0.85)
		"arrows":
			var rng := RandomNumberGenerator.new()
			rng.seed = seed
			for j in 9:
				var sp := p + Vector2(rng.randf_range(-r * 1.6, r * 1.6), r * 0.6 + rng.randf_range(0, 4))
				ci.draw_line(sp.floor(), (sp + Vector2(-3, -5)).floor(), Color(0.75, 0.6, 0.4, 0.85), 1.0)
				_px(ci, sp + Vector2(-3, -5), Color(0.95, 0.95, 0.9, 0.85))
		"hooves":
			var tt := t * 1.6
			var hp := p + Vector2(cos(tt) * (r + 12.0), sin(tt) * (r + 6.0) * 0.5 + 2.0)
			spr(ci, "horse0" if int(t * 10.0) % 2 == 0 else "horse1", hp, 0.8, 1.0, sin(tt) > 0.0)
		"feathers":
			spr(ci, "eagle_up" if fmod(t, 1.2) < 0.6 else "eagle_dn", p + Vector2(0, -r - 6), 0.85)
		"grind":
			var R2 := 6.0
			var wc := p + Vector2(-r - 6, 3)
			ci.draw_arc(wc, R2, 0, TAU, 16, Color(0.6, 0.55, 0.5, 0.85), 2.0)
			for j in 4:
				ci.draw_line(wc.floor(), (wc + Vector2.from_angle(t * 14.0 + j * PI / 2.0) * R2).floor(), Color(0.8, 0.75, 0.65, 0.85), 1.0)
		"brackets":
			for j in 12:
				var ang2 := t * 0.5 + j * TAU / 12.0
				var lp := p + Vector2(cos(ang2), sin(ang2) * 0.8) * (r + 5.0)
				ci.draw_rect(Rect2(lp.floor() - Vector2(1, 1), Vector2(3, 2) if j % 2 == 0 else Vector2(2, 3)), Color(0.62, 0.66, 0.75, 0.85), false, 1.0)
		"frost":
			for j in 9:
				var ang3 := j * TAU / 9.0
				var bp := p + Vector2(cos(ang3) * (r + 2.0), sin(ang3) * (r + 2.0) * 0.7)
				var H := 5.0 + 2.0 * sin(t * 1.5 + j)
				ci.draw_colored_polygon(PackedVector2Array([(bp + Vector2(-1.5, 0)).floor(), (bp + Vector2(cos(ang3) * 0.4 * H, -H)).floor(), (bp + Vector2(1.5, 0)).floor()]), Color(0.6, 0.88, 1, 0.75))
		"runes":
			var open := 1.0 if fmod(t, 3.0) > 0.18 else 0.0
			if open > 0.0:
				spr_eye(ci, p + Vector2(0, -r - 9), 0.8)
			for j in 8:
				var ang4 := t * 1.2 + j * TAU / 8.0
				_px(ci, p + Vector2(cos(ang4), sin(ang4) * 0.7) * (r + 6.0) - Vector2(1, 1), Color(0.85, 0.6, 1, 0.7 + 0.3 * sin(t * 6.0 + j)), 2.0, 2.0)
		"blood":
			var beat := 1.0 if fmod(t, 0.9) < 0.1 or (fmod(t, 0.9) > 0.18 and fmod(t, 0.9) < 0.26) else 0.0
			spr(ci, "heart", p + Vector2(0, -r - 6), 0.85, 1.0 + beat)
		"harvest":
			for j in 9:
				var bx := p + Vector2((j - 4) * 3.0, r + 3)
				var sway := sin(t * 2.5 + j * 0.5) * 1.5
				var top := bx + Vector2(sway, -9.0 - (j % 3) * 2.0)
				ci.draw_line(bx.floor(), top.floor(), Color(0.55, 0.65, 0.25, 0.85), 1.0)
				_px(ci, top - Vector2(0, 2), Color(0.98, 0.85, 0.4, 0.9), 1.0, 3.0)
		"heal":
			ci.draw_rect(Rect2(Vector2(p.x - 3, p.y - 50).floor(), Vector2(6, 50)), Color(0.55, 1, 0.7, 0.08 + 0.04 * sin(t * 3.0)))
		"wall":
			for j in 5:
				spr(ci, "tower", p + Vector2((j - 2) * 6.0, r - 1), 0.8)
		"laurel":
			for j in 16:
				var ang5 := PI * 0.15 + j * (PI * 1.7) / 15.0 + PI / 2.0
				_px(ci, p + Vector2(cos(ang5), sin(ang5) * 0.8) * (r + 4.0), Color(0.45, 0.8, 0.3, 0.85) if j % 2 == 0 else Color(0.96, 0.8, 0.42, 0.85), 2.0, 1.0)
		"javelins":
			for j in 3:
				var bp2 := p + Vector2((j - 1) * 9.0, r + 2)
				_spear(ci, bp2 + Vector2((j - 1) * 3.0, -12), bp2, 0.8)
		"beam":
			var dv6 := (p - Vector2(158, 141)).normalized()
			ci.draw_line(p.floor(), (p + dv6 * 26.0).floor(), Color(0.6, 1, 0.6, 0.3 + 0.2 * sin(t * 4.0)), 1.0)
		"crown":
			spr(ci, "crown", p + Vector2(0, -r - 5.0 + sin(t * 2.0)), 0.9)
		"skull":
			spr(ci, "skull", p + Vector2(0, -r - 7.0 + sin(t * 1.5)), 0.8)
		"bloodbanner":
			spr(ci, "flag", p + Vector2(r + 5, -4), 0.85)
		"clang":
			spr(ci, "helm", p + Vector2(0, -r - 4), 0.8)
		"sun":
			for j in 12:
				var ang6 := t * 0.25 + j * TAU / 12.0
				ci.draw_line((p + Vector2.from_angle(ang6) * (r + 3.0)).floor(), (p + Vector2.from_angle(ang6) * (r + 9.0 + 2.0 * sin(t * 2.0 + j))).floor(), Color(1, 0.88, 0.5, 0.6), 1.0)
		"aurora":
			_aurora(ci, p, r, 0.7, false)
		"stars":
			_constellation(ci, p, r + 14.0, seed, 0.75, 1.0)
		"shatter":
			ci.draw_line((p + Vector2(-r * 0.3, -r * 0.8)).floor(), (p + Vector2(r * 0.1, 0)).floor(), Color(0.8, 0.8, 0.85, 0.6), 1.0)
			ci.draw_line((p + Vector2(r * 0.1, 0)).floor(), (p + Vector2(-r * 0.2, r * 0.8)).floor(), Color(0.8, 0.8, 0.85, 0.6), 1.0)


func spr_eye(ci: CanvasItem, p: Vector2, a: float) -> void:
	var rows := ["..#####..", ".#..#..#.", "#..###..#", ".#..#..#.", "..#####.."]
	for y in rows.size():
		for x in 9:
			if rows[y][x] == "#":
				var c := Color(0.55, 0.15, 0.85, a) if abs(x - 4) <= 1 and abs(y - 2) <= 1 else Color(0.9, 0.75, 1, a)
				_px(ci, p + Vector2(x - 4, y - 2), c)


# ------------------------------------------------------------------ simulation
func update(delta: float) -> void:
	t += delta
	flash.a = max(0.0, flash.a - delta * 0.9)
	shake = max(0.0, shake - delta * 14.0)
	for i in range(parts.size() - 1, -1, -1):
		var q: Dictionary = parts[i]
		q["life"] -= delta
		if q["life"] <= 0.0:
			parts.remove_at(i)
			continue
		q["o"] = q["p"]
		match q["k"]:
			"spark":
				q["v"] *= 1.0 - delta * 3.4
				q["v"] += Vector2(0, 50) * delta
			"flame":
				q["v"] += Vector2(sin(t * 9.0 + q["spin"]) * 30.0, -40.0) * delta
				q["v"].x *= 1.0 - delta * 3.0
			"ember":
				q["v"] += Vector2(sin(t * 5.0 + q["spin"]) * 26.0, -8.0) * delta
			"smoke":
				q["v"] += Vector2(sin(t * 2.0 + q["spin"]) * 6.0, -4.0) * delta
			"shard":
				q["v"] *= 1.0 - delta * 1.5
				q["v"] += Vector2(0, 110) * delta
				q["spin"] += delta * 10.0
			"mote", "glint":
				q["v"] *= 1.0 - delta * 2.4
			"snow":
				q["v"].x = sin(t * 2.0 + q["spin"]) * 6.0
			"feather", "leaf":
				q["v"] *= 1.0 - delta * 1.6
				q["v"] += Vector2(sin(t * 3.0 + q["spin"]) * 18.0, 14.0) * delta
				q["spin"] += delta * 4.0
			"coin", "drop":
				q["v"] += Vector2(0, 150) * delta
				q["spin"] += delta * 14.0
			"cross":
				q["v"] *= 1.0 - delta * 0.6
			"arrow":
				q["v"] += Vector2(0, 110) * delta
			"dust":
				q["v"] *= 1.0 - delta * 4.0
				q["sz"] += delta * 2.0
			"streak":
				if q.get("wind", false):
					q["v"] = Vector2(140, sin(t * 6.0 + q["spin"]) * 6.0)
			"rune", "orbit":
				q["ang"] += delta * (2.5 if q["k"] == "rune" else 4.0)
				q["rad"] += delta * (0.0 if q["k"] == "rune" else 6.0)
				q["v"] = Vector2.ZERO
				q["p"] = q["cx"] + Vector2(cos(q["ang"]) * q["rad"], sin(q["ang"]) * q["rad"] * 0.6)
			"grain":
				q["ang"] += delta * 5.0
				q["rad"] *= 1.0 - delta * 0.6
				q["cx"] += Vector2(0, -22) * delta
				q["v"] = Vector2.ZERO
				q["p"] = q["cx"] + Vector2(cos(q["ang"]) * q["rad"], sin(q["ang"]) * q["rad"] * 0.4)
		q["p"] += q["v"] * delta
	for i in range(shapes.size() - 1, -1, -1):
		var s: Dictionary = shapes[i]
		if float(s["delay"]) > 0.0:
			s["delay"] -= delta
			continue
		s["life"] -= delta
		var age: float = float(s["max"]) - float(s["life"])
		if s.has("hit_t") and not s.get("hit", false) and age >= float(s["hit_t"]):
			s["hit"] = true
			_on_hit(s)
		match s["k"]:
			"runner":
				var u: float = clamp(age / 0.8, 0.0, 1.0)
				if u < 1.0:
					var x: float = lerp(float(s["x0"]), float(s["x1"]), u)
					var feet := Vector2(x, float(s["p"].y))
					emit("dust", feet + Vector2(-6, 0), 2, Color(0.72, 0.6, 0.42), 26.0)
					if randf() < 0.5:
						parts.append({"k": "print", "p": feet + Vector2(randf_range(-4, 4), 1), "o": feet, "v": Vector2.ZERO, "life": 1.0, "max": 1.0, "c": Color(0.45, 0.35, 0.25), "front": false, "spin": 0.0, "sz": 1.0})
			"swoop":
				if age >= 0.45 and not s.get("landed", false):
					s["landed"] = true
					emit("feather", s["p"], 30 if s.get("full", false) else 16, Color(1, 0.9, 0.65), 50.0)
					emit("glint", s["p"], 10, GOLD, 40.0)
					shape("ring", s["p"], 0.5, {"c": GOLD, "v": 130.0, "r": 6.0})
					shake = max(shake, 3.0)
			"spike":
				if float(s["life"]) < 0.2 and not s.get("broke", false):
					s["broke"] = true
					emit("shard", s["p"] + Vector2(0, -float(s["H"]) * 0.5), 4, Color(0.75, 0.95, 1), 50.0)
		if s.has("v"):
			s["r"] += float(s["v"]) * delta
		if s["life"] <= 0.0:
			shapes.remove_at(i)


# ------------------------------------------------------------------ drawing (pixel style: whole pixels, no smoothing)
func _px(ci: CanvasItem, p: Vector2, c: Color, w := 1.0, h := 1.0) -> void:
	ci.draw_rect(Rect2(p.floor(), Vector2(w, h)), c)


func _fire_col(k: float, a: float) -> Color:
	var i: int = clamp(int(k * 5.0), 0, 4)
	var c: Color = FIRE[i]
	return Color(c.r, c.g, c.b, a)


func draw_parts(ci: CanvasItem, front: bool) -> void:
	for q in parts:
		if bool(q["front"]) != front:
			continue
		var k: float = float(q["life"]) / float(q["max"])
		var a: float = clamp(k * 2.0, 0.0, 1.0)
		var c: Color = q["c"]
		var p: Vector2 = q["p"]
		match q["k"]:
			"spark":
				var o: Vector2 = q["o"]
				ci.draw_line(p.floor(), (p - (p - o) * 2.0).floor(), Color(c.r, c.g, c.b, a), 1.0)
			"flame":
				var fc := _fire_col(k, min(1.0, k * 3.0))
				var sz := 3.0 if k > 0.7 else (2.0 if k > 0.35 else 1.0)
				_px(ci, p - Vector2(sz * 0.5, sz * 0.5), fc, sz, sz)
			"ember":
				_px(ci, p, _fire_col(k * 0.8, a) if c.r > c.b + 0.2 else Color(c.r, c.g, c.b, a))
			"smoke":
				var s2 := 2.0 + (1.0 - k) * 2.0
				_px(ci, p - Vector2(s2 * 0.5, s2 * 0.5), Color(c.r, c.g, c.b, 0.5 * k), s2, s2)
			"shard":
				var d := Vector2(1, 0) if fmod(q["spin"], PI) < PI * 0.5 else Vector2(0, 1)
				_px(ci, p, Color(c.r, c.g, c.b, a))
				_px(ci, p + d, Color(c.r * 0.7, c.g * 0.7, c.b * 0.7, a))
			"glint":
				var L := int(round(2.0 * k + 0.4))
				_px(ci, p, Color(1, 1, 1, a))
				for j in range(1, L + 1):
					for dv in [Vector2(j, 0), Vector2(-j, 0), Vector2(0, j), Vector2(0, -j)]:
						_px(ci, p + dv, Color(c.r, c.g, c.b, a * 0.8))
			"snow":
				_px(ci, p, Color(c.r, c.g, c.b, a))
			"feather":
				var hz: bool = sin(q["spin"]) > 0.0
				_px(ci, p, Color(c.r, c.g, c.b, a), 3.0 if hz else 1.0, 1.0 if hz else 2.0)
			"leaf":
				var hz2: bool = sin(q["spin"]) > 0.0
				_px(ci, p, Color(c.r, c.g, c.b, a), 2.0 if hz2 else 1.0, 1.0 if hz2 else 2.0)
			"coin":
				var wd := 2.0 if cos(q["spin"]) > 0.0 else 1.0
				_px(ci, p, Color(1, 0.88, 0.4, a), wd, 2.0)
			"drop":
				_px(ci, p, Color(c.r, c.g, c.b, a), 1.0, 2.0)
			"cross":
				_px(ci, p + Vector2(-1, 0), Color(c.r, c.g, c.b, a), 3.0, 1.0)
				_px(ci, p + Vector2(0, -1), Color(c.r, c.g, c.b, a), 1.0, 3.0)
			"arrow":
				var dv2: Vector2 = Vector2(q["v"]).normalized()
				ci.draw_line(p.floor(), (p - dv2 * 4.0).floor(), Color(0.85, 0.75, 0.55, a), 1.0)
				_px(ci, p, Color(c.r, c.g, c.b, a))
			"dust":
				var s3: float = 1.0 + float(q["sz"])
				_px(ci, p - Vector2(s3 * 0.5, s3 * 0.5), Color(c.r, c.g, c.b, 0.5 * k), s3, s3)
			"streak":
				var dv3: Vector2 = Vector2(q["v"]).normalized()
				ci.draw_line(p.floor(), (p - dv3 * 6.0).floor(), Color(c.r, c.g, c.b, a * 0.8), 1.0)
			"rune":
				var fl := 0.6 + 0.4 * sin(t * 10.0 + q["spin"])
				_px(ci, p - Vector2(1, 1), Color(c.r, c.g, c.b, a * fl), 2.0, 2.0)
			"orbit":
				if q.get("leafy", false):
					_px(ci, p, Color(c.r, c.g, c.b, a), 2.0, 1.0)
				else:
					_px(ci, p - Vector2(1, 1), Color(c.r, c.g, c.b, 0.6 * a), 2.0, 2.0)
			_:
				_px(ci, p, Color(c.r, c.g, c.b, a))


func draw_shapes(ci: CanvasItem, back: bool) -> void:
	for s in shapes:
		if float(s["delay"]) > 0.0 or bool(s.get("back", false)) != back:
			continue
		var k: float = float(s["life"]) / float(s["max"])          # 1 at birth -> 0
		var e: float = 1.0 - k
		var p: Vector2 = s["p"]
		var c: Color = s.get("c", Color.WHITE)
		var a: float = clamp(k * 1.6, 0.0, 1.0)
		var rng := RandomNumberGenerator.new()
		rng.seed = int(s["seed"])
		match s["k"]:
			"ring":
				ci.draw_arc(p, float(s["r"]), 0, TAU, 40, Color(c.r, c.g, c.b, a), 1.0)
			"bolt":
				var from: Vector2 = s["from"]
				rng.seed = int(s["seed"]) + int(e * 4.0)            # re-jags a few times while it lives
				var n := 9 if not s.get("small", false) else 5
				var prev := from
				for j in range(1, n + 1):
					var nx := from.lerp(p, float(j) / n)
					if j < n:
						nx += Vector2(rng.randf_range(-7, 7), rng.randf_range(-3, 3))
						if rng.randf() < 0.35:
							var br := nx + Vector2(rng.randf_range(-12, 12), rng.randf_range(4, 14))
							ci.draw_line(nx.floor(), br.floor(), Color(0.75, 0.85, 1, a * 0.8), 1.0)
					ci.draw_line(prev.floor(), nx.floor(), Color(0.7, 0.8, 1, a), 3.0)
					ci.draw_line(prev.floor(), nx.floor(), Color(1, 1, 1, a), 1.0)
					prev = nx
			"arc":
				var a0 := rng.randf() * TAU
				var R: float = s["R"]
				var p0 := p + Vector2.from_angle(a0) * R
				var p1 := p + Vector2.from_angle(a0 + 0.9) * (R + 3.0)
				ci.draw_line(p0.floor(), p0.lerp(p1, 0.5).floor() + Vector2(rng.randi_range(-2, 2), rng.randi_range(-2, 2)), Color(1, 1, 0.8, a), 1.0)
				ci.draw_line(p0.lerp(p1, 0.5).floor(), p1.floor(), Color(1, 1, 0.8, a), 1.0)
			"crystal":
				var L: float = float(s["L"]) * min(1.0, e * 4.0)
				for j in 6:
					var ang := float(s.get("rot", 0.0)) + j * PI / 3.0
					var dv := Vector2.from_angle(ang)
					ci.draw_line(p.floor(), (p + dv * L).floor(), Color(c.r, c.g, c.b, a), 1.0)
					for b in [0.5, 0.75]:
						var bp: Vector2 = p + dv * L * b
						ci.draw_line(bp.floor(), (bp + Vector2.from_angle(ang + 0.7) * L * 0.25).floor(), Color(c.r, c.g, c.b, a * 0.8), 1.0)
						ci.draw_line(bp.floor(), (bp + Vector2.from_angle(ang - 0.7) * L * 0.25).floor(), Color(c.r, c.g, c.b, a * 0.8), 1.0)
					_px(ci, p + dv * L, Color(1, 1, 1, a))
			"runecircle":
				var R2: float = float(s["R"]) * min(1.0, e * 5.0)
				var dir: float = s.get("dir", 1.0)
				ci.draw_arc(p, R2, 0, TAU, 36, Color(c.r, c.g, c.b, a * 0.8), 1.0)
				ci.draw_arc(p, R2 - 3.0, 0, TAU, 32, Color(c.r, c.g, c.b, a * 0.4), 1.0)
				for j in 8:
					var ang2 := dir * t * 2.0 + j * TAU / 8.0
					var rp := p + Vector2.from_angle(ang2) * (R2 - 1.5)
					_px(ci, rp - Vector2(1, 1), Color(1, 0.85, 1, a), 2.0 + float(j % 2), 2.0)
			"star":
				var L2: float = float(s["L"]) * (0.4 + 0.6 * min(1.0, e * 6.0))
				var n2: int = s.get("n", 4)
				for j in n2:
					var ang3 := j * TAU / n2 + (PI / 4.0 if n2 == 4 else 0.0)
					var ll := L2 * (1.0 if j % 2 == 0 or n2 == 4 else 0.55)
					ci.draw_line(p.floor(), (p + Vector2.from_angle(ang3) * ll).floor(), Color(c.r, c.g, c.b, a), 1.0)
				_px(ci, p - Vector2(1, 1), Color(1, 1, 1, a), 3.0, 3.0)
			"rays":
				var n3: int = s["n"]
				for j in n3:
					var ang4 := float(s["seed"] % 100) + j * TAU / n3 + e * 0.5
					var L3 := 18.0 + e * 26.0
					ci.draw_line((p + Vector2.from_angle(ang4) * 8.0).floor(), (p + Vector2.from_angle(ang4) * L3).floor(), Color(c.r, c.g, c.b, a * 0.6), 1.0)
			"brackets":
				var R3: float = float(s["R"]) + 16.0 * max(0.0, 1.0 - e * 6.0)
				for j in 4:
					var corner := p + Vector2(R3 if j % 2 == 0 else -R3, R3 if j < 2 else -R3)
					var sx := -1.0 if j % 2 == 0 else 1.0
					var sy := -1.0 if j < 2 else 1.0
					ci.draw_line(corner.floor(), (corner + Vector2(sx * 4, 0)).floor(), Color(c.r, c.g, c.b, a), 1.0)
					ci.draw_line(corner.floor(), (corner + Vector2(0, sy * 4)).floor(), Color(c.r, c.g, c.b, a), 1.0)
			"spokes":
				var n4: int = s["n"]
				var out := sin(min(1.0, e * 2.5) * PI)
				for j in n4:
					var ang5 := float(s.get("rot", 0.0)) + j * TAU / n4 - PI / 2.0
					var dv4 := Vector2.from_angle(ang5)
					var base := p + dv4 * (float(s["R"]) + 1.0)
					var tip := base + dv4 * float(s["L"]) * out
					ci.draw_line(base.floor(), tip.floor(), Color(0.6, 0.45, 0.3, a), 1.0)
					_px(ci, tip - Vector2(1, 1), Color(c.r, c.g, c.b, a), 2.0, 2.0)
			"hexdome":
				var R4: float = float(s["R"]) * min(1.0, e * 5.0)
				var pts := PackedVector2Array()
				for j in 7:
					pts.append((p + Vector2.from_angle(j * PI / 3.0 + PI / 6.0) * R4).floor())
				ci.draw_polyline(pts, Color(c.r, c.g, c.b, a), 1.0)
				for j in 6:
					ci.draw_line(p.floor(), pts[j], Color(c.r, c.g, c.b, a * 0.25), 1.0)
			"stomp":
				var R5 := 3.0 + e * 26.0
				ci.draw_arc(p, R5, PI, TAU, 24, Color(c.r, c.g, c.b, a), 1.0)
				ci.draw_line((p + Vector2(-R5, 0)).floor(), (p + Vector2(R5, 0)).floor(), Color(c.r, c.g, c.b, a * 0.5), 1.0)
			"wings":
				_wings(ci, p, float(s["R"]), c, a, sin(e * PI * 2.0) * 0.4)
			"wall":
				for j in 5:
					var rise: float = min(1.0, e * 4.0 - j * 0.15)
					if rise <= 0.0:
						continue
					var bx := p.x - 13.0 + j * 5.5
					var hh := 7.0 * rise
					ci.draw_rect(Rect2(Vector2(bx, p.y + float(s["R"]) - hh).floor(), Vector2(4, hh)), Color(c.r, c.g, c.b, a))
			"beam":
				var dvb := (p - Vector2(158, 141)).normalized()
				var Lb: float = 70.0 * min(1.0, e * 4.0)
				ci.draw_line(p.floor(), (p + dvb * Lb).floor(), Color(c.r, c.g, c.b, a), 2.0)
				ci.draw_line(p.floor(), (p + dvb * Lb).floor(), Color(1, 1, 1, a), 1.0)
			"speedlines":
				for j in 8:
					var yy := p.y - 12.0 + j * 3.0
					var x0 := p.x - 30.0 + fmod(e * 120.0 + j * 17.0, 60.0)
					ci.draw_line(Vector2(x0, yy).floor(), Vector2(x0 + 8, yy).floor(), Color(1, 0.9, 0.6, a * 0.7), 1.0)
			"crown":
				_crown(ci, p + Vector2(0, -e * 6.0), Color(c.r, c.g, c.b, a))
			"skull":
				_skull(ci, p + Vector2(0, -e * 10.0), Color(0.9, 0.85, 0.8, a))
			"shieldbreak":
				var sp := e * 10.0
				var R6: float = s["R"]
				for side in [-1.0, 1.0]:
					var o := Vector2(side * sp, e * e * 14.0)
					var pts2 := PackedVector2Array([p + o + Vector2(0, -R6), p + o + Vector2(side * R6 * 0.8, -R6), p + o + Vector2(side * R6 * 0.8, 0), p + o + Vector2(0, R6)])
					ci.draw_polyline(pts2, Color(0.8, 0.8, 0.85, a), 1.0)
			"aurora":
				_aurora(ci, p, float(s["R"]), a, bool(s.get("wide", false)))
			"constellation":
				_constellation(ci, p, float(s["R"]), int(s["seed"]), a, e)
			_:
				_shape2(ci, s, k, e, a)


func draw_glow(ci: CanvasItem) -> void:
	for q in parts:
		var k: float = float(q["life"]) / float(q["max"])
		var c: Color = q["c"]
		match q["k"]:
			"flame":
				ci.draw_circle(q["p"], 3.0, Color(1, 0.45, 0.1, 0.12 * k))
			"spark", "glint", "snow", "rune", "cross", "coin":
				ci.draw_circle(q["p"], 2.0, Color(c.r, c.g, c.b, 0.18 * k))
			"ember", "mote", "shard", "orbit", "grain":
				ci.draw_circle(q["p"], 1.5, Color(c.r, c.g, c.b, 0.12 * k))
	for s in shapes:
		if float(s["delay"]) > 0.0:
			continue
		var k2: float = float(s["life"]) / float(s["max"])
		match s["k"]:
			"bolt":
				ci.draw_circle(s["p"], 12.0, Color(0.7, 0.8, 1, 0.4 * k2))
				ci.draw_line(s["from"], s["p"], Color(0.6, 0.7, 1, 0.25 * k2), 6.0)
			"ring":
				var c2: Color = s["c"]
				ci.draw_arc(s["p"], float(s["r"]), 0, TAU, 40, Color(c2.r, c2.g, c2.b, 0.3 * k2), 3.0)
			"star", "rays", "crystal", "runecircle":
				var c3: Color = s.get("c", Color.WHITE)
				ci.draw_circle(s["p"], 10.0, Color(c3.r, c3.g, c3.b, 0.2 * k2))
	if flash.a > 0.0:
		ci.draw_rect(Rect2(0, 0, 480, 270), flash)


func draw_ambient_glow(ci: CanvasItem, theme: String, p: Vector2, r: float) -> void:
	match theme:
		"fire", "wildfire":
			var fl := 0.8 + 0.2 * sin(t * 13.0) * sin(t * 7.0)
			ci.draw_circle(p + Vector2(0, -2), r * 2.2, Color(1, 0.35, 0.08, 0.10 * fl))
			ci.draw_circle(p, r * 1.4, Color(1, 0.55, 0.15, 0.10 * fl))
		"lightning":
			ci.draw_circle(p, r * 1.6, Color(0.7, 0.8, 1, 0.06 + 0.05 * sin(t * 20.0)))
		"frost":
			ci.draw_circle(p, r * 1.8, Color(0.5, 0.85, 1, 0.08))
		"blood", "bloodbanner":
			ci.draw_circle(p, r * 1.6, Color(0.9, 0.05, 0.1, 0.06 + 0.04 * max(0.0, sin(t * 6.0))))
		"sun", "glint", "crown", "laurel", "feathers", "coins", "harvest":
			ci.draw_circle(p, r * 1.8, Color(1, 0.85, 0.5, 0.07))
		"aurora":
			ci.draw_circle(p + Vector2(0, -r - 8), r * 2.0, Color(0.3, 1, 0.7, 0.06))
		"runes", "stars":
			ci.draw_circle(p, r * 1.8, Color(0.7, 0.45, 1, 0.07))


# ------------------------------------------------------------------ the bold pictures
const SPR := {
	"anvil": ["..#######..", "###########", "+#########+", "...#####...", "..#######..", ".#########."],
	"horse0": [".........##..", "........###+.", ".########.#..", "###########..", "#.#######....", "..#.....#....", ".#.......#...", "#.........#.."],
	"horse1": [".........##..", "........###+.", ".########.#..", "###########..", "#.#######....", "...#...#.....", "...#...#.....", "..#...#......"],
	"eagle_up": ["#.............#", "##...........##", ".##....+....##.", "..###.###.###..", "....#######....", ".......#.......", "......#+#......"],
	"eagle_dn": [".......+.......", "......###......", "..###########..", ".##.#######.##.", "##....###....##", "#......#......#", "......#+#......"],
	"heart": [".##.##.", "#+#####", "#######", ".#####.", "..###..", "...#..."],
	"skull": ["..#####..", ".#######.", "#########", "##..#..##", "##..#..##", "####.####", ".###.###.", "..#.#.#..", "..#####.."],
	"tower": ["#####", "#+++#", "#+#+#", "#+++#", "#+#+#", "#+++#", "#+++#", ".###."],
	"helm": ["..#####..", ".###+###.", "#########", "###...###", "##.....##", "##.....##"],
	"crown": ["+...+...+", "#+.###.+#", "#########", "#+##+##+#", "#########"],
	"flag": ["#+++++++", "#+++++++", "#++##+++", "#+++++++", "#++++++.", "#+++++..", "#.......", "#.......", "#.......", "#......."],
}
const SPR_COL := {
	"anvil": [Color(0.42, 0.44, 0.5), Color(0.75, 0.78, 0.85)],
	"horse0": [Color(0.45, 0.28, 0.16), Color(0.9, 0.85, 0.7)],
	"horse1": [Color(0.45, 0.28, 0.16), Color(0.9, 0.85, 0.7)],
	"eagle_up": [Color(0.96, 0.8, 0.42), Color(1, 1, 0.85)],
	"eagle_dn": [Color(0.96, 0.8, 0.42), Color(1, 1, 0.85)],
	"heart": [Color(0.85, 0.08, 0.15), Color(1, 0.6, 0.6)],
	"skull": [Color(0.9, 0.86, 0.78), Color(0.6, 0.1, 0.1)],
	"tower": [Color(0.55, 0.22, 0.16), Color(0.85, 0.45, 0.3)],
	"helm": [Color(0.7, 0.72, 0.8), Color(0.95, 0.4, 0.3)],
	"crown": [Color(0.96, 0.8, 0.42), Color(0.9, 0.4, 0.9)],
	"flag": [Color(0.4, 0.28, 0.18), Color(0.8, 0.08, 0.15)],
}


func spr(ci: CanvasItem, name: String, p: Vector2, a: float, sc := 1.0, flip := false) -> void:
	## draw a little pixel sprite centred on p (sc 2 = chunky and bold)
	var rows: Array = SPR[name]
	var cols: Array = SPR_COL[name]
	var h := rows.size()
	var w: int = str(rows[0]).length()
	for y in h:
		var row: String = rows[y]
		for x in w:
			var ch := row[x]
			if ch == "." or ch == " ":
				continue
			var c: Color = cols[0] if ch == "#" else cols[1]
			var xx := (w - 1 - x) if flip else x
			ci.draw_rect(Rect2((p + Vector2(xx - w / 2.0, y - h / 2.0) * sc).floor(), Vector2(sc, sc)), Color(c.r, c.g, c.b, a))


func _spear(ci: CanvasItem, tail: Vector2, tip: Vector2, a: float) -> void:
	var dv := (tip - tail).normalized()
	ci.draw_line(tail.floor(), (tip - dv * 3.0).floor(), Color(0.55, 0.38, 0.22, a), 1.0)
	ci.draw_line((tip - dv * 3.0).floor(), tip.floor(), Color(0.9, 0.92, 1.0, a), 2.0)
	_px(ci, tip - dv * 5.0 + dv.orthogonal(), Color(0.85, 0.15, 0.1, a))


func _shape2(ci: CanvasItem, s: Dictionary, k: float, e: float, a: float) -> void:
	var p: Vector2 = s["p"]
	var age: float = float(s["max"]) - float(s["life"])
	var sc: float = float(s.get("scale", 1.0))
	match s["k"]:
		"fall":
			var hit_t: float = s["hit_t"]
			var from: Vector2 = s["from"]
			var u: float = clamp(age / hit_t, 0.0, 1.0)
			var at := from.lerp(p, u * u) + Vector2(0, -sin(PI * u) * float(s.get("arc", 0.0)))
			var dv := (p - from).normalized()
			var fade: float = clamp(float(s["life"]) / 0.35, 0.0, 1.0)
			match str(s["what"]):
				"spear":
					_spear(ci, at - dv * 26.0, at, fade)
				"javelin":
					_spear(ci, at - dv * 13.0, at, fade)
				"arrow":
					ci.draw_line((at - dv * 6.0).floor(), at.floor(), Color(0.75, 0.6, 0.4, fade), 1.0)
					_px(ci, at, Color(0.9, 0.92, 1, fade))
					_px(ci, at - dv * 6.0 + dv.orthogonal(), Color(0.95, 0.95, 0.9, fade))
				"coin":
					_px(ci, at, Color(1, 0.88, 0.4, fade), 2.0 if int(age * 20.0) % 2 == 0 else 1.0, 2.0)
				_:
					spr(ci, str(s["what"]), at + Vector2(0, -3.0 * sc), fade, sc)
		"runner":
			var u2: float = clamp(age / 0.8, 0.0, 1.0)
			var x: float = lerp(float(s["x0"]), float(s["x1"]), u2)
			if u2 < 1.0:
				spr(ci, "horse0" if int(age * 14.0) % 2 == 0 else "horse1", Vector2(x, p.y - 4.0 * sc), 1.0, sc)
		"swoop":
			var from2: Vector2 = s["from"]
			var u3: float = clamp(age / 0.45, 0.0, 1.0)
			var at2 := from2.lerp(p + Vector2(0, -18), 1.0 - (1.0 - u3) * (1.0 - u3))
			if age > 0.9:
				at2 += Vector2(0, -(age - 0.9) * 160.0)
			var fr := "eagle_dn" if u3 < 1.0 or int(age * 8.0) % 2 == 0 else "eagle_up"
			spr(ci, fr, at2, clamp(float(s["life"]) / 0.3, 0.0, 1.0), sc)
		"wheel":
			var R: float = s["R"]
			ci.draw_arc(p, R, 0, TAU, 20, Color(0.6, 0.55, 0.5, a), 2.0)
			for j in 4:
				var ang := age * 22.0 + j * PI / 2.0
				ci.draw_line(p.floor(), (p + Vector2.from_angle(ang) * R).floor(), Color(0.75, 0.7, 0.62, a), 1.0)
		"slash":
			var L: float = float(s["L"]) * min(1.0, e * 6.0)
			var dvs := Vector2.from_angle(float(s["ang"]))
			var sep: float = max(0.0, e - 0.3) * 10.0
			for side in [-1.0, 1.0]:
				var o: Vector2 = dvs.orthogonal() * sep * side
				ci.draw_line((p - dvs * L * 0.5 + o).floor(), (p + dvs * L * 0.5 + o).floor(), Color(1, 0.3, 0.25, a), 3.0 if sep < 1.0 else 1.0)
				ci.draw_line((p - dvs * L * 0.5 + o).floor(), (p + dvs * L * 0.5 + o).floor(), Color(1, 1, 1, a), 1.0)
		"spike":
			var H: float = float(s["H"]) * min(1.0, e * 7.0)
			var lean: float = s["lean"]
			var tip := p + Vector2(lean * H, -H)
			var pts := PackedVector2Array([(p + Vector2(-2.5, 0)).floor(), tip.floor(), (p + Vector2(2.5, 0)).floor()])
			ci.draw_colored_polygon(pts, Color(0.55, 0.85, 1, a * 0.85))
			ci.draw_line((p + Vector2(-2.5, 0)).floor(), tip.floor(), Color(0.95, 1, 1, a), 1.0)
		"eye":
			var open: float = min(1.0, e * 5.0) * min(1.0, k * 5.0)
			var rows := 7
			for y in rows:
				var dy: float = abs(y - 3)
				if dy > open * 3.5:
					continue
				var row: String = ["....#####....", "..##.....##..", ".#...###...#.", "#...##+##...#", ".#...###...#.", "..##.....##..", "....#####...."][y]
				for x in 13:
					if row[x] == ".":
						continue
					var c := Color(0.9, 0.75, 1, a) if row[x] == "#" else Color(1, 1, 1, a)
					if row[x] == "#" and abs(x - 6) <= 1 and abs(y - 3) <= 1:
						c = Color(0.55, 0.15, 0.85, a)
					ci.draw_rect(Rect2((p + Vector2(x - 6.5, y - 3.5) * sc).floor(), Vector2(sc, sc)), c)
			if open > 0.8:
				var bot := p + Vector2(0, 4.0 * sc)
				var tgt := bot + Vector2(0, 14.0 + 4.0 * sc)
				ci.draw_line(bot.floor(), tgt.floor(), Color(0.7, 0.4, 1, a * 0.8), 2.0)
				ci.draw_line(bot.floor(), tgt.floor(), Color(1, 0.9, 1, a), 1.0)
		"splat":
			var R2: float = float(s["R"]) * min(1.0, e * 6.0)
			var rng := RandomNumberGenerator.new()
			rng.seed = int(s["seed"])
			for i in 70:
				var ang2 := rng.randf() * TAU
				var d := pow(rng.randf(), 0.6) * R2 * (0.7 + 0.5 * sin(ang2 * 5.0 + float(s["seed"] % 7)))
				_px(ci, p + Vector2(cos(ang2) * d, sin(ang2) * d * 0.6), Color(0.6 + rng.randf() * 0.25, 0.03, 0.08, a))
			for i in 5:
				var dx := rng.randf_range(-R2, R2) * 0.8
				var Ld: float = min(1.0, e * 2.0) * rng.randf_range(4, 14)
				ci.draw_line((p + Vector2(dx, 0)).floor(), (p + Vector2(dx, Ld)).floor(), Color(0.65, 0.03, 0.08, a), 1.0)
		"heart":
			var beat := 1.0 + (0.5 if fmod(age, 0.6) < 0.08 or (fmod(age, 0.6) > 0.16 and fmod(age, 0.6) < 0.24) else 0.0)
			spr(ci, "heart", p, a, sc * beat)
		"stalk":
			var H2: float = float(s["H"]) * min(1.0, e * 4.0)
			var sway: float = sin(age * 4.0 + p.x * 0.3) * 2.0 * min(1.0, e * 3.0)
			var top := p + Vector2(sway, -H2)
			ci.draw_line(p.floor(), top.floor(), Color(0.55, 0.65, 0.25, a), 1.0)
			_px(ci, top - Vector2(0, 2), Color(0.98, 0.85, 0.4, a), 1.0, 3.0)
			_px(ci, top + Vector2(-1, -1), Color(0.9, 0.75, 0.3, a))
			_px(ci, top + Vector2(1, -2), Color(0.9, 0.75, 0.3, a))
		"pillar":
			var W: float = float(s["W"]) * sin(min(1.0, e * 1.0) * PI)
			var c2: Color = s["c"]
			if W > 0.5:
				ci.draw_rect(Rect2(Vector2(p.x - W / 2.0, 0).floor(), Vector2(max(1.0, W), p.y + 6.0)), Color(c2.r, c2.g, c2.b, 0.35 * a))
				ci.draw_rect(Rect2(Vector2(p.x - W / 4.0, 0).floor(), Vector2(max(1.0, W / 2.0), p.y + 6.0)), Color(1, 1, 1, 0.3 * a))
		"rise":
			var up: float = min(1.0, e * 5.0)
			spr(ci, str(s["what"]), p + Vector2(0, -4.0 - 6.0 * up), a)
		"wreath":
			var dn: float = min(1.0, e * 2.5)
			var c3 := p + Vector2(0, -30.0 * (1.0 - dn))
			var R3: float = s["R"]
			for j in 18:
				var ang3 := PI * 0.15 + j * (PI * 1.7) / 17.0 + PI / 2.0
				var lp := c3 + Vector2(cos(ang3), sin(ang3) * 0.8) * R3
				_px(ci, lp, Color(0.45, 0.8, 0.3, a) if j % 2 == 0 else Color(0.96, 0.8, 0.42, a), 2.0, 1.0)
		"bash":
			var out: float = sin(min(1.0, e * 2.0) * PI)
			spr(ci, "tower", p + Vector2(float(s["R"]) + 4.0 + out * 12.0, 0), a, 2.0)
			for j in 5:
				var ang4 := (j - 2) * 0.22
				var base := p + Vector2(float(s["R"]) + 14.0 + out * 12.0, 0)
				ci.draw_line(base.floor(), (base + Vector2.from_angle(ang4) * (6.0 + e * 26.0)).floor(), Color(0.8, 0.9, 1, a * 0.8), 1.0)
		"tornado":
			var R4: float = s["R"]
			for j in 12:
				var hy: float = p.y + 6.0 - j * 3.5 * min(1.0, e * 3.0)
				var w2 := (3.0 + j * 1.6) * (0.8 + 0.2 * sin(age * 10.0 + j))
				var cx := p.x + sin(age * 6.0 + j * 0.6) * 3.0
				ci.draw_arc(Vector2(cx, hy), w2, age * 8.0 + j, age * 8.0 + j + PI * 1.4, 10, Color(0.8, 1, 0.75, a * (1.0 - j / 14.0)), 1.0)
		"comet":
			var R5: float = s["R"]
			for j in 14:
				var tt := age * 9.0 - j * 0.12
				var cp := p + Vector2(cos(tt) * R5 * 1.3, sin(tt) * R5 * 0.6)
				_px(ci, cp, Color(1, 0.9 - j * 0.04, 0.55 - j * 0.03, a * (1.0 - j / 14.0)), 2.0 if j < 3 else 1.0, 2.0 if j < 3 else 1.0)
		"sprite":
			spr(ci, str(s["what"]), p + Vector2(0, -float(s.get("rise", 0.0)) * e), a, sc)
		"tally":
			var n: int = int(min(10.0, e * 16.0))
			for j in n:
				var x2 := p.x + j * 3.0 + (2.0 if j >= 5 else 0.0)
				ci.draw_line(Vector2(x2, p.y).floor(), Vector2(x2, p.y + 6).floor(), Color(0.9, 0.85, 0.8, a), 1.0)
			if e > 0.66:
				ci.draw_line((p + Vector2(-2, 7)).floor(), (p + Vector2(32, -1)).floor(), Color(0.9, 0.1, 0.1, a), 1.0)
		"steps":
			var n2: int = int(min(10.0, e * 14.0))
			for j in n2:
				var sp := p + Vector2(-40.0 + j * 9.0, 10.0 + (3.0 if j % 2 == 0 else -1.0))
				_px(ci, sp, Color(0.85, 0.75, 0.55, a * (0.4 + 0.6 * float(j) / 10.0)), 2.0, 1.0)
				_px(ci, sp + Vector2(2, -1), Color(0.85, 0.75, 0.55, a * 0.6))
		"sunbeam":
			var x3: float = s["x"]
			var top2 := Vector2(x3 - 30.0, 0)
			var wbeam: float = 4.0 * sin(min(1.0, e) * PI)
			ci.draw_line(top2.floor(), (p + Vector2(x3 - p.x, 0)).floor(), Color(1, 0.9, 0.6, 0.28 * a), max(1.0, wbeam))
		"shooting":
			var from3: Vector2 = s["from"]
			var u4: float = clamp(e / 0.6, 0.0, 1.0)
			var head := from3.lerp(p, u4)
			for j in 16:
				_px(ci, head - (p - from3).normalized() * j * 2.0, Color(1, 0.95, 1, a * (1.0 - j / 16.0)))
			if u4 >= 1.0:
				_px(ci, p - Vector2(1, 1), Color(1, 1, 1, a), 3.0, 3.0)


# ------------------------------------------------------------------ little pictures
func _wings(ci: CanvasItem, p: Vector2, r: float, c: Color, a: float, flap: float) -> void:
	for side in [-1.0, 1.0]:
		for j in 5:
			var ang: float = (-PI / 2.0 + side * (0.5 + j * 0.28 + flap))
			var base: Vector2 = p + Vector2(side * r * 0.6, -r * 0.2)
			var L := r * 0.9 + 6.0 - j * 1.2
			ci.draw_line(base.floor(), (base + Vector2.from_angle(ang) * L).floor(), Color(c.r, c.g, c.b, a * (1.0 - j * 0.12)), 1.0)


func _crown(ci: CanvasItem, p: Vector2, c: Color) -> void:
	var pts := PackedVector2Array([p + Vector2(-5, 2), p + Vector2(-5, -2), p + Vector2(-3, 0), p + Vector2(0, -4), p + Vector2(3, 0), p + Vector2(5, -2), p + Vector2(5, 2), p + Vector2(-5, 2)])
	for i in pts.size():
		pts[i] = pts[i].floor()
	ci.draw_polyline(pts, c, 1.0)
	_px(ci, p + Vector2(0, -5), Color(1, 1, 1, c.a))


func _skull(ci: CanvasItem, p: Vector2, c: Color) -> void:
	var rows := ["01110", "11111", "10101", "11111", "01010"]
	for y in rows.size():
		for x in 5:
			if rows[y][x] == "1":
				_px(ci, p + Vector2(x - 2, y - 3), c)


func _aurora(ci: CanvasItem, p: Vector2, r: float, a: float, wide := false) -> void:
	var span := 150 if wide else 24
	var base_y := p.y if wide else p.y - r - 14.0
	for x in range(-span, span + 1, 1):
		var y0 := base_y + sin(t * 1.2 + x * 0.06 * (0.4 if wide else 3.0)) * (8.0 if wide else 4.0)
		var h := (14.0 if wide else 6.0) + 4.0 * sin(t * 0.8 + x * 0.12)
		var k := 0.5 + 0.5 * sin(t * 0.7 + x * 0.05)
		var c := Color(0.3, 1, 0.65).lerp(Color(0.6, 0.45, 1), k)
		var fade := 1.0 - absf(float(x)) / float(span + 1)
		ci.draw_rect(Rect2(Vector2(p.x + x, y0).floor(), Vector2(1, h)), Color(c.r, c.g, c.b, a * 0.35 * fade))


func _constellation(ci: CanvasItem, p: Vector2, R: float, seed: int, a: float, grow: float) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	var pts: Array = []
	for i in 6:
		pts.append(p + Vector2.from_angle(rng.randf() * TAU) * rng.randf_range(R * 0.5, R))
	var shown: int = int(clamp(grow * 8.0, 0.0, 6.0))
	for i in range(1, shown):
		ci.draw_line(Vector2(pts[i - 1]).floor(), Vector2(pts[i]).floor(), Color(0.75, 0.65, 1, a * 0.45), 1.0)
	for i in shown:
		var tw := 0.6 + 0.4 * sin(t * 3.0 + i * 1.7)
		_px(ci, pts[i], Color(1, 0.95, 1, a * tw))
