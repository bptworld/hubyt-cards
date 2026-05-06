from io import BytesIO

CARD_ID = "pong_loop"
CARD_NAME = "Pong Loop"
CARD_DETAIL = "Tiny paddles and ball"
CARD_OPTIONS = [
    {"key": "speed", "label": "Speed", "type": "text", "default": "normal", "maxlength": 8},
]


def _duration(value):
    speed = str(value or "normal").strip().lower()
    if speed == "fast":
        return 55
    if speed == "slow":
        return 135
    return 85


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    frames = []
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
    except Exception:
        font = ImageFont.load_default()

    path = [
        (10, 7), (16, 10), (22, 13), (28, 16), (34, 19), (40, 22), (48, 19), (54, 16),
        (48, 13), (40, 10), (34, 7), (28, 10), (22, 13), (16, 16)
    ]
    for frame, (x, y) in enumerate(path):
        image = Image.new("RGB", (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.line((31, 1, 31, 30), fill=(40, 40, 50))
        for yy in range(3, 30, 6):
            draw.point((31, yy), fill=(90, 90, 105))
        left_y = max(3, min(22, y - 4))
        right_y = max(3, min(22, 28 - y))
        draw.rectangle((3, left_y, 5, left_y + 8), fill=(220, 240, 255))
        draw.rectangle((58, right_y, 60, right_y + 8), fill=(220, 240, 255))
        draw.rectangle((x, y, x + 2, y + 2), fill=(255, 255, 255))
        draw.text((19, -4), "3", fill=(90, 200, 255), font=font)
        draw.text((41, -4), "2", fill=(255, 190, 90), font=font)
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=_duration(opts.get("speed")), loop=0, lossless=True, quality=100)
    return out.getvalue()
