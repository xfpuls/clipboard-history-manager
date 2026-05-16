"""Generate a clean clipboard icon for the app tray."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math


def create_clipboard_icon(size=256):
    """Create a modern clipboard icon with subtle shading."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale helper
    s = size / 256.0

    # --- Clipboard body (rounded rectangle) ---
    body_color = (91, 155, 213)  # #5B9BD5
    body_dark = (74, 138, 196)

    # Shadow
    shadow_margin = int(16 * s)
    shadow_rect = [
        shadow_margin,
        int(30 * s) + shadow_margin,
        size - shadow_margin,
        size - int(8 * s),
    ]
    temp = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(temp)
    r = int(16 * s)
    shadow_draw.rounded_rectangle(shadow_rect, r, fill=(0, 0, 0, 35))
    temp = temp.filter(ImageFilter.GaussianBlur(radius=8 * s))
    img = Image.alpha_composite(img, temp)

    # Main body
    body_rect = [
        int(8 * s),
        int(28 * s),
        size - int(8 * s),
        size - int(12 * s),
    ]
    draw = ImageDraw.Draw(img)
    r_body = int(14 * s)
    draw.rounded_rectangle(body_rect, r_body, fill=body_color)

    # Slight gradient highlight on left side
    highlight_rect = [
        int(12 * s),
        int(32 * s),
        int(60 * s),
        size - int(16 * s),
    ]
    draw.rounded_rectangle(highlight_rect, int(10 * s), fill=(110, 175, 225, 120))

    # --- Top clip ---
    clip_color = (64, 128, 186)
    clip_rect = [
        int(80 * s),
        int(8 * s),
        int(176 * s),
        int(36 * s),
    ]
    draw.rounded_rectangle(clip_rect, int(8 * s), fill=clip_color)

    # Clip inner
    clip_inner_rect = [
        int(100 * s),
        int(14 * s),
        int(156 * s),
        int(30 * s),
    ]
    draw.rounded_rectangle(clip_inner_rect, int(4 * s), fill=(74, 138, 196))

    # --- Paper lines ---
    line_color = (255, 255, 255, 200)
    line_x = int(32 * s)
    line_w = size - int(64 * s)
    line_h = max(int(6 * s), 2)

    # Line 1
    y1 = int(56 * s)
    draw.rounded_rectangle([line_x, y1, line_x + int(line_w * 0.85), y1 + line_h],
                           int(line_h // 2), fill=line_color)

    # Line 2
    y2 = int(76 * s)
    draw.rounded_rectangle([line_x, y2, line_x + int(line_w * 0.65), y2 + line_h],
                           int(line_h // 2), fill=line_color)

    # Line 3
    y3 = int(96 * s)
    draw.rounded_rectangle([line_x, y3, line_x + int(line_w * 0.75), y3 + line_h],
                           int(line_h // 2), fill=line_color)

    # Line 4
    y4 = int(116 * s)
    draw.rounded_rectangle([line_x, y4, line_x + int(line_w * 0.5), y4 + line_h],
                           int(line_h // 2), fill=line_color)

    # Line 5 - shorter
    y5 = int(136 * s)
    draw.rounded_rectangle([line_x, y5, line_x + int(line_w * 0.7), y5 + line_h],
                           int(line_h // 2), fill=line_color)

    # --- Small checkmark detail (bottom right area) ---
    check_color = (255, 255, 255, 140)
    check_x = size - int(60 * s)
    check_y = size - int(60 * s)
    pts = [
        (check_x, check_y + int(14 * s)),
        (check_x + int(8 * s), check_y + int(22 * s)),
        (check_x + int(24 * s), check_y),
    ]
    draw.line(pts, fill=check_color, width=max(int(4 * s), 2), joint='curve')

    return img


# Generate sizes for ICO
sizes = [16, 24, 32, 48, 64, 128, 256]
images = []

for size in sizes:
    icon = create_clipboard_icon(size)
    images.append(icon)

# Save as PNG
png_path = 'd:/lishiwenjian/lishijiil/clipboard_icon.png'
images[-1].save(png_path, 'PNG')
print(f'PNG saved: {png_path}')

# Save as ICO
ico_path = 'd:/lishiwenjian/lishijiil/clipboard_icon.ico'
images[0].save(ico_path, format='ICO', sizes=[(s, s) for s in sizes], append_images=images[1:])
print(f'ICO saved: {ico_path}')
