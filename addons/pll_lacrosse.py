from datetime import datetime, timezone

from card_utils import render_sport_card

CARD_ID = "pll_lacrosse"
CARD_NAME = "PLL Lacrosse"
CARD_DETAIL = "Live ESPN PLL scoreboard"
CARD_OPTIONS = [
    {
        "key": "favoriteTeam",
        "label": "Team",
        "type": "select",
        "default": "CAN",
        "choices": [
            {"value": "CAN", "label": "Boston Cannons"},
            {"value": "RED", "label": "California Redwoods"},
            {"value": "CHA", "label": "Carolina Chaos"},
            {"value": "OUT", "label": "Denver Outlaws"},
            {"value": "WHP", "label": "Maryland Whipsnakes"},
            {"value": "ATL", "label": "New York Atlas"},
            {"value": "WAT", "label": "Philadelphia Waterdogs"},
            {"value": "ARC", "label": "Utah Archers"},
        ],
    }
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/lacrosse/pll/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (220, 120, 255)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO PLL")
