import socket
import time
import board
import neopixel
import json

num_pixels = 30
local_pixels = neopixel.NeoPixel(
    board.D18, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB
)
networked_pixels = neopixel.NeoPixel(
    board.D21, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB
)

colors = ["d062ff", "00b097", "50cc00", "8dcaff", "d062ff"]
colors_rgb = [tuple(int(colors[i][j:j+2], 16) for j in (0, 2, 4)) for i in range(len(colors))]
color_offsets = [0, .25, .5, .75, 1]

UDP_HOST = "steamdeck"
UDP_PORT_LOCAL = 4444
UDP_PORT_NETWORKED = 4433

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", UDP_PORT_LOCAL))
sock.setblocking(0)

FULL_DARK_ROTATION_DELTA = .1
PATTERN_REPETITION = 5
LIGHT_SLOWDOWN_SPEED = 1

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))
def wrap(value, min_value, max_value):
    range_size = max_value - min_value
    while value < min_value:
        value += range_size
    while value >= max_value:
        value -= range_size
    return value
def lerp(a, b, t):
    return a + (b - a) * t
def pingpong(value, max):
    value = wrap(value, 0, max * 2)
    if value > max:
        value = max * 2 - value
    return value
def sample_color_gradient(t):
    t = wrap(t, 0, 1)
    for i in range(len(color_offsets) - 1):
        if t >= color_offsets[i] and t <= color_offsets[i + 1]:
            local_t = (t - color_offsets[i]) / (color_offsets[i + 1] - color_offsets[i])
            color_a = colors_rgb[i]
            color_b = colors_rgb[i + 1]
            return tuple(int(lerp(color_a[j], color_b[j], local_t)) for j in range(3))
    return colors_rgb[-1]
def send_data(value, delta):
    message = json.dumps({"value": value, "delta": delta}).encode('utf-8')
    sock.sendto(message, (UDP_HOST, UDP_PORT_NETWORKED))
def shortest_diff(old, new):
    diff = old - new
    wrapped_diff = (new + 1) - old
    if abs(wrapped_diff) < abs(diff):
        diff = -wrapped_diff
    wrapped_diff = (old + 1) - new
    if abs(wrapped_diff) < abs(diff):
        diff = wrapped_diff
    return diff

class Lights:
    virtual_rotation = 0
    color = (255, 255, 255)
    expected_rotation_delta = 0
    def __init__(self, pixels):
        self.pixels = pixels

    def process(self, delta):
        self.virtual_rotation += self.expected_rotation_delta * (delta * 60)
        max_darkness = clamp(abs(self.expected_rotation_delta / FULL_DARK_ROTATION_DELTA), 0, 1)
        for i in range(num_pixels):
            pattern_offset = wrap((i + (self.virtual_rotation * PATTERN_REPETITION)) / PATTERN_REPETITION, 0, 1)
            energy = (1 - (1 - pattern_offset) * max_darkness)
            new_color = tuple(x * energy for x in self.color)
            self.pixels[i] = new_color
        self.pixels.show()
        self.expected_rotation_delta = lerp(self.expected_rotation_delta, 0, delta * LIGHT_SLOWDOWN_SPEED)

local_lights = Lights(local_pixels)
networked_lights = Lights(networked_pixels)

last_time = time.time()
while True:
    current_time = time.time()
    delta = current_time - last_time
    last_time = current_time

    try:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode('utf-8'))
        value = message.get("value", 0)
        delta_value = message.get("delta", 0)

        if value:
            networked_lights.color = sample_color_gradient(value)
        if delta_value:
            networked_lights.expected_rotation_delta = delta_value
    except BlockingIOError:
        pass

    # todo: get input from local sensors

    local_lights.process(delta)
    networked_lights.process(delta)

    time.sleep(0.03)