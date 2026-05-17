from io import BytesIO

CARD_ID = "tiny_traffic"
CARD_NAME = "Tiny Traffic"
CARD_DETAIL = "Cars and signal lights"
CARD_OPTIONS = [
    {"key": "speed", "label": "Speed", "type": "text", "default": "normal", "maxlength": 8},
]


def _duration(value):
    speed = str(value or "normal").strip().lower()
    if speed == "fast":
        return 75
    if speed == "slow":
        return 165
    return 110


def _car(draw, x, y, color):
    draw.rectangle((x, y + 2, x + 10, y + 5), fill=color)
    draw.rectangle((x + 2, y, x + 7, y + 2), fill=color)
    draw.point((x + 2, y + 6), fill=(20, 20, 20))
    draw.point((x + 8, y + 6), fill=(20, 20, 20))


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    frames = []
    dwell_ms = max(3000, min(60000, int(opts.get("_dwell", 10) or 10) * 1000))
    base_duration = _duration(opts.get("speed"))
    frame_count = max(24, min(72, int(round(dwell_ms / base_duration))))
    frame_duration = max(45, int(round(dwell_ms / frame_count)))
    for frame in range(frame_count):
        t = frame / frame_count
        image = Image.new("RGB", (width, 32), (3, 7, 10))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 10, width - 1, 23), fill=(18, 20, 23))
        draw.line((0, 16, width - 1, 16), fill=(190, 170, 80))
        for x in range(0, width, 10):
            draw.line((x, 16, x + 4, 16), fill=(245, 220, 100))
        light = ["red", "red", "green", "green", "yellow", "green"][frame // 4 % 6]
        lx = width - 12
        draw.rectangle((lx, 1, lx + 7, 9), fill=(30, 30, 35))
        draw.ellipse((lx + 2, 2, lx + 4, 4), fill=(255, 45, 35) if light == "red" else (60, 20, 20))
        draw.ellipse((lx + 2, 5, lx + 4, 7), fill=(255, 220, 60) if light == "yellow" else (50, 40, 20))
        draw.ellipse((lx + 2, 8, lx + 4, 10), fill=(80, 255, 90) if light == "green" else (20, 50, 20))
        lane = width + 24
        _car(draw, -12 + int(t * lane), 11, (80, 170, 255))
        _car(draw, width + 8 - int(((t + 0.45) % 1.0) * lane), 18, (255, 95, 80))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=frame_duration, loop=1, lossless=True, quality=100)
    return out.getvalue()
