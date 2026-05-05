from datetime import datetime
from io import BytesIO
from card_utils import draw_sharp_text, fetch_json_request, render_text_webp

CARD_ID = "weather_forecast"
CARD_NAME = "Weather Forecast"
CARD_DETAIL = "5-day forecast with icons"
CARD_OPTIONS = [
    {"key": "zipCode", "label": "ZIP Code", "type": "text", "default": "10001",
     "maxlength": 5, "inputmode": "numeric"},
]


def _zip_forecast(zip_code):
    loc = fetch_json_request(f"https://api.zippopotam.us/us/{zip_code}", seconds=86400)
    p = loc["places"][0]
    lat, lon = float(p["latitude"]), float(p["longitude"])
    pt = fetch_json_request(f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}", seconds=86400)
    fc = fetch_json_request(pt["properties"]["forecast"], seconds=3600)
    return fc["properties"]["periods"]


def _day_label(name):
    n = name.upper()
    if any(x in n for x in ("TODAY", "THIS AFTERNOON", "THIS MORNING", "THIS EVENING")):
        return ["Mo","Tu","We","Th","Fr","Sa","Su"][datetime.now().weekday()]
    for full, abbr in [("MONDAY","Mo"),("TUESDAY","Tu"),("WEDNESDAY","We"),
                       ("THURSDAY","Th"),("FRIDAY","Fr"),("SATURDAY","Sa"),("SUNDAY","Su")]:
        if full in n:
            return abbr
    return name[:2].title()


def _icon(text):
    t = (text or "").lower()
    if any(x in t for x in ("snow","sleet","ice","blizzard","wintry","flurr")):
        return "snow"
    if any(x in t for x in ("rain","shower","storm","thunder","drizzle","showers")):
        return "rain"
    if any(x in t for x in ("cloud","overcast","fog","haze","mostly cloudy","partly cloudy")):
        return "cloud"
    return "sun"


def _draw_icon(draw, icon, cx, y):
    if icon == "sun":
        draw.ellipse((cx-3, y+1, cx+3, y+7), fill=(255, 210, 50))
        for pt in [(cx, y),(cx, y+8),(cx-5, y+4),(cx+5, y+4)]:
            draw.point(pt, fill=(255, 230, 100))
    elif icon == "cloud":
        draw.ellipse((cx-5, y+2, cx-1, y+6), fill=(140, 160, 175))
        draw.ellipse((cx-2, y+1, cx+4, y+6), fill=(165, 185, 200))
        draw.rectangle((cx-4, y+4, cx+4, y+7), fill=(165, 185, 200))
    elif icon == "rain":
        draw.ellipse((cx-5, y+1, cx-1, y+5), fill=(110, 135, 155))
        draw.ellipse((cx-2, y+0, cx+4, y+5), fill=(130, 155, 175))
        draw.rectangle((cx-4, y+3, cx+4, y+5), fill=(130, 155, 175))
        for dx in (-3, 0, 3):
            draw.line((cx+dx, y+6, cx+dx-1, y+8), fill=(80, 160, 255))
    elif icon == "snow":
        draw.ellipse((cx-5, y+1, cx-1, y+5), fill=(175, 195, 215))
        draw.ellipse((cx-2, y+0, cx+4, y+5), fill=(200, 215, 230))
        draw.rectangle((cx-4, y+3, cx+4, y+5), fill=(200, 215, 230))
        for dx in (-3, 0, 3):
            draw.point((cx+dx, y+7), fill=(220, 240, 255))


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont
    opts = options or {}
    zip_code = (opts.get("zipCode") or "").strip()
    if len(zip_code) != 5:
        return render_text_webp("SET ZIP", (100, 180, 255))

    try:
        periods = _zip_forecast(zip_code)
    except Exception:
        return render_text_webp("WTHR ERR", (238, 80, 80))

    days  = [p for p in periods if p.get("isDaytime", True)][:4]
    nights = [p for p in periods if not p.get("isDaytime", True)][:4]

    if not days:
        return render_text_webp("NO DATA", (150, 150, 150))

    image = Image.new("RGB", (64, 32), (0, 5, 15))
    draw  = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    # 4 columns — dividers at x=16,32,48; centers at 8,24,40,56
    cols     = [8, 24, 40, 56]
    dividers = [16, 32, 48]

    for x in dividers:
        draw.line((x, 0, x, 31), fill=(25, 35, 50))

    for i, (cx, period) in enumerate(zip(cols, days)):
        label = _day_label(period["name"])
        icon  = _icon(period.get("shortForecast", ""))
        high  = str(period.get("temperature", "--"))
        low   = str(nights[i].get("temperature", "--")) if i < len(nights) else "--"

        label_color = (24, 182, 163) if i == 0 else (160, 190, 215)

        lw = draw.textbbox((0, 0), label, font=font)[2]
        draw_sharp_text(image, (cx - lw // 2, -3), label, label_color, font)

        _draw_icon(draw, icon, cx, 5)

        hw = draw.textbbox((0, 0), high, font=bold)[2]
        draw_sharp_text(image, (cx - hw // 2, 14), high, (255, 175, 70), bold)

        lw2 = draw.textbbox((0, 0), low, font=font)[2]
        draw_sharp_text(image, (cx - lw2 // 2, 22), low, (110, 175, 255), font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
