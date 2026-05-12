from datetime import datetime, timedelta, timezone
from io import BytesIO
import re
import urllib.request
import xml.etree.ElementTree as ET
from card_utils import draw_sharp_text, render_text_webp

CARD_ID = "airport_delays"
CARD_NAME = "Airport Delays"
CARD_DETAIL = "FAA delay status"
CARD_OPTIONS = [
    {"key": "airports", "label": "Airports", "type": "text", "default": "BOS", "maxlength": 32},
]

_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "events": []}
_FAA_URL = "https://nasstatus.faa.gov/api/airport-status-information"


def _text(node, path, default=""):
    found = node.find(path)
    return (found.text or "").strip() if found is not None else default


def _clean_reason(reason):
    reason = re.sub(r"^(WX|VOL|RWY|TM Initiatives):", "", reason or "", flags=re.I)
    reason = reason.replace(":", " ").replace("_", " ")
    return re.sub(r"\s+", " ", reason).strip() or "Delay"


def _delay_events():
    now = datetime.now(timezone.utc)
    if _CACHE["expires"] > now:
        return _CACHE["events"]

    req = urllib.request.Request(_FAA_URL, headers={"User-Agent": "Hubyt/0.1"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        root = ET.fromstring(resp.read())

    events = []
    for item in root.findall(".//Ground_Delay"):
        events.append({
            "airport": _text(item, "ARPT").upper(),
            "kind": "GDP",
            "delay": _text(item, "Avg") or _text(item, "Max"),
            "reason": _clean_reason(_text(item, "Reason")),
        })
    for item in root.findall(".//Arrival_Departure_Delay_List/Delay"):
        detail = item.find("Arrival_Departure")
        dtype = detail.attrib.get("Type", "Delay")[:3].upper() if detail is not None else "DLY"
        delay = ""
        if detail is not None:
            delay = (_text(detail, "Min") + "-" + _text(detail, "Max")).strip("-")
        events.append({
            "airport": _text(item, "ARPT").upper(),
            "kind": dtype,
            "delay": delay,
            "reason": _clean_reason(_text(item, "Reason")),
        })
    for item in root.findall(".//Airport_Closure_List/Airport"):
        events.append({
            "airport": _text(item, "ARPT").upper(),
            "kind": "CLOSED",
            "delay": _text(item, "Reopen"),
            "reason": _clean_reason(_text(item, "Reason")),
        })

    _CACHE["events"] = [e for e in events if e["airport"]]
    _CACHE["expires"] = now + timedelta(seconds=120)
    return _CACHE["events"]


def _airport_codes(value):
    codes = re.findall(r"[A-Za-z]{3,4}", value or "")
    return [c.upper()[:4] for c in codes][:6]


def _short_delay(delay):
    d = (delay or "").lower()
    m = re.search(r"(\d+)\s*hour", d)
    mins = re.search(r"(\d+)\s*minute", d)
    if m and mins:
        return f"{m.group(1)}h{mins.group(1)}m"
    if m:
        return f"{m.group(1)}h"
    if mins:
        return f"{mins.group(1)}m"
    return (delay or "")[:9]


def _render_ok_image(code):
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (64, 32), (0, 5, 12))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(12, 24, 24))
    draw_sharp_text(image, (1, -4), "AIRPORT", (100, 190, 255), bold)
    draw_sharp_text(image, (1, 6), (code or "FAA")[:4], (255, 255, 255), bold)
    draw_sharp_text(image, (1, 15), "NO DELAYS", (100, 220, 140), font)
    draw_sharp_text(image, (1, 23), "FAA STATUS", (150, 170, 185), font)
    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    codes = _airport_codes(opts.get("airports"))
    try:
        events = _delay_events()
    except Exception:
        return render_text_webp("FAA ERR", (238, 80, 80))

    if codes:
        matches = [e for e in events if e["airport"] in codes]
        if not matches:
            return _render_ok_image(codes[0])
    else:
        matches = events[:3]
        if not matches:
            return _render_ok_image("FAA")

    image = Image.new("RGB", (64, 32), (2, 8, 16))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(24, 30, 42))
    draw_sharp_text(image, (1, -3), "AIR DELAY", (255, 190, 80), bold)
    y = 8
    for event in matches[:3]:
        draw_sharp_text(image, (1, y), event["airport"][:4], (100, 190, 255), bold)
        draw_sharp_text(image, (24, y), _short_delay(event["delay"])[:8], (255, 235, 145), font)
        y += 8
    if matches:
        draw_sharp_text(image, (1, 24), matches[0]["reason"][:12].upper(), (180, 195, 210), font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
