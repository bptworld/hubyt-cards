from card_utils import fetch_json_request, render_message_wrap

CARD_ID = "joke_of_day"
CARD_NAME = "Joke of the Day"
CARD_DETAIL = "Tiny clean joke"
CARD_OPTIONS = [
    {
        "key": "style",
        "label": "Style",
        "type": "select",
        "default": "daily",
        "choices": [
            {"value": "daily", "label": "Daily joke"},
            {"value": "random", "label": "Random joke"},
        ],
    }
]

FALLBACK = "I told my LED matrix a joke. It lit up."


def _joke():
    try:
        data = fetch_json_request("https://official-joke-api.appspot.com/jokes/general/random", seconds=21600)
        if isinstance(data, list) and data:
            item = data[0]
            return f"{item.get('setup', '')} {item.get('punchline', '')}".strip()
    except Exception:
        pass
    return FALLBACK


def render(options=None):
    return render_message_wrap(_joke()[:100], (255, 220, 80))
