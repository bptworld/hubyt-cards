from io import BytesIO
import json
import re
import urllib.request
from datetime import datetime, timedelta, timezone

WEATHER_CACHE = {}


def fetch_json_url(url, cache, seconds=45):
    now = datetime.now(timezone.utc)
    if cache is not None and cache["body"] and cache["expires"] > now:
        return json.loads(cache["body"].decode("utf-8"))
    request = urllib.request.Request(url, headers={"User-Agent": "Hubyt/0.1"})
    with urllib.request.urlopen(request, timeout=10) as response:
        body = response.read()
    if cache is not None:
        cache["body"] = body
        cache["expires"] = now + timedelta(seconds=seconds)
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
    favorite = (favorite or "").upper()
    for state in ("in", "pre", "post"):
        for event in events:
            competition = event.get("competitions", [{}])[0]
            ev_state = competition.get("status", {}).get("type", {}).get("state")
            teams = json.dumps(event).upper()
            if ev_state == state and (not favorite or f'"{favorite}"' in teams):
                return event
    return events[0] if events else None


def render_sport_card(options, url, cache, status_color, fallback_text):
    from PIL import Image, ImageDraw, ImageFont
    favorite = (options or {}).get("favoriteTeam", "")
    data = fetch_json_url(url, cache, seconds=15)
    event = pick_sport_event(data.get("events", []), favorite)
    if not event:
        cache["expires"] = datetime.now(timezone.utc) + timedelta(seconds=900)
        return render_text_webp(fallback_text, status_color)

    competition = event.get("competitions", [{}])[0]
    competitors = competition.get("competitors", [])
    away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[-1] if competitors else {})
    home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0] if competitors else {})
    away_team = away.get("team", {})
    home_team = home.get("team", {})
    state = competition.get("status", {}).get("type", {}).get("state")

    cache["expires"] = datetime.now(timezone.utc) + timedelta(seconds=15 if state == "in" else 900)
    status = competition.get("status", {}).get("type", {}).get("shortDetail", "")
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
    by1, by2 = 8, 8 + sh + pad * 2
    draw.rounded_rectangle((bx1, by1, bx2, by2), radius=3, fill=(18, 29, 39), outline=(69, 87, 104))
    draw_sharp_text(image, (32 - sw // 2, 5 + pad), score, (247, 251, 255), score_font)

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
