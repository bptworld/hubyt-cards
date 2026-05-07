from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import urllib.parse
import urllib.request
from card_utils import (
    draw_sharp_text, fetch_airline_logo, iata_to_icao_prefix, lookup_airline,
    render_text_webp,
)

CARD_ID = "flight_track"
CARD_NAME = "Flight Tracker"
CARD_DETAIL = "Flightradar24 live and summary tracking"
CARD_OPTIONS = [
    {
        "key": "airline",
        "label": "Airline",
        "type": "select",
        "default": "WN",
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
    {"key": "flightNumber", "label": "Flight Number", "type": "text", "default": "3416", "maxlength": 6, "inputmode": "numeric"},
    {"key": "origin", "label": "Origin", "type": "text", "default": "", "maxlength": 3},
    {"key": "destination", "label": "Destination", "type": "text", "default": "", "maxlength": 3},
    {"key": "apiKey", "label": "Flightradar24 API Token", "type": "text", "default": ""},
]

_CACHE = {}
_API_ROOT = "https://fr24api.flightradar24.com/api"


def _clean(value):
    return "".join(ch for ch in str(value or "").upper() if ch.isalnum())


def _ident_from_options(opts, use_icao=False):
    number = "".join(ch for ch in str(opts.get("flightNumber") or "") if ch.isdigit())
    airline = _clean(opts.get("airline") or "")
    if airline and number:
        if use_icao and len(airline) == 2:
            airline = iata_to_icao_prefix(airline) or airline
        return airline + number
    return _clean(opts.get("callsign") or "")


def _flight_number_from_options(opts):
    return "".join(ch for ch in str(opts.get("flightNumber") or "") if ch.isdigit())


def _airline_icao_from_options(opts):
    airline = _clean(opts.get("airline") or "")
    if len(airline) == 2:
        return iata_to_icao_prefix(airline) or airline
    return airline


def _route_from_options(opts):
    origin = _clean(opts.get("origin") or "")[:3]
    destination = _clean(opts.get("destination") or "")[:3]
    if origin and destination:
        return f"{origin}-{destination}"
    return ""


def _parse_time(value):
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except Exception:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _fmt_time(value):
    dt = _parse_time(value)
    if not dt:
        return "--:--"
    return dt.astimezone().strftime("%I:%M").lstrip("0")


def _airport_code(value):
    if isinstance(value, str) and value:
        return value[:3].upper()
    if not isinstance(value, dict):
        return "---"
    return value.get("code_iata") or value.get("code_lid") or value.get("code") or "---"


def _flight_number(flight):
    ident = flight.get("flight") or flight.get("ident_iata") or flight.get("ident") or flight.get("callsign") or ""
    if ident:
        return ident.replace(" ", "")[:8]
    op = flight.get("operator_iata") or flight.get("operator") or ""
    num = str(flight.get("flight_number") or "")
    return (op + num)[:8]


def _delay_minutes(flight):
    return 0


def _status(flight):
    if flight.get("_summary"):
        if flight.get("datetime_landed"):
            return "LAND", (95, 230, 135)
        if flight.get("datetime_takeoff"):
            return "ENRT", (100, 190, 255)
        return "SCHED", (255, 220, 90)
    try:
        alt = int(float(flight.get("alt") or 0))
    except Exception:
        alt = 0
    try:
        speed = int(float(flight.get("gspeed") or 0))
    except Exception:
        speed = 0
    source = str(flight.get("source") or "").upper()
    if alt > 1000:
        return "ENRT", (100, 190, 255)
    if speed > 40:
        return "TAXI", (255, 220, 90)
    if source == "ESTIMATED":
        return "EST", (255, 220, 90)
    return "LIVE", (95, 230, 135)


def _event_time(flight):
    if flight.get("_summary"):
        if flight.get("datetime_landed"):
            return "LAND " + _fmt_time(flight.get("datetime_landed"))
        if flight.get("datetime_takeoff"):
            return "OFF " + _fmt_time(flight.get("datetime_takeoff"))
        return "SEEN " + _fmt_time(flight.get("first_seen"))
    if flight.get("eta"):
        return "ETA " + _fmt_time(flight.get("eta"))
    try:
        speed = int(float(flight.get("gspeed") or 0))
    except Exception:
        speed = 0
    return f"{speed}KT" if speed else "LIVE"


def _gate_line(flight):
    if flight.get("_summary"):
        seconds = flight.get("flight_time")
        try:
            mins = int(seconds or 0) // 60
        except Exception:
            mins = 0
        return f"{mins // 60}H{mins % 60:02d}" if mins else ""
    try:
        alt = int(float(flight.get("alt") or 0))
    except Exception:
        alt = 0
    return f"{alt // 100}FL" if alt >= 10000 else ""


def _airline_iata(flight):
    ident = str(flight.get("flight") or "").strip().upper()
    if len(ident) >= 2:
        return ident[:2]
    airline = lookup_airline(flight.get("operating_as") or flight.get("callsign") or "")
    if airline:
        return airline[1]
    painted = str(flight.get("painted_as") or flight.get("operating_as") or "").upper()
    reverse = {
        "AAL": "AA", "UAL": "UA", "DAL": "DL", "SWA": "WN", "ASA": "AS",
        "JBU": "B6", "FFT": "F9", "NKS": "NK", "HAL": "HA", "BAW": "BA",
        "AFR": "AF", "DLH": "LH", "UAE": "EK", "ACA": "AC",
    }
    return reverse.get(painted)


def _draw_southwest_heart(draw, x, y):
    # 16x16 pixel version of the Southwest heart icon.
    gray = (190, 194, 198)
    red = (222, 20, 35)
    blue = (25, 78, 170)
    yellow = (255, 184, 32)
    white = (245, 245, 245)

    outline = [(4, 0), (6, 0), (8, 2), (10, 0), (12, 0), (14, 2), (15, 5),
               (15, 7), (14, 10), (8, 16), (2, 10), (0, 7), (0, 4), (2, 1)]
    draw.polygon([(x + px, y + py) for px, py in outline], fill=gray)
    inner = [(4, 2), (6, 2), (8, 4), (10, 2), (12, 2), (13, 3), (14, 5),
             (14, 7), (13, 9), (8, 14), (3, 9), (1, 7), (1, 5), (2, 3)]
    draw.polygon([(x + px, y + py) for px, py in inner], fill=white)
    draw.polygon([(x + 2, y + 5), (x + 7, y + 9), (x + 12, y + 13),
                  (x + 8, y + 14), (x + 3, y + 9), (x + 1, y + 7)],
                 fill=blue)
    draw.polygon([(x + 3, y + 3), (x + 6, y + 3), (x + 8, y + 5),
                  (x + 13, y + 9), (x + 12, y + 13), (x + 2, y + 5)],
                 fill=red)
    draw.polygon([(x + 9, y + 4), (x + 10, y + 2), (x + 12, y + 3),
                  (x + 14, y + 5), (x + 14, y + 7), (x + 13, y + 9)],
                 fill=yellow)
    draw.line((x + 2, y + 5, x + 12, y + 13), fill=white)
    draw.line((x + 8, y + 4, x + 13, y + 9), fill=white)
    draw.line((x + 8, y + 14, x + 12, y + 13), fill=white)


def _fit_text(draw, text, font, max_width):
    text = str(text or "")
    while text and draw.textbbox((0, 0), text, font=font)[2] > max_width:
        text = text[:-1]
    return text


def _draw_tight_text(image, text, x, y, fill, font, spacing=-1):
    from PIL import Image, ImageDraw
    cursor = x
    for ch in str(text or ""):
        mask = Image.new("1", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.text((cursor, y), ch, fill=1, font=font)
        image.paste(Image.new("RGB", image.size, fill), (0, 0), mask)
        cursor += draw.textbbox((0, 0), ch, font=font)[2] + spacing
    return cursor


def _fetch(endpoint, params, api_key):
    now = datetime.now(timezone.utc)
    key = endpoint + "?" + urllib.parse.urlencode(sorted(params.items()))
    cached = _CACHE.get(key)
    if cached and cached["expires"] > now:
        return cached["data"]
    url = f"{_API_ROOT}{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Hubyt/0.1",
        "Authorization": "Bearer " + api_key,
        "Accept": "application/json",
        "Accept-Version": "v1",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    _CACHE[key] = {"data": data, "expires": now + timedelta(seconds=90)}
    return data


def _data_rows(data):
    if isinstance(data, dict):
        rows = data.get("data")
        return rows if isinstance(rows, list) else []
    return data if isinstance(data, list) else []


def _pick_flight(flights):
    if not flights:
        return None
    now = datetime.now(timezone.utc)

    def score(f):
        try:
            alt = int(float(f.get("alt") or 0))
        except Exception:
            alt = 0
        if alt > 0:
            return 0
        eta = _parse_time(f.get("eta"))
        if eta:
            delta = abs((eta - now).total_seconds())
            return 1 + delta / 86400
        return 999

    return sorted(flights, key=score)[0]


def _pick_summary(rows):
    if not rows:
        return None
    now = datetime.now(timezone.utc)

    def score(row):
        if row.get("datetime_takeoff") and not row.get("datetime_landed"):
            return 0
        for key in ("first_seen", "datetime_takeoff", "datetime_landed"):
            dt = _parse_time(row.get(key))
            if dt:
                return 1 + abs((dt - now).total_seconds()) / 86400
        return 999

    picked = sorted(rows, key=score)[0]
    picked["_summary"] = True
    return picked


def _load_flight(opts):
    api_key = str(opts.get("apiKey") or "").strip()
    if not api_key:
        return None, "SET API"
    ident = _ident_from_options(opts, use_icao=False)
    if not ident:
        return None, "SET FLT"
    last_error = None
    flight_no = _flight_number_from_options(opts)
    airline_icao = _airline_icao_from_options(opts)
    route = _route_from_options(opts)
    iata_ident = ident
    icao_ident = _ident_from_options(opts, use_icao=True)
    candidates = [
        {"flights": iata_ident, "limit": "5"},
        {"callsigns": icao_ident, "limit": "5"} if icao_ident else None,
        {"flights": iata_ident, "operating_as": airline_icao, "limit": "5"} if iata_ident and airline_icao else None,
        {"flights": iata_ident, "painted_as": airline_icao, "limit": "5"} if iata_ident and airline_icao else None,
        {"routes": route, "operating_as": airline_icao, "limit": "10"} if route and airline_icao else None,
    ]
    for params in candidates:
        if not params:
            continue
        try:
            data = _fetch("/live/flight-positions/full", params, api_key)
            flight = _pick_flight(_data_rows(data))
            if flight:
                return flight, None
        except urllib.error.HTTPError as err:
            if err.code in (401, 403):
                return None, "BAD API"
            if err.code in (404, 422):
                last_error = "NO LIVE"
                continue
            last_error = "API ERR"
        except Exception:
            last_error = "API ERR"

    now = datetime.now(timezone.utc)
    summary_params = {
        "flight_datetime_from": (now - timedelta(hours=18)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "flight_datetime_to": (now + timedelta(hours=36)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": "10",
    }
    if iata_ident:
        summary_params["flights"] = iata_ident
    if icao_ident:
        summary_params["callsigns"] = icao_ident
    if route:
        summary_params["routes"] = route
    try:
        data = _fetch("/flight-summary/full", summary_params, api_key)
        flight = _pick_summary(_data_rows(data))
        if flight:
            return flight, None
        last_error = "NO LIVE"
    except urllib.error.HTTPError as err:
        if err.code in (401, 403):
            return None, "BAD API"
        last_error = "NO LIVE"
    except Exception:
        last_error = "API ERR"
    return None, last_error or "NO LIVE"


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    flight, error = _load_flight(options or {})
    if error:
        color = (100, 190, 255) if error.startswith("SET") else (238, 80, 80)
        return render_text_webp(error, color)

    image = Image.new("RGB", (64, 32), (0, 5, 18))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    ident = _flight_number(flight)
    status, status_color = _status(flight)
    if _airline_iata(flight) == "WN":
        logo_left = 0
        logo_top = 0
        text_left = 18
        ident_max = 45
        route_max = 45
        bottom_max = 45
    else:
        logo_left = 52
        logo_top = 1
        text_left = 1
        ident_max = 39
        route_max = 62
        bottom_max = 62
    ident = _fit_text(draw, ident, font, ident_max)
    status = _fit_text(draw, status, bold, 62)
    route = f"{_airport_code(flight.get('orig_iata') or flight.get('orig_icao'))}>{_airport_code(flight.get('dest_iata') or flight.get('dest_icao'))}"
    time_line = _event_time(flight)
    gate = _gate_line(flight)
    bottom = time_line
    if gate:
        bottom = (time_line + " " + gate).strip()

    iata = _airline_iata(flight)
    if iata == "WN":
        _draw_southwest_heart(draw, logo_left, logo_top)
    else:
        logo = fetch_airline_logo(iata) if iata else None
        if logo:
            image.paste(logo, (logo_left, logo_top), logo)
        elif iata:
            lw = draw.textbbox((0, 0), iata[:2], font=bold)[2]
            draw_sharp_text(image, (63 - lw, -3), iata[:2], (100, 190, 255), bold)

    draw_sharp_text(image, (text_left, -3), ident, (235, 245, 255), font)
    status_y = 4 if status.startswith("ENRT ") else 6
    if status.startswith("ENRT "):
        next_x = _draw_tight_text(image, "ENRT", text_left, status_y, status_color, font, -1)
        draw_sharp_text(image, (next_x + 3, status_y), status[5:], status_color, font)
    else:
        draw_sharp_text(image, (text_left, status_y), status, status_color, font)
    draw_sharp_text(image, (text_left, 11), _fit_text(draw, route, font, route_max), (100, 190, 255), font)
    draw_sharp_text(image, (text_left, 18), _fit_text(draw, bottom, font, bottom_max), (255, 220, 90), font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
