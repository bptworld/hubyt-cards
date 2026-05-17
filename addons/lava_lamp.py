from io import BytesIO
import math

CARD_ID = "lava_lamp"
CARD_NAME = "Lava Lamp"
CARD_DETAIL = "Drifting pixel blobs"
CARD_OPTIONS = [
    {"key": "palette", "label": "Palette", "type": "text", "default": "neon", "maxlength": 8},
]


def _colors(name):
    if str(name or "").lower() == "warm":
        return [(255, 70, 35), (255, 160, 45), (255, 60, 120)]
    if str(name or "").lower() == "cool":
        return [(40, 190, 255), (70, 255, 190), (120, 90, 255)]
    return [(255, 70, 190), (40, 220, 255), (120, 255, 90)]


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    colors = _colors(opts.get("palette"))
    frames = []
    dwell_ms = max(3000, min(60000, int(opts.get("_dwell", 10) or 10) * 1000))
    frame_count = max(24, min(72, int(round(dwell_ms / 110))))
    frame_duration = max(45, int(round(dwell_ms / frame_count)))
    for frame in range(frame_count):
        t = frame / frame_count
        image = Image.new("RGB", (width, 32), (1, 0, 10))
        draw = ImageDraw.Draw(image)
        blob_count = 5 if width == 128 else 3
        for i in range(blob_count):
            color = colors[i % len(colors)]
            cx = 10 + i * ((width - 20) // max(1, blob_count - 1)) + int(math.sin(t * math.tau + i) * 7)
            cy = 15 + int(math.cos(t * math.tau + i * 1.7) * 8)
            rx = 6 + (i % 2) * 2
            ry = 5 + ((i + 1) % 2) * 2
            draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=color)
            draw.ellipse((cx - rx + 2, cy - ry + 1, cx + rx - 3, cy + ry - 2),
                         outline=tuple(min(255, c + 35) for c in color))
        draw.rectangle((0, 0, width - 1, 31), outline=(18, 22, 45))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=frame_duration, loop=1, lossless=True, quality=100)
    return out.getvalue()
