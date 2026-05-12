from event_sport_utils import render_event_sport_card

CARD_ID = "tennis_wta"
CARD_NAME = "Tennis WTA"
CARD_DETAIL = "ESPN WTA tournament status"
CARD_OPTIONS = []


def render(options=None):
    return render_event_sport_card("tennis", "wta", "WTA", (255, 160, 210), "NO WTA", icon="tennis")
