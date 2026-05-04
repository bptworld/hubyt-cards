from card_utils import draw_sharp_text, draw_mini_weather_icon, weather_for_zip

CARD_ID = "clock"
CARD_NAME = "Clock"
CARD_DETAIL = "Time plus local weather"
CARD_OPTIONS = [
    {"key": "zipCode", "label": "ZIP", "type": "text", "default": "02134", "maxlength": 5, "inputmode": "numeric"}
]


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from datetime import datetime

    image = Image.new("RGB", (64, 32), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    try:
        time_font = ImageFont.truetype("Silkscreen-Bold.ttf", 16)
        small_font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
    except Exception:
        time_font = small_font = ImageFont.load_default()

    text = datetime.now().strftime("%I:%M").lstrip("0")
    tb = draw.textbbox((0, 0), text, font=time_font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]

    zip_code = (options or {}).get("zipCode", "")
    if zip_code:
        try:
            weather = weather_for_zip(zip_code)
            temp = f"{weather['temperature']}{weather['temperatureUnit']}"
            tempb = draw.textbbox((0, 0), temp[:6], font=small_font)
            temp_w, temp_h = tempb[2] - tempb[0], tempb[3] - tempb[1]
            icon_h, icon_w = 11, 13
            draw_sharp_text(image, ((64 - tw) // 2, -4), text, (20, 149, 255), time_font)
            row_w = icon_w + 5 + temp_w
            row_x = (64 - row_w) // 2
            row_y = 32 - icon_h - 4
            draw_mini_weather_icon(draw, weather["icon"], row_x + icon_w // 2, row_y)
            draw_sharp_text(image, (row_x + icon_w + 5, row_y + (icon_h - temp_h) // 2 - 3), temp[:6], (235, 247, 255), small_font)
        except Exception:
            draw_sharp_text(image, ((64 - tw) // 2, -4), text, (20, 149, 255), time_font)
    else:
        draw_sharp_text(image, ((64 - tw) // 2, -4), text, (20, 149, 255), time_font)

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
