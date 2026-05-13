from io import BytesIO
import urllib.parse

from card_utils import draw_sharp_text, fetch_json_with_headers, render_text_webp

CARD_ID = "lastfm_now_playing"
CARD_NAME = "Last.fm Now Playing"
CARD_DETAIL = "Current or recent track"
CARD_OPTIONS = [
    {"key": "username", "label": "Last.fm Username", "type": "text", "default": "", "maxlength": 40},
    {"key": "apiKey", "label": "Last.fm API Key", "type": "password", "default": ""},
]


def _track(username, api_key):
    qs = urllib.parse.urlencode({
        "method": "user.getrecenttracks",
        "user": username,
        "api_key": api_key,
        "format": "json",
        "limit": "1",
    })
    data = fetch_json_with_headers(f"https://ws.audioscrobbler.com/2.0/?{qs}", seconds=60, cache_key=f"lastfm:{username}")
    tracks = data.get("recenttracks", {}).get("track") or []
    if not tracks:
        return None
    t = tracks[0]
    artist = (t.get("artist") or {}).get("#text") or ""
    title = t.get("name") or ""
    now = (t.get("@attr") or {}).get("nowplaying") == "true"
    return {"artist": artist, "title": title, "now": now}


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    username = (opts.get("username") or "").strip()
    api_key = (opts.get("apiKey") or "").strip()
    if not username or not api_key:
        return render_text_webp("SET FM", (100, 180, 255))
    try:
        track = _track(username, api_key)
    except Exception:
        return render_text_webp("FM ERR", (238, 80, 80))
    if not track:
        return render_text_webp("NO MUSIC", (160, 170, 180))

    image = Image.new("RGB", (64, 32), (0, 5, 12))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()
    draw.rectangle((0, 0, 63, 8), fill=(30, 5, 10))
    draw_sharp_text(image, (1, -3), "LAST.FM", (220, 35, 50), bold)
    draw.ellipse((2, 12, 13, 23), outline=(220, 35, 50), width=2)
    draw.polygon([(12, 16), (18, 12), (18, 24)], fill=(220, 35, 50))
    draw_sharp_text(image, (23, 8), (track["title"] or "TRACK")[:9].upper(), (245, 250, 255), font)
    draw_sharp_text(image, (23, 17), (track["artist"] or "ARTIST")[:9].upper(), (150, 170, 185), font)
    if track["now"]:
        draw_sharp_text(image, (47, 24), "LIVE", (80, 220, 120), font)
    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
