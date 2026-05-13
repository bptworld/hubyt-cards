from io import BytesIO
import base64
import json
import math
import re
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

WEATHER_CACHE = {}


def fetch_json_url(url, cache, seconds=45):
    now = datetime.now(timezone.utc)
    if cache is not None and cache.get("body") and cache.get("expires", now) > now and cache.get("url", url) == url:
        return json.loads(cache["body"].decode("utf-8"))
    request = urllib.request.Request(url, headers={"User-Agent": "Hubyt/0.1"})
    with urllib.request.urlopen(request, timeout=10) as response:
        body = response.read()
    if cache is not None:
        cache["body"] = body
        cache["expires"] = now + timedelta(seconds=seconds)
        cache["url"] = url
    return json.loads(body.decode("utf-8"))


def fetch_json_request(url, seconds=600):
    now = datetime.now(timezone.utc)
    cached = WEATHER_CACHE.get(url)
    if cached and cached["expires"] > now:
        return cached["data"]
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Hubyt/0.1", "Accept": "application/geo+json, application/json"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    WEATHER_CACHE[url] = {"expires": now + timedelta(seconds=seconds), "data": data}
    return data


def fetch_json_with_headers(url, headers=None, seconds=600, cache_key=None):
    now = datetime.now(timezone.utc)
    key = cache_key or url + "|" + json.dumps(headers or {}, sort_keys=True)
    cached = WEATHER_CACHE.get(key)
    if cached and cached["expires"] > now:
        return cached["data"]
    request_headers = {"User-Agent": "Hubyt/0.1", "Accept": "application/json"}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    WEATHER_CACHE[key] = {"expires": now + timedelta(seconds=seconds), "data": data}
    return data


def format_compact_number(value):
    try:
        n = float(value)
    except Exception:
        return "--"
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1000000000:
        return f"{sign}{n/1000000000:.1f}B"
    if n >= 1000000:
        return f"{sign}{n/1000000:.1f}M"
    if n >= 10000:
        return f"{sign}{n/1000:.0f}K"
    if n >= 1000:
        return f"{sign}{n/1000:.1f}K"
    return f"{sign}{int(round(n))}"


def _draw_counter_logo(draw, logo, x, y, color):
    logo = (logo or "").lower()
    if logo == "youtube":
        draw.rounded_rectangle((x, y + 3, x + 17, y + 15), radius=3, fill=(255, 0, 0))
        draw.polygon([(x + 7, y + 6), (x + 7, y + 12), (x + 13, y + 9)], fill=(255, 255, 255))
    elif logo == "facebook":
        draw.rounded_rectangle((x + 2, y + 1, x + 16, y + 15), radius=3, fill=(24, 119, 242))
        draw.rectangle((x + 9, y + 5, x + 12, y + 15), fill=(255, 255, 255))
        draw.rectangle((x + 7, y + 8, x + 14, y + 10), fill=(255, 255, 255))
        draw.rectangle((x + 10, y + 3, x + 15, y + 5), fill=(255, 255, 255))
        draw.point((x + 15, y + 5), fill=(24, 119, 242))
    elif logo == "x":
        draw.line((x + 3, y + 2, x + 15, y + 15), fill=(245, 250, 255), width=2)
        draw.line((x + 15, y + 2, x + 3, y + 15), fill=(245, 250, 255), width=2)
    elif logo == "instagram":
        draw.point((x + 3, y + 2), fill=(255, 220, 80))
        draw.line((x + 4, y + 1, x + 14, y + 1), fill=(245, 80, 170), width=2)
        draw.line((x + 15, y + 3, x + 15, y + 13), fill=(180, 80, 255), width=2)
        draw.line((x + 4, y + 15, x + 14, y + 15), fill=(255, 120, 60), width=2)
        draw.line((x + 2, y + 4, x + 2, y + 12), fill=(255, 200, 80), width=2)
        draw.ellipse((x + 6, y + 5, x + 12, y + 11), outline=(245, 250, 255))
        draw.point((x + 13, y + 4), fill=(255, 210, 80))
    else:
        draw.ellipse((x + 3, y + 2, x + 15, y + 14), outline=color)


def render_counter_card(title, label, value, color=(80, 180, 255), sublabel="FOLLOWERS", logo=None):
    from PIL import Image, ImageDraw, ImageFont
    image = Image.new("RGB", (64, 32), (0, 5, 12))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
        big = ImageFont.truetype("Silkscreen-Bold.ttf", 16)
    except Exception:
        font = bold = big = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(5, 18, 28))
    title = str(title or "")[:12].upper()
    tw = draw.textbbox((0, 0), title, font=bold)[2]
    draw_sharp_text(image, ((64 - tw) // 2, -3), title, color, bold)

    if logo:
        _draw_counter_logo(draw, logo, 1, 10, color)
        value_left = 20
        value_width = 44
    else:
        value_left = 0
        value_width = 64

    val = format_compact_number(value)
    vw = draw.textbbox((0, 0), val, font=big)[2]
    if vw <= value_width - 2:
        draw_sharp_text(image, (value_left + (value_width - vw) // 2, 6), val, (245, 250, 255), big)
    else:
        vw = draw.textbbox((0, 0), val, font=bold)[2]
        draw_sharp_text(image, (value_left + (value_width - vw) // 2, 9), val, (245, 250, 255), bold)

    bottom = (str(label or sublabel or "")[:9] or sublabel).upper()
    bw = draw.textbbox((0, 0), bottom, font=font)[2]
    draw_sharp_text(image, ((64 - bw) // 2, 22), bottom, (145, 165, 182), font)
    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()


def weather_for_zip(zip_code):
    zip_code = re.sub(r"\D", "", zip_code or "")[:5]
    if len(zip_code) != 5:
        raise ValueError("Enter a 5 digit ZIP code.")
    location = fetch_json_request(f"https://api.zippopotam.us/us/{zip_code}", seconds=86400)
    place = location["places"][0]
    lat, lon = place["latitude"], place["longitude"]
    point = fetch_json_request(f"https://api.weather.gov/points/{lat},{lon}", seconds=86400)
    forecast_url = point["properties"]["forecastHourly"]
    forecast = fetch_json_request(forecast_url, seconds=600)
    period = forecast["properties"]["periods"][0]
    short = period.get("shortForecast", "Weather")
    lower = short.lower()
    if "snow" in lower or "sleet" in lower or "ice" in lower:
        icon = "snow"
    elif "rain" in lower or "shower" in lower or "storm" in lower:
        icon = "rain"
    elif "cloud" in lower or "overcast" in lower:
        icon = "cloud"
    else:
        icon = "sun"
    return {
        "temperature": period.get("temperature"),
        "temperatureUnit": period.get("temperatureUnit", "F"),
        "shortForecast": short,
        "icon": icon,
    }


def draw_sharp_text(image, xy, text, fill, font):
    from PIL import Image, ImageDraw
    mask = Image.new("1", image.size, 0)
    ImageDraw.Draw(mask).text(xy, text, fill=1, font=font)
    image.paste(Image.new("RGB", image.size, fill), (0, 0), mask)


def draw_mini_weather_icon(draw, icon, cx, y):
    if icon == "sun":
        draw.ellipse((cx - 4, y + 2, cx + 4, y + 8), fill=(255, 205, 64))
        for pts in [
            (cx, y, cx, y + 1), (cx, y + 9, cx, y + 10),
            (cx - 6, y + 5, cx - 5, y + 5), (cx + 5, y + 5, cx + 6, y + 5),
        ]:
            draw.line(pts, fill=(255, 225, 90))
    elif icon == "cloud":
        draw.ellipse((cx - 6, y + 3, cx, y + 8), fill=(135, 155, 175))
        draw.ellipse((cx - 2, y + 1, cx + 6, y + 8), fill=(170, 190, 205))
        draw.rectangle((cx - 5, y + 5, cx + 7, y + 9), fill=(170, 190, 205))
    elif icon == "rain":
        draw.ellipse((cx - 6, y + 2, cx, y + 6), fill=(120, 150, 170))
        draw.ellipse((cx - 2, y, cx + 6, y + 6), fill=(145, 170, 190))
        draw.rectangle((cx - 5, y + 4, cx + 7, y + 7), fill=(145, 170, 190))
        for dx in (-4, 0, 4):
            draw.line((cx + dx, y + 7, cx + dx - 1, y + 10), fill=(64, 181, 255))
    elif icon == "snow":
        draw.ellipse((cx - 6, y + 2, cx, y + 6), fill=(180, 200, 215))
        draw.ellipse((cx - 2, y, cx + 6, y + 6), fill=(205, 220, 230))
        draw.rectangle((cx - 5, y + 4, cx + 7, y + 7), fill=(205, 220, 230))
        for dx in (-4, 0, 4):
            draw.point((cx + dx, y + 9), fill=(235, 250, 255))


def fetch_logo(url):
    try:
        from PIL import Image
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "Hubyt/0.1"}), timeout=5
        ) as response:
            data = response.read()
        img = Image.open(BytesIO(data)).convert("RGBA").resize((11, 11), Image.NEAREST)
        r, g, b, a = img.split()
        a = a.point(lambda p: 255 if p > 128 else 0)
        return Image.merge("RGBA", (r, g, b, a))
    except Exception:
        return None


def get_team_record(competitor):
    for record in competitor.get("records", []):
        if record.get("type") == "total" or record.get("name") == "overall":
            return record.get("summary", "")
    return ""


_NAMED_COLORS = {
    "white": (255, 255, 255), "red": (238, 80, 80), "green": (100, 220, 100),
    "blue": (80, 150, 255), "orange": (255, 160, 60), "yellow": (255, 230, 60),
    "teal": (24, 182, 163), "purple": (180, 120, 255), "pink": (255, 120, 180),
}


def parse_color(value):
    v = str(value or "").strip()
    if v.startswith("#"):
        h = v.lstrip("#")
        if len(h) == 6:
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return _NAMED_COLORS.get(v.lower(), (255, 255, 255))


def _msg_font():
    from PIL import ImageFont
    try:
        return ImageFont.truetype("Silkscreen-Regular.ttf", 8)
    except Exception:
        return ImageFont.load_default()


def message_text_width(text):
    from PIL import Image, ImageDraw
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    return draw.textbbox((0, 0), text, font=_msg_font())[2]


def _wrap_frame(text, color_rgb):
    from PIL import Image, ImageDraw
    image = Image.new("RGB", (64, 32), (0, 0, 0))
    font = _msg_font()
    draw = ImageDraw.Draw(image)
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip() if current else word
        if draw.textbbox((0, 0), test, font=font)[2] <= 62:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    lines = lines[:4]
    line_h = 8
    y = (32 - len(lines) * line_h) // 2 - 3
    for line in lines:
        w = draw.textbbox((0, 0), line, font=font)[2]
        draw_sharp_text(image, ((64 - w) // 2, y), line, color_rgb, font)
        y += line_h
    return image


def render_message_wrap(text, color_rgb):
    out = BytesIO()
    _wrap_frame(text, color_rgb).save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()


def render_message_flash(text, color_rgb):
    from PIL import Image
    on_frame = _wrap_frame(text, color_rgb)
    off_frame = Image.new("RGB", (64, 32), (0, 0, 0))
    out = BytesIO()
    on_frame.save(
        out, "WEBP", save_all=True,
        append_images=[off_frame],
        duration=[500, 250],
        loop=0,
    )
    return out.getvalue()


def render_message_scroll(text, color_rgb):
    from PIL import Image, ImageDraw
    font = _msg_font()
    draw_dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    text_w = draw_dummy.textbbox((0, 0), text, font=font)[2]
    px_per_frame = 2
    frame_ms = 33
    total = 64 + text_w + 32
    frames = []
    for i in range(0, total, px_per_frame):
        img = Image.new("RGB", (64, 32), (0, 0, 0))
        x = 64 - i
        if x < 64:
            draw_sharp_text(img, (x, 12), text, color_rgb, font)
        frames.append(img)
    out = BytesIO()
    frames[0].save(
        out, "WEBP", save_all=True,
        append_images=frames[1:],
        duration=frame_ms,
        loop=0,
    )
    return out.getvalue()


def render_text_webp(text, color):
    from PIL import Image, ImageDraw, ImageFont
    image = Image.new("RGB", (64, 32), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    draw_sharp_text(
        image,
        ((64 - (bbox[2] - bbox[0])) // 2, (32 - (bbox[3] - bbox[1])) // 2),
        text, color, font,
    )
    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()


def pick_sport_event(events, favorite):
    from datetime import date
    today = date.today()
    favorite = (favorite or "").upper()
    today_events = []
    for event in events:
        raw = event.get("date", "")
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.astimezone().date() == today:
                today_events.append(event)
        except Exception:
            today_events.append(event)
    events = today_events or []
    for state in ("in", "pre", "post"):
        for event in events:
            competition = event.get("competitions", [{}])[0]
            ev_state = competition.get("status", {}).get("type", {}).get("state")
            teams = json.dumps(event).upper()
            if ev_state == state and (not favorite or f'"{favorite}"' in teams):
                return event
    return None


def dated_scoreboard_url(url):
    today = datetime.now().strftime("%Y%m%d")
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}dates={today}"


def render_sport_card(options, url, cache, status_color, fallback_text):
    from PIL import Image, ImageDraw, ImageFont
    favorite = (options or {}).get("favoriteTeam", "")
    data = fetch_json_url(dated_scoreboard_url(url), cache, seconds=15)
    event = pick_sport_event(data.get("events", []), favorite)
    if not event:
        cache["expires"] = datetime.now(timezone.utc) + timedelta(seconds=900)
        return None

    competition = event.get("competitions", [{}])[0]
    competitors = competition.get("competitors", [])
    away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[-1] if competitors else {})
    home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0] if competitors else {})
    away_team = away.get("team", {})
    home_team = home.get("team", {})
    state = competition.get("status", {}).get("type", {}).get("state")

    if state == "in":
        cache_secs = 15
    elif state == "pre":
        try:
            event_dt = datetime.fromisoformat(event.get("date", "").replace("Z", "+00:00"))
            secs_until = (event_dt - datetime.now(timezone.utc)).total_seconds()
            cache_secs = 15 if secs_until < 600 else 900
        except Exception:
            cache_secs = 900
    else:
        cache_secs = 900
    cache["expires"] = datetime.now(timezone.utc) + timedelta(seconds=cache_secs)
    status = competition.get("status", {}).get("type", {}).get("shortDetail", "")
    status = re.sub(r"\s+[A-Z]{2,3}T?$", "", status)   # strip timezone (ET, CT, PT…)
    status = re.sub(r"\s+-\s+", " ", status)             # "5/4 - 6:40" → "5/4 6:40"
    status = re.sub(r"\s+(AM|PM)", r"\1", status)        # "6:40 PM" → "6:40PM"
    score = "VS" if state == "pre" else f"{away.get('score', '0')}-{home.get('score', '0')}"

    image = Image.new("RGB", (64, 32), (5, 7, 10))
    draw = ImageDraw.Draw(image)
    try:
        tiny = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        small = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
        score_font = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        tiny = small = score_font = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(8, 18, 28))
    draw_sharp_text(image, (1, -3), status[:18].upper(), status_color, tiny)

    sb = draw.textbbox((0, 0), score, font=score_font)
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    pad = 3
    bx1, bx2 = 32 - sw // 2 - pad, 32 + (sw + 1) // 2 + pad
    by1, by2 = 7, 7 + sh + pad * 2
    draw.rounded_rectangle((bx1, by1, bx2, by2), radius=3, fill=(18, 29, 39), outline=(69, 87, 104))
    draw_sharp_text(image, (32 - sw // 2, 4 + pad), score, (247, 251, 255), score_font)

    away_abbrev = away_team.get("abbreviation", "AWY")[:3]
    home_abbrev = home_team.get("abbreviation", "HME")[:3]
    habb_w = draw.textbbox((0, 0), home_abbrev, font=small)[2]
    draw_sharp_text(image, (2, 15), away_abbrev, (255, 255, 255), small)
    draw_sharp_text(image, (63 - habb_w, 15), home_abbrev, (255, 255, 255), small)

    away_rec = get_team_record(away)[:7]
    home_rec = get_team_record(home)[:7]
    draw_sharp_text(image, (2, 22), away_rec, (174, 185, 196), tiny)
    if home_rec:
        hrec_w = draw.textbbox((0, 0), home_rec, font=tiny)[2]
        draw_sharp_text(image, (63 - hrec_w, 22), home_rec, (174, 185, 196), tiny)

    away_logo = fetch_logo(away_team.get("logo", ""))
    home_logo = fetch_logo(home_team.get("logo", ""))
    if away_logo:
        image.paste(away_logo, (2, 7), away_logo)
    if home_logo:
        image.paste(home_logo, (52, 7), home_logo)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()


# ── Flight utilities ──────────────────────────────────────────────────────────

_AIRLINES = {
    "AAL": ("American",    "AA"), "UAL": ("United",      "UA"), "DAL": ("Delta",       "DL"),
    "SWA": ("Southwest",   "WN"), "ASA": ("Alaska",      "AS"), "JBU": ("JetBlue",     "B6"),
    "FFT": ("Frontier",    "F9"), "NKS": ("Spirit",      "NK"), "HAL": ("Hawaiian",    "HA"),
    "SKW": ("SkyWest",     "OO"), "RPA": ("Republic",    "YX"), "FDX": ("FedEx",       "FX"),
    "UPS": ("UPS Air",     "5X"), "GTI": ("Atlas",       "GT"), "SWQ": ("Sun Country", "SY"),
    "ENY": ("Envoy",       "MQ"), "PDT": ("Piedmont",    "PT"), "PSA": ("PSA",         "OH"),
    "WEN": ("Endeavor",    "9E"), "BAW": ("British",     "BA"), "AFR": ("Air France",  "AF"),
    "DLH": ("Lufthansa",   "LH"), "UAE": ("Emirates",    "EK"), "QFA": ("Qantas",      "QF"),
    "ANA": ("ANA",         "NH"), "JAL": ("Japan Air",   "JL"), "KAL": ("Korean Air",  "KE"),
    "CPA": ("Cathay",      "CX"), "SIA": ("Singapore",   "SQ"), "ACA": ("Air Canada",  "AC"),
    "WJA": ("WestJet",     "WS"), "THY": ("Turkish",     "TK"), "IBE": ("Iberia",      "IB"),
    "EZY": ("easyJet",     "U2"), "RYR": ("Ryanair",     "FR"), "KLM": ("KLM",         "KL"),
    "CSN": ("China South", "CZ"), "CCA": ("Air China",   "CA"), "AMX": ("Aeromexico",  "AM"),
    "VOI": ("Volaris",     "Y4"), "TAM": ("LATAM",       "JJ"), "AVA": ("Avianca",     "AV"),
    "GLO": ("GOL",         "G3"), "AZU": ("Azul",        "AD"), "SAS": ("SAS",         "SK"),
    "VLG": ("Vueling",     "VY"), "WZZ": ("Wizz",        "W6"), "EIN": ("Aer Lingus",  "EI"),
    "SWR": ("Swiss",       "LX"), "AUA": ("Austrian",    "OS"), "ETH": ("Ethiopian",   "ET"),
    "QTR": ("Qatar",       "QR"), "SVA": ("Saudia",      "SV"), "AIC": ("Air India",   "AI"),
    "MSR": ("EgyptAir",    "MS"), "TUI": ("TUI",         "BY"), "AEE": ("Aegean",      "A3"),
}

_IATA_TO_ICAO = {iata: icao for icao, (_, iata) in _AIRLINES.items()}
_AIRLINE_LOGO_CACHE = {}
_AIRLINE_LOGO_BASE = "https://raw.githubusercontent.com/bptworld/hubyt-cards/main/assets/airlines"
_OPENSKY_TOKEN = {"token": None, "expires": datetime.min.replace(tzinfo=timezone.utc)}


def lookup_airline(callsign):
    prefix = (callsign or "").strip().upper()[:3]
    return _AIRLINES.get(prefix)


def iata_to_icao_prefix(iata):
    return _IATA_TO_ICAO.get((iata or "").upper())


def fetch_airline_logo(iata):
    iata = (iata or "").strip().upper()
    if iata in _AIRLINE_LOGO_CACHE:
        return _AIRLINE_LOGO_CACHE[iata]
    logo = fetch_logo(f"{_AIRLINE_LOGO_BASE}/{iata}.png")
    if logo is None:
        logo = fetch_logo(f"https://images.kiwi.com/airlines/64/{iata.lower()}.png")
    _AIRLINE_LOGO_CACHE[iata] = logo
    return logo


def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def compass_dir(lat1, lon1, lat2, lon2):
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(math.radians(lat2))
    y = (math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) -
         math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(dlon))
    deg = math.degrees(math.atan2(x, y)) % 360
    return ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][round(deg / 45) % 8]


def _opensky_token(client_id, client_secret):
    now = datetime.now(timezone.utc)
    if _OPENSKY_TOKEN["token"] and _OPENSKY_TOKEN["expires"] > now:
        return _OPENSKY_TOKEN["token"]
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(
        "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Hubyt/0.1"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    _OPENSKY_TOKEN["token"] = result["access_token"]
    _OPENSKY_TOKEN["expires"] = now + timedelta(seconds=result.get("expires_in", 1800) - 60)
    return _OPENSKY_TOKEN["token"]


def fetch_opensky(cache, client_id="", client_secret="", lamin=None, lamax=None, lomin=None, lomax=None):
    now = datetime.now(timezone.utc)
    if cache.get("body") and cache.get("expires", now) > now:
        return cache["body"]
    url = "https://opensky-network.org/api/states/all"
    if lamin is not None:
        url += f"?lamin={lamin:.4f}&lamax={lamax:.4f}&lomin={lomin:.4f}&lomax={lomax:.4f}"
    req = urllib.request.Request(url, headers={"User-Agent": "Hubyt/0.1"})
    if client_id and client_secret:
        try:
            req.add_header("Authorization", f"Bearer {_opensky_token(client_id, client_secret)}")
        except Exception:
            pass
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    cache["body"] = data
    cache["expires"] = now + timedelta(seconds=30)
    return data


def render_flight_image(flight_num, airline_name, iata, alt_ft, speed_kt, line4):
    from PIL import Image, ImageDraw, ImageFont
    image = Image.new("RGB", (64, 32), (0, 5, 18))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()
    draw.rectangle((0, 0, 63, 8), fill=(0, 15, 45))
    logo = fetch_airline_logo(iata) if iata else None
    tx = 1
    if logo:
        image.paste(logo, (1, -1), logo)
        tx = 14
    draw_sharp_text(image, (tx, -3), flight_num[:9], (255, 255, 255), bold)
    draw_sharp_text(image, (1, 5), airline_name[:10], (100, 190, 255), font)
    alt_str = f"{alt_ft // 1000}K ft" if alt_ft >= 1000 else f"{alt_ft}ft"
    spd_str = f"{speed_kt}kt"
    draw_sharp_text(image, (1, 13), alt_str, (200, 230, 255), font)
    sw = draw.textbbox((0, 0), spd_str, font=font)[2]
    draw_sharp_text(image, (63 - sw, 13), spd_str, (200, 230, 255), font)
    draw_sharp_text(image, (1, 21), line4[:14], (150, 200, 255), font)
    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
