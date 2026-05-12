from datetime import datetime, timezone

from card_utils import render_sport_card

CARD_ID = "college_softball"
CARD_NAME = "College Softball"
CARD_DETAIL = "Live ESPN college softball scoreboard"
CARD_OPTIONS = [
    {
        "key": "favoriteTeam",
        "label": "Team",
        "type": "select",
        "default": "OU",
        "choices": [
            {"value": "ALA", "label": "Alabama Crimson Tide"},
            {"value": "ARK", "label": "Arkansas Razorbacks"},
            {"value": "AUB", "label": "Auburn Tigers"},
            {"value": "BAY", "label": "Baylor Bears"},
            {"value": "CLEM", "label": "Clemson Tigers"},
            {"value": "DUKE", "label": "Duke Blue Devils"},
            {"value": "FLA", "label": "Florida Gators"},
            {"value": "FSU", "label": "Florida State Seminoles"},
            {"value": "UGA", "label": "Georgia Bulldogs"},
            {"value": "LSU", "label": "LSU Tigers"},
            {"value": "MIZ", "label": "Missouri Tigers"},
            {"value": "NEB", "label": "Nebraska Cornhuskers"},
            {"value": "OKST", "label": "Oklahoma State Cowgirls"},
            {"value": "OU", "label": "Oklahoma Sooners"},
            {"value": "ORE", "label": "Oregon Ducks"},
            {"value": "STAN", "label": "Stanford Cardinal"},
            {"value": "TENN", "label": "Tennessee Volunteers"},
            {"value": "TEX", "label": "Texas Longhorns"},
            {"value": "TAMU", "label": "Texas A&M Aggies"},
            {"value": "UCLA", "label": "UCLA Bruins"},
            {"value": "WASH", "label": "Washington Huskies"},
        ],
    }
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/baseball/college-softball/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (245, 120, 170)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO SOFT")
