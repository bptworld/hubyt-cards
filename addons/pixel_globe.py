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
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    frames = []
    land = [(-.7, -.2), (-.4, .25), (.15, -.35), (.45, .1), (.75, -.18)]
    dwell_ms = max(3000, min(60000, int(opts.get("_dwell", 10) or 10) * 1000))
    base_duration = _duration(opts.get("speed"))
    frame_count = max(24, min(72, int(round(dwell_ms / base_duration))))
    frame_duration = max(45, int(round(dwell_ms / frame_count)))
    for frame in range(frame_count):
        image = Image.new("RGB", (width, 32), (0, 0, 10))
        draw = ImageDraw.Draw(image)
        for x, y in [(6, 5), (12, 24), (width - 14, 4), (width - 6, 17), (width - 22, 27)]:
            draw.point((x, y), fill=(120, 150, 210))
        cx, cy, r = width // 2, 16, 12
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(35, 105, 220), outline=(100, 190, 255))
        rot = frame / frame_count * math.tau
        for lon, lat in land:
            x = int(cx + math.sin(lon * math.pi + rot) * r * math.cos(lat))
            y = int(cy + lat * r)
            if cx - r < x < cx + r:
                draw.ellipse((x - 2, y - 2, x + 3, y + 2), fill=(70, 210, 110))
        draw.arc((cx - r, cy - r, cx + r, cy + r), 270, 90, fill=(0, 20, 50))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=frame_duration, loop=1, lossless=True, quality=100)
    return out.getvalue()
