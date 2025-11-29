# session.py
import random
import time
from urllib.parse import urljoin

from selenium.webdriver.support.ui import WebDriverWait

from config import (
    DOMAINS,
    ENTRY_POINTS,
    BASE_MIN_DWELL,
    BASE_MAX_DWELL,
    BASE_MAX_CLICKS,
)
from human_actions import (
    desktop_scroll,
    mobile_swipe,
    micro_hesitate,
    hover_ads,
    click_internal,
)
from utils import log

# -----------------------------------------------
# BLOCKED URL SUBSTRINGS — NEVER CLICK THESE
# -----------------------------------------------
BLOCKED_KEYWORDS = [
    "wp-login",
    "wp-admin",
    "lostpassword",
    "reset",
    "admin",
    "checkout",
    "cart",
    "signin",
    "signup",
    "login",
    "rates",
    "cdn-cgi",
    "privacy",
    "support",
    "terms",
]


def is_safe_url(href: str) -> bool:
    """Filter out URLs that lead to login/reset/admin/cart pages."""
    if not href:
        return False

    h = href.lower()
    for bad in BLOCKED_KEYWORDS:
        if bad in h:
            return False
    return True


# ---------------------------------------------------------
# DNS-SAFE NAVIGATION WRAPPER
# Retries up to 2 times (human-like)
# ---------------------------------------------------------
def safe_get(driver, url):
    attempts = 0
    while attempts < 3:  # 1st attempt + 2 retries
        try:
            driver.get(url)
            return True
        except Exception as e:
            attempts += 1
            log(f"[ERROR] Navigation failed ({attempts}/3): {e}")

            # human-like wait before retrying
            time.sleep(random.uniform(2.5, 5.0))

    # Give up — behave human-like and fall back
    log(f"[FALLBACK] Could not load: {url}")
    return False


# ---------------------------------------------------------
# MAIN SESSION LOOP
# ---------------------------------------------------------
def run_session(driver, persona, is_mobile: bool):
    visited = set()

    # Pick 2–4 domains for this session
    max_depth = random.randint(2, 4)
    sites = random.sample(DOMAINS, k=max_depth)

    log("[SESSION] Sites: " + " → ".join(sites))
    log(f"[SESSION] Persona: {persona.name} (mobile={is_mobile})")

    # -----------------------------------------------------
    # Visit each domain in the list
    # -----------------------------------------------------
    for domain in sites:
        entry = random.choice(ENTRY_POINTS.get(domain, ["/"]))
        url = urljoin(domain, entry)

        # SAFE navigation (DNS / timeout / connection errors handled)
        if not safe_get(driver, url):
            continue

        # Wait for DOM to fully load
        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            log("[WARN] Page load state unknown (timeout)")

        log(f"[ENTRY] {url}")

        # Session dwell time for this site
        dwell_base = random.randint(BASE_MIN_DWELL, BASE_MAX_DWELL)
        end_time = time.time() + dwell_base * persona.dwell_multiplier
        clicks = 0

        # -----------------------------------------------------
        # Behave on the page until dwell time expires
        # -----------------------------------------------------
        while time.time() < end_time and clicks < BASE_MAX_CLICKS:

            # Human-style scrolling
            if is_mobile:
                mobile_swipe(driver, persona)
            else:
                desktop_scroll(driver, persona)

            # Random hesitation
            micro_hesitate(driver, persona)

            # Hover ads (rare click)
            hover_ads(driver, persona)

            # Internal click (safe)
            href = click_internal(driver, persona, visited, return_href=True)

            if href:
                if is_safe_url(href):
                    clicks += 1

                    # Human-like dwell after a click
                    t = random.uniform(5, 15)
                    log(f"[EXPLORE] dwell {t:.1f}s")
                    time.sleep(t)
                else:
                    log(f"[SKIP] Blocked sensitive URL: {href}")

            # tiny pacing delay between actions
            time.sleep(random.uniform(1.0, 2.0))

    log("[SESSION] Completed")
