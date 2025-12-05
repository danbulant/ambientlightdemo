import board
import neopixel

pixels = neopixel.NeoPixel(
    board.D12, 25, brightness=1, auto_write=False, pixel_order=neopixel.GRB
)

pixels.fill((255, 255, 255))
pixels.show()
