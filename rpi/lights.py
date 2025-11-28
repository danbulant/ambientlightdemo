import board
import neopixel
from gdmath import *

pixels = neopixel.NeoPixel(
    board.D12, 10, brightness=.2, auto_write=False, pixel_order=neopixel.GRB
)

class Lights:
    virtual_rotation = 0
    color = (255, 255, 255)
    expected_rotation_delta = 0
    def __init__(self, pixels):
        self.pixels = pixels

    def process(self, delta):
        self.virtual_rotation += self.expected_rotation_delta * (delta * 60)
        max_darkness = clamp(abs(self.expected_rotation_delta / FULL_DARK_ROTATION_DELTA), 0, 1)
        for i in range(pixels.n):
            pattern_offset = wrap((i + (self.virtual_rotation * PATTERN_REPETITION)) / PATTERN_REPETITION, 0, 1)
            energy = (1 - (1 - pattern_offset) * max_darkness)
            new_color = tuple(x * energy for x in self.color)
            self.pixels[i] = new_color
        self.pixels.show()
        self.expected_rotation_delta = lerp(self.expected_rotation_delta, 0, delta * LIGHT_SLOWDOWN_SPEED)
