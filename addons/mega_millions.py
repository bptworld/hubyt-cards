from datetime import datetime, timedelta, timezone
from html import unescape
from io import BytesIO
import re
import urllib.request

from card_utils import draw_sharp_text, render_text_webp

CARD_ID = "mega_millions"
CARD_NAME = "Mega Millions"
CARD_DETAIL = "Latest Mega Millions draw"
CARD_OPTIONS = []

URL = "https://www.lottery.net/mega-millions/numbers"
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


def _latest():
    html = _fetch_html(URL)
    block_match = re.search(r'<div class="[^"]*latestResults[^"]*".*?</div>\s*</div>\s*</div>', html, re.I | re.S)
    block = block_match.group(0) if block_match else html
    date_match = re.search(r'<div class="latest"[^>]*>(.*?)</div>', block, re.I | re.S)
    date_text = _clean_html(date_match.group(1)) if date_match else "LATEST"
    numbers = re.findall(r'<li class="ball">(\d+)</li>', block, re.I)
    special_match = re.search(r'<li class="mega-ball">(\d+)</li>', block, re.I)
    jackpot_match = re.search(r'Jackpot for this draw:\s*<br>\s*<span>(.*?)</span>', block, re.I | re.S)
    if len(numbers) < 5 or not special_match:
        raise ValueError("Mega Millions numbers not found")
    return {
        "date": date_text,
        "numbers": numbers[:5],
        "special": special_match.group(1),
        "jackpot": _clean_html(jackpot_match.group(1)) if jackpot_match else "",
    }


def _center(image, text, y, color, font, x1=0, x2=63):
    from PIL import ImageDraw

    draw = ImageDraw.Draw(image)
    width = draw.textbbox((0, 0), str(text), font=font)[2]
    draw_sharp_text(image, (x1 + ((x2 - x1 + 1) - width) // 2, y), str(text), color, font)


def _draw(data):
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (64, 32), (0, 4, 10))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(23, 9, 38))
    _center(image, "MEGA MILL", -3, (255, 215, 70), bold)
    nums = data["numbers"]
    _center(image, " ".join(nums[:3]), 8, (245, 250, 255), bold)
    _center(image, f"{nums[3]} {nums[4]} +{data['special']}", 17, (255, 220, 80), bold)
    bottom = (data.get("jackpot") or data.get("date") or "")[:12].upper()
    _center(image, bottom, 25, (175, 150, 205), font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()


def render(options=None):
    try:
        return _draw(_latest())
    except Exception:
        return render_text_webp("MEGA ERR", (255, 210, 80))
