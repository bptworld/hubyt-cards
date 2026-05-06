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
    tall = str(opts.get("height", "normal")).lower() == "tall"
    frames = []
    colors = [(255, 45, 15), (255, 115, 25), (255, 195, 45), (120, 30, 10)]
    for frame in range(18):
        image = Image.new("RGB", (64, 32), (2, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 27, 63, 31), fill=(45, 20, 10))
        draw.rectangle((7, 25, 57, 27), fill=(85, 40, 18))
        for x in range(8, 57, 4):
            h = 6 + ((x * 3 + frame * 5) % (13 if tall else 9))
            base = 26
            color = colors[(x + frame) % 3]
            draw.polygon([(x, base), (x + 2, base - h), (x + 4, base)], fill=color)
            if h > 9:
                draw.polygon([(x + 1, base - 2), (x + 2, base - h + 4), (x + 3, base - 2)], fill=(255, 230, 80))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=85, loop=0, lossless=True, quality=100)
    return out.getvalue()
