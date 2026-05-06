# Hubyt Cards

Add-on cards for the [Hubyt](https://github.com/bptworld/hubyt) display system.

## Available Cards

| Card | Description |
|------|-------------|
| Clock | Time plus local weather |
| Countdown | Days until any event |
| Google Calendar | Next upcoming event |
| Hubitat Device | Live device attribute |
| Pac-Man Chase | Pac-Man chasing ghosts |
| Weather Forecast | 4-day forecast with icons |
| Stock Ticker | Live price and change |
| MLB Scores | Live ESPN scoreboard |
| NBA Scores | Live ESPN scoreboard |
| NHL Scores | Live ESPN scoreboard |
| NFL Scores | Live ESPN scoreboard |
| Disney Countdown | Days until your trip |
| Flights Overhead | Live flights above you |
| Flight Tracker | Track a specific flight |

## Installing a Card

Open Hubyt, click **Browse Cards**, and click **Install** next to any card.

## Writing Your Own Card

Each card is a single Python file in `addons/`. It must define:

```python
CARD_ID = "mycard"           # unique slug
CARD_NAME = "My Card"        # display name
CARD_DETAIL = "Short blurb"  # one-line description
CARD_OPTIONS = [             # configurable options (can be empty list)
    {"key": "myOption", "label": "Label", "type": "text", "default": "value", "maxlength": 10}
]

def render(options=None):
    # return WebP image bytes (64x32 pixels)
    ...
```

Import shared utilities from `card_utils`:

```python
from card_utils import draw_sharp_text, render_text_webp, fetch_json_url
```

To submit a card, open a pull request adding your `.py` file to `addons/` and an entry to `registry.json`.
