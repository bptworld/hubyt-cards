from datetime import datetime, timezone
from card_utils import (
    fetch_opensky, lookup_airline, iata_to_icao_prefix,
    render_flight_image, render_text_webp,
)

CARD_ID = "flight_track"
CARD_NAME = "Flight Tracker"
CARD_DETAIL = "Track a specific flight"
CARD_OPTIONS = [
    {
        "key": "airline",
        "label": "Airline",
        "type": "select",
        "default": "UA",
        "choices": [
            {"value": "AA", "label": "American"},
            {"value": "UA", "label": "United"},
            {"value": "DL", "label": "Delta"},
            {"value": "WN", "label": "Southwest"},
            {"value": "AS", "label": "Alaska"},
            {"value": "B6", "label": "JetBlue"},
            {"value": "F9", "label": "Frontier"},
            {"value": "NK", "label": "Spirit"},
            {"value": "HA", "label": "Hawaiian"},
            {"value": "BA", "label": "British Airways"},
            {"value": "AF", "label": "Air France"},
            {"value": "LH", "label": "Lufthansa"},
            {"value": "EK", "label": "Emirates"},
            {"value": "AC", "label": "Air Canada"},
        ],
    },
    {"key": "flightNumber", "label": "Flight Number", "type": "text", "default": "1", "maxlength": 6, "inputmode": "numeric"},
    {"key": "clientId",     "label": "OpenSky Client ID",     "type": "text", "default": ""},
    {"key": "clientSecret", "label": "OpenSky Client Secret", "type": "text", "default": ""},
]

_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": None, "ttl": 60}


def _normalize(cs):
    cs = "".join(ch for ch in cs.strip().upper() if ch.isalnum())
    if len(cs) > 2 and cs[2].isdigit():
        icao = iata_to_icao_prefix(cs[:2])
        if icao:
            return icao + cs[2:]
    return cs


def _target_from_options(opts):
    flight_number = "".join(ch for ch in str(opts.get("flightNumber") or "") if ch.isdigit())
    airline = "".join(ch for ch in str(opts.get("airline") or "") if ch.isalnum()).upper()
    if airline and flight_number:
        if len(airline) == 2:
            airline = iata_to_icao_prefix(airline) or airline
        return _normalize(airline + flight_number)
    return _normalize(opts.get("callsign") or "")


def _callsign_variants(callsign):
    callsign = _normalize(callsign)
    variants = {callsign}
    prefix = callsign[:3]
    number = callsign[3:]
    if number.isdigit():
        variants.add(prefix + str(int(number)))
        variants.add(prefix + number.zfill(4))
    return variants


def render(options=None):
    opts = options or {}
    target = _target_from_options(opts)
    if not target:
        return render_text_webp("SET FLIGHT", (100, 190, 255))

    cid  = opts.get("clientId", "")
    csec = opts.get("clientSecret", "")
    targets = _callsign_variants(target)

    _CACHE.setdefault("expires", datetime.min.replace(tzinfo=timezone.utc))
    data   = fetch_opensky(_CACHE, cid, csec)
    states = data.get("states") or []

    match = None
    for s in states:
        cs = _normalize(s[1] or "")
        if cs in targets:
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
