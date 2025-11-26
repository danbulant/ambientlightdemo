extends Node3D

@onready var lights: Lights = %Lights
@onready var slider: HSlider = %HSlider
@onready var networked_lights: Lights = %NetworkedLights

@export var light_rotation: float = 0.0
@export var color_gradient: Gradient

var peer: PacketPeerUDP

func _ready():
	slider.value_changed.connect(set_local_light_rotation)
	peer = PacketPeerUDP.new()
	peer.bind(4433)
	peer.set_dest_address("rpi", 4444)
	

func send_data(data: Dictionary) -> void:
	var json_data := JSON.stringify(data)
	var byte_array := json_data.to_utf8_buffer()
	peer.put_packet(byte_array)

var error_correction := 0.

func set_local_light_rotation(value: float) -> void:
	value = wrapf(value, 0, 1)
	var polarized_value := pingpong(value * 4, 1)
	lights.light_intensity = 1.0 - polarized_value
	lights.light_color = color_gradient.sample(value)
	slider.value = value

	# get shortest diff including wrapping
	var diff = light_rotation - value
	var wrapped_diff = (value + 1) - light_rotation
	if abs(wrapped_diff) < abs(diff):
		diff = -wrapped_diff
	wrapped_diff = (light_rotation + 1) - value
	if abs(wrapped_diff) < abs(diff):
		diff = wrapped_diff

	# ignore small movements until a bigger one occurs or until they accumulate enough, to avoid reseting the light movement
	diff += error_correction
	if abs(diff) < .05:
		error_correction = diff
		send_data({"value": value})
		return

	lights.expected_rotation_delta = diff
	light_rotation = value
	send_data({"value": value, "delta": diff})

func _process(_delta):
	if peer.get_available_packet_count() > 0:
		var array_bytes = peer.get_packet()
		var packet_string = array_bytes.get_string_from_ascii()
		var json = JSON.parse_string(packet_string)
		if json != null:
			var value = json.value
			var delta = json.delta
			networked_lights.expected_rotation_delta = delta
			
			var polarized_value := pingpong(value * 4, 1)
			networked_lights.light_intensity = 1.0 - polarized_value
			networked_lights.light_color = color_gradient.sample(value)