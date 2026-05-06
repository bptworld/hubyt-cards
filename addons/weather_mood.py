from io import BytesIO
from card_utils import weather_for_zip

CARD_ID = "weather_mood"
CARD_NAME = "Weather Mood"
CARD_DETAIL = "Animated weather vibe"
CARD_OPTIONS = [
    {"key": "zipCode", "label": "ZIP", "type": "text", "default": "02134", "maxlength": 5, "inputmode": "numeric"},
]


def _kind(zip_code):
    try:
        weather = weather_for_zip(zip_code)
        text = str(weather.get("icon", "") + " " + weather.get("shortForecast", "")).lower()
    except Exception:
        text = "sun"
    if any(x in text for x in ("snow", "sleet", "ice")):
        return "snow"
    if any(x in text for x in ("rain", "storm", "shower", "drizzle")):
        return "rain"
    if "cloud" in text or "fog" in text:
        return "cloud"
    return "sun"


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    kind = _kind((opts.get("zipCode") or "").strip())
    frames = []
    for frame in range(16):
        bg = (0, 8, 22) if kind in ("rain", "snow") else (2, 18, 42)
        image = Image.new("RGB", (64, 32), bg)
        draw = ImageDraw.Draw(image)
        if kind == "sun":
            cx, cy = 46, 12
            draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(255, 215, 45))
            for i in range(8):
                x = cx + int((10 + frame % 3) * [1,0,-1,0,1,-1,1,-1][i])
                y = cy + int((10 + frame % 3) * [0,1,0,-1,1,1,-1,-1][i])
                draw.point((x, y), fill=(255, 240, 120))
        elif kind == "cloud":
            for cx in (18, 42):
                draw.ellipse((cx - 10, 10, cx, 20), fill=(120, 145, 165))
                draw.ellipse((cx - 3, 7, cx + 10, 20), fill=(155, 175, 195))
                draw.rectangle((cx - 9, 14, cx + 11, 21), fill=(155, 175, 195))
        elif kind == "rain":
            draw.ellipse((16, 5, 31, 18), fill=(110, 130, 150))
            draw.ellipse((26, 3, 48, 18), fill=(135, 155, 175))
            draw.rectangle((16, 12, 50, 19), fill=(135, 155, 175))
            for x in range(4, 64, 7):
                y = (frame * 3 + x) % 32
                draw.line((x, y, x - 2, y + 4), fill=(80, 170, 255))
        else:
            draw.ellipse((16, 5, 31, 18), fill=(150, 165, 180))
            draw.ellipse((26, 3, 48, 18), fill=(185, 200, 215))
            draw.rectangle((16, 12, 50, 19), fill=(185, 200, 215))
            for x in range(3, 64, 6):
                y = (frame * 2 + x) % 32
                draw.point((x, y), fill=(230, 245, 255))
                draw.point((x + 1, y), fill=(230, 245, 255))
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=110, loop=0, lossless=True, quality=100)
    return out.getvalue()
