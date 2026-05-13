# Hubyt Cards

Add-on cards for the [Hubyt](https://github.com/bptworld/hubyt) display system.

## Available Cards - 87

### Finance

| Card | Description |
|------|-------------|
| Crypto Watch | BTC, ETH, and more |
| Market Indexes | Dow, S&P, Nasdaq |
| Market Open / Closed | NYSE/Nasdaq open status |
| Portfolio Pulse | Value and daily gain |
| Stock Ticker | Scrolling stocks and crypto |

### Fun

| Card | Description |
|------|-------------|
| 8-Bit Heartbeat | Pulsing pixel heart |
| Alien March | Retro invader parade |
| Fireplace | Pixel flames |
| Fortune Cookie | Tiny daily fortune |
| Lava Lamp | Drifting pixel blobs |
| Matrix Rain | Falling green code |
| Pac-Man Chase | Pac-Man chasing ghosts |
| Pixel Aquarium | Fish and bubbles |
| Pixel Globe | Tiny rotating world |
| Pong Loop | Tiny paddles and ball |
| Snake | Snake eats dots |
| Tiny Traffic | Cars and signal lights |

### Smart Home

| Card | Description |
|------|-------------|
| DNS Stats | Pi-hole or AdGuard stats |
| Home Assistant Entity | Live Home Assistant state |
| Hubitat Device | Live device attribute |
| Hubitat Multi | Several Hubitat devices |
| Hubitat Safety | All secure or open list |
| Water Leak Alert | Skips when all dry |

### Social

| Card | Description |
|------|-------------|
| Facebook Followers | Page followers via Graph API |
| Instagram Followers | Follower count via Instagram Graph |
| Last.fm Now Playing | Current or recent track |
| Music Assistant Now Playing | Direct Music Assistant player |
| X / Twitter Followers | Follower count via X API |
| YouTube Subscribers | Channel subscriber count |

### Sports

| Card | Description |
|------|-------------|
| CFL Scores | Live ESPN CFL scoreboard |
| College Baseball | Live ESPN college baseball scoreboard |
| College Football | Live ESPN scoreboard |
| College Softball | Live ESPN college softball scoreboard |
| F1 Racing | ESPN Formula 1 status |
| LPGA Golf | ESPN LPGA leaderboard |
| Men's College Basketball | Live ESPN scoreboard |
| Men's College Lacrosse | Live ESPN men's college lacrosse scoreboard |
| MLB Scores | Live ESPN scoreboard |
| NASCAR | ESPN NASCAR Cup status |
| NBA G League | Live ESPN NBA G League scoreboard |
| NBA Scores | Live ESPN scoreboard |
| NCAA Hockey | Live ESPN men's college hockey scoreboard |
| NFL Scores | Live ESPN scoreboard |
| NHL Scores | Live ESPN scoreboard |
| NLL Lacrosse | Live ESPN NLL scoreboard |
| PGA Golf | ESPN PGA leaderboard |
| PLL Lacrosse | Live ESPN PLL scoreboard |
| Soccer Scores | Live ESPN soccer scoreboard |
| Sports Standings | Top teams from ESPN standings |
| Tennis ATP | ESPN ATP tournament status |
| Tennis WTA | ESPN WTA tournament status |
| UFC | ESPN UFC event status |
| UFL Scores | Live ESPN UFL scoreboard |
| WNBA Scores | Live ESPN scoreboard |
| Women's College Basketball | Live ESPN scoreboard |
| Women's College Lacrosse | Live ESPN women's college lacrosse scoreboard |
| Women's College Volleyball | Live ESPN women's college volleyball scoreboard |

### Travel

| Card | Description |
|------|-------------|
| Airport Delays | FAA delay status |
| Commute Time | Drive time estimate |
| Flight Tracker | Flightradar24 live and summary tracking |
| Flights Overhead | Live flights above you |
| Gas Price Local | AAA local gas average |

### Utility

| Card | Description |
|------|-------------|
| Battery Reminder | Rotating battery checklist |
| Clock | Time plus local weather |
| Countdown | Days until any event |
| Countdown Confetti | Event countdown with confetti |
| Disney Countdown | Days until your trip |
| GitHub Issues Watch | Open issue count |
| GitHub Release Watch | Latest release for a repo |
| Google Calendar | Next upcoming event |
| Hubyt Update Watch | Hubyt release and card updates |
| Joke of the Day | Tiny clean joke |
| Mega Millions | Latest Mega Millions draw |
| Megabucks | Latest MA Megabucks draw |
| Moon Phase | Current moon phase |
| Package Watch | Manual package status |
| Ping Monitor | TCP latency monitor |
| Quote of the Day | Short daily quote |
| RSS Headlines | Scrolling RSS headline |
| Sunrise / Sunset | Sun and daylight times by ZIP |
| Trash + Recycling | Weekly and bi-weekly pickup reminder |
| Website Uptime | URL up/down monitor |
| Word of the Day | Daily word with short meaning |

### Weather

| Card | Description |
|------|-------------|
| Air Quality | AQI, pollen, and UV by ZIP |
| Weather Alert | Skips when clear |
| Weather Forecast | 5-day forecast with icons |
| Weather Mood | Animated weather vibe |

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
    # Return WebP bytes for a 64x32 card frame.
    ...
```

See [`docs/card-creation/STEP_BY_STEP.md`](docs/card-creation/STEP_BY_STEP.md) for the card framework walkthrough.
