extends Node
## Scene switcher with a fade. Every screen is a script that builds itself in code.

const SCENES := {
	"title": "res://scripts/intro.gd",
	"expedition": "res://scripts/expedition.gd",
	"battle": "res://scripts/battle.gd",
	"ending": "res://scripts/ending.gd",
}

var current: Node = null
var fade: ColorRect
var busy := false


func _ready() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 50
	add_child(layer)
	fade = ColorRect.new()
	fade.color = Color(0, 0, 0, 1)
	fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(fade)
	Game.scene_requested.connect(_on_scene)
	_swap("title")


func _on_scene(scene_name: String) -> void:
	if busy:
		return
	busy = true
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 1.0, 0.4)
	tw.tween_callback(_swap.bind(scene_name))


func _swap(scene_name: String) -> void:
	if current != null:
		current.queue_free()
	var scr: GDScript = load(SCENES[scene_name])
	current = scr.new()
	add_child(current)
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 0.0, 0.6)
	busy = false
