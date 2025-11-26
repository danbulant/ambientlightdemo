extends Marker3D
class_name Lights

@export var light_count: int = 1
@export var light_radius: float = 5.0
@export var light_slowdown_speed: float = 1.0
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


var virtual_rotation: float = 0.0

const FULL_DARK_ROTATION_DELTA := .1

func _process(delta: float) -> void:
	virtual_rotation += expected_rotation_delta * (delta * 60)
	var max_darkness := clampf(abs(expected_rotation_delta / FULL_DARK_ROTATION_DELTA), 0, 1)
	var i := 0
	for light in get_children():
		if light is SpotLight3D:
			var pattern_offset := wrapf((i + (virtual_rotation * pattern_repetition)) / pattern_repetition, 0, 1)
			light.light_color = light_color
			light.light_energy = (1 - (1 - pattern_offset) * max_darkness) * light_intensity
			i += 1
	expected_rotation_delta = lerp(expected_rotation_delta, 0.0, delta * light_slowdown_speed)