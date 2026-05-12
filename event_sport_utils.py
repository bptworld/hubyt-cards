from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import re
import urllib.request

from card_utils import draw_sharp_text, fetch_logo, render_text_webp

_CACHE = {}


def _dated_url(sport, league):
    now = datetime.now()
    end = now + timedelta(days=45)
    dates = now.strftime("%Y%m%d") + "-" + end.strftime("%Y%m%d")
    return f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard?dates={dates}"


def _fetch_events(sport, league):
    key = f"{sport}/{league}"
    now = datetime.now(timezone.utc)
    cached = _CACHE.get(key)
    if cached and cached["expires"] > now:
        return cached["events"]
    req = urllib.request.Request(_dated_url(sport, league), headers={"User-Agent": "Hubyt/0.1"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    events = data.get("events") or []
    _CACHE[key] = {"events": events, "expires": now + timedelta(minutes=15)}
    return events


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def _event_state(event):
    comp = (event.get("competitions") or [{}])[0]
    return (comp.get("status") or event.get("status") or {}).get("type", {})


def _pick_event(events):
    now = datetime.now(timezone.utc)
    upcoming = []
    completed = []
    for event in events:
        dt = _parse_dt(event.get("date"))
        state = _event_state(event).get("state", "")
        if state != "post" and (not dt or dt >= now - timedelta(days=1)):
            upcoming.append((dt or now, event))
        elif dt:
            completed.append((dt, event))
    if upcoming:
        return sorted(upcoming, key=lambda item: item[0])[0][1]
    if completed:
        return sorted(completed, key=lambda item: item[0], reverse=True)[0][1]
    return events[0] if events else None


def _fmt_event_time(event):
    status = _event_state(event)
    short = status.get("shortDetail") or status.get("detail") or ""
    short = re.sub(r"\s+[A-Z]{2,3}T?$", "", short)
    short = re.sub(r"\s+-\s+", " ", short)
    short = re.sub(r"\s+(AM|PM)", r"\1", short)
    if short:
        return short.upper()[:18]
    dt = _parse_dt(event.get("date"))
    if not dt:
        return ""
    return dt.astimezone().strftime("%-m/%-d %-I:%M%p").upper().replace(" ", "")


def _short_name(value, limit=14):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit]


def _competitors(event):
    comp = (event.get("competitions") or [{}])[0]
    return comp.get("competitors") or []


def _leader_rows(event, count=2):
    rows = []
    for competitor in _competitors(event)[:count]:
        athlete = competitor.get("athlete") or {}
        rank = str(competitor.get("order") or "")
        name = athlete.get("shortName") or athlete.get("displayName") or athlete.get("fullName") or ""
        score = competitor.get("score") or ("WIN" if competitor.get("winner") else "")
        flag = (athlete.get("flag") or {}).get("href", "")
        rows.append({"rank": rank, "name": name, "score": score, "flag": flag})
    return rows


def _draw_golf_icon(draw, x, y, color):
    draw.line((x + 3, y + 1, x + 3, y + 14), fill=color)
    draw.polygon([(x + 4, y + 1), (x + 13, y + 4), (x + 4, y + 7)], fill=(255, 80, 80))
    draw.ellipse((x + 7, y + 17, x + 13, y + 23), fill=(235, 245, 245))
    draw.arc((x + 0, y + 12, x + 15, y + 26), 180, 360, fill=(80, 140, 90))


def _draw_race_icon(draw, x, y, color):
    for row in range(4):
        for col in range(4):
            fill = (235, 245, 255) if (row + col) % 2 == 0 else color
            draw.rectangle((x + col * 3, y + row * 3, x + col * 3 + 2, y + row * 3 + 2), fill=fill)
    draw.line((x, y, x, y + 22), fill=(160, 170, 185))


def _draw_fight_icon(draw, x, y, color):
    draw.rectangle((x + 2, y + 5, x + 7, y + 12), fill=color)
    draw.rectangle((x + 8, y + 3, x + 13, y + 10), fill=(245, 80, 90))
    draw.line((x + 4, y + 13, x + 1, y + 20), fill=(180, 195, 210))
    draw.line((x + 11, y + 11, x + 15, y + 18), fill=(180, 195, 210))


def _draw_tennis_icon(draw, x, y, color):
    draw.ellipse((x + 1, y + 2, x + 13, y + 14), fill=(185, 240, 80), outline=color)
    draw.arc((x + 3, y + 3, x + 11, y + 13), 80, 280, fill=(245, 255, 210))
    draw.arc((x + 3, y + 3, x + 11, y + 13), -100, 100, fill=(245, 255, 210))
    draw.line((x + 11, y + 14, x + 15, y + 22), fill=(180, 195, 210))


def _draw_flag(image, href, x, y):
    logo = fetch_logo(href) if href else None
    if logo:
        image.paste(logo, (x, y), logo)
        return True
    return False


def render_event_sport_card(sport, league, title, color, fallback, icon="race"):
    from PIL import Image, ImageDraw, ImageFont

    try:
        event = _pick_event(_fetch_events(sport, league))
    except Exception:
        return render_text_webp(fallback + " ERR", (238, 80, 80))
    if not event:
        return None

    image = Image.new("RGB", (64, 32), (0, 5, 12))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(6, 17, 26))
    draw_sharp_text(image, (1, -3), title[:10], color, bold)

    if icon == "golf":
        _draw_golf_icon(draw, 1, 8, color)
    elif icon == "fight":
        _draw_fight_icon(draw, 1, 8, color)
    elif icon == "tennis":
        _draw_tennis_icon(draw, 1, 8, color)
    else:
        _draw_race_icon(draw, 1, 8, color)

    rows = _leader_rows(event, 2)
    if rows and _event_state(event).get("state") in ("in", "post"):
        y = 8
        for row in rows:
            if not _draw_flag(image, row.get("flag"), 16, y):
                draw_sharp_text(image, (16, y), (row.get("rank") or "")[:2], (180, 195, 210), font)
            text = _short_name(row.get("name"), 10)
            draw_sharp_text(image, (29, y), text, (235, 245, 255), font)
            score = str(row.get("score") or "")[:4]
            if score:
                w = draw.textbbox((0, 0), score, font=font)[2]
                draw_sharp_text(image, (63 - w, y), score, color, font)
            y += 8
        draw_sharp_text(image, (16, 24), _fmt_event_time(event), (170, 185, 200), font)
    else:
        name = event.get("shortName") or event.get("name") or title
        words = _short_name(name, 28).split()
        line1 = " ".join(words[:2]) or title
        line2 = " ".join(words[2:]) or _fmt_event_time(event)
        draw_sharp_text(image, (18, 8), _short_name(line1, 13).upper(), (235, 245, 255), font)
        draw_sharp_text(image, (18, 16), _short_name(line2, 13).upper(), (235, 245, 255), font)
        draw_sharp_text(image, (18, 24), _fmt_event_time(event), color, font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
