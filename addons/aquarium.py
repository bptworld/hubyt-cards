from io import BytesIO

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
    frames = []
    for frame in range(24):
        image = Image.new("RGB", (64, 32), (0, 15, 35))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 26, 63, 31), fill=(30, 40, 20))
        for x in range(2, 64, 9):
            draw.line((x, 30, x + 2, 25), fill=(40, 130, 80))
        for i in range(5):
            bx = 8 + i * 11
            by = 25 - ((frame * 2 + i * 6) % 28)
            if by > 1:
                draw.ellipse((bx, by, bx + 2, by + 2), outline=(130, 210, 255))
        _fish(draw, (frame * 3) % 78 - 8, 11, (255, 170, 55))
        _fish(draw, 70 - ((frame * 2) % 82), 20, (80, 220, 255), left=True)
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=_duration(opts.get("speed")), loop=0, lossless=True, quality=100)
    return out.getvalue()
