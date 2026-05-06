from io import BytesIO

CARD_ID = "snake"
CARD_NAME = "Snake"
CARD_DETAIL = "Snake eats dots"
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


def _path():
    pts = []
    for x in range(4, 58, 4):
        pts.append((x, 8))
    for y in range(12, 25, 4):
        pts.append((56, y))
    for x in range(52, 5, -4):
        pts.append((x, 24))
    for y in range(20, 9, -4):
        pts.append((8, y))
    return pts


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    path = _path()
    frames = []
    for frame in range(len(path)):
        image = Image.new("RGB", (64, 32), (0, 5, 0))
        draw = ImageDraw.Draw(image)
        food = path[(frame + 7) % len(path)]
        draw.rectangle((food[0] - 1, food[1] - 1, food[0] + 1, food[1] + 1), fill=(255, 80, 80))
        for i in range(9):
            x, y = path[(frame - i) % len(path)]
            col = (80, 255 - i * 16, 80)
            draw.rectangle((x - 2, y - 2, x + 2, y + 2), fill=col)
        hx, hy = path[frame]
        draw.point((hx + 1, hy - 1), fill=(0, 0, 0))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=_duration(opts.get("speed")), loop=0, lossless=True, quality=100)
    return out.getvalue()
