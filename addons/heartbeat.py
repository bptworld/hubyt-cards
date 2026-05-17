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
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    color = _color(opts.get("color"))
    frames = []
    dwell_ms = max(3000, min(60000, int(opts.get("_dwell", 10) or 10) * 1000))
    base_sizes = [7, 8, 10, 8, 7, 7, 9, 7]
    frame_count = max(16, min(72, int(round(dwell_ms / 120))))
    frame_duration = max(45, int(round(dwell_ms / frame_count)))
    sizes = [base_sizes[i % len(base_sizes)] for i in range(frame_count)]
    for frame, size in enumerate(sizes):
        image = Image.new("RGB", (width, 32), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        cx, cy = width // 2, 16
        s = size
        draw.ellipse((cx - s, cy - s, cx, cy), fill=color)
        draw.ellipse((cx, cy - s, cx + s, cy), fill=color)
        draw.polygon([(cx - s, cy - 2), (cx + s, cy - 2), (cx, cy + s + 6)], fill=color)
        if frame in (2, 6):
            draw.line((4, 17, cx - 18, 17, cx - 14, 11, cx - 8, 23, cx - 3, 17), fill=(80, 220, 255))
            draw.line((cx + 7, 17, cx + 13, 17, cx + 17, 11, width - 9, 23, width - 4, 17), fill=(80, 220, 255))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=frame_duration, loop=1, lossless=True, quality=100)
    return out.getvalue()
