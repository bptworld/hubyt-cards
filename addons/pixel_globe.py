from io import BytesIO
import math

CARD_ID = "pixel_globe"
CARD_NAME = "Pixel Globe"
CARD_DETAIL = "Tiny rotating world"
CARD_OPTIONS = [
    {"key": "speed", "label": "Speed", "type": "text", "default": "normal", "maxlength": 8},
]


def _duration(value):
    speed = str(value or "normal").strip().lower()
    if speed == "fast":
        return 85
    if speed == "slow":
        return 180
    return 125


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    frames = []
    land = [(-.7, -.2), (-.4, .25), (.15, -.35), (.45, .1), (.75, -.18)]
    for frame in range(20):
        image = Image.new("RGB", (64, 32), (0, 0, 10))
        draw = ImageDraw.Draw(image)
        for x, y in [(6, 5), (12, 24), (50, 4), (58, 17), (42, 27)]:
            draw.point((x, y), fill=(120, 150, 210))
        cx, cy, r = 32, 16, 12
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(35, 105, 220), outline=(100, 190, 255))
        rot = frame / 20 * math.tau
        for lon, lat in land:
            x = int(cx + math.sin(lon * math.pi + rot) * r * math.cos(lat))
            y = int(cy + lat * r)
            if cx - r < x < cx + r:
                draw.ellipse((x - 2, y - 2, x + 3, y + 2), fill=(70, 210, 110))
        draw.arc((cx - r, cy - r, cx + r, cy + r), 270, 90, fill=(0, 20, 50))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=_duration(opts.get("speed")), loop=0, lossless=True, quality=100)
    return out.getvalue()
