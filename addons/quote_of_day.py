from io import BytesIO

from card_utils import draw_sharp_text, fetch_json_request, render_message_wrap

CARD_ID = "quote_of_day"
CARD_NAME = "Quote of the Day"
CARD_DETAIL = "Short daily quote"
CARD_OPTIONS = [
    {"key": "fallbackQuote", "label": "Fallback Quote", "type": "text", "default": "Make today useful.", "maxlength": 60},
]

FALLBACKS = [
    "Make today useful.",
    "Small steps still move.",
    "Keep building.",
    "Choose the next right thing.",
    "Attention turns work into craft.",
]


def _quote(opts):
    try:
        data = fetch_json_request("https://zenquotes.io/api/today", seconds=21600)
        if isinstance(data, list) and data:
            return data[0].get("q") or data[0].get("quote")
    except Exception:
        pass
    return (opts.get("fallbackQuote") or FALLBACKS[0]).strip() or FALLBACKS[0]


def render(options=None):
    return render_message_wrap(_quote(options or {})[:90], (245, 250, 255))
