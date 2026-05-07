from io import BytesIO
from card_utils import draw_sharp_text, fetch_json_request, render_text_webp

CARD_ID = "weather_alert"
CARD_NAME = "Weather Alert"
CARD_DETAIL = "Skips when clear"
CARD_OPTIONS = [
    {"key": "zipCode", "label": "ZIP Code", "type": "text", "default": "10001", "maxlength": 5, "inputmode": "numeric"},
]


def _zip_latlon(zip_code):
    loc = fetch_json_request(f"https://api.zippopotam.us/us/{zip_code}", seconds=86400)
    p = loc["places"][0]
    return float(p["latitude"]), float(p["longitude"])


def _severity_color(severity):
    sev = (severity or "").lower()
    if sev == "extreme":
        return (255, 60, 90)
    if sev == "severe":
        return (255, 95, 70)
    if sev == "moderate":
        return (255, 190, 70)
    return (255, 230, 90)


def _short_event(event):
    text = (event or "Weather Alert").upper()
    for word in ("WARNING", "WATCH", "ADVISORY", "STATEMENT"):
        text = text.replace(word, word[:4])
    return " ".join(text.split())[:14]


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    zip_code = (opts.get("zipCode") or "").strip()
    if len(zip_code) != 5:
        return render_text_webp("SET ZIP", (100, 180, 255))

    try:
        lat, lon = _zip_latlon(zip_code)
        data = fetch_json_request(f"https://api.weather.gov/alerts/active?point={lat:.4f},{lon:.4f}", seconds=120)
    except Exception:
        return render_text_webp("ALERT ERR", (238, 80, 80))

    alerts = data.get("features") or []
    if not alerts:
        return None

    props = alerts[0].get("properties", {})
    event = _short_event(props.get("event"))
    severity = props.get("severity", "")
    color = _severity_color(severity)

    image = Image.new("RGB", (64, 32), (18, 6, 0))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(45, 14, 0))
    draw_sharp_text(image, (1, -3), "WX ALERT", color, bold)
    draw.ellipse((48, 10, 58, 20), outline=color)
    draw.arc((41, 3, 65, 27), 205, 335, fill=(80, 110, 130))
    draw.arc((37, -1, 69, 31), 205, 335, fill=(45, 70, 90))
    draw.polygon([(53, 7), (47, 20), (54, 17), (49, 28), (61, 13), (54, 15)], fill=(255, 230, 80))
    draw_sharp_text(image, (1, 10), event, (245, 245, 245), font)
    sev = (severity or "Alert").upper()[:8]
    draw_sharp_text(image, (1, 21), sev, color, font)
    if len(alerts) > 1:
        draw_sharp_text(image, (49, 21), f"+{len(alerts)-1}", (210, 220, 225), font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
