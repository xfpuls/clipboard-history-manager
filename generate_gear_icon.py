"""Generate a small gear/cog icon for the settings button."""
from PIL import Image, ImageDraw
import math


def create_gear_icon(size=32, color=(91, 155, 213)):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2, size / 2
    outer_r = size * 0.44
    inner_r = size * 0.24
    teeth = 8
    tooth_depth = size * 0.08

    points = []
    for i in range(teeth * 2):
        angle = (math.pi * i / teeth) - math.pi / 2
        if i % 2 == 0:
            r = outer_r + tooth_depth
        else:
            r = outer_r - tooth_depth * 0.4
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))

    if len(points) >= 3:
        draw.polygon(points, fill=color)

    # Inner circle (cutout)
    draw.ellipse(
        [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
        fill=(235, 243, 250)  # background color
    )

    # Center dot
    dot_r = size * 0.08
    draw.ellipse(
        [cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
        fill=color
    )

    return img


# Generate sizes
for size in [20, 24, 32, 48]:
    img = create_gear_icon(size)
    img.save(f'd:/lishiwenjian/lishijiil/gear_icon_{size}.png')
    print(f'Gear {size}x{size} saved')

# Also generate a hover version (slightly darker)
img_hover = create_gear_icon(32, color=(74, 138, 196))
img_hover.save('d:/lishiwenjian/lishijiil/gear_icon_hover.png')
print('Done - all gear icons generated')
