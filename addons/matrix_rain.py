from io import BytesIO

CARD_ID = "matrix_rain"
CARD_NAME = "Matrix Rain"
CARD_DETAIL = "Falling green code"
CARD_OPTIONS = [
    {"key": "speed", "label": "Speed", "type": "text", "default": "normal", "maxlength": 8},
]


def _duration(value):
    speed = str(value or "normal").strip().lower()
    if speed == "fast":
        return 70
    if speed == "slow":
        return 150
    return 100


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    frames = []
    columns = list(range(1, width, 5))
    drops = [(i * 9) % 32 for i in range(len(columns))]

    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
    except Exception:
        font = ImageFont.load_default()

    glyphs = "101001110101"
    dwell_ms = max(3000, min(60000, int(opts.get("_dwell", 10) or 10) * 1000))
    base_duration = _duration(opts.get("speed"))
    frame_count = max(24, min(72, int(round(dwell_ms / base_duration))))
    frame_duration = max(45, int(round(dwell_ms / frame_count)))
    for frame in range(frame_count):
        image = Image.new("RGB", (width, 32), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for index, x in enumerate(columns):
            head = (drops[index] + frame) % 40 - 6
            for trail in range(5):
                y = head - trail * 6
                if -8 <= y <= 32:
                    brightness = max(35, 255 - trail * 45)
                    color = (120, 255, 150) if trail == 0 else (0, brightness, 60)
                    draw.text((x, y), glyphs[(frame + index + trail) % len(glyphs)], fill=color, font=font)
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=frame_duration, loop=1, lossless=True, quality=100)
    return out.getvalue()
