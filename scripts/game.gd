extends Node
## Autoload "Game": run state, data tables, and small UI helpers shared by every scene.

signal changed
signal ledger_written(text)
signal scene_requested(scene_name)

const QUOTA := 120            # grain the Emperor's ledger demands at the Great Altar
const TRIBUTE_NEEDED := 3     # sacred offerings the ledger demands
## testing switch: start every run with a bottomless purse
const INFINITE_GOLD := true
const MAX_REGS := 7
const MAX_MEN := 35
const TOTAL_LEGS := 5
const MEN_PER_GRAIN := 8.0

# ---------------------------------------------------------------- data tables
const UNITS := {
	"spear": {"name": "Hastati", "hp": 30.0, "atk": 7.0, "r_atk": 0.0, "m_arm": 2.0, "r_arm": 1.0, "cd": 1.0, "speed": 24.0, "reach": 11.0, "cost": 3, "idx": 0,
		"blurb": "Cheap. Holds a line. Kills horses."},
	"shield": {"name": "Scutarii", "hp": 40.0, "atk": 6.0, "r_atk": 0.0, "m_arm": 3.0, "r_arm": 4.0, "cd": 0.9, "speed": 21.0, "reach": 9.0, "cost": 4, "idx": 1,
		"blurb": "Soaks arrows and blows. Slow."},
	"archer": {"name": "Sagittarii", "hp": 20.0, "atk": 4.0, "r_atk": 7.0, "m_arm": 0.0, "r_arm": 0.0, "cd": 1.1, "speed": 24.0, "reach": 9.0, "cost": 4, "idx": 2,
		"blurb": "Shreds light armour. Dies to cavalry."},
	"cavalry": {"name": "Equites", "hp": 46.0, "atk": 9.0, "r_atk": 0.0, "m_arm": 2.0, "r_arm": 1.0, "cd": 1.0, "speed": 54.0, "reach": 11.0, "cost": 8, "idx": 3,
		"blurb": "Expensive. Flanks. Breaks archers and shields."},
}

const FORMATIONS := {
	"line": {"name": "Line", "desc": "7 wide, fills front ranks first. No modifiers."},
	"wedge": {"name": "Wedge", "desc": "Charge damage up. Enemies struck lose attack and attack speed."},
	"ring": {"name": "Ring", "desc": "Big melee armour and attack. Almost immobile. Never flanked."},
	"loose": {"name": "Loose", "desc": "Faster, dodges volleys. Weaker armour."},
	"testudo": {"name": "Testudo", "desc": "Huge armour, near-immune to arrows. Crawls. Cavalry charges break it."},
	"dense": {"name": "Dense", "desc": "Weaker single shots, much stronger volleys."},
}
const FORMS_BY_TYPE := {
	"spear": ["line", "wedge", "ring", "loose"],
	"shield": ["line", "testudo", "ring", "wedge", "loose"],
	"cavalry": ["line", "wedge"],
	"archer": ["line", "dense", "loose"],
}

const ITEMS := {
	"ivory": {"name": "Ivory Tusk", "icon": 0, "value": 30, "kind": "wealth", "tribute": true, "desc": "Taken from a merchant's wreck. The ledger lists it as an offering."},
	"serpent_ring": {"name": "Serpent Ring", "icon": 1, "value": 45, "kind": "wealth", "tribute": true, "desc": "Gold wound into a snake biting nothing. Someone wore it for a lifetime."},
	"gem": {"name": "Sea-Glass Gem", "icon": 2, "value": 35, "kind": "wealth", "tribute": true, "desc": "Cold and blue. Priests say the inner sea sweats them."},
	"gladius": {"name": "Good Gladius", "icon": 3, "value": 20, "kind": "wealth", "tribute": false, "equip": "any", "desc": "EQUIP at camp: one regiment gains +1 attack."},
	"leather": {"name": "Cured Hides", "icon": 4, "value": 12, "kind": "wealth", "tribute": false, "desc": "Sells anywhere. Smells everywhere."},
	"relic_horn": {"name": "Ancestral Horn", "icon": 6, "value": 60, "kind": "oath", "tribute": true, "desc": "Frostbay's war-horn. The Empire carried it south as an 'offering'. They want it back."},
	"seed_pouch": {"name": "Seed Grain", "icon": 7, "value": 25, "kind": "growth", "tribute": true, "desc": "Next year's forest-edge harvest, in a pouch."},
	"codex": {"name": "Sealed Codex", "icon": 8, "value": 40, "kind": "memory", "tribute": true, "desc": "A Duskviolet record of omens. Unique. Flammable."},
	"white_ox": {"name": "White Ox", "icon": 9, "value": 50, "kind": "life", "tribute": true, "desc": "Unblemished. It has walked beside the column since the fortress."},
	"amber": {"name": "Amber", "icon": 10, "value": 22, "kind": "oath", "tribute": false, "desc": "Northern sap-stone. Oaths are sworn on it."},
	"silver_cup": {"name": "Silver Cup", "icon": 11, "value": 28, "kind": "wealth", "tribute": true, "desc": "A libation cup from a shrine that no longer has a roof."},
	"spearheads": {"name": "Iron Spearheads", "icon": 12, "value": 26, "kind": "wealth", "tribute": false, "equip": "spear", "desc": "EQUIP at camp: a spear regiment gains +2 attack."},
	"bowstrings": {"name": "Sinew Bowstrings", "icon": 13, "value": 26, "kind": "wealth", "tribute": false, "equip": "archer", "desc": "EQUIP at camp: an archer regiment gains +2 ranged attack."},
	"family_portrait": {"name": "Painted Portrait", "icon": 14, "value": 0, "kind": "memory", "tribute": false, "desc": "Livia and the child, on a cedar board. Worth nothing to anyone else."},
	"salt": {"name": "Salt Cone", "icon": 15, "value": 18, "kind": "growth", "tribute": false, "desc": "The forest tribes cannot make it. They will remember who brought it."},
}

const REGIONS := {
	"south": {"name": "Vermilion Empire", "road": "the Imperial Road", "faction": "bandit", "values": ["wealth", "life"],
		"values_text": "wealth and lives", "enemy": "Deserters", "ground": "grass", "tint": Color(1.0, 0.95, 0.9),
		"blurb": "Roads, aqueducts, hungry villages.\nEnemy: deserters. Plain, predictable."},
	"west": {"name": "Thorncrown Tribes", "road": "the Thorn Woods", "faction": "west", "values": ["growth"],
		"values_text": "what would have grown", "enemy": "Thorncrown warbands", "ground": "mud", "tint": Color(0.9, 1.0, 0.94),
		"blurb": "Old forest, goblin oaths.\nEnemy: many, weak, and they AMBUSH from a flank."},
	"north": {"name": "Frostbay Clans", "road": "the Fjord Road", "faction": "north", "values": ["oath"],
		"values_text": "oaths and honour", "enemy": "Frostbay oathshields", "ground": "snow", "tint": Color(0.9, 0.97, 1.06),
		"blurb": "Cold coast, tall clans.\nEnemy: few, heavy, hard to break."},
	"east": {"name": "Duskviolet Court", "road": "the Violet Causeway", "faction": "east", "values": ["memory"],
		"values_text": "memory and knowledge", "enemy": "Veiled cohorts", "ground": "ash", "tint": Color(1.0, 0.86, 1.1),
		"blurb": "Towers, veils, seals.\nEnemy: hexers that strip armour; fragile up close."},
}

const FACTION_STATS := {
	"bandit": {"hp": 0.85, "atk": 0.9, "speed": 1.0},
	"north": {"hp": 1.5, "atk": 1.25, "speed": 0.9},
	"west": {"hp": 0.62, "atk": 0.8, "speed": 1.2},
	"east": {"hp": 0.75, "atk": 1.05, "speed": 1.0},
	"south": {"hp": 1.0, "atk": 1.0, "speed": 1.0},
}

## The doctrine wheel.
## Ring 0: five corps, 5 drills each (every drill fills 20% of its circle).
## Ring 1: ten arts, 3 levels each. An art's level N needs its corps at level N + 1.
## Ring 2: ten specialisations, two per corps, chosen once the corps is mastered - taking one seals the other.
## Ring 3: five war-orders (strong, each with a price; at most two) and four lore nodes that only the road can unlock.
const TREE := {
	"spear": {"ring": 0, "ang": -90.0, "max": 5, "name": "Hastati", "icon": "spear", "col": Color(0.93, 0.42, 0.28),
		"per": "Hastati: +6% health and attack", "mile": {3: "Wedge Drill - any wedge charges twice as hard", 5: "Hollow Square - ring gains +40% armour and moves faster"}},
	"shield": {"ring": 0, "ang": -18.0, "max": 5, "name": "Scutarii", "icon": "shield", "col": Color(0.42, 0.62, 0.92),
		"per": "Scutarii: +8% health, +0.4 armour", "mile": {3: "Testudo Drill - testudo moves 50% faster", 5: "Iron Testudo - cavalry can no longer break it"}},
	"archer": {"ring": 0, "ang": 54.0, "max": 5, "name": "Sagittarii", "icon": "bow", "col": Color(0.5, 0.82, 0.4),
		"per": "Sagittarii: +0.8 ranged attack", "mile": {3: "Volley Discipline - volley recharges 35% faster", 5: "Heavy Shafts - every arrow hits 25% harder"}},
	"cavalry": {"ring": 0, "ang": 126.0, "max": 5, "name": "Equites", "icon": "horse", "col": Color(0.95, 0.76, 0.3),
		"per": "Equites: +6% attack, +4% speed", "mile": {3: "Lances - charges deal +50% damage", 5: "Trampling - charged men are shaken (slower, weaker)"}},
	"eagle": {"ring": 0, "ang": 198.0, "max": 5, "name": "The Eagle", "icon": "eagle", "col": Color(0.86, 0.36, 0.7),
		"per": "Every regiment: +3% health", "mile": {3: "Camp Augur - enemy numbers known before battle", 5: "While the Eagle stands - all regiments +10% armour"}},
	# ---- ring 1: arts
	"whet": {"ring": 1, "ang": -108.0, "max": 3, "parent": "spear", "name": "Whetstones", "icon": "swords", "col": Color(0.98, 0.55, 0.35),
		"per": "+5% damage, all regiments"},
	"crit": {"ring": 1, "ang": -72.0, "max": 3, "parent": "spear", "name": "Weak Points", "icon": "star", "col": Color(1.0, 0.86, 0.4),
		"per": "+5% chance to strike for x1.8 (CRITICAL)"},
	"iron": {"ring": 1, "ang": -36.0, "max": 3, "parent": "shield", "name": "Iron Discipline", "icon": "shield2", "col": Color(0.6, 0.72, 0.9),
		"per": "+7% armour, all regiments"},
	"frost": {"ring": 1, "ang": 0.0, "max": 3, "parent": "shield", "name": "Northern Rime", "icon": "snow", "col": Color(0.55, 0.9, 1.0),
		"per": "+5% chance a hit FREEZES: the man slows and weakens"},
	"fire": {"ring": 1, "ang": 36.0, "max": 3, "parent": "archer", "name": "Burning Pitch", "icon": "flame", "col": Color(1.0, 0.5, 0.18),
		"per": "+5% chance a hit SETS ABLAZE: 2.5 damage a second for 3s"},
	"hex": {"ring": 1, "ang": 72.0, "max": 3, "parent": "archer", "name": "Violet Hex", "icon": "eye", "col": Color(0.74, 0.45, 1.0),
		"per": "+6% chance a hit CURSES the regiment: half armour for 4s"},
	"bolt": {"ring": 1, "ang": 108.0, "max": 3, "parent": "cavalry", "name": "Jove's Bolt", "icon": "bolt", "col": Color(1.0, 0.97, 0.55),
		"per": "+4% chance a hit calls LIGHTNING: jumps to 2 nearby men"},
	"blood": {"ring": 1, "ang": 144.0, "max": 3, "parent": "cavalry", "name": "Blood Oath", "icon": "drop", "col": Color(0.92, 0.2, 0.26),
		"per": "Melee hits heal the striker for 6% of the damage"},
	"forage": {"ring": 1, "ang": 180.0, "max": 3, "parent": "eagle", "name": "Quartermaster", "icon": "wheat", "col": Color(0.92, 0.82, 0.5),
		"per": "The column eats 10% less grain  (level 3: recruits 1 d cheaper)"},
	"medici": {"ring": 1, "ang": 216.0, "max": 3, "parent": "eagle", "name": "Field Medici", "icon": "cross", "col": Color(0.5, 0.95, 0.66),
		"per": "+12% of the fallen walk again after a victory"},
	# ---- ring 2: specialisations (one of each pair)
	"triarii": {"ring": 2, "ang": -100.0, "max": 1, "parent": "spear", "rival": "velites", "name": "Triarii", "icon": "wall", "col": Color(0.86, 0.36, 0.24),
		"per": "Hastati become veterans: +40% health, +2 armour, 15% slower"},
	"velites": {"ring": 2, "ang": -80.0, "max": 1, "parent": "spear", "rival": "triarii", "name": "Velites", "icon": "javelin", "col": Color(1.0, 0.6, 0.4),
		"per": "Hastati run light: +30% speed and they CHARGE like horse"},
	"praetor": {"ring": 2, "ang": -28.0, "max": 1, "parent": "shield", "rival": "bash", "name": "Praetorians", "icon": "helm", "col": Color(0.5, 0.6, 1.0),
		"per": "Scutarii: +3 armour, +15% attack"},
	"bash": {"ring": 2, "ang": -8.0, "max": 1, "parent": "shield", "rival": "praetor", "name": "Shield Bash", "icon": "fist", "col": Color(0.4, 0.78, 1.0),
		"per": "Scutarii melee hits have 20% chance to STUN (shaken 1.5s)"},
	"longbow": {"ring": 2, "ang": 44.0, "max": 1, "parent": "archer", "rival": "skirm", "name": "Longbowmen", "icon": "bow2", "col": Color(0.4, 0.9, 0.5),
		"per": "Sagittarii: +30% range, +1 ranged attack"},
	"skirm": {"ring": 2, "ang": 64.0, "max": 1, "parent": "archer", "rival": "longbow", "name": "Skirmishers", "icon": "feet", "col": Color(0.7, 0.95, 0.4),
		"per": "Sagittarii: +40% speed, shoot 25% faster"},
	"cata": {"ring": 2, "ang": 116.0, "max": 1, "parent": "cavalry", "rival": "raider", "name": "Cataphracts", "icon": "helm", "col": Color(0.95, 0.65, 0.25),
		"per": "Equites in mail: +50% health, +2 armour, 15% slower"},
	"raider": {"ring": 2, "ang": 136.0, "max": 1, "parent": "cavalry", "rival": "cata", "name": "Raiders", "icon": "feet", "col": Color(1.0, 0.88, 0.45),
		"per": "Equites: +25% speed, charges hit another +50%"},
	"aeterna": {"ring": 2, "ang": 188.0, "max": 1, "parent": "eagle", "rival": "auxilia", "name": "Legio Aeterna", "icon": "laurel", "col": Color(0.95, 0.45, 0.8),
		"per": "Every regiment: +10% health, +10% damage"},
	"auxilia": {"ring": 2, "ang": 208.0, "max": 1, "parent": "eagle", "rival": "aeterna", "name": "Auxilia", "icon": "coin", "col": Color(0.8, 0.5, 0.95),
		"per": "Recruits cost 2 d less, and every village offers half again as many men"},
	# ---- ring 3: war-orders (price attached, at most two) ...
	"decim": {"ring": 3, "ang": -54.0, "max": 1, "order": true, "name": "Decimation", "icon": "skull", "col": Color(0.9, 0.25, 0.25),
		"per": "All regiments +20% damage", "cost_txt": "After every battle, each regiment executes one of its own"},
	"scorch": {"ring": 3, "ang": 18.0, "max": 1, "order": true, "name": "Scorched Earth", "icon": "flame", "col": Color(1.0, 0.45, 0.15),
		"per": "Every victory: burn the enemy's stores, +15 grain", "cost_txt": "Villages offer half as many recruits"},
	"forced": {"ring": 3, "ang": 90.0, "max": 1, "order": true, "name": "Forced March", "icon": "feet", "col": Color(0.95, 0.8, 0.4),
		"per": "The column rides 40% faster", "cost_txt": "The column eats 25% more grain"},
	"bloodstd": {"ring": 3, "ang": 162.0, "max": 1, "order": true, "name": "Blood on the Standard", "icon": "drop", "col": Color(0.85, 0.15, 0.3),
		"per": "All regiments +25% health", "cost_txt": "The Field Medici save no one"},
	"shieldsdown": {"ring": 3, "ang": 234.0, "max": 1, "order": true, "name": "Shields Down", "icon": "swords", "col": Color(1.0, 0.6, 0.3),
		"per": "All regiments +30% damage", "cost_txt": "All regiments -30% armour"},
	# ---- ... and lore, given only by the road
	"lore_south": {"ring": 3, "ang": -90.0, "max": 1, "lore": "lore_south", "name": "Sons of the Vicus", "icon": "laurel", "col": Color(1.0, 0.85, 0.6),
		"per": "Hastati and Scutarii +15% health (local boys know the ground)", "hint": "Feed a village instead of taxing it"},
	"lore_north": {"ring": 3, "ang": -18.0 + 0.0, "max": 1, "lore": "lore_north", "name": "Frostbay Oath", "icon": "snow", "col": Color(0.7, 0.92, 1.0),
		"per": "Scutarii +2 armour; Northern Rime freezes 10% more often", "hint": "Keep faith with Frostbay over the horn"},
	"lore_west": {"ring": 3, "ang": 54.0, "max": 1, "lore": "lore_west", "name": "Thorncrown Paths", "icon": "leaf", "col": Color(0.55, 0.95, 0.5),
		"per": "First 12 seconds of every battle: +40% damage (you know the ground)", "hint": "Leave the forest its seed"},
	"lore_east": {"ring": 3, "ang": 126.0, "max": 1, "lore": "lore_east", "name": "Violet Calendar", "icon": "eye", "col": Color(0.8, 0.6, 1.0),
		"per": "Enemy numbers always known; volleys recharge 30% faster", "hint": "Trade with the Duskviolet envoy"},
}
const TREE_COSTS := [[8, 14, 22, 32, 44], [14, 24, 36], [60], [90]]
const LORE_COST := 40
const ORDER_NEED := 12          # drills learned before any war-order may be given
const MAX_ORDERS := 2
## pairs of arts that, both learned, produce a combined effect
const SYNERGIES := {
	"shatter": {"a": "frost", "b": "bolt", "name": "Shatter", "col": Color(0.7, 0.95, 1.0), "desc": "Lightning on a frozen man deals double and bursts into ice shards"},
	"wildfire": {"a": "fire", "b": "hex", "name": "Wildfire", "col": Color(0.85, 0.4, 1.0), "desc": "Burning men who die pass the fire to two neighbours; cursed men burn 50% hotter"},
	"bloodlust": {"a": "crit", "b": "blood", "name": "Bloodlust", "col": Color(1.0, 0.35, 0.35), "desc": "Critical hits heal the striker three times as much"},
	"glacier": {"a": "iron", "b": "frost", "name": "Glacier Wall", "col": Color(0.6, 0.85, 1.0), "desc": "Men who strike your ranks have 10% chance to freeze"},
	"surgeons": {"a": "blood", "b": "medici", "name": "Battle Surgeons", "col": Color(0.6, 1.0, 0.7), "desc": "Blood Oath works for arrows too; Medici save 10% more"},
	"wellfed": {"a": "forage", "b": "whet", "name": "Well Fed", "col": Color(1.0, 0.85, 0.5), "desc": "With 5 days of grain in the carts, all regiments +12% damage"},
}

# ---------------------------------------------------------------- run state
var denarii := 40
var grain := 45
var day := 1
var leg := 0
var region := "south"
var regiments: Array = []
var inventory: Array = []
var ledger: Array = []
var upgrades: Dictionary = {}     # doctrine id -> level
var promises: Array = []
var flags: Dictionary = {}
var omen: Dictionary = {}
var leg_state: Dictionary = {}
var next_battle: Dictionary = {}
var route_log: Array = []
var fallen := 0
var marched := 0
var battle_buff := {"dmg": 0.0, "armor": 0.0}
var game_over_reason := ""
var _reg_serial := 0

var theme: Theme
var font: Font
var font_en: Font
var font_zh: Font

# ---------------------------------------------------------------- language
const ZH_TABLE = preload("res://scripts/zh.gd")
const SETTINGS_PATH := "user://settings.cfg"
var lang := "en"
var LH := 9                     # text line step for hand-drawn text (13 in Chinese)
var settings_open := false
var _lcache: Dictionary = {}
var _nouns: Array = []
signal lang_changed
var _sfx: Dictionary = {}
var _sfx_missing: Dictionary = {}
var _players: Array = []
var _music: AudioStreamPlayer
var _music_name := ""
var tex_items: Texture2D
var tex_coin: Texture2D


func _ready() -> void:
	randomize()
	_load_settings()
	_build_nouns()
	_build_theme()
	tex_items = load("res://assets/ui/items.png")
	tex_coin = load("res://assets/ui/coin.png")
	for n in ["coin", "upgrade", "click", "clash", "arrow", "thud", "horn", "ritual", "ambient", "drums"]:
		var s = load("res://assets/audio/%s.wav" % n)
		if s != null:
			_sfx[n] = s
	for i in 14:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_players.append(p)
	_music = AudioStreamPlayer.new()
	_music.volume_db = -8.0
	add_child(_music)
	_music.finished.connect(func(): _music.play())
	process_mode = Node.PROCESS_MODE_ALWAYS
	new_run()


func new_run() -> void:
	denarii = 999999 if INFINITE_GOLD else 40
	grain = 45
	day = 1
	leg = 0
	region = "south"
	regiments = []
	_reg_serial = 0
	add_regiment("spear", 24)
	add_regiment("shield", 20)
	add_regiment("archer", 16)
	add_regiment("cavalry", 10)
	inventory = ["family_portrait", "white_ox", "relic_horn"]
	ledger = []
	upgrades = {}
	promises = [{"id": "home", "text": L("The fortress: grain before the snows."), "state": "open"}]
	flags = {}
	omen = {}
	leg_state = {}
	route_log = []
	fallen = 0
	marched = total_men()
	battle_buff = {"dmg": 0.0, "armor": 0.0}
	game_over_reason = ""
	write(L("Opened the gates to the refugees. Promised they could stay while the standard stood."))
	write(L("Accepted the Emperor's writ: reopen the north road, collect %d grain and %d offerings.") % [QUOTA, TRIBUTE_NEEDED])


# ---------------------------------------------------------------- regiments
func add_regiment(type: String, men: int, elite_name := "", mult := 1.0) -> Dictionary:
	_reg_serial += 1
	var numerals := ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
	var r := {
		"id": _reg_serial, "type": type, "men": men, "kills": 0, "rank": 0,
		"formation": "line", "atk_bonus": 0.0, "r_atk_bonus": 0.0, "mult": mult,
		"name": (elite_name if elite_name != "" else "%s %s" % [numerals[(_reg_serial - 1) % numerals.size()], UNITS[type]["name"]]),
		"elite": elite_name != "",
	}
	regiments.append(r)
	changed.emit()
	return r


func total_men() -> int:
	var n := 0
	for r in regiments:
		n += int(r["men"])
	return n


func lose_men(n: int) -> int:
	## removes n men starting from the largest regiments; returns how many were actually lost
	var lost := 0
	while n > 0 and total_men() > 0:
		var big = null
		for r in regiments:
			if big == null or r["men"] > big["men"]:
				big = r
		if big == null or big["men"] <= 0:
			break
		big["men"] -= 1
		n -= 1
		lost += 1
	fallen += lost
	regiments = regiments.filter(func(r): return r["men"] > 0)
	changed.emit()
	return lost


func lvl(id: String) -> int:
	return int(upgrades.get(id, 0))


func syn(id: String) -> bool:
	var sy: Dictionary = SYNERGIES[id]
	return lvl(str(sy["a"])) > 0 and lvl(str(sy["b"])) > 0


func total_drills() -> int:
	var n := 0
	for id in upgrades:
		n += int(upgrades[id])
	return n


func orders_given() -> int:
	var n := 0
	for id in TREE:
		if TREE[id].get("order", false) and lvl(id) > 0:
			n += 1
	return n


func tree_cost(id: String) -> int:
	## price of the next level, or -1 when maxed
	var l := lvl(id)
	var t: Dictionary = TREE[id]
	if l >= int(t["max"]):
		return -1
	if t.has("lore"):
		return LORE_COST
	return int(TREE_COSTS[int(t["ring"])][l])


func tree_need(id: String) -> int:
	## corps level an art needs before its next level can be bought (0 when not an art)
	var t: Dictionary = TREE[id]
	if int(t["ring"]) != 1:
		return 0
	return lvl(id) + 2


func tree_block(id: String) -> String:
	## why the next level cannot be bought (ignoring money); "" when it can
	var t: Dictionary = TREE[id]
	match int(t["ring"]):
		1:
			if lvl(str(t["parent"])) < tree_need(id):
				return L("needs %s level %d") % [L(str(TREE[t["parent"]]["name"])), tree_need(id)]
		2:
			if lvl(str(t["rival"])) > 0:
				return L("sealed - you chose %s") % L(str(TREE[t["rival"]]["name"]))
			if lvl(str(t["parent"])) < 5:
				return L("needs %s level 5") % L(str(TREE[t["parent"]]["name"]))
		3:
			if t.has("lore"):
				if not flags.has(str(t["lore"])):
					return L("unknown - ") + (L(str(t["hint"])) if lang != "en" else str(t["hint"]).to_lower())
			else:
				if total_drills() < ORDER_NEED:
					return L("needs %d drills learned (%d)") % [ORDER_NEED, total_drills()]
				if orders_given() >= MAX_ORDERS and lvl(id) == 0:
					return L("only %d war-orders may stand") % MAX_ORDERS
	return ""


func tree_open(id: String) -> bool:
	return tree_block(id) == ""


func recruit_cost(type: String) -> int:
	return max(1, int(UNITS[type]["cost"]) - (1 if lvl("forage") >= 3 else 0) - (2 if lvl("auxilia") > 0 else 0))


# ---------------------------------------------------------------- economy / time
func daily_need() -> int:
	var need := total_men() / MEN_PER_GRAIN
	need *= 1.0 - 0.1 * lvl("forage")
	if lvl("forced") > 0:
		need *= 1.25
	return int(ceil(need))


func pass_day() -> String:
	## One day's march. Returns a line describing what the day cost.
	day += 1
	var need := daily_need()
	var msg := L("Day %d. The column ate %d grain.") % [day, min(need, grain)]
	if grain >= need:
		grain -= need
	else:
		var deficit := need - grain
		grain = 0
		var lost := lose_men(deficit * 2)
		msg = L("Day %d. The grain ran out. %d men did not get up this morning.") % [day, lost]
		write(L("No grain. %d men starved or slipped away in the night.") % lost)
	changed.emit()
	return msg


func add_item(id: String) -> void:
	inventory.append(id)
	changed.emit()


func remove_item(id: String) -> bool:
	var i := inventory.find(id)
	if i < 0:
		return false
	inventory.remove_at(i)
	changed.emit()
	return true


func tribute_count() -> int:
	var n := 0
	for id in inventory:
		if ITEMS[id].get("tribute", false):
			n += 1
	return n


func write(text: String) -> void:
	ledger.append({"day": day, "text": text})
	if ledger.size() > 2:
		sfx("quill", -8.0, randf_range(0.9, 1.1))
	changed.emit()
	ledger_written.emit(text)


func promise(id: String, text: String) -> void:
	promises.append({"id": id, "text": text, "state": "open"})


func set_promise(id: String, state: String) -> void:
	for p in promises:
		if p["id"] == id:
			p["state"] = state


func has_promise(id: String, state := "open") -> bool:
	for p in promises:
		if p["id"] == id and p["state"] == state:
			return true
	return false


# ---------------------------------------------------------------- legs & battles
func start_leg(new_region: String) -> void:
	region = new_region
	route_log.append(new_region)
	omen = {}
	var first_visit := not flags.has("event_" + new_region)
	var ev: String = new_region
	if not first_visit:
		ev = "deserters" if randf() < 0.5 else "refugees"
	var pois: Array = [{"type": "camp", "x": 150.0, "used": false}]
	pois.append({"type": "event", "x": 520.0, "used": false, "event": ev})
	if new_region == "south" or randf() < 0.65:
		pois.append({"type": "shop", "x": 830.0, "used": false, "stock": _shop_stock()})
	pois.append({"type": "altar", "x": 1090.0, "used": false})
	pois.append({"type": "warning", "x": 1340.0, "used": false})
	pois.append({"type": "crossroads", "x": 1640.0, "used": false})
	leg_state = {"pois": pois, "x": 60.0, "length": 1760.0, "won": false, "options": _route_options()}
	next_battle = make_battle(new_region, leg)
	changed.emit()


func _route_options() -> Array:
	if leg >= TOTAL_LEGS - 1:
		return ["altar"]
	var pool := ["south", "west", "north", "east"]
	pool.shuffle()
	return [pool[0], pool[1]]


func _shop_stock() -> Array:
	var pool := ["gladius", "spearheads", "bowstrings", "salt", "leather", "amber", "silver_cup", "gem", "white_ox"]
	pool.shuffle()
	return [pool[0], pool[1], pool[2], pool[3]]


func make_battle(reg_name: String, leg_i: int) -> Dictionary:
	var faction: String = REGIONS[reg_name]["faction"]
	var men := 15 + leg_i * 3
	var main: Array = []
	var flank: Array = []
	match faction:
		"bandit":
			main = [["spear", men], ["spear", men], ["archer", men - 4]]
			if leg_i >= 1:
				main.append(["shield", men])
			flank = [["cavalry", 6 + leg_i * 2]]
		"north":
			main = [["shield", men - 4], ["shield", men - 4], ["spear", men - 5]]
			if leg_i >= 2:
				main.append(["shield", men - 4])
			flank = [["shield", men - 6]]
		"west":
			main = [["spear", men + 10], ["spear", men + 10], ["archer", men + 2], ["archer", men + 2]]
			flank = [["spear", men + 4], ["archer", men]]
			if flags.has("west_hostile"):
				flank.append(["spear", men + 4])
		"east":
			main = [["archer", men], ["archer", men], ["spear", men + 4], ["spear", men + 4]]
			flank = [["cavalry", 7 + leg_i * 2]]
	if leg_i >= 3:
		main.append([main[0][0], men])
	if flags.has("north_hostile") and faction == "north":
		main.append(["shield", men - 4])
	var loot_pool := {
		"bandit": ["gladius", "leather", "silver_cup", "spearheads"],
		"north": ["amber", "amber", "ivory", "gladius"],
		"west": ["leather", "seed_pouch", "bowstrings", "salt"],
		"east": ["gem", "codex", "serpent_ring", "silver_cup"],
	}
	var pool: Array = loot_pool[faction]
	return {
		"faction": faction, "region": reg_name, "main": main, "flank": flank,
		"flank_side": ("left" if randf() < 0.5 else "right"), "flank_time": randf_range(14.0, 22.0),
		"reward_denarii": 16 + leg_i * 7 + randi() % 8, "reward_grain": 6 + randi() % 10,
		"loot": pool[randi() % pool.size()], "name": L("%s, day %d") % [L(str(REGIONS[reg_name]["road"])), day],
	}


func rebuild_battle() -> void:
	## regenerate the next battle after the player changed a faction's mood, keeping what an omen may already have revealed
	var side = next_battle.get("flank_side", "left")
	var time = next_battle.get("flank_time", 16.0)
	next_battle = make_battle(region, leg)
	next_battle["flank_side"] = side
	next_battle["flank_time"] = time


func battle_enemy_men() -> int:
	var n := 0
	for g in next_battle["main"]:
		n += int(g[1])
	for g in next_battle["flank"]:
		n += int(g[1])
	return n


func go(scene_name: String) -> void:
	scene_requested.emit(scene_name)


# ---------------------------------------------------------------- audio
func sfx(sname: String, vol := 0.0, pitch := 1.0) -> void:
	if not _sfx.has(sname):
		if _sfx_missing.has(sname):
			return
		var path := "res://assets/audio/%s.wav" % sname
		var s: AudioStream = null
		if ResourceLoader.exists(path):
			s = load(path)
		elif FileAccess.file_exists(path):
			s = AudioStreamWAV.load_from_file(ProjectSettings.globalize_path(path))
		if s == null:
			_sfx_missing[sname] = true
			return
		_sfx[sname] = s
	for p in _players:
		if not p.playing:
			p.stream = _sfx[sname]
			p.volume_db = vol
			p.pitch_scale = pitch
			p.play()
			return


func music(mname: String) -> void:
	if _music_name == mname:
		return
	_music_name = mname
	_music.stop()
	if _sfx.has(mname):
		_music.stream = _sfx[mname]
		_music.play()


# ---------------------------------------------------------------- UI kit
func _build_theme() -> void:
	theme = Theme.new()
	if ResourceLoader.exists("res://assets/ui/pixel.fnt"):
		font_en = load("res://assets/ui/pixel.fnt")
	if font_en == null:
		font_en = ThemeDB.fallback_font
	if ResourceLoader.exists("res://assets/ui/zh.fnt"):
		font_zh = load("res://assets/ui/zh.fnt")
	if font_zh == null:
		font_zh = font_en
	_apply_font()
	var panel := _sb(Color(0.09, 0.07, 0.07, 0.96), Color(0.54, 0.41, 0.23), 5)
	theme.set_stylebox("panel", "PanelContainer", panel)
	theme.set_stylebox("normal", "Button", _sb(Color(0.17, 0.13, 0.11), Color(0.42, 0.32, 0.2), 3))
	theme.set_stylebox("hover", "Button", _sb(Color(0.3, 0.2, 0.13), Color(0.86, 0.68, 0.3), 3))
	theme.set_stylebox("pressed", "Button", _sb(Color(0.42, 0.16, 0.12), Color(0.86, 0.68, 0.3), 3))
	theme.set_stylebox("disabled", "Button", _sb(Color(0.11, 0.1, 0.1), Color(0.22, 0.2, 0.18), 3))
	var focus_sb := _sb(Color(0, 0, 0, 0), Color(1.0, 0.9, 0.55), 3)
	focus_sb.draw_center = false
	theme.set_stylebox("focus", "Button", focus_sb)
	theme.set_color("font_color", "Button", Color(0.91, 0.84, 0.66))
	theme.set_color("font_hover_color", "Button", Color(1.0, 0.93, 0.7))
	theme.set_color("font_pressed_color", "Button", Color(1, 1, 1))
	theme.set_color("font_disabled_color", "Button", Color(0.42, 0.39, 0.35))
	theme.set_color("font_color", "Label", Color(0.91, 0.84, 0.66))
	theme.set_constant("separation", "VBoxContainer", 3)
	theme.set_constant("separation", "HBoxContainer", 4)
	theme.set_constant("line_spacing", "Label", 1)
	_roman_skin()
	_apply_font()


func load_tex(path: String) -> Texture2D:
	## imported texture if the editor has seen it, else read the png straight from disk
	if ResourceLoader.exists(path):
		return load(path)
	if FileAccess.file_exists(path):
		var img := Image.load_from_file(ProjectSettings.globalize_path(path))
		if img != null:
			return ImageTexture.create_from_image(img)
	return null


func _tsb(path: String, m: int, content: Vector4, tile := true) -> StyleBoxTexture:
	var tx := load_tex(path)
	if tx == null:
		return null
	var sb := StyleBoxTexture.new()
	sb.texture = tx
	sb.texture_margin_left = m
	sb.texture_margin_right = m
	sb.texture_margin_top = m
	sb.texture_margin_bottom = m
	sb.content_margin_left = content.x
	sb.content_margin_top = content.y
	sb.content_margin_right = content.z
	sb.content_margin_bottom = content.w
	if tile:
		sb.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
		sb.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
	return sb


func _roman_skin() -> void:
	## gold meander frames, bronze plaques for buttons, a scroll-tipped rule for separators
	var panel := _tsb("res://assets/ui/roman_panel.png", 12, Vector4(13, 12, 13, 12))
	if panel != null:
		theme.set_stylebox("panel", "PanelContainer", panel)
	for st in ["normal", "hover", "pressed", "disabled"]:
		var b := _tsb("res://assets/ui/roman_btn_%s.png" % st, 4, Vector4(7, 3, 7, 3), false)
		if b != null:
			theme.set_stylebox(st, "Button", b)
	var sep_tx := load_tex("res://assets/ui/roman_sep.png")
	if sep_tx != null:
		var sep := StyleBoxTexture.new()
		sep.texture = sep_tx
		sep.texture_margin_left = 8
		sep.texture_margin_right = 8
		sep.content_margin_top = 2
		sep.content_margin_bottom = 2
		theme.set_stylebox("separator", "HSeparator", sep)
		theme.set_constant("separation", "HSeparator", 7)
	var tp := _tsb("res://assets/ui/roman_title.png", 5, Vector4(9, 1, 9, 1), false)
	if tp != null:
		theme.set_type_variation("TitlePlate", "PanelContainer")
		theme.set_stylebox("panel", "TitlePlate", tp)


func _sb(bg: Color, border: Color, margin: int) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(1)
	sb.set_content_margin_all(margin)
	sb.anti_aliasing = false
	return sb


func label(text: String, color = null, wrap_width := 0) -> Label:
	var l := Label.new()
	l.text = L(text)
	if color != null:
		l.add_theme_color_override("font_color", color)
	if wrap_width > 0:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size.x = wrap_width
	return l


func button(text: String, cb: Callable, enabled := true) -> Button:
	var b := Button.new()
	b.text = L(text)
	b.disabled = not enabled
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.focus_mode = Control.FOCUS_NONE
	var on_press := func():
		sfx("ui_press", -4.0, randf_range(0.95, 1.05))
		cb.call()
	b.pressed.connect(on_press)
	b.mouse_entered.connect(_btn_hover.bind(b))
	return b


func _btn_hover(b: Button) -> void:
	if is_instance_valid(b) and not b.disabled:
		sfx("ui_hover", -14.0, randf_range(0.95, 1.1))


func enable_keys(root) -> void:
	## make every button under root reachable with arrows / Tab and Enter, and focus the first usable one
	if not is_instance_valid(root) or not root.is_inside_tree():
		return
	var first: Button = null
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		var kids := n.get_children()
		kids.reverse()
		stack.append_array(kids)
		if n is Button:
			n.focus_mode = Control.FOCUS_ALL
			if first == null and not n.disabled and n.text != "x":
				first = n
	if first != null:
		first.grab_focus()


func item_icon(id: String) -> AtlasTexture:
	var a := AtlasTexture.new()
	a.atlas = tex_items
	a.region = Rect2(int(ITEMS[id]["icon"]) * 16, 0, 16, 16)
	return a


func icon_rect(tex: Texture2D) -> TextureRect:
	var t := TextureRect.new()
	t.texture = tex
	t.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	t.custom_minimum_size = Vector2(16, 16)
	return t


# ---------------------------------------------------------------- localisation
func L(s) -> String:
	## translate a visible string. English is the source language; Chinese comes from scripts/zh.gd.
	var t := str(s)
	if lang == "en" or t == "":
		return t
	var D: Dictionary = ZH_TABLE.D
	if D.has(t):
		return D[t]
	if _lcache.has(t):
		return _lcache[t]
	var out := t
	if t.find("\n") >= 0:
		var parts := t.split("\n")
		for i in parts.size():
			parts[i] = L(parts[i])
		out = "\n".join(parts)
	else:
		# composite text (already-translated sentence + an English proper name): swap the names
		for pair in _nouns:
			if out.find(pair[0]) >= 0:
				out = out.replace(pair[0], pair[1])
	if _lcache.size() > 4000:
		_lcache.clear()
	_lcache[t] = out
	return out


func _build_nouns() -> void:
	var D: Dictionary = ZH_TABLE.D
	var names := {}
	for tbl in [UNITS, FORMATIONS, ITEMS, TREE, SYNERGIES]:
		for k in tbl:
			names[str(tbl[k]["name"])] = true
	for k in REGIONS:
		for f in ["name", "road", "enemy", "values_text"]:
			names[str(REGIONS[k][f])] = true
	names["Frostbay Oathshields"] = true
	_nouns.clear()
	for n in names:
		if D.has(n):
			_nouns.append([n, D[n]])
	_nouns.sort_custom(func(a, b): return str(a[0]).length() > str(b[0]).length())


func _apply_font() -> void:
	font = font_zh if lang == "zh" else font_en
	LH = 13 if lang == "zh" else 9
	theme.default_font = font
	theme.default_font_size = 8
	theme.set_constant("line_spacing", "Label", 0 if lang == "zh" else 1)


func _load_settings() -> void:
	var cf := ConfigFile.new()
	if cf.load(SETTINGS_PATH) == OK:
		lang = str(cf.get_value("general", "language", "en"))
	if lang != "zh":
		lang = "en"


func set_lang(l: String) -> void:
	if l == lang:
		return
	lang = l
	_lcache.clear()
	_apply_font()
	var cf := ConfigFile.new()
	cf.load(SETTINGS_PATH)
	cf.set_value("general", "language", lang)
	cf.save(SETTINGS_PATH)
	lang_changed.emit()


func open_settings(on_close: Callable = Callable()) -> void:
	## a small modal: language English / 中文. Lives on its own layer so any screen can open it.
	if settings_open:
		return
	settings_open = true
	var layer := CanvasLayer.new()
	layer.layer = 40
	add_child(layer)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.65)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	layer.add_child(dim)
	var root := Control.new()
	root.theme = theme
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(root)
	var pc := PanelContainer.new()
	root.add_child(pc)
	var vb := VBoxContainer.new()
	pc.add_child(vb)
	vb.add_child(label("Settings", Color(0.96, 0.8, 0.42)))
	vb.add_child(label("Language", Color(0.6, 0.56, 0.5)))
	var row := HBoxContainer.new()
	vb.add_child(row)
	for pair in [["en", "English"], ["zh", "中文"]]:
		var code: String = pair[0]
		var b := Button.new()
		b.text = ("> " if lang == code else "   ") + str(pair[1])
		b.focus_mode = Control.FOCUS_NONE
		b.pressed.connect(_settings_pick.bind(code, layer, on_close))
		row.add_child(b)
	vb.add_child(button("Back", _settings_back.bind(layer, on_close)))
	pc.custom_minimum_size = Vector2(150, 0)
	var center := func():
		if is_instance_valid(pc):
			pc.position = ((Vector2(480, 270) - pc.size) / 2.0).round()
	center.call_deferred()
	enable_keys.call_deferred(pc)


func _settings_pick(code: String, layer: Node, on_close: Callable) -> void:
	sfx("click", -6.0)
	settings_open = false
	layer.queue_free()
	set_lang(code)
	open_settings(on_close)


func _settings_back(layer: Node, on_close: Callable) -> void:
	settings_open = false
	layer.queue_free()
	if on_close.is_valid():
		on_close.call()
