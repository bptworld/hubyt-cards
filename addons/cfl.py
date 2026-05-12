from datetime import datetime, timezone

from card_utils import render_sport_card

CARD_ID = "cfl"
CARD_NAME = "CFL Scores"
CARD_DETAIL = "Live ESPN CFL scoreboard"
CARD_OPTIONS = [
    {
        "key": "favoriteTeam",
        "label": "Team",
        "type": "select",
        "default": "BCL",
        "choices": [
            {"value": "BCL", "label": "BC Lions"},
            {"value": "CSP", "label": "Calgary Stampeders"},
            {"value": "EES", "label": "Edmonton Elks"},
            {"value": "HTC", "label": "Hamilton Tiger-Cats"},
            {"value": "MTA", "label": "Montreal Alouettes"},
            {"value": "ORB", "label": "Ottawa Redblacks"},
            {"value": "SRR", "label": "Saskatchewan Roughriders"},
            {"value": "TAT", "label": "Toronto Argonauts"},
            {"value": "WBB", "label": "Winnipeg Blue Bombers"},
        ],
    }
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/football/cfl/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (235, 70, 80)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO CFL")
