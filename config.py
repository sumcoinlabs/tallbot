# config.py
import random

# -------------------------------------------------------------------
# GLOBAL SITE MAP
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
        "/", "/privacy/", "news/about.html"
    ],

    "https://totalitywallet.io": [
        "/", "/privacy/"
    ],
}

# -------------------------------------------------------------------
# USER AGENTS
# -------------------------------------------------------------------

MOBILE_UAS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15A372 Safari/604.1",

    "Mozilla/5.0 (Linux; Android 13; SM-G996U) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",

    "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
    "AppleWebKit/537.36 Chrome/118.0.0.0 Mobile Safari/537.36",
]

DESKTOP_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "Chrome/129.0.0.0 Safari/537.36",

    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "Chrome/129.0.0.0 Safari/537.36",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 Chrome/129.0.0.0 Safari/537.36",
]

# -------------------------------------------------------------------
# DEFAULT TIMING (scaled by persona)
# -------------------------------------------------------------------
BASE_MIN_DWELL = 90
BASE_MAX_DWELL = 240
BASE_MAX_CLICKS = 4
BASE_AD_HOVER_BASE = 0.51
BASE_SCROLL_STEP = (350, 750)

LOG_FILE = "traffic_engine.log"

# -------------------------------------------------------------------
# AD CLICK SETTING
# -------------------------------------------------------------------
AD_CLICK_CHANCE = 0.055   # 1.5% chance per ad-hover event
