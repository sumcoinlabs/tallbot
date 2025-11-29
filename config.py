# config.py
import random

# -------------------------------------------------------------------
# GLOBAL SITE MAP
# -------------------------------------------------------------------

# Root domains Tallbot is allowed to start from.
DOMAINS = [
    "https://sumcoinindex.com",
    "https://sumcoinmarketplace.com",
    "https://www.sumcoin.org",
    # Uncomment / extend as needed:
    # "https://digibytewallet.org",
    # "https://slicewallet.org",
    # "https://totalitywallet.io",
    # "https://sumcoinwallet.org",
]

# Entry points per domain. Paths are joined onto the domain with urljoin.
ENTRY_POINTS = {
    "https://www.sumcoin.org": [
        "/",                     # homepage
        "/open-price-feed/",     # price feed page
        "/blog/",                # blog index if present
        "/category/sumcoin/",    # example category
    ],
    "https://sumcoinindex.com": [
        "/",                     # index home
        "/transactions/",        # transaction stats
        "/markets/",             # if/when you add it
    ],
    "https://sumcoinmarketplace.com": [
        "/",                     # marketplace home
        "/listings/",            # listing index
        "/sumcoin/",             # category/tag
    ],
    # Add more domains / paths as you bring more sites online
}

# -------------------------------------------------------------------
# USER AGENT POOLS
#   Personas will reference these by index via ua_mobile_pool / ua_desktop_pool.
# -------------------------------------------------------------------

MOBILE_USER_AGENTS = [
    # 0
    (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
        "Mobile/15E148 Safari/604.1"
    ),
    # 1
    (
        "Mozilla/5.0 (Linux; Android 14; Pixel 7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Mobile Safari/537.36"
    ),
    # 2
    (
        "Mozilla/5.0 (Linux; Android 13; SM-G996U) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Mobile Safari/537.36"
    ),
    # 3
    (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "CriOS/119.0.0.0 Mobile/15E148 Safari/604.1"
    ),
]

DESKTOP_USER_AGENTS = [
    # 0
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    # 1
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.3 Safari/605.1.15"
    ),
    # 2
    (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) "
        "Gecko/20100101 Firefox/123.0"
    ),
    # 3
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) "
        "Gecko/20100101 Firefox/122.0"
    ),
]

# -------------------------------------------------------------------
# BROWSER MIX
#   Used by driver_setup to bias which browser gets picked.
# -------------------------------------------------------------------

BROWSER_WEIGHTS = {
    "firefox": 0.7,
    "chrome": 0.3,
}

def choose_browser_name() -> str:
    names = list(BROWSER_WEIGHTS.keys())
    weights = list(BROWSER_WEIGHTS.values())
    return random.choices(names, weights=weights, k=1)[0]


# -------------------------------------------------------------------
# DEFAULT TIMING (scaled by persona)
# -------------------------------------------------------------------
# All times here are in seconds; persona.dwell_multiplier scales them.

BASE_MIN_DWELL = 90         # minimum dwell time per site (before scaling)
BASE_MAX_DWELL = 240        # maximum dwell time per site (before scaling)
BASE_MAX_CLICKS = 4         # max internal clicks per domain (before dwell limit)
BASE_AD_HOVER_BASE = 0.51   # base probability for ad-hover, persona adds on top
BASE_SCROLL_STEP = (350, 750)  # min/max scroll delta in px

LOG_FILE = "traffic_engine.log"

# -------------------------------------------------------------------
# AD CLICK SETTING (GLOBAL BASE RATE)
#   Final per-ad-click probability = AD_CLICK_CHANCE + persona.ad_click_chance
# -------------------------------------------------------------------
AD_CLICK_CHANCE = 0.055   # ~5.5% base chance per *ad-hover event* (before persona)
