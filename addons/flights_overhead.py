from datetime import datetime, timezone
import math
from card_utils import (
    fetch_json_request, fetch_opensky, lookup_airline,
    haversine_miles, compass_dir, render_flight_image, render_text_webp,
)

CARD_ID = "flights_overhead"
CARD_NAME = "Flights Overhead"
CARD_DETAIL = "Live flights above you"
CARD_OPTIONS = [
    {"key": "zipCode",        "label": "ZIP Code",       "type": "text",     "default": "10001", "maxlength": 5, "inputmode": "numeric"},
    {"key": "radiusMiles",    "label": "Radius (mi)",    "type": "number",   "default": "50"},
    {"key": "clientId",       "label": "OpenSky Client ID",     "type": "text",     "default": ""},
    {"key": "clientSecret",   "label": "OpenSky Client Secret", "type": "text",     "default": ""},
]

_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": None}


def _zip_latlon(zip_code):
    loc = fetch_json_request(f"https://api.zippopotam.us/us/{zip_code}", seconds=86400)
    p = loc["places"][0]
    return float(p["latitude"]), float(p["longitude"])


def _bbox(lat, lon, radius_miles):
    dlat = radius_miles / 69.0
    dlon = radius_miles / (69.0 * math.cos(math.radians(lat)))
    return lat - dlat, lat + dlat, lon - dlon, lon + dlon


def render(options=None):
    opts = options or {}
    zip_code = (opts.get("zipCode") or "10001").strip()
    radius = max(10, min(500, int(opts.get("radiusMiles") or 50)))
    cid = opts.get("clientId", "")
    csec = opts.get("clientSecret", "")

    lat, lon = _zip_latlon(zip_code)
    lamin, lamax, lomin, lomax = _bbox(lat, lon, radius)

    data = fetch_opensky(_CACHE, cid, csec, lamin, lamax, lomin, lomax)
    states = data.get("states") or []

    flights = []
    for s in states:
        if s[6] is None or s[5] is None or s[8]:
            continue
        dist = haversine_miles(lat, lon, float(s[6]), float(s[5]))
        flights.append((dist, s))
    flights.sort(key=lambda x: x[0])

    if not flights:
        return None

    dist, s = flights[0]
    callsign  = (s[1] or "").strip()
    alt_ft    = int((s[7] or s[13] or 0) * 3.28084)
    speed_kt  = int((s[9] or 0) * 1.94384)
    direction = compass_dir(lat, lon, float(s[6]), float(s[5]))

    airline      = lookup_airline(callsign)
    airline_name = airline[0] if airline else callsign[:8]
    iata         = airline[1] if airline else None
    flight_num   = (iata + callsign[3:]) if (airline and iata) else callsign

    extra = f"  +{len(flights)-1}" if len(flights) > 1 else ""
    line4 = f"{dist:.0f}mi {direction}{extra}"

    return render_flight_image(flight_num, airline_name, iata, alt_ft, speed_kt, line4)
