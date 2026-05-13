from datetime import datetime, timezone
from io import BytesIO

from card_utils import draw_sharp_text, fetch_json_request, render_text_webp

CARD_ID = "sunrise_sunset"
CARD_NAME = "Sunrise / Sunset"
CARD_DETAIL = "Sun and daylight times by ZIP"
CARD_OPTIONS = [
    {"key": "zipCode", "label": "ZIP Code", "type": "text", "default": "01826", "maxlength": 5, "inputmode": "numeric"},
    {
        "key": "mode",
        "label": "Show",
        "type": "select",
        "default": "both",
        "choices": [
            {"value": "both", "label": "Sunrise and sunset"},
            {"value": "sunrise", "label": "Sunrise only"},
            {"value": "sunset", "label": "Sunset only"},
        ],
    },
]


def _location_for_zip(zip_code):
    zip_code = "".join(ch for ch in str(zip_code or "") if ch.isdigit())[:5]
    if len(zip_code) != 5:
        raise ValueError("ZIP needed")
    data = fetch_json_request(f"https://api.zippopotam.us/us/{zip_code}", seconds=86400)
    place = data["places"][0]
    return place["latitude"], place["longitude"]


def _time_label(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()
    return dt.strftime("%I:%M").lstrip("0")


def _sun_data(zip_code):
    lat, lon = _location_for_zip(zip_code)
    data = fetch_json_request(
        f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0",
        seconds=3600,
    )
    results = data.get("results", {})
    return _time_label(results["sunrise"]), _time_label(results["sunset"])


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    try:
        sunrise, sunset = _sun_data(opts.get("zipCode", "01826"))
    except Exception:
        return render_text_webp("SUN ERR", (255, 190, 80))

    image = Image.new("RGB", (64, 32), (0, 5, 12))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.ellipse((5, 7, 19, 21), fill=(255, 196, 58))
    for line in [(12, 3, 12, 5), (12, 23, 12, 26), (1, 14, 4, 14), (20, 14, 23, 14)]:
        draw.line(line, fill=(255, 226, 110))
    draw.line((2, 25, 24, 25), fill=(60, 180, 225))

    mode = opts.get("mode", "both")
    if mode == "sunrise":
        rows = [("RISE", sunrise, (255, 210, 80))]
    elif mode == "sunset":
        rows = [("SET", sunset, (255, 125, 80))]
    else:
        rows = [("RISE", sunrise, (255, 210, 80)), ("SET", sunset, (255, 125, 80))]

    y = 5 if len(rows) == 2 else 10
    for label, value, color in rows:
        draw_sharp_text(image, (27, y), label, color, font)
        draw_sharp_text(image, (27, y + 8), value, (235, 245, 255), bold)
        y += 16

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
