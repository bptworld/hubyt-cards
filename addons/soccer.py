from datetime import datetime, timezone

from card_utils import render_sport_card

CARD_ID = "soccer"
CARD_NAME = "Soccer Scores"
CARD_DETAIL = "Live ESPN soccer scoreboard"
CARD_OPTIONS = [
    {
        "key": "league",
        "label": "League",
        "type": "select",
        "default": "eng.1",
        "choices": [
            {"value": "eng.1", "label": "Premier League"},
            {"value": "usa.1", "label": "MLS"},
            {"value": "esp.1", "label": "La Liga"},
            {"value": "ita.1", "label": "Serie A"},
            {"value": "ger.1", "label": "Bundesliga"},
            {"value": "fra.1", "label": "Ligue 1"},
            {"value": "uefa.champions", "label": "Champions League"},
            {"value": "uefa.europa", "label": "Europa League"},
            {"value": "usa.nwsl", "label": "NWSL"},
        ],
    },
    {
        "key": "favoriteTeam",
        "label": "Team",
        "type": "select",
        "default": "ARS",
        "choices": [
            {"value": "ARS", "label": "Arsenal"},
            {"value": "AVL", "label": "Aston Villa"},
            {"value": "CHE", "label": "Chelsea"},
            {"value": "LIV", "label": "Liverpool"},
            {"value": "MNC", "label": "Manchester City"},
            {"value": "MAN", "label": "Manchester United"},
            {"value": "NEW", "label": "Newcastle United"},
            {"value": "TOT", "label": "Tottenham Hotspur"},
        ],
    },
]

_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (70, 220, 125)


def render(options=None):
    opts = options or {}
    league = str(opts.get("league") or "eng.1").strip()
    if not league:
        league = "eng.1"
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard"
    return render_sport_card(opts, url, _CACHE, _COLOR, "NO SOCCER")
