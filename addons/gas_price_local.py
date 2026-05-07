from datetime import datetime, timedelta, timezone
from io import BytesIO
import re
import urllib.request
from card_utils import draw_sharp_text, render_text_webp

CARD_ID = "gas_price_local"
CARD_NAME = "Gas Price Local"
CARD_DETAIL = "AAA state gas average"
CARD_OPTIONS = [
    {"key": "state", "label": "State", "type": "text", "default": "MA", "maxlength": 2},
]

_CACHE = {}
_STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota",
    "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin",
    "WY": "Wyoming",
}


def _fetch(state):
    state = re.sub(r"[^A-Za-z]", "", state or "MA").upper()[:2] or "MA"
    now = datetime.now(timezone.utc)
    cached = _CACHE.get(state)
    if cached and cached["expires"] > now:
        return cached["data"]
    url = f"https://gasprices.aaa.com/?state={state}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://gasprices.aaa.com/",
        "Connection": "close",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    state_name = _STATE_NAMES.get(state, state)
    state_match = re.search(rf"Today's AAA\s+{re.escape(state_name)} Avg\.\s+\$([0-9.]+)", html)
    national_match = re.search(r"Today.s AAA National Average\s+\$([0-9.]+)", html)
    date_match = re.search(r"Price as of\s+([0-9/]+)", html)
    data = {
        "state": state,
        "state_name": state_name,
        "price": float(state_match.group(1)) if state_match else None,
        "national": float(national_match.group(1)) if national_match else None,
        "date": date_match.group(1) if date_match else "",
    }
    _CACHE[state] = {"data": data, "expires": now + timedelta(hours=6)}
    return data


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    try:
        data = _fetch(opts.get("state") or "MA")
    except Exception:
        return render_text_webp("GAS ERR", (238, 80, 80))
    if data["price"] is None:
        return render_text_webp("NO GAS", (160, 160, 160))

    diff = data["price"] - (data["national"] or data["price"])
    color = (238, 80, 80) if diff > 0 else (80, 220, 120)
    image = Image.new("RGB", (64, 32), (0, 5, 12))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
        big = ImageFont.truetype("Silkscreen-Bold.ttf", 16)
    except Exception:
        font = bold = big = ImageFont.load_default()

    draw.rectangle((2, 6, 14, 26), outline=(90, 170, 255), fill=(8, 18, 30))
    draw.rectangle((5, 9, 11, 13), fill=(90, 170, 255))
    draw.line((14, 10, 19, 14, 19, 22), fill=(90, 170, 255))
    draw_sharp_text(image, (22, -3), f"GAS {data['state']}", (255, 220, 80), bold)
    price = f"${data['price']:.2f}"
    draw_sharp_text(image, (22, 7), price, (235, 245, 255), big)
    tag = f"{diff:+.2f} vs US"
    draw_sharp_text(image, (22, 22), tag[:10], color, font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
