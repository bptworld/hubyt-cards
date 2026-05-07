from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import urllib.request
from card_utils import draw_sharp_text, render_text_webp

CARD_ID = "market_indexes"
CARD_NAME = "Market Indexes"
CARD_DETAIL = "Dow, S&P, Nasdaq"
CARD_OPTIONS = [
    {"key": "indexes", "label": "Indexes", "type": "text", "default": "^DJI,^GSPC,^IXIC", "maxlength": 32},
]

_CACHE = {}


def _fetch_one(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    meta = raw["chart"]["result"][0]["meta"]
    price = meta.get("regularMarketPrice") or 0
    prev = meta.get("previousClose") or meta.get("chartPreviousClose") or price
    pct = ((price - prev) / prev * 100) if prev else 0
    return {"symbol": meta.get("symbol", symbol), "price": price, "pct": pct}


def _fetch(symbols):
    symbols = [s.strip().upper() for s in symbols if s.strip()][:3]
    key = ",".join(symbols)
    now = datetime.now(timezone.utc)
    cached = _CACHE.get(key)
    if cached and cached["expires"] > now:
        return cached["data"]
    data = [_fetch_one(symbol) for symbol in symbols]
    _CACHE[key] = {"data": data, "expires": now + timedelta(seconds=60)}
    return data


def _label(symbol):
    return {"^DJI": "DOW", "^GSPC": "S&P", "^IXIC": "NAS", "^RUT": "RUT"}.get(symbol, symbol.replace("^", "")[:3])


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    symbols = (opts.get("indexes") or "^DJI,^GSPC,^IXIC").split(",")[:3]
    try:
        quotes = _fetch(symbols)
    except Exception:
        return render_text_webp("MKT ERR", (238, 80, 80))

    if not quotes:
        return render_text_webp("NO DATA", (160, 160, 160))

    image = Image.new("RGB", (64, 32), (0, 5, 15))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(6, 18, 30))
    draw_sharp_text(image, (1, -3), "MARKETS", (100, 190, 255), bold)

    y = 7
    for q in quotes[:3]:
        symbol = q.get("symbol", "")
        price = q.get("price") or 0
        pct = q.get("pct") or 0
        color = (80, 220, 120) if pct >= 0 else (238, 80, 80)
        row = f"{_label(symbol):3} {price:>5.0f}"
        draw_sharp_text(image, (1, y), row[:10], (235, 245, 255), font)
        pct_s = f"{pct:+.1f}%"
        w = draw.textbbox((0, 0), pct_s, font=font)[2]
        draw_sharp_text(image, (63 - w, y), pct_s, color, font)
        y += 8

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
