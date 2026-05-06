from io import BytesIO
from datetime import datetime, timezone
import math

CARD_ID = "moon_phase"
CARD_NAME = "Moon Phase"
CARD_DETAIL = "Current moon phase"
CARD_OPTIONS = []


def _phase():
    known_new = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    days = (datetime.now(timezone.utc) - known_new).total_seconds() / 86400.0
    age = days % 29.53058867
    return age / 29.53058867, age


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    phase, age = _phase()
    image = Image.new("RGB", (64, 32), (0, 0, 12))
    draw = ImageDraw.Draw(image)
    for x, y in [(4, 5), (14, 2), (25, 7), (51, 4), (59, 11), (42, 25), (8, 26)]:
        draw.point((x, y), fill=(120, 150, 210))

    cx, cy, r = 23, 16, 11
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(210, 218, 230))
    illum = math.cos(2 * math.pi * phase)
    shadow_w = int(abs(illum) * r)
    if phase < .5:
        draw.rectangle((cx - r, cy - r, cx, cy + r), fill=(8, 12, 30))
        draw.ellipse((cx - shadow_w, cy - r, cx + shadow_w, cy + r), fill=(210, 218, 230))
    else:
        draw.rectangle((cx, cy - r, cx + r, cy + r), fill=(8, 12, 30))
        draw.ellipse((cx - shadow_w, cy - r, cx + shadow_w, cy + r), fill=(210, 218, 230))

    label = "NEW" if age < 2 or age > 27.5 else "FULL" if 13 < age < 16 else "MOON"
    try:
        font = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = ImageFont.load_default()
    draw.text((43, 7), label, fill=(140, 190, 255), font=font)
    draw.text((43, 17), f"{int(age)}D", fill=(220, 230, 255), font=font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
