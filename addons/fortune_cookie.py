from io import BytesIO
from datetime import date

CARD_ID = "fortune_cookie"
CARD_NAME = "Fortune Cookie"
CARD_DETAIL = "Tiny daily fortune"
CARD_OPTIONS = [
    {
        "key": "mode",
        "label": "Mode",
        "type": "select",
        "default": "fortune",
        "choices": [
            {"value": "fortune", "label": "Daily Fortune"},
            {"value": "random", "label": "Random Fortune"},
        ],
    },
]

FORTUNES = [
    "TRY AGAIN",
    "GOOD LUCK",
    "SAY YES",
    "MAKE IT",
    "KEEP GOING",
    "BIG IDEAS",
    "SHIP IT",
    "BE KIND",
    "STAY WEIRD",
    "LOOK UP",
]


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    mode = str(opts.get("mode") or "fortune").lower()
    idx = date.today().toordinal() % len(FORTUNES)
    msg = FORTUNES[idx] if mode != "random" else FORTUNES[(idx * 7 + 3) % len(FORTUNES)]

    image = Image.new("RGB", (width, 32), (8, 3, 0))
    draw = ImageDraw.Draw(image)
    cx = width // 2
    draw.polygon([(cx - 28, 20), (cx - 12, 9), (cx + 3, 20), (cx - 12, 27)], fill=(230, 170, 80))
    draw.polygon([(cx - 4, 20), (cx + 11, 9), (cx + 28, 20), (cx + 11, 27)], fill=(250, 195, 100))
    draw.rectangle((cx - 14, 13, cx + 15, 18), fill=(245, 238, 210))

    try:
        font = ImageFont.truetype("PixelifySans-Bold.ttf", 8)
    except Exception:
        font = ImageFont.load_default()
    max_chars = 20 if width == 128 else 10
    w = draw.textbbox((0, 0), msg[:max_chars], font=font)[2]
    draw.text(((width - w) // 2, -3), msg[:max_chars], fill=(120, 230, 255), font=font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()

