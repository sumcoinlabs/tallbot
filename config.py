# config.py
import random

# -------------------------------------------------------------------
# DOMAINS AND ENTRY POINTS
# -------------------------------------------------------------------
DOMAINS = [
    "https://sumcoinindex.com",
    "https://sumcoinmarketplace.com",
    "https://www.sumcoin.org",
#    "https://digibytewallet.org",
#    "https://slicewallet.org",
#    "https://totalitywallet.io",
#    "https://sumcoinwallet.org",
]

ENTRY_POINTS = {
    "https://sumcoinindex.com": [
        "/", "/coin/bitcoin", "/faucets/", "/coin/dogecoin",
        "/coin/litecoin", "/coin/ethereum", "/coin/xrp"
    ],

    "https://sumcoinmarketplace.com": [
        "/", "/ads/", "/privacy/", "/ads/vehicles/"
    ],

    "https://www.sumcoin.org": [
        "/", "/about/", "/faq", "/migrations/", "/buy-adspace/"
    ],

    "https://digibytewallet.org": [
        "/", "/faucet/", "/recovery/", "/news/"
    ],

    "https://sumcoinwallet.org": [
        "/", "/news/", "/recovery/"
    ],

    "https://slicewallet.org": [
        "/", "/privacy/", "/news/about.html"
    ],

    "https://totalitywallet.io": [
        "/", "/privacy/"
    ],
}

# -------------------------------------------------------------------
# USER AGENT POOLS
# -------------------------------------------------------------------
MOBILE_USER_AGENTS = [
    # iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    # Android Chrome
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36",
    # Another Android variant
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
]

DESKTOP_USER_AGENTS = [
    # Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    # macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    # Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
]

# -------------------------------------------------------------------
# BROWSER WEIGHTS
# -------------------------------------------------------------------
BROWSER_WEIGHTS = {
    "firefox": 0.7,
    "chrome": 0.3,
}

# -------------------------------------------------------------------
# TIMING / BEHAVIOR CONSTANTS
# -------------------------------------------------------------------
BASE_MIN_DWELL = 90          # min seconds per domain
BASE_MAX_DWELL = 240         # max seconds per domain
BASE_MAX_CLICKS = 4          # max internal clicks per domain

# scroll distance in px (min, max)
BASE_SCROLL_STEP = (350, 750)

# log file
LOG_FILE = "traffic_engine.log"

# Base probability of clicking an ad *per hover*.
AD_CLICK_CHANCE = 0.055

# Minimum seconds on a page before Tallbot is allowed to click any link.
MIN_TIME_BEFORE_CLICK = 10

# -------------------------------------------------------------------
# BROWSER PICKER
# -------------------------------------------------------------------
def choose_browser_name():
    names = list(BROWSER_WEIGHTS.keys())
    weights = [BROWSER_WEIGHTS[n] for n in names]
    # random.choices is available in Python 3.6+
    return random.choices(names, weights=weights, k=1)[0]
