from io import BytesIO
from datetime import date

CARD_ID = "fortune_cookie"
CARD_NAME = "Fortune Cookie"
CARD_DETAIL = "Tiny daily fortune"
CARD_OPTIONS = [
    {"key": "mode", "label": "Mode", "type": "text", "default": "fortune", "maxlength": 8},
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
    mode = str(opts.get("mode") or "fortune").lower()
    idx = date.today().toordinal() % len(FORTUNES)
    msg = FORTUNES[idx] if mode != "random" else FORTUNES[(idx * 7 + 3) % len(FORTUNES)]

    image = Image.new("RGB", (64, 32), (8, 3, 0))
    draw = ImageDraw.Draw(image)
    draw.polygon([(4, 20), (20, 9), (35, 20), (20, 27)], fill=(230, 170, 80))
    draw.polygon([(28, 20), (43, 9), (60, 20), (43, 27)], fill=(250, 195, 100))
    draw.rectangle((18, 13, 47, 18), fill=(245, 238, 210))

    try:
        font = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = ImageFont.load_default()
    w = draw.textbbox((0, 0), msg[:10], font=font)[2]
    draw.text(((64 - w) // 2, -3), msg[:10], fill=(120, 230, 255), font=font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
