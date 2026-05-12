from event_sport_utils import render_event_sport_card

CARD_ID = "ufc"
CARD_NAME = "UFC"
CARD_DETAIL = "ESPN UFC event status"
CARD_OPTIONS = []


def render(options=None):
    return render_event_sport_card("mma", "ufc", "UFC", (245, 80, 90), "NO UFC", icon="fight")
