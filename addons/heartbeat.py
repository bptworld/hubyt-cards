from io import BytesIO

CARD_ID = "heartbeat"
CARD_NAME = "8-Bit Heartbeat"
CARD_DETAIL = "Pulsing pixel heart"
CARD_OPTIONS = [
    {"key": "color", "label": "Color", "type": "text", "default": "red", "maxlength": 8},
]


def _color(value):
    v = str(value or "red").lower()
    if v == "blue":
        return (60, 170, 255)
    if v == "pink":
        return (255, 90, 190)
    if v == "green":
        return (80, 240, 120)
    return (255, 45, 75)


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    color = _color(opts.get("color"))
    frames = []
    sizes = [7, 8, 10, 8, 7, 7, 9, 7]
    for frame, size in enumerate(sizes):
        image = Image.new("RGB", (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        cx, cy = 32, 16
        s = size
        draw.ellipse((cx - s, cy - s, cx, cy), fill=color)
        draw.ellipse((cx, cy - s, cx + s, cy), fill=color)
        draw.polygon([(cx - s, cy - 2), (cx + s, cy - 2), (cx, cy + s + 6)], fill=color)
        if frame in (2, 6):
            draw.line((4, 17, 14, 17, 18, 11, 24, 23, 29, 17), fill=(80, 220, 255))
            draw.line((39, 17, 45, 17, 49, 11, 55, 23, 60, 17), fill=(80, 220, 255))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=120, loop=0, lossless=True, quality=100)
    return out.getvalue()
