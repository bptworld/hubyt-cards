from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import urllib.request
from card_utils import draw_sharp_text, render_text_webp

CARD_ID = "hubitat_multi"
CARD_NAME = "Hubitat Multi"
CARD_DETAIL = "Several Hubitat devices"
CARD_OPTIONS = [
    {"key": "hubIp", "label": "Hub IP", "type": "text", "default": "192.168.1.100"},
    {"key": "appId", "label": "Maker API App #", "type": "text", "default": ""},
    {"key": "token", "label": "Access Token", "type": "text", "default": ""},
    {"key": "devices", "label": "Devices", "type": "hubitatDevices", "default": "", "maxlength": 160},
    {"key": "attribute", "label": "Attribute", "type": "text", "default": "temperature"},
]

_CACHE = {}


def _parse_devices(value):
    devices = []
    for part in str(value or "").split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            label, device_id = part.split(":", 1)
        else:
            label, device_id = part, part
        label = label.strip()[:10]
        device_id = device_id.strip()
        if device_id:
            devices.append((label or device_id, device_id))
    return devices[:4]


def _fetch_device(hub_ip, app_id, token, device_id):
    now = datetime.now(timezone.utc)
    key = f"{hub_ip}:{app_id}:{device_id}"
    cached = _CACHE.get(key)
    if cached and cached["expires"] > now:
        return cached["data"]
    url = f"http://{hub_ip}/apps/api/{app_id}/devices/{device_id}?access_token={token}"
    req = urllib.request.Request(url, headers={"User-Agent": "Pixora/0.1", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    _CACHE[key] = {"data": data, "expires": now + timedelta(seconds=30)}
    return data


def _get_attr(device, attr_name):
    for attr in device.get("attributes", []):
        if attr.get("name", "").lower() == attr_name.lower():
            return attr.get("currentValue")
    return None


def _fmt(value, attr):
    if value is None:
        return "--", (150, 160, 170)
    name = attr.lower()
    raw = str(value)
    if name in ("temperature", "humidity", "battery", "level", "power"):
        try:
            n = float(raw)
            suffix = {"temperature": "°", "humidity": "%", "battery": "%", "level": "%", "power": "W"}.get(name, "")
            return f"{n:.0f}{suffix}", (255, 195, 80) if name in ("temperature", "power") else (100, 185, 255)
        except Exception:
            pass
    return raw.upper()[:7], (235, 245, 255)


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    hub_ip = (opts.get("hubIp") or "").strip()
    app_id = (opts.get("appId") or "").strip()
    token = (opts.get("token") or "").strip()
    attr = (opts.get("attribute") or "temperature").strip()
    devices = _parse_devices(opts.get("devices"))
    if not all([hub_ip, app_id, token]) or not devices:
        return render_text_webp("SET HUB", (100, 180, 255))

    rows = []
    try:
        for label, device_id in devices:
            device = _fetch_device(hub_ip, app_id, token, device_id)
            value, color = _fmt(_get_attr(device, attr), attr)
            rows.append((label, value, color))
    except Exception:
        return render_text_webp("HUB ERR", (238, 80, 80))

    image = Image.new("RGB", (64, 32), (0, 5, 15))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("Silkscreen-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, 63, 8), fill=(0, 15, 40))
    draw_sharp_text(image, (1, -3), attr.upper()[:10], (120, 190, 255), bold)
    y = 7
    for label, value, color in rows:
        draw_sharp_text(image, (1, y), label[:7], (185, 205, 225), font)
        w = draw.textbbox((0, 0), value, font=font)[2]
        draw_sharp_text(image, (63 - w, y), value, color, font)
        y += 8

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
