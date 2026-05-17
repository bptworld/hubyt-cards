from io import BytesIO

from card_utils import draw_sharp_text, fetch_json_request, render_text_webp

CARD_ID = "air_quality"
CARD_NAME = "Air Quality"
CARD_DETAIL = "AQI, pollen, and UV by ZIP"
CARD_OPTIONS = [
    {"key": "zipCode", "label": "ZIP Code", "type": "text", "default": "02134", "maxlength": 5, "inputmode": "numeric"},
]


def _zip_latlon(zip_code):
    loc = fetch_json_request(f"https://api.zippopotam.us/us/{zip_code}", seconds=86400)
    p = loc["places"][0]
    return float(p["latitude"]), float(p["longitude"])


def _environment(zip_code):
    lat, lon = _zip_latlon(zip_code)
    aq_url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat:.4f}&longitude={lon:.4f}"
        "&current=us_aqi,grass_pollen,alder_pollen,birch_pollen,mugwort_pollen,olive_pollen,ragweed_pollen"
        "&timezone=auto"
    )
    uv_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat:.4f}&longitude={lon:.4f}"
        "&current=uv_index&timezone=auto"
    )
    aq = fetch_json_request(aq_url, seconds=1800).get("current", {})
    uv = fetch_json_request(uv_url, seconds=1800).get("current", {})
    pollen_values = [
        aq.get("grass_pollen"),
        aq.get("alder_pollen"),
        aq.get("birch_pollen"),
        aq.get("mugwort_pollen"),
        aq.get("olive_pollen"),
        aq.get("ragweed_pollen"),
    ]
    pollen = max([float(v) for v in pollen_values if v is not None] or [0])
    return {
        "aqi": aq.get("us_aqi"),
        "aqiSource": "weather.gov",
        "pollen": pollen,
        "uv": uv.get("uv_index"),
    }


def _aqi_level(aqi):
    if aqi is None:
        return "--", (155, 165, 175)
    aqi = int(round(float(aqi)))
    if 1 <= aqi <= 5:
        colors = {
            1: (80, 225, 110),
            2: (245, 215, 70),
            3: (255, 150, 60),
            4: (245, 90, 105),
            5: (190, 80, 190),
        }
        return str(aqi), colors.get(aqi, (155, 165, 175))
    if aqi <= 50:
        return str(aqi), (80, 225, 110)
    if aqi <= 100:
        return str(aqi), (245, 215, 70)
    if aqi <= 150:
        return str(aqi), (255, 150, 60)
    return str(aqi), (245, 70, 90)


def _pollen_level(value):
    if value <= 0:
        return "LOW", (80, 225, 110)
    if value < 20:
        return "LOW", (80, 225, 110)
    if value < 80:
        return "MED", (245, 215, 70)
    return "HIGH", (245, 80, 100)


def _uv_level(value):
    if value is None:
        return "--", (155, 165, 175)
    uv = float(value)
    text = str(int(round(uv)))
    if uv < 3:
        return text, (80, 225, 110)
    if uv < 6:
        return text, (245, 215, 70)
    if uv < 8:
        return text, (255, 150, 60)
    return text, (245, 70, 90)


def _center_text(image, text, x1, x2, y, color, font):
    from PIL import ImageDraw

    draw = ImageDraw.Draw(image)
    w = draw.textbbox((0, 0), text, font=font)[2]
    draw_sharp_text(image, (x1 + ((x2 - x1 + 1) - w) // 2, y), text, color, font)


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    zip_code = ((options or {}).get("zipCode") or "").strip()
    if len(zip_code) != 5:
        return render_text_webp("SET ZIP", (100, 180, 255))

    try:
        env = _environment(zip_code)
    except Exception:
        return render_text_webp("AIR ERR", (238, 80, 80))

    is_wide = (options or {}).get("_target") == "matrixportal-s3-128x32"
    width = 128 if is_wide else 64
    image = Image.new("RGB", (width, 32), (0, 5, 10))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
        bold = ImageFont.truetype("PixelifySans-Bold.ttf", 8)
    except Exception:
        font = bold = ImageFont.load_default()

    draw.rectangle((0, 0, width - 1, 8), fill=(5, 18, 23))
    _center_text(image, "AIR QUALITY" if is_wide else "AIR", 0, width - 1, -3, (125, 220, 255), bold)

    cols = [(2, 39), (44, 83), (88, 125)] if is_wide else [(0, 20), (22, 42), (44, 63)]
    labels = ["AQI", "POL", "UV"]
    aqi_text, aqi_color = _aqi_level(env.get("aqi"))
    pollen_text, pollen_color = _pollen_level(env.get("pollen", 0))
    uv_text, uv_color = _uv_level(env.get("uv"))
    values = [(aqi_text, aqi_color), (pollen_text, pollen_color), (uv_text, uv_color)]

    for x in ((42, 86) if is_wide else (21, 43)):
        draw.line((x, 10, x, 31), fill=(22, 34, 42))
    for (x1, x2), label, (value, color) in zip(cols, labels, values):
        _center_text(image, label, x1, x2, 9, (150, 170, 185), font)
        _center_text(image, value, x1, x2, 20, color, bold)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()

