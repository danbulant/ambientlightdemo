extends Node3D

@onready var lights: Lights = %Lights
@onready var slider: HSlider = %HSlider
@onready var plane: MeshInstance3D = %Plane

@export var light_rotation: float = 0.0
@export var color_gradient: Gradient

func _ready():
	slider.value_changed.connect(set_light_rotation)

var error_correction := 0.

func set_light_rotation(value: float) -> void:
	value = wrapf(value, 0, 1)

	# get shortest diff including wrapping
	var diff = light_rotation - value
	var wrapped_diff = (value + 1) - light_rotation
	if abs(wrapped_diff) < abs(diff):
		diff = -wrapped_diff
	wrapped_diff = (light_rotation + 1) - value
	if abs(wrapped_diff) < abs(diff):
		diff = wrapped_diff

	# ignore small movements until a bigger one occurs or until they accumulate enough, to avoid reseting the light movement
	# diff += error_correction
	# if diff < .05:
	# 	error_correction = diff
	# 	return

	lights.expected_rotation_delta = diff
	light_rotation = value
	lights.light_color = color_gradient.sample(value)
	slider.value = value
