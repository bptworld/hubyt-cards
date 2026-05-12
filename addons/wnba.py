from datetime import datetime, timezone

from card_utils import render_sport_card

CARD_ID = "wnba"
CARD_NAME = "WNBA Scores"
CARD_DETAIL = "Live ESPN scoreboard"
CARD_OPTIONS = [
    {
        "key": "favoriteTeam",
        "label": "Team",
        "type": "select",
        "default": "CONN",
        "choices": [
            {"value": "ATL", "label": "Atlanta Dream"},
            {"value": "CHI", "label": "Chicago Sky"},
            {"value": "CONN", "label": "Connecticut Sun"},
            {"value": "DAL", "label": "Dallas Wings"},
            {"value": "GS", "label": "Golden State Valkyries"},
            {"value": "IND", "label": "Indiana Fever"},
            {"value": "LV", "label": "Las Vegas Aces"},
            {"value": "LA", "label": "Los Angeles Sparks"},
            {"value": "MIN", "label": "Minnesota Lynx"},
            {"value": "NY", "label": "New York Liberty"},
            {"value": "PHX", "label": "Phoenix Mercury"},
            {"value": "POR", "label": "Portland Fire"},
            {"value": "SEA", "label": "Seattle Storm"},
            {"value": "TOR", "label": "Toronto Tempo"},
            {"value": "WSH", "label": "Washington Mystics"},
        ],
    }
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (210, 120, 255)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO WNBA")
