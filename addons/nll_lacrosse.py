from datetime import datetime, timezone

from card_utils import render_sport_card

CARD_ID = "nll_lacrosse"
CARD_NAME = "NLL Lacrosse"
CARD_DETAIL = "Live ESPN NLL scoreboard"
CARD_OPTIONS = [
    {
        "key": "favoriteTeam",
        "label": "Team",
        "type": "select",
        "default": "BUF",
        "choices": [
            {"value": "BUF", "label": "Buffalo Bandits"},
            {"value": "CGY", "label": "Calgary Roughnecks"},
            {"value": "COL", "label": "Colorado Mammoth"},
            {"value": "GA", "label": "Georgia Swarm"},
            {"value": "HFX", "label": "Halifax Thunderbirds"},
            {"value": "LV", "label": "Las Vegas Desert Dogs"},
            {"value": "OSH", "label": "Oshawa FireWolves"},
            {"value": "OTT", "label": "Ottawa Black Bears"},
            {"value": "PHI", "label": "Philadelphia Wings"},
            {"value": "ROC", "label": "Rochester Knighthawks"},
            {"value": "SD", "label": "San Diego Seals"},
            {"value": "SAS", "label": "Saskatchewan Rush"},
            {"value": "TOR", "label": "Toronto Rock"},
            {"value": "VAN", "label": "Vancouver Warriors"},
        ],
    }
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/lacrosse/nll/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (170, 125, 255)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO NLL")
