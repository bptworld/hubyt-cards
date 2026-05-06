from io import BytesIO

CARD_ID = "pacman"
CARD_NAME = "Pac-Man Chase"
CARD_DETAIL = "Pac-Man chasing ghosts"
CARD_OPTIONS = [
    {"key": "speed", "label": "Speed", "type": "text", "default": "normal", "maxlength": 8},
    {"key": "dots", "label": "Dots", "type": "text", "default": "on", "maxlength": 3},
]


def _on(value):
    return str(value or "").strip().lower() not in ("off", "no", "false", "0")


def _speed_ms(value):
    speed = str(value or "normal").strip().lower()
    if speed in ("fast", "quick"):
        return 65
    if speed in ("slow", "chill"):
        return 150
    return 95


def _draw_maze(draw, show_dots):
    blue = (20, 64, 190)
    dot = (255, 214, 150)

    draw.rectangle((0, 0, 63, 31), outline=blue)
    draw.line((0, 8, 18, 8), fill=blue)
    draw.line((46, 8, 63, 8), fill=blue)
    draw.line((0, 23, 18, 23), fill=blue)
    draw.line((46, 23, 63, 23), fill=blue)
    draw.line((24, 4, 39, 4), fill=blue)
    draw.line((24, 27, 39, 27), fill=blue)
    draw.line((31, 9, 31, 22), fill=blue)

    if not show_dots:
        return

    for x in range(6, 62, 6):
        if x not in (30, 36):
            draw.point((x, 15), fill=dot)
    for x in range(7, 60, 8):
        draw.point((x, 4), fill=dot)
        draw.point((x, 27), fill=dot)


def _draw_pacman(draw, cx, cy, mouth):
    yellow = (255, 224, 35)
    if mouth == 0:
        draw.pieslice((cx - 6, cy - 6, cx + 6, cy + 6), 25, 335, fill=yellow)
    elif mouth == 1:
        draw.pieslice((cx - 6, cy - 6, cx + 6, cy + 6), 12, 348, fill=yellow)
    else:
        draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=yellow)
    draw.point((cx + 1, cy - 4), fill=(25, 20, 0))


def _draw_ghost(draw, x, y, color, step):
    draw.rectangle((x + 1, y + 4, x + 10, y + 11), fill=color)
    draw.pieslice((x + 1, y, x + 10, y + 9), 180, 360, fill=color)

    feet = y + 11
    if step % 2:
        draw.polygon([(x + 1, feet), (x + 3, feet + 2), (x + 5, feet)], fill=color)
        draw.polygon([(x + 5, feet), (x + 7, feet + 2), (x + 10, feet)], fill=color)
    else:
        draw.polygon([(x + 1, feet), (x + 4, feet + 2), (x + 6, feet)], fill=color)
        draw.polygon([(x + 6, feet), (x + 8, feet + 2), (x + 10, feet)], fill=color)

    draw.rectangle((x + 3, y + 4, x + 4, y + 5), fill=(255, 255, 255))
    draw.rectangle((x + 7, y + 4, x + 8, y + 5), fill=(255, 255, 255))
    draw.point((x + 4, y + 5), fill=(30, 60, 255))
    draw.point((x + 8, y + 5), fill=(30, 60, 255))


def render(options=None):
    from PIL import Image, ImageDraw

    opts = options or {}
    show_dots = _on(opts.get("dots", "on"))
    duration = _speed_ms(opts.get("speed", "normal"))
    frames = []

    ghost_colors = [
        (255, 65, 65),
        (255, 153, 214),
        (75, 220, 255),
    ]

    frame_count = 26
    step = 3
    wrap = 78
    start_x = -6
    gap = 15

    for frame in range(frame_count):
        image = Image.new("RGB", (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        _draw_maze(draw, show_dots)

        pac_x = start_x + ((frame * step) % wrap)
        _draw_pacman(draw, pac_x, 16, frame % 3)

        for index, color in enumerate(ghost_colors):
            gx = pac_x + 13 + index * gap
            while gx < -12:
                gx += wrap
            while gx > 65:
                gx -= wrap
            _draw_ghost(draw, gx, 10, color, frame + index)

        frames.append(image)

    out = BytesIO()
    frames[0].save(
        out,
        "WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        lossless=True,
        quality=100,
    )
    return out.getvalue()
