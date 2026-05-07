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
CARD_DETAIL = "FlightAware status"
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
    {"key": "apiKey", "label": "FlightAware API Key", "type": "text", "default": ""},
]

_CACHE = {}
_API_ROOT = "https://aeroapi.flightaware.com/aeroapi"


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
    if not isinstance(value, dict):
        return "---"
    return value.get("code_iata") or value.get("code_lid") or value.get("code") or "---"


def _flight_number(flight):
    ident = flight.get("ident_iata") or flight.get("ident") or ""
    if ident:
        return ident.replace(" ", "")[:8]
    op = flight.get("operator_iata") or flight.get("operator") or ""
    num = str(flight.get("flight_number") or "")
    return (op + num)[:8]


def _delay_minutes(flight):
    dep = flight.get("departure_delay")
    arr = flight.get("arrival_delay")
    seconds = dep if dep not in (None, "") else arr
    try:
        return int(round(float(seconds) / 60.0))
    except Exception:
        return 0


def _status(flight):
    raw = str(flight.get("status") or "").upper()
    delay = _delay_minutes(flight)
    if flight.get("cancelled"):
        return "CANCEL", (255, 80, 80)
    if flight.get("diverted"):
        return "DIVERT", (255, 160, 80)
    if flight.get("actual_in"):
        return "AT GATE", (95, 230, 135)
    if flight.get("actual_on"):
        return "LANDED", (95, 230, 135)
    if flight.get("actual_off"):
        pct = flight.get("progress_percent")
        return (f"AIR {pct}%" if pct not in (None, "") else "IN AIR"), (100, 190, 255)
    if flight.get("actual_out"):
        return "TAXI", (255, 220, 90)
    if "BOARD" in raw:
        return "BOARD", (95, 230, 135)
    if delay >= 15:
        return f"DLY {delay}m", (255, 120, 80)
    if raw:
        first = raw.split("/")[0].strip()
        if first:
            return first[:8], (95, 230, 135)
    return "ON TIME", (95, 230, 135)


def _event_time(flight):
    if flight.get("actual_in"):
        return "GATE " + _fmt_time(flight.get("actual_in"))
    if flight.get("actual_on"):
        return "LAND " + _fmt_time(flight.get("actual_on"))
    if flight.get("actual_off"):
        return "ETA " + _fmt_time(flight.get("estimated_in") or flight.get("scheduled_in"))
    if flight.get("actual_out"):
        return "OFF " + _fmt_time(flight.get("estimated_off") or flight.get("scheduled_off"))
    return "DEP " + _fmt_time(flight.get("estimated_out") or flight.get("scheduled_out"))


def _gate_line(flight):
    gate = flight.get("gate_origin")
    terminal = flight.get("terminal_origin")
    if flight.get("actual_off") or flight.get("actual_on") or flight.get("actual_in"):
        gate = flight.get("gate_destination") or gate
        terminal = flight.get("terminal_destination") or terminal
    parts = []
    if terminal:
        parts.append("T" + str(terminal))
    if gate:
        parts.append("G" + str(gate))
    return " ".join(parts)[:10]


def _airline_iata(flight):
    iata = flight.get("operator_iata")
    if iata:
        return str(iata).upper()
    ident = str(flight.get("ident_iata") or "").strip().upper()
    if len(ident) >= 2:
        return ident[:2]
    airline = lookup_airline(flight.get("ident") or "")
    return airline[1] if airline else None


def _draw_airline_mark(image, draw, iata):
    if iata == "WN":
        # Tiny Southwest-style heart mark. External logo feeds often return a
        # generic plane icon for WN, which is less useful on a 64x32 matrix.
        x, y = 52, 1
        blue = (45, 80, 210)
        red = (230, 45, 65)
        yellow = (255, 200, 40)
        draw.polygon([(x + 5, y + 10), (x + 1, y + 5), (x + 1, y + 2),
                      (x + 3, y), (x + 5, y + 2), (x + 7, y),
                      (x + 9, y + 2), (x + 9, y + 5)], fill=blue)
        draw.polygon([(x + 5, y + 10), (x + 1, y + 5), (x + 9, y + 5)], fill=red)
        draw.polygon([(x + 5, y + 10), (x + 3, y + 7), (x + 7, y + 7)], fill=yellow)
        return True
    return False


def _fit_text(draw, text, font, max_width):
    text = str(text or "")
    while text and draw.textbbox((0, 0), text, font=font)[2] > max_width:
        text = text[:-1]
    return text


def _fetch(ident, api_key):
    now = datetime.now(timezone.utc)
    key = ident
    cached = _CACHE.get(key)
    if cached and cached["expires"] > now:
        return cached["data"]
    encoded = urllib.parse.quote(ident, safe="")
    url = f"{_API_ROOT}/flights/{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "Hubyt/0.1", "x-apikey": api_key, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    _CACHE[key] = {"data": data, "expires": now + timedelta(seconds=90)}
    return data


def _pick_flight(flights):
    if not flights:
        return None
    now = datetime.now(timezone.utc)

    def score(f):
        if f.get("actual_off") and not f.get("actual_in"):
            return 0
        out = _parse_time(f.get("estimated_out") or f.get("scheduled_out"))
        if out:
            delta = abs((out - now).total_seconds())
            return 1 + delta / 86400
        return 999

    return sorted(flights, key=score)[0]


def _load_flight(opts):
    api_key = str(opts.get("apiKey") or "").strip()
    if not api_key:
        return None, "SET API"
    ident = _ident_from_options(opts, use_icao=False)
    if not ident:
        return None, "SET FLT"
    last_error = None
    for candidate in [ident, _ident_from_options(opts, use_icao=True)]:
        if not candidate:
            continue
        try:
            data = _fetch(candidate, api_key)
            flight = _pick_flight(data.get("flights") or [])
            if flight:
                return flight, None
        except urllib.error.HTTPError as err:
            if err.code in (401, 403):
                return None, "BAD API"
            if err.code == 404:
                last_error = "NOT FOUND"
                continue
            last_error = "API ERR"
        except Exception:
            last_error = "API ERR"
    return None, last_error or "NOT FOUND"


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
    text_width = 49
    ident = _fit_text(draw, ident, bold, text_width)
    status = _fit_text(draw, status, bold, text_width)
    route = f"{_airport_code(flight.get('origin'))}>{_airport_code(flight.get('destination'))}"
    time_line = _event_time(flight)
    gate = _gate_line(flight)
    bottom = time_line
    if gate:
        bottom = (time_line + " " + gate).strip()

    iata = _airline_iata(flight)
    logo_drawn = _draw_airline_mark(image, draw, iata) if iata else False
    logo = fetch_airline_logo(iata) if iata and not logo_drawn else None
    if logo and not logo_drawn:
        image.paste(logo, (52, 1), logo)
    elif iata and not logo_drawn:
        lw = draw.textbbox((0, 0), iata[:2], font=bold)[2]
        draw_sharp_text(image, (63 - lw, -3), iata[:2], (100, 190, 255), bold)

    draw_sharp_text(image, (1, -3), ident, (235, 245, 255), bold)
    draw_sharp_text(image, (1, 6), status, status_color, bold)
    draw_sharp_text(image, (1, 15), _fit_text(draw, route, font, text_width), (100, 190, 255), font)
    draw_sharp_text(image, (1, 24), _fit_text(draw, bottom, font, text_width), (255, 220, 90), font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
