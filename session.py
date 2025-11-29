# session.py
import random
import time
from urllib.parse import urljoin
from selenium.webdriver.support.ui import WebDriverWait

from config import *
from human_actions import *
from utils import log


BLOCKED_KEYWORDS = [
    "wp-login", "wp-admin", "lostpassword", "reset", "admin",
    "checkout", "cart", "signin", "signup", "login",
    "rates", "cdn-cgi", "privacy", "support", "terms"
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

    # pick 2–4 domains
    max_depth = random.randint(2, 4)
    sites = random.sample(DOMAINS, k=max_depth)
    log("[SESSION] Sites: {}".format(" → ".join(sites)))

    for domain in sites:
        entry = random.choice(ENTRY_POINTS.get(domain, ["/"]))
        url = urljoin(domain, entry)

        if not safe_get(driver, url):
            continue

        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except:
            log("[WARN] Page load incomplete")

        log("[ENTRY] {}".format(url))

        end_time = time.time() + random.randint(
            BASE_MIN_DWELL, BASE_MAX_DWELL
        ) * persona.dwell_multiplier

        clicks = 0

        while time.time() < end_time and clicks < BASE_MAX_CLICKS:

            # scrolling
            if is_mobile:
                mobile_swipe(driver, persona)
            else:
                desktop_scroll(driver, persona)

            micro_hesitate(driver, persona)
            hover_ads(driver, persona)

            href = click_internal(driver, persona, visited, return_href=True)

            if href:
                if is_safe_url(href):
                    clicks += 1
                    dwell = random.uniform(5, 15)
                    log("[EXPLORE] Dwell {:.1f}s".format(dwell))
                    time.sleep(dwell)
                else:
                    log("[SKIP] unsafe URL {}".format(href))

            time.sleep(random.uniform(1.0, 2.0))

    log("[SESSION] Completed")
