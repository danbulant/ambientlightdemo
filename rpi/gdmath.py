colors = ["d062ff", "00b097", "50cc00", "8dcaff", "d062ff"]
colors_rgb = [tuple(int(colors[i][j:j+2], 16) for j in (0, 2, 4)) for i in range(len(colors))]
color_offsets = [0, .25, .5, .75, 1]

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