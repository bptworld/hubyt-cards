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


def _path(width=64):
    pts = []
    for x in range(4, width - 6, 4):
        pts.append((x, 8))
    for y in range(12, 25, 4):
        pts.append((width - 8, y))
    for x in range(width - 12, 5, -4):
        pts.append((x, 24))
    for y in range(20, 9, -4):
        pts.append((8, y))
    return pts


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    path = _path(width)
    dwell_ms = max(3000, min(60000, int(opts.get("_dwell", 10) or 10) * 1000))
    base_duration = _duration(opts.get("speed"))
    frame_count = max(len(path), min(96, int(round(dwell_ms / base_duration))))
    frame_duration = max(45, int(round(dwell_ms / frame_count)))
    frames = []
    for frame in range(frame_count):
        image = Image.new("RGB", (width, 32), (0, 5, 0))
        draw = ImageDraw.Draw(image)
        food = path[(frame + 7) % len(path)]
        draw.rectangle((food[0] - 1, food[1] - 1, food[0] + 1, food[1] + 1), fill=(255, 80, 80))
        for i in range(9):
            x, y = path[(frame - i) % len(path)]
            col = (80, 255 - i * 16, 80)
            draw.rectangle((x - 2, y - 2, x + 2, y + 2), fill=col)
        hx, hy = path[frame % len(path)]
        draw.point((hx + 1, hy - 1), fill=(0, 0, 0))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=frame_duration, loop=1, lossless=True, quality=100)
    return out.getvalue()
