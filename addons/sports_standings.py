from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import urllib.request

from card_utils import draw_sharp_text, render_text_webp

CARD_ID = "sports_standings"
CARD_NAME = "Sports Standings"
CARD_DETAIL = "Top teams from ESPN standings"
CARD_OPTIONS = [
    {
        "key": "league",
        "label": "League",
        "type": "select",
        "default": "mlb",
        "choices": [
            {"value": "mlb", "label": "MLB"},
            {"value": "nba", "label": "NBA"},
            {"value": "nhl", "label": "NHL"},
            {"value": "nfl", "label": "NFL"},
            {"value": "wnba", "label": "WNBA"},
        ],
    },
    {
        "key": "group",
        "label": "Group",
        "type": "select",
        "default": "auto",
        "choices": [
            {"value": "auto", "label": "Default"},
            {"value": "east", "label": "East / AL"},
            {"value": "west", "label": "West / NL"},
        ],
    },
]

LEAGUES = {
    "mlb": ("MLB", "https://site.web.api.espn.com/apis/v2/sports/baseball/mlb/standings", (117, 231, 214)),
    "nba": ("NBA", "https://site.web.api.espn.com/apis/v2/sports/basketball/nba/standings", (245, 150, 65)),
    "nhl": ("NHL", "https://site.web.api.espn.com/apis/v2/sports/hockey/nhl/standings", (80, 220, 255)),
    "nfl": ("NFL", "https://site.web.api.espn.com/apis/v2/sports/football/nfl/standings", (80, 150, 255)),
    "wnba": ("WNBA", "https://site.web.api.espn.com/apis/v2/sports/basketball/wnba/standings", (255, 170, 210)),
}
_CACHE = {}


def _fetch(url):
    now = datetime.now(timezone.utc)
    cached = _CACHE.get(url)
    if cached and cached["expires"] > now:
        return cached["data"]
    request = urllib.request.Request(url, headers={"User-Agent": "Pixora/0.1", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    _CACHE[url] = {"data": data, "expires": now + timedelta(seconds=1800)}
    return data


def _stat(entry, *names):
    names = {n.lower() for n in names}
    for stat in entry.get("stats", []):
        if str(stat.get("type", "")).lower() in names or str(stat.get("abbreviation", "")).lower() in names:
            return stat.get("displayValue", "")
    return ""


def _pick_child(children, group):
    if not children:
        return None
    if group == "auto":
        return children[0]
    wanted = {
        "east": ("east", "american", "al"),
        "west": ("west", "national", "nl"),
    }.get(group, ())
    for child in children:
        text = " ".join(str(child.get(k, "")) for k in ("name", "abbreviation", "shortName")).lower()
        if any(term in text for term in wanted):
            return child
    return children[0]


def _standings(opts):
    league_key = str((opts or {}).get("league", "mlb")).lower()
    title, url, color = LEAGUES.get(league_key, LEAGUES["mlb"])
    data = _fetch(url)
    child = _pick_child(data.get("children", []), str((opts or {}).get("group", "auto")).lower())
    entries = ((child or {}).get("standings") or {}).get("entries", [])
    rows = []
    for entry in entries[:3]:
        team = entry.get("team", {})
        abbr = team.get("abbreviation") or team.get("shortDisplayName") or "?"
        wins = _stat(entry, "wins", "w")
        losses = _stat(entry, "losses", "l")
        ties = _stat(entry, "ties", "t")
        gb = _stat(entry, "gamesbehind", "gb")
        pts = _stat(entry, "points", "pts")
        record = f"{wins}-{losses}" if wins or losses else pts
        if ties and ties != "0":
            record += f"-{ties}"
        right = "GB -" if gb in ("", "-") else f"GB {gb}"
        if league_key == "nhl" and pts:
            right = f"PTS {pts}"
        rows.append((abbr[:4].upper(), record[:7], right[:7]))
    return title, color, rows


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    try:
        title, color, rows = _standings(options or {})
    except Exception:
        return render_text_webp("STAND ERR", (238, 80, 80))
    if not rows:
        return render_text_webp("NO STAND", (160, 160, 160))

    image = Image.new("RGB", (64, 32), (0, 5, 12))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(6, 18, 26))
    draw_sharp_text(image, (1, -3), title, color, bold)
    draw_sharp_text(image, (25, -3), "STAND", (150, 170, 185), font)
    y = 7
    for idx, (abbr, record, right) in enumerate(rows, start=1):
        draw_sharp_text(image, (1, y), str(idx), color, font)
        draw_sharp_text(image, (8, y), abbr, (245, 250, 255), bold)
        draw_sharp_text(image, (28, y), record, (190, 205, 218), font)
        width = draw.textbbox((0, 0), right, font=font)[2]
        draw_sharp_text(image, (63 - width, y), right, (145, 165, 182), font)
        y += 8

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
