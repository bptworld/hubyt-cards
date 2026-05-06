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
    frames = []
    for frame in range(24):
        image = Image.new("RGB", (64, 32), (3, 7, 10))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 10, 63, 23), fill=(18, 20, 23))
        draw.line((0, 16, 63, 16), fill=(190, 170, 80))
        for x in range(0, 64, 10):
            draw.line((x, 16, x + 4, 16), fill=(245, 220, 100))
        light = ["red", "red", "green", "green", "yellow", "green"][frame // 4 % 6]
        draw.rectangle((52, 1, 59, 9), fill=(30, 30, 35))
        draw.ellipse((54, 2, 56, 4), fill=(255, 45, 35) if light == "red" else (60, 20, 20))
        draw.ellipse((54, 5, 56, 7), fill=(255, 220, 60) if light == "yellow" else (50, 40, 20))
        draw.ellipse((54, 8, 56, 10), fill=(80, 255, 90) if light == "green" else (20, 50, 20))
        _car(draw, (frame * 3) % 78 - 12, 11, (80, 170, 255))
        _car(draw, 70 - ((frame * 2) % 82), 18, (255, 95, 80))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=_duration(opts.get("speed")), loop=0, lossless=True, quality=100)
    return out.getvalue()
