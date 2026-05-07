# Hubyt Cards

Add-on cards for the [Hubyt](https://github.com/bptworld/hubyt) display system.

## Available Cards - 38

### Utility

| Preview | Card | Description |
|---------|------|-------------|
| <img src="assets/previews/clock.webp" width="96" alt="Clock preview"> | Clock | Time plus local weather |
| <img src="assets/previews/countdown.webp" width="96" alt="Countdown preview"> | Countdown | Days until any event |
| <img src="assets/previews/disney.webp" width="96" alt="Disney Countdown preview"> | Disney Countdown | Days until your trip |
| <img src="assets/previews/weather_forecast.webp" width="96" alt="Weather Forecast preview"> | Weather Forecast | 4-day forecast with icons |
| <img src="assets/previews/gcal.webp" width="96" alt="Google Calendar preview"> | Google Calendar | Next upcoming event |
| <img src="assets/previews/moon_phase.webp" width="96" alt="Moon Phase preview"> | Moon Phase | Current moon phase |
| <img src="assets/previews/countdown_confetti.webp" width="96" alt="Countdown Confetti preview"> | Countdown Confetti | Event countdown with confetti |

### Finance

| Preview | Card | Description |
|---------|------|-------------|
| <img src="assets/previews/stocks.webp" width="96" alt="Stock Ticker preview"> | Stock Ticker | Live price and change |
| <img src="assets/previews/market_indexes.webp" width="96" alt="Market Indexes preview"> | Market Indexes | Dow, S&P, Nasdaq |
| <img src="assets/previews/crypto_watch.webp" width="96" alt="Crypto Watch preview"> | Crypto Watch | BTC, ETH, and more |
| <img src="assets/previews/gas_price_local.webp" width="96" alt="Gas Price Local preview"> | Gas Price Local | AAA ZIP/metro gas average |
| <img src="assets/previews/portfolio_pulse.webp" width="96" alt="Portfolio Pulse preview"> | Portfolio Pulse | Value and daily gain |

### Smart Home

| Preview | Card | Description |
|---------|------|-------------|
| <img src="assets/previews/hubitat.webp" width="96" alt="Hubitat Device preview"> | Hubitat Device | Live device attribute |
| <img src="assets/previews/hubitat_multi.webp" width="96" alt="Hubitat Multi preview"> | Hubitat Multi | Several Hubitat devices |
| <img src="assets/previews/hubitat_safety.webp" width="96" alt="Hubitat Safety preview"> | Hubitat Safety | All secure or open list |
| <img src="assets/previews/water_leak_alert.webp" width="96" alt="Water Leak Alert preview"> | Water Leak Alert | Skips when all dry |

### Fun

| Preview | Card | Description |
|---------|------|-------------|
| <img src="assets/previews/pacman.webp" width="96" alt="Pac-Man Chase preview"> | Pac-Man Chase | Pac-Man chasing ghosts |
| <img src="assets/previews/matrix_rain.webp" width="96" alt="Matrix Rain preview"> | Matrix Rain | Falling green code |
| <img src="assets/previews/pong_loop.webp" width="96" alt="Pong Loop preview"> | Pong Loop | Tiny paddles and ball |
| <img src="assets/previews/lava_lamp.webp" width="96" alt="Lava Lamp preview"> | Lava Lamp | Drifting pixel blobs |
| <img src="assets/previews/alien_march.webp" width="96" alt="Alien March preview"> | Alien March | Retro invader parade |
| <img src="assets/previews/snake.webp" width="96" alt="Snake preview"> | Snake | Snake eats dots |
| <img src="assets/previews/aquarium.webp" width="96" alt="Pixel Aquarium preview"> | Pixel Aquarium | Fish and bubbles |
| <img src="assets/previews/fireplace.webp" width="96" alt="Fireplace preview"> | Fireplace | Pixel flames |
| <img src="assets/previews/tiny_traffic.webp" width="96" alt="Tiny Traffic preview"> | Tiny Traffic | Cars and signal lights |
| <img src="assets/previews/fortune_cookie.webp" width="96" alt="Fortune Cookie preview"> | Fortune Cookie | Tiny daily fortune |
| <img src="assets/previews/heartbeat.webp" width="96" alt="8-Bit Heartbeat preview"> | 8-Bit Heartbeat | Pulsing pixel heart |
| <img src="assets/previews/pixel_globe.webp" width="96" alt="Pixel Globe preview"> | Pixel Globe | Tiny rotating world |

### Weather

| Preview | Card | Description |
|---------|------|-------------|
| <img src="assets/previews/weather_mood.webp" width="96" alt="Weather Mood preview"> | Weather Mood | Animated weather vibe |
| <img src="assets/previews/weather_alert.webp" width="96" alt="Weather Alert preview"> | Weather Alert | Skips when clear |

### Sports

| Preview | Card | Description |
|---------|------|-------------|
| <img src="assets/previews/mlb.webp" width="96" alt="MLB Scores preview"> | MLB Scores | Live ESPN scoreboard |
| <img src="assets/previews/nba.webp" width="96" alt="NBA Scores preview"> | NBA Scores | Live ESPN scoreboard |
| <img src="assets/previews/nhl.webp" width="96" alt="NHL Scores preview"> | NHL Scores | Live ESPN scoreboard |
| <img src="assets/previews/nfl.webp" width="96" alt="NFL Scores preview"> | NFL Scores | Live ESPN scoreboard |

### Travel

| Preview | Card | Description |
|---------|------|-------------|
| <img src="assets/previews/airport_delays.webp" width="96" alt="Airport Delays preview"> | Airport Delays | FAA delay status |
| <img src="assets/previews/commute_time.webp" width="96" alt="Commute Time preview"> | Commute Time | Drive time estimate |
| <img src="assets/previews/flights_overhead.webp" width="96" alt="Flights Overhead preview"> | Flights Overhead | Live flights above you |
| <img src="assets/previews/flight_track.webp" width="96" alt="Flight Tracker preview"> | Flight Tracker | Track a specific flight |

## Installing a Card

Open Hubyt, click **Browse Cards**, and click **Install** next to any card.

## Writing Your Own Card

Each card is a single Python file in `addons/`. It must define:

```python
CARD_ID = "mycard"           # unique slug
CARD_NAME = "My Card"        # display name
CARD_DETAIL = "Short blurb"  # one-line description
CARD_OPTIONS = [             # configurable options (can be empty list)
    {"key": "myOption", "label": "Label", "type": "text", "default": "value", "maxlength": 10}
]

def render(options=None):
    # return WebP image bytes (64x32 pixels)
    ...
```

Import shared utilities from `card_utils`:

```python
from card_utils import draw_sharp_text, render_text_webp, fetch_json_url
```

To submit a card, open a pull request adding your `.py` file to `addons/` and an entry to `registry.json`.
