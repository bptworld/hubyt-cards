from io import BytesIO
from datetime import date

CARD_ID = "countdown_confetti"
CARD_NAME = "Countdown Confetti"
CARD_DETAIL = "Event countdown with confetti"
CARD_OPTIONS = [
    {"key": "eventName", "label": "Event", "type": "text", "default": "PARTY", "maxlength": 10},
    {"key": "targetDate", "label": "Date", "type": "date", "default": ""},
]


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    event = (opts.get("eventName") or "PARTY").upper()[:10]
    target = opts.get("targetDate") or ""
    try:
        days = (date.fromisoformat(target) - date.today()).days
    except Exception:
        days = None

    frames = []
    try:
        font = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
        big = ImageFont.truetype("Silkscreen-Bold.ttf", 16)
    except Exception:
        font = big = ImageFont.load_default()

    for frame in range(14):
        image = Image.new("RGB", (64, 32), (4, 3, 16))
        draw = ImageDraw.Draw(image)
        for i in range(18):
            x = (i * 11 + frame * 3) % 64
            y = (i * 7 + frame * 2) % 32
            color = [(255,80,120), (80,220,255), (255,220,60), (120,255,120)][i % 4]
            draw.point((x, y), fill=color)
        label = "SET DATE" if days is None else ("TODAY!" if days == 0 else f"{max(0, days)}D")
        ew = draw.textbbox((0, 0), event, font=font)[2]
        lw = draw.textbbox((0, 0), label, font=big if days is not None else font)[2]
        draw.text(((64 - ew) // 2, -3), event, fill=(255, 230, 120), font=font)
        draw.text(((64 - lw) // 2, 9), label, fill=(255, 255, 255), font=big if days is not None else font)
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=120, loop=0, lossless=True, quality=100)
    return out.getvalue()
