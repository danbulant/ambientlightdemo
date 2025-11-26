extends Marker3D
class_name Lights

@export var light_count: int = 1
@export var light_radius: float = 5.0
@export var light_template: PackedScene
@export var pattern_repetition: int = 5

@export var light_color: Color = Color.WHITE
@export var light_intensity: float = 1.0
@export var expected_rotation_delta: float = 0.

func _ready() -> void:
	for i in light_count:
		var angle = (TAU / light_count) * i
		var x = light_radius * cos(angle)
		var z = light_radius * sin(angle)
		var light_instance = light_template.instantiate()
		light_instance.position = Vector3(x, 0, z)
		add_child(light_instance)

const BASE_DELTA: float = 16

var virtual_rotation: float = 0.0

const FULL_DARK_ROTATION_DELTA := .1

func _process(delta: float) -> void:
	var frames_elapsed = delta / BASE_DELTA
	virtual_rotation += expected_rotation_delta
	var max_darkness = expected_rotation_delta / FULL_DARK_ROTATION_DELTA
	var i := 0
	for light in get_children():
		if light is SpotLight3D:
			var pattern_offset := ((i + int(virtual_rotation * pattern_repetition)) % pattern_repetition) / float(pattern_repetition)
			light.light_color = light_color
			light.light_energy = 1 - (1 - pattern_offset) * max_darkness
		i += 1
	expected_rotation_delta = lerp(expected_rotation_delta, 0.0, frames_elapsed * 5)