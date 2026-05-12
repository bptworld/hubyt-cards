from event_sport_utils import render_event_sport_card

CARD_ID = "tennis_atp"
CARD_NAME = "Tennis ATP"
CARD_DETAIL = "ESPN ATP tournament status"
CARD_OPTIONS = []


def render(options=None):
    return render_event_sport_card("tennis", "atp", "ATP", (185, 240, 80), "NO ATP", icon="tennis")
