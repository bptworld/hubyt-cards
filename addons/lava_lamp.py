from io import BytesIO
import math

CARD_ID = "lava_lamp"
CARD_NAME = "Lava Lamp"
CARD_DETAIL = "Drifting pixel blobs"
CARD_OPTIONS = [
    {"key": "palette", "label": "Palette", "type": "text", "default": "neon", "maxlength": 8},
]


def _colors(name):
    if str(name or "").lower() == "warm":
        return [(255, 70, 35), (255, 160, 45), (255, 60, 120)]
    if str(name or "").lower() == "cool":
        return [(40, 190, 255), (70, 255, 190), (120, 90, 255)]
    return [(255, 70, 190), (40, 220, 255), (120, 255, 90)]


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    colors = _colors(opts.get("palette"))
    frames = []
    for frame in range(20):
        image = Image.new("RGB", (64, 32), (1, 0, 10))
        draw = ImageDraw.Draw(image)
        for i, color in enumerate(colors):
            cx = 10 + i * 20 + int(math.sin(frame * .45 + i) * 7)
            cy = 15 + int(math.cos(frame * .35 + i * 1.7) * 8)
            rx = 6 + (i % 2) * 2
            ry = 5 + ((i + 1) % 2) * 2
            draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=color)
            draw.ellipse((cx - rx + 2, cy - ry + 1, cx + rx - 3, cy + ry - 2),
                         outline=tuple(min(255, c + 35) for c in color))
        draw.rectangle((0, 0, 63, 31), outline=(18, 22, 45))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=110, loop=0, lossless=True, quality=100)
    return out.getvalue()
