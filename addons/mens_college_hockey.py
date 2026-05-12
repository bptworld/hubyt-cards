from datetime import datetime, timezone

from card_utils import render_sport_card

CARD_ID = "mens_college_hockey"
CARD_NAME = "NCAA Hockey"
CARD_DETAIL = "Live ESPN men's college hockey scoreboard"
CARD_OPTIONS = [
    {
        "key": "favoriteTeam",
        "label": "Team",
        "type": "select",
        "default": "BC",
        "choices": [
            {"value": "AF", "label": "Air Force Falcons"},
            {"value": "ASU", "label": "Arizona State Sun Devils"},
            {"value": "ARMY", "label": "Army Black Knights"},
            {"value": "BST", "label": "Bemidji State Beavers"},
            {"value": "BC", "label": "Boston College Eagles"},
            {"value": "BU", "label": "Boston University Terriers"},
            {"value": "BGSU", "label": "Bowling Green Falcons"},
            {"value": "BRWN", "label": "Brown Bears"},
            {"value": "COR", "label": "Cornell Big Red"},
            {"value": "DART", "label": "Dartmouth Big Green"},
            {"value": "HARV", "label": "Harvard Crimson"},
            {"value": "HC", "label": "Holy Cross Crusaders"},
            {"value": "ME", "label": "Maine Black Bears"},
            {"value": "MASS", "label": "Massachusetts Minutemen"},
            {"value": "M-OH", "label": "Miami (OH) RedHawks"},
            {"value": "MSU", "label": "Michigan State Spartans"},
            {"value": "MICH", "label": "Michigan Wolverines"},
            {"value": "UMD", "label": "Minnesota Duluth Bulldogs"},
            {"value": "MINN", "label": "Minnesota Golden Gophers"},
            {"value": "UNH", "label": "New Hampshire Wildcats"},
            {"value": "UND", "label": "North Dakota Fighting Hawks"},
            {"value": "NE", "label": "Northeastern Huskies"},
            {"value": "ND", "label": "Notre Dame Fighting Irish"},
            {"value": "OSU", "label": "Ohio State Buckeyes"},
            {"value": "PSU", "label": "Penn State Nittany Lions"},
            {"value": "PRIN", "label": "Princeton Tigers"},
            {"value": "RIT", "label": "RIT Tigers"},
            {"value": "CONN", "label": "UConn Huskies"},
            {"value": "UVM", "label": "Vermont Catamounts"},
            {"value": "WIS", "label": "Wisconsin Badgers"},
            {"value": "YALE", "label": "Yale Bulldogs"},
        ],
    }
]

_URL = "https://site.api.espn.com/apis/site/v2/sports/hockey/mens-college-hockey/scoreboard"
_CACHE = {"expires": datetime.min.replace(tzinfo=timezone.utc), "body": b""}
_COLOR = (80, 220, 255)


def render(options=None):
    return render_sport_card(options, _URL, _CACHE, _COLOR, "NO HOCK")
