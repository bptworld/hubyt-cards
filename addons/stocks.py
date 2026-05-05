from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import urllib.request
from card_utils import draw_sharp_text, render_text_webp

CARD_ID = "stocks"
CARD_NAME = "Stock Ticker"
CARD_DETAIL = "Live price and change"
CARD_OPTIONS = [
    {"key": "symbol", "label": "Ticker (e.g. AAPL, BTC-USD)", "type": "text",
     "default": "AAPL", "maxlength": 12},
]

_CACHE = {}


def _fetch_quote(symbol):
    now = datetime.now(timezone.utc)
    cached = _CACHE.get(symbol)
    if cached and cached["expires"] > now:
        return cached["data"]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    meta  = raw["chart"]["result"][0]["meta"]
    price = meta.get("regularMarketPrice", 0)
    prev  = meta.get("previousClose") or meta.get("chartPreviousClose") or price
    change     = price - prev
    change_pct = (change / prev) if prev else 0
    quote = {
        "symbol":     meta.get("symbol", symbol),
        "name":       "".join(c for c in meta.get("shortName", symbol) if ord(c) < 128),
        "price":      price,
        "change":     change,
        "change_pct": change_pct,
        "state":      meta.get("marketState", "CLOSED"),
    }
    _CACHE[symbol] = {"data": quote, "expires": now + timedelta(seconds=60)}
    return quote


def _fmt_price(p):
    if p >= 10000: return f"${p:,.0f}"
    if p >= 1000:  return f"${p:,.1f}"
    if p >= 1:     return f"${p:.2f}"
    return f"${p:.4f}"


def _fmt_change(c):
    sign = "+" if c >= 0 else ""
    return f"{sign}{c:.2f}" if abs(c) >= 0.01 else f"{sign}{c:.4f}"


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont
    opts   = options or {}
    symbol = (opts.get("symbol") or "AAPL").strip().upper()

    try:
        q = _fetch_quote(symbol)
    except Exception as e:
        return render_text_webp(str(e)[:10] or "ERR", (238, 80, 80))

    up           = q["change"] >= 0
    change_color = (80, 220, 120) if up else (238, 80, 80)
    price_str    = _fmt_price(q["price"])
    chg_str      = _fmt_change(q["change"])
    pct_str      = f"{'+'if up else ''}{q['change_pct']*100:.2f}%"
    name_str     = q["name"][:14]

    image = Image.new("RGB", (64, 32), (0, 5, 15))
    draw  = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    # Row 1: ticker left, market state right (only when not regular hours)
    draw_sharp_text(image, (1, -3), q["symbol"][:6], (255, 255, 255), bold)
    state = q["state"]
    if state != "REGULAR":
        tag = {"PRE": "PRE", "POST": "AH", "CLOSED": "CLO"}.get(state, state[:3])
        tw = draw.textbbox((0, 0), tag, font=font)[2]
        draw_sharp_text(image, (63 - tw, -3), tag, (180, 140, 60), font)

    # Row 2: price centered
    pw = draw.textbbox((0, 0), price_str, font=bold)[2]
    draw_sharp_text(image, ((64 - pw) // 2, 5), price_str, (255, 255, 255), bold)

    # Row 3: dollar change left, percent right
    draw_sharp_text(image, (1, 14), chg_str, change_color, font)
    pw2 = draw.textbbox((0, 0), pct_str, font=font)[2]
    draw_sharp_text(image, (63 - pw2, 14), pct_str, change_color, font)

    # Row 4: company name centered, muted
    nw = draw.textbbox((0, 0), name_str, font=font)[2]
    draw_sharp_text(image, ((64 - nw) // 2, 22), name_str, (90, 110, 135), font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
