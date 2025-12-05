import board
import neopixel
from gdmath import *
from math import cos, pi

pixels = neopixel.NeoPixel(
    board.D12, 25, brightness=1, auto_write=False, pixel_order=neopixel.GRB
)

class Lights:
    virtual_rotation = 0
    color = (255, 255, 255)
    expected_rotation_delta_remote = 0
    expected_rotation_delta_local = 0
    rotation_remote = 0
    rotation_local = 0
    def __init__(self, pixels):
        self.pixels = pixels

    def process(self, delta):
        self.virtual_rotation += self.expected_rotation_delta_remote * (delta * 60)
        max_darkness = clamp(abs(self.expected_rotation_delta_remote / FULL_DARK_ROTATION_DELTA), 0, 1)
        light_intensity = 1 - cos(self.rotation_local * 2 * pi - self.rotation_remote * 2 * pi) ** 2
        for i in range(pixels.n):
            pattern_offset = wrap((i + (self.virtual_rotation * PATTERN_REPETITION)) / PATTERN_REPETITION, 0, 1)
            energy = (1 - (1 - pattern_offset) * max_darkness) * light_intensity
            new_color = tuple(int(x * energy) for x in self.color)
            self.pixels[i] = new_color
        self.pixels.show()
        self.expected_rotation_delta_remote = lerp(self.expected_rotation_delta_remote, 0, delta * LIGHT_SLOWDOWN_SPEED)

lights = Lights(pixels)
