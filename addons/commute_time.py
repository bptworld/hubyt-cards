from datetime import datetime, timedelta, timezone
from io import BytesIO
import urllib.parse
from card_utils import draw_sharp_text, fetch_json_request, render_text_webp

CARD_ID = "commute_time"
CARD_NAME = "Commute Time"
CARD_DETAIL = "Drive time estimate"
CARD_OPTIONS = [
    {"key": "origin", "label": "From", "type": "text", "default": "Home address"},
    {"key": "destination", "label": "To", "type": "text", "default": "Work address"},
    {"key": "label", "label": "Label", "type": "text", "default": "COMMUTE", "maxlength": 10},
]

_GEOCODE_CACHE = {}
_ROUTE_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "route": None}


def _coords(value):
    text = (value or "").strip()
    if "," in text:
        parts = [p.strip() for p in text.split(",", 1)]
        try:
            return float(parts[0]), float(parts[1])
        except Exception:
            pass

    now = datetime.now(timezone.utc)
    cached = _GEOCODE_CACHE.get(text.lower())
    if cached and cached["expires"] > now:
        return cached["coords"]

    query = urllib.parse.urlencode({"q": text, "format": "json", "limit": "1"})
    data = fetch_json_request(f"https://nominatim.openstreetmap.org/search?{query}", seconds=86400)
    if not data:
        raise ValueError("Address not found")
    coords = (float(data[0]["lat"]), float(data[0]["lon"]))
    _GEOCODE_CACHE[text.lower()] = {"coords": coords, "expires": now + timedelta(days=7)}
    return coords


def _route(origin, destination):
    now = datetime.now(timezone.utc)
    key = f"{origin}:{destination}"
    cached = _ROUTE_CACHE.get("route")
    if cached and cached["key"] == key and _ROUTE_CACHE["expires"] > now:
        return cached
    olat, olon = origin
    dlat, dlon = destination
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{olon:.6f},{olat:.6f};{dlon:.6f},{dlat:.6f}?overview=false&alternatives=false&steps=false"
    )
    data = fetch_json_request(url, seconds=180)
    route = data["routes"][0]
    result = {
        "key": key,
        "minutes": int(round(route["duration"] / 60.0)),
        "miles": route["distance"] / 1609.344,
    }
    _ROUTE_CACHE["route"] = result
    _ROUTE_CACHE["expires"] = now + timedelta(seconds=180)
    return result


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    origin = (opts.get("origin") or "").strip()
    destination = (opts.get("destination") or "").strip()
    label = (opts.get("label") or "COMMUTE").strip().upper()[:10]
    if not origin or not destination or "address" in origin.lower() or "address" in destination.lower():
        return render_text_webp("SET ROUTE", (100, 180, 255))

    try:
        route = _route(_coords(origin), _coords(destination))
    except Exception:
        return render_text_webp("ROUTE ERR", (238, 80, 80))

    minutes = route["minutes"]
    color = (100, 230, 140) if minutes < 30 else (255, 205, 75) if minutes < 60 else (255, 95, 80)

    image = Image.new("RGB", (64, 32), (3, 8, 11))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw_sharp_text(image, (1, -3), label, (115, 205, 255), font)
    draw.line((4, 23, 58, 23), fill=(60, 80, 88))
    for x in (8, 24, 40, 56):
        draw.rectangle((x, 21, x + 1, 24), fill=(110, 130, 135))
    draw.rectangle((9, 18, 20, 23), fill=(45, 160, 255))
    draw.rectangle((11, 16, 18, 18), fill=(85, 190, 255))
    draw.point((11, 24), fill=(230, 240, 245))
    draw.point((18, 24), fill=(230, 240, 245))
    text = f"{minutes}m"
    tw = draw.textbbox((0, 0), text, font=bold)[2]
    draw_sharp_text(image, (63 - tw, 7), text, color, bold)
    miles = f"{route['miles']:.0f}mi"
    mw = draw.textbbox((0, 0), miles, font=font)[2]
    draw_sharp_text(image, (63 - mw, 17), miles, (180, 200, 205), font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
