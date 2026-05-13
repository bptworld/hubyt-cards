from datetime import datetime, timedelta, timezone
from html import unescape
from io import BytesIO
import re
import urllib.request

from card_utils import draw_sharp_text, render_text_webp

CARD_ID = "megabucks"
CARD_NAME = "Megabucks"
CARD_DETAIL = "Latest MA Megabucks draw"
CARD_OPTIONS = [
    {"key": "manualNumbers", "label": "Manual Numbers", "type": "text", "default": "", "maxlength": 32},
    {"key": "manualDate", "label": "Manual Draw Date", "type": "text", "default": "", "maxlength": 18},
]

URL = "https://www.lottery.net/massachusetts/megabucks/numbers"
CACHE = {}


def _fetch_html(url, seconds=21600):
    now = datetime.now(timezone.utc)
    if CACHE.get("expires", now) > now and CACHE.get("html"):
        return CACHE["html"]
    request = urllib.request.Request(url, headers={"User-Agent": "Hubyt/0.1"})
    with urllib.request.urlopen(request, timeout=10) as response:
        html = response.read().decode("utf-8", errors="ignore")
    CACHE["html"] = html
    CACHE["expires"] = now + timedelta(seconds=seconds)
    return html


def _clean_html(text):
    text = re.sub(r"<sup>.*?</sup>", "", text, flags=re.I | re.S)
    text = re.sub(r"<.*?>", " ", text, flags=re.S)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _parse_manual(opts):
    raw = (opts.get("manualNumbers") or "").strip()
    nums = re.findall(r"\d+", raw)
    if len(nums) >= 6:
        return {
            "date": (opts.get("manualDate") or "MANUAL").strip()[:18],
            "numbers": nums[:6],
        }
    return None


def _latest():
    html = _fetch_html(URL)
    marker = '<ul class="massachusetts results megabucks">'
    idx = html.find(marker)
    block = html[idx - 900: idx + 1000] if idx >= 0 else html
    date_match = re.search(r'<div class="dateSmall">\s*(.*?)\s*</div>', block, re.I | re.S)
    date_text = _clean_html(date_match.group(1)) if date_match else "LATEST"
    date_text = re.sub(r"\s*\(Draw:.*?\)", "", date_text, flags=re.I).strip()
    numbers = re.findall(r'<li class="ball">(\d+)</li>', block, re.I)
    if len(numbers) < 6:
        raise ValueError("Megabucks numbers not found")
    return {"date": date_text, "numbers": numbers[:6]}


def _center(image, text, y, color, font, x1=0, x2=63):
    from PIL import ImageDraw

    draw = ImageDraw.Draw(image)
    width = draw.textbbox((0, 0), str(text), font=font)[2]
    draw_sharp_text(image, (x1 + ((x2 - x1 + 1) - width) // 2, y), str(text), color, font)


def _draw(data):
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (64, 32), (0, 5, 10))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(5, 24, 20))
    _center(image, "MEGABUCKS", -3, (70, 230, 170), bold)
    nums = data["numbers"]
    _center(image, " ".join(nums[:3]), 8, (245, 250, 255), bold)
    _center(image, " ".join(nums[3:6]), 17, (245, 250, 255), bold)
    _center(image, (data.get("date") or "")[:13].upper(), 25, (120, 190, 170), font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()


def render(options=None):
    opts = options or {}
    try:
        return _draw(_parse_manual(opts) or _latest())
    except Exception:
        manual = _parse_manual(opts)
        if manual:
            return _draw(manual)
        return render_text_webp("BUCKS ERR", (70, 230, 170))
