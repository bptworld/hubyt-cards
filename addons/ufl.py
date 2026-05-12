from datetime import datetime, timezone

from card_utils import render_sport_card

CARD_ID = "ufl"
CARD_NAME = "UFL Scores"
CARD_DETAIL = "Live ESPN UFL scoreboard"
CARD_OPTIONS = [
    {
        "key": "favoriteTeam",
        "label": "Team",
        "type": "select",
        "default": "DC",
        "choices": [
            {"value": "BHAM", "label": "Birmingham Stallions"},
            {"value": "CLB", "label": "Columbus Aviators"},
            {"value": "DAL", "label": "Dallas Renegades"},
            {"value": "DC", "label": "DC Defenders"},
            {"value": "HOU", "label": "Houston Gamblers"},
            {"value": "LOU", "label": "Louisville Kings"},
            {"value": "ORL", "label": "Orlando Storm"},
            {"value": "STL", "label": "St. Louis Battlehawks"},
        ],
    }
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/football/ufl/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (80, 190, 255)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO UFL")
