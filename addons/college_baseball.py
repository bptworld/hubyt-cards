from datetime import datetime, timezone

from card_utils import render_sport_card

CARD_ID = "college_baseball"
CARD_NAME = "College Baseball"
CARD_DETAIL = "Live ESPN college baseball scoreboard"
CARD_OPTIONS = [
    {
        "key": "favoriteTeam",
        "label": "Team",
        "type": "select",
        "default": "BC",
        "choices": [
            {"value": "ASU", "label": "Arizona State Sun Devils"},
            {"value": "ARIZ", "label": "Arizona Wildcats"},
            {"value": "ARK", "label": "Arkansas Razorbacks"},
            {"value": "AUB", "label": "Auburn Tigers"},
            {"value": "BC", "label": "Boston College Eagles"},
            {"value": "CAL", "label": "California Golden Bears"},
            {"value": "DUKE", "label": "Duke Blue Devils"},
            {"value": "ECU", "label": "East Carolina Pirates"},
            {"value": "FLA", "label": "Florida Gators"},
            {"value": "FSU", "label": "Florida State Seminoles"},
            {"value": "UGA", "label": "Georgia Bulldogs"},
            {"value": "GT", "label": "Georgia Tech Yellow Jackets"},
            {"value": "UK", "label": "Kentucky Wildcats"},
            {"value": "LOU", "label": "Louisville Cardinals"},
            {"value": "LSU", "label": "LSU Tigers"},
            {"value": "MD", "label": "Maryland Terrapins"},
            {"value": "MSU", "label": "Michigan State Spartans"},
            {"value": "MICH", "label": "Michigan Wolverines"},
            {"value": "MINN", "label": "Minnesota Golden Gophers"},
            {"value": "MIZ", "label": "Missouri Tigers"},
            {"value": "NCSU", "label": "NC State Wolfpack"},
            {"value": "NEB", "label": "Nebraska Cornhuskers"},
            {"value": "UNC", "label": "North Carolina Tar Heels"},
            {"value": "ND", "label": "Notre Dame Fighting Irish"},
            {"value": "MISS", "label": "Ole Miss Rebels"},
            {"value": "RUTG", "label": "Rutgers Scarlet Knights"},
            {"value": "STAN", "label": "Stanford Cardinal"},
            {"value": "UCLA", "label": "UCLA Bruins"},
            {"value": "CONN", "label": "UConn Huskies"},
            {"value": "USC", "label": "USC Trojans"},
            {"value": "WAKE", "label": "Wake Forest Demon Deacons"},
        ],
    }
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/baseball/college-baseball/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (95, 210, 130)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO CBASE")
