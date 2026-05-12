from event_sport_utils import render_event_sport_card

CARD_ID = "lpga"
CARD_NAME = "LPGA Golf"
CARD_DETAIL = "ESPN LPGA leaderboard"
CARD_OPTIONS = []


def render(options=None):
    return render_event_sport_card("golf", "lpga", "LPGA", (255, 135, 205), "NO LPGA", icon="golf")
