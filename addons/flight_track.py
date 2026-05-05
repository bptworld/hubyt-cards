from datetime import datetime, timezone
from card_utils import (
    fetch_opensky, lookup_airline, iata_to_icao_prefix,
    render_flight_image, render_text_webp,
)

CARD_ID = "flight_track"
CARD_NAME = "Flight Tracker"
CARD_DETAIL = "Track a specific flight"
CARD_OPTIONS = [
    {"key": "callsign",     "label": "Flight # or Callsign", "type": "text", "default": "UA1", "maxlength": 8},
    {"key": "clientId",     "label": "OpenSky Client ID",     "type": "text", "default": ""},
    {"key": "clientSecret", "label": "OpenSky Client Secret", "type": "text", "default": ""},
]

_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": None, "ttl": 60}


def _normalize(cs):
    cs = cs.strip().upper()
    if len(cs) > 2 and cs[2].isdigit():
        icao = iata_to_icao_prefix(cs[:2])
        if icao:
            return icao + cs[2:]
    return cs


def render(options=None):
    opts = options or {}
    raw = (opts.get("callsign") or "").strip()
    if not raw:
        return render_text_webp("SET FLIGHT", (100, 190, 255))

    cid  = opts.get("clientId", "")
    csec = opts.get("clientSecret", "")
    target = _normalize(raw)

    _CACHE.setdefault("expires", datetime.min.replace(tzinfo=timezone.utc))
    data   = fetch_opensky(_CACHE, cid, csec)
    states = data.get("states") or []

    match = None
    for s in states:
        cs = (s[1] or "").strip().upper()
        if cs == target or cs.startswith(target):
            match = s
            break

    if not match:
        return render_text_webp("NOT FOUND", (238, 80, 80))

    s         = match
    callsign  = (s[1] or "").strip()
    on_ground = bool(s[8])
    alt_ft    = int((s[7] or s[13] or 0) * 3.28084)
    speed_kt  = int((s[9] or 0) * 1.94384)
    track_deg = s[10] or 0
    heading   = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][round(track_deg / 45) % 8]

    airline      = lookup_airline(callsign)
    airline_name = airline[0] if airline else callsign[:8]
    iata         = airline[1] if airline else None
    flight_num   = (iata + callsign[3:]) if (airline and iata) else callsign

    if on_ground:
        line4 = "ON GROUND"
    else:
        line4 = f"EN ROUTE {heading}"

    return render_flight_image(flight_num, airline_name, iata, alt_ft, speed_kt, line4)
