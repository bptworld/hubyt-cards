from io import BytesIO
import math

CARD_ID = "pong_loop"
CARD_NAME = "Pong Loop"
CARD_DETAIL = "Tiny paddles and ball"
CARD_OPTIONS = [
    {"key": "speed", "label": "Speed", "type": "text", "default": "normal", "maxlength": 8},
]


def _duration(value):
    speed = str(value or "normal").strip().lower()
    if speed == "fast":
        return 55
    if speed == "slow":
        return 135
    return 85


def render(options=None):
    from PIL import Image, ImageDraw, ImageFont

    opts = options or {}
    width = 128 if opts.get("_target") == "matrixportal-s3-128x32" else 64
    frames = []
    try:
        font = ImageFont.truetype("Silkscreen-Regular.ttf", 8)
    except Exception:
        font = ImageFont.load_default()

    dwell_ms = max(3000, min(60000, int(opts.get("_dwell", 10) or 10) * 1000))
    base_duration = _duration(opts.get("speed"))
    frame_count = max(24, min(72, int(round(dwell_ms / base_duration))))
    frame_duration = max(45, int(round(dwell_ms / frame_count)))
    left_wall = 8
    right_wall = width - 11
    travel = right_wall - left_wall
    for frame in range(frame_count):
        t = frame / frame_count
        phase = t * 2.0
        if phase < 1.0:
            x = left_wall + int(phase * travel)
        else:
            x = right_wall - int((phase - 1.0) * travel)
        y = 7 + int((math.sin(t * math.tau * 2.0) + 1.0) * 7.5)
        image = Image.new("RGB", (width, 32), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        mid = width // 2 - 1
        draw.line((mid, 1, mid, 30), fill=(40, 40, 50))
        for yy in range(3, 30, 6):
            draw.point((mid, yy), fill=(90, 90, 105))
        left_y = max(3, min(22, y - 4))
        right_y = max(3, min(22, 28 - y))
        draw.rectangle((3, left_y, 5, left_y + 8), fill=(220, 240, 255))
        draw.rectangle((width - 6, right_y, width - 4, right_y + 8), fill=(220, 240, 255))
        draw.rectangle((x, y, x + 2, y + 2), fill=(255, 255, 255))
        draw.text((width // 2 - 14, -4), "3", fill=(90, 200, 255), font=font)
        draw.text((width // 2 + 9, -4), "2", fill=(255, 190, 90), font=font)
        frames.append(image)

    out = BytesIO()
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:],
                   duration=frame_duration, loop=1, lossless=True, quality=100)
    return out.getvalue()
