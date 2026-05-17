from io import BytesIO
import math

CARD_ID = "aquarium"
CARD_NAME = "Pixel Aquarium"
CARD_DETAIL = "Fish and bubbles"
CARD_OPTIONS = [
    {"key": "speed", "label": "Speed", "type": "text", "default": "normal", "maxlength": 8},
]


def _duration(value):
    speed = str(value or "normal").strip().lower()
    if speed == "fast":
        return 80
    if speed == "slow":
        return 170
    return 115


def _fish(draw, x, y, color, left=False):
    body = (x - 4, y - 2, x + 4, y + 2)
    draw.ellipse(body, fill=color)
    if left:
        draw.polygon([(x + 4, y), (x + 8, y - 3), (x + 8, y + 3)], fill=color)
        draw.point((x - 3, y - 1), fill=(0, 0, 0))
    else:
        draw.polygon([(x - 4, y), (x - 8, y - 3), (x - 8, y + 3)], fill=color)
        draw.point((x + 3, y - 1), fill=(0, 0, 0))


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    dwell_ms = max(3000, min(60000, int(opts.get("_dwell", 10) or 10) * 1000))
    base_duration = _duration(opts.get("speed"))
    frame_count = max(24, min(72, int(round(dwell_ms / base_duration))))
    frame_duration = max(45, int(round(dwell_ms / frame_count)))
    frames = []
    for frame in range(frame_count):
        t = frame / frame_count
        image = Image.new("RGB", (width, 32), (0, 15, 35))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 26, width - 1, 31), fill=(30, 40, 20))
        for x in range(2, width, 9):
            draw.line((x, 30, x + 2, 25), fill=(40, 130, 80))
        bubbles = 10 if width == 128 else 5
        for i in range(bubbles):
            bx = 8 + i * 11
            by = 28 - (((t + i / bubbles) % 1.0) * 34)
            if by > 1:
                draw.ellipse((int(bx), int(by), int(bx + 2), int(by + 2)), outline=(130, 210, 255))
        swim = width + 28
        fish1_x = -10 + int(t * swim)
        fish2_x = width + 10 - int(((t + 0.35) % 1.0) * swim)
        _fish(draw, fish1_x, 11 + int(math.sin(t * math.tau) * 1), (255, 170, 55))
        _fish(draw, fish2_x, 20 + int(math.cos(t * math.tau) * 1), (80, 220, 255), left=True)
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=frame_duration, loop=1, lossless=True, quality=100)
    return out.getvalue()
