from card_utils import render_sport_card
from datetime import datetime, timezone

CARD_ID = "mlb"
CARD_NAME = "MLB Scores"
CARD_DETAIL = "Live ESPN scoreboard"
CARD_OPTIONS = [
    {"key": "favoriteTeam", "label": "Team", "type": "text", "default": "BOS", "maxlength": 3}
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (117, 231, 214)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO MLB")
