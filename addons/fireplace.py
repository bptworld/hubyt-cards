from io import BytesIO

CARD_ID = "fireplace"
CARD_NAME = "Fireplace"
CARD_DETAIL = "Pixel flames"
CARD_OPTIONS = [
    {"key": "height", "label": "Height", "type": "text", "default": "normal", "maxlength": 8},
]


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    tall = str(opts.get("height", "normal")).lower() == "tall"
    frames = []
    colors = [(255, 45, 15), (255, 115, 25), (255, 195, 45), (120, 30, 10)]
    dwell_ms = max(3000, min(60000, int(opts.get("_dwell", 10) or 10) * 1000))
    frame_count = max(24, min(72, int(round(dwell_ms / 85))))
    frame_duration = max(45, int(round(dwell_ms / frame_count)))
    for frame in range(frame_count):
        image = Image.new("RGB", (width, 32), (2, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 27, width - 1, 31), fill=(45, 20, 10))
        draw.rectangle((7, 25, width - 7, 27), fill=(85, 40, 18))
        for x in range(8, width - 7, 4):
            period = 12 if tall else 8
            h = 6 + ((x // 4 + frame) % period)
            base = 26
            color = colors[(x + frame) % 3]
            draw.polygon([(x, base), (x + 2, base - h), (x + 4, base)], fill=color)
            if h > 9:
                draw.polygon([(x + 1, base - 2), (x + 2, base - h + 4), (x + 3, base - 2)], fill=(255, 230, 80))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=frame_duration, loop=1, lossless=True, quality=100)
    return out.getvalue()
