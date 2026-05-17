from io import BytesIO

from card_utils import draw_sharp_text

CARD_ID = "custom_text"
CARD_NAME = "Custom Text"
CARD_DETAIL = "Two-line custom message"
CARD_OPTIONS = [
    {"key": "topLine", "label": "Top Line", "type": "text", "default": "Welcome to", "maxlength": 40},
    {"key": "bottomLine", "label": "Bottom Line", "type": "text", "default": "Bryan's Man Cave", "maxlength": 60},
]


def _font(size, bold=False):
    from PIL import ImageFont

    names = ["Silkscreen-Bold.ttf", "Silkscreen-Regular.ttf"] if bold else ["Silkscreen-Regular.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _fit_font(draw, text, max_width, start_size, min_size, bold=False):
    text = str(text or "").strip()
    for size in range(start_size, min_size - 1, -1):
        font = _font(size, bold=bold)
        if _text_width(draw, text, font) <= max_width:
            return font
    return _font(min_size, bold=bold)


def _wrap_words(draw, text, font, max_width, max_lines=2):
    words = str(text or "").strip().split()
    if not words:
        return [""]
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip() if current else word
        if _text_width(draw, test, font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) <= max_lines:
        return lines
    kept = lines[:max_lines]
    while kept[-1] and _text_width(draw, kept[-1] + "...", font) > max_width:
        kept[-1] = kept[-1][:-1].rstrip()
    kept[-1] = (kept[-1] + "...").strip()
    return kept


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    top = str(opts.get("topLine") or "Welcome to").strip()
    bottom = str(opts.get("bottomLine") or "Bryan's Man Cave").strip()

    image = Image.new("RGB", (width, 32), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    top_font = _fit_font(draw, top, width - 4, 8 if width == 128 else 7, 6, bold=False)
    bottom_font = _fit_font(draw, bottom, width - 4, 14 if width == 128 else 11, 8, bold=True)
    top_color = (70, 230, 255)
    bottom_color = (255, 255, 255)

    top_w = _text_width(draw, top, top_font)
    draw_sharp_text(image, ((width - top_w) // 2, 1), top, top_color, top_font)

    if _text_width(draw, bottom, bottom_font) <= width - 4:
        bottom_w = _text_width(draw, bottom, bottom_font)
        draw_sharp_text(image, ((width - bottom_w) // 2, 14), bottom, bottom_color, bottom_font)
    else:
        wrap_font = _font(8, bold=True)
        lines = _wrap_words(draw, bottom, wrap_font, width - 4, max_lines=2)
        y = 13
        for line in lines:
            line_w = _text_width(draw, line, wrap_font)
            draw_sharp_text(image, ((width - line_w) // 2, y), line, bottom_color, wrap_font)
            y += 9

    out = BytesIO()
    image.save(out, "WEBP", lossless=True, quality=100)
    return out.getvalue()
