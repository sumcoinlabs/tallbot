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
    MIN_TIME_BEFORE_CLICK,
)
from human_actions import (
    desktop_scroll,
    mobile_swipe,
    micro_hesitate,
    hover_ads,
    click_internal,
    handle_popups,
)
from utils import log


BLOCKED_KEYWORDS = [
    "wp-login", "wp-admin", "lostpassword", "reset", "admin",
    "checkout", "cart", "signin", "signup", "login",
    "rates", "cdn-cgi", "privacy", "support", "terms",
]


def is_safe_url(href):
    if not href:
        return False
    h = href.lower()
    for bad in BLOCKED_KEYWORDS:
        if bad in h:
            return False
    return True


def safe_get(driver, url):
    attempts = 0
    while attempts < 3:
        try:
            driver.get(url)
            return True
        except Exception as e:
            attempts += 1
            log("[ERROR] Navigation failed ({}/3): {}".format(attempts, e))
            time.sleep(random.uniform(2.5, 5.0))

    log("[FALLBACK] Could not load {}".format(url))
    return False


def run_session(driver, persona, is_mobile):
    visited = set()

# Choose 2–4 domains, but never more than available
requested = random.randint(2, 4)
max_depth = min(requested, len(DOMAINS))

sites = random.sample(DOMAINS, k=max_depth)

    log("[SESSION] Persona='{}' mobile={} Sites: {}".format(
        persona.name, is_mobile, " → ".join(sites))
    )

    for domain in sites:
        entry = random.choice(ENTRY_POINTS.get(domain, ["/"]))
        url = urljoin(domain, entry)

        if not safe_get(driver, url):
            continue

        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            log("[WARN] Page load incomplete")

        current_url = driver.current_url
        log("[ENTRY] {}".format(current_url))

        dwell_base = random.randint(BASE_MIN_DWELL, BASE_MAX_DWELL)
        end_time = time.time() + dwell_base * persona.dwell_multiplier
        clicks = 0

        page_start_time = time.time()

        while time.time() < end_time and clicks < BASE_MAX_CLICKS:
            # 1) handle overlays/popups if any
            handle_popups(driver, persona)

            # 2) scroll/swipe
            if is_mobile:
                mobile_swipe(driver, persona)
            else:
                desktop_scroll(driver, persona)

            # 3) hesitation (reading)
            micro_hesitate(driver, persona)

            # 4) hover ads / rare click
            hover_ads(driver, persona)

            # 5) internal click, but only after minimum dwell has passed
            now = time.time()
            href = None

            if now - page_start_time >= MIN_TIME_BEFORE_CLICK:
                href = click_internal(driver, persona, visited, return_href=True)
            else:
                log(
                    "[EXPLORE] Too early to click ({}s < MIN_TIME_BEFORE_CLICK {}s)".format(
                        int(now - page_start_time), MIN_TIME_BEFORE_CLICK
                    )
                )

            if href:
                if is_safe_url(href):
                    clicks += 1
                    dwell = random.uniform(5, 15)
                    log("[EXPLORE] dwell {:.1f}s after click".format(dwell))
                    time.sleep(dwell)
                    # reset page_start_time for new page
                    page_start_time = time.time()
                else:
                    log("[SKIP] unsafe URL {}".format(href))

            # pacing between loops
            time.sleep(random.uniform(1.0, 2.0))

    log("[SESSION] Completed")
