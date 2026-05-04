from card_utils import render_sport_card
from datetime import datetime, timezone

CARD_ID = "nfl"
CARD_NAME = "NFL Scores"
CARD_DETAIL = "Live ESPN scoreboard"
CARD_OPTIONS = [
    {"key": "favoriteTeam", "label": "Team", "type": "text", "default": "NE", "maxlength": 3}
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (100, 220, 80)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO NFL")
