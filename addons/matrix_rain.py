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
    frames = []
    columns = list(range(1, 64, 5))
    drops = [(i * 9) % 32 for i in range(len(columns))]

    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
    except Exception:
        font = ImageFont.load_default()

    glyphs = "101001110101"
    for frame in range(16):
        image = Image.new("RGB", (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for index, x in enumerate(columns):
            head = (drops[index] + frame * 3) % 40 - 6
            for trail in range(5):
                y = head - trail * 6
                if -8 <= y <= 32:
                    brightness = max(35, 255 - trail * 45)
                    color = (120, 255, 150) if trail == 0 else (0, brightness, 60)
                    draw.text((x, y), glyphs[(frame + index + trail) % len(glyphs)], fill=color, font=font)
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=_duration(opts.get("speed")), loop=0, lossless=True, quality=100)
    return out.getvalue()
