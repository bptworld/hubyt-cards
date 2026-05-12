from event_sport_utils import render_event_sport_card

CARD_ID = "nascar"
CARD_NAME = "NASCAR"
CARD_DETAIL = "ESPN NASCAR Cup status"
CARD_OPTIONS = []


def render(options=None):
    return render_event_sport_card("racing", "nascar-premier", "NASCAR", (255, 210, 70), "NO NASCAR", icon="race")
