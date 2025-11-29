# human_actions.py
import random
import time
from urllib.parse import urlparse, urljoin

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

from config import DOMAINS, BASE_SCROLL_STEP, AD_CLICK_CHANCE
from utils import log


# -------------------------------------------------------------------
# HOST / DOMAIN CONFIG
# -------------------------------------------------------------------
ALLOWED_HOSTS = set()
for d in DOMAINS:
    try:
        host = urlparse(d).hostname
        if host:
            ALLOWED_HOSTS.add(host)
    except Exception:
        pass

# Ad / popup heuristics
AD_KEYWORDS = ["ad", "ads", "sponsored", "promo", "banner"]
POPUP_CLASS_HINTS = ["modal", "popup", "overlay", "lightbox"]
CLOSE_TEXT_HINTS = [
    "close",
    "dismiss",
    "no thanks",
    "no, thanks",
    "×",
    "x",
    "got it",
    "accept",
]


# -------------------------------------------------------------------
# SCROLLING / SWIPING / HESITATION
# -------------------------------------------------------------------
def desktop_scroll(driver, persona):
    dy = random.randint(BASE_SCROLL_STEP[0], BASE_SCROLL_STEP[1])
    # sometimes scroll up
    if random.random() < 0.2:
        dy = -dy

    try:
        driver.execute_script("window.scrollBy(0, arguments[0]);", dy)
        log("[SCROLL] desktop dy={}".format(dy))
    except Exception as e:
        log("[SCROLL-ERROR] {}".format(e))

    base_delay = random.uniform(0.4, 1.2)
    delay = base_delay / max(persona.scroll_speed, 0.25)
    time.sleep(delay)


def mobile_swipe(driver, persona):
    dy = random.randint(220, 520)
    if random.random() < 0.25:
        dy = -dy

    try:
        driver.execute_script("window.scrollBy(0, arguments[0]);", dy)
        log("[SWIPE] mobile dy={}".format(dy))
    except Exception as e:
        log("[SWIPE-ERROR] {}".format(e))

    base_delay = random.uniform(0.3, 0.9)
    delay = base_delay / max(persona.scroll_speed, 0.25)
    time.sleep(delay)


def micro_hesitate(driver, persona):
    base = random.uniform(0.4, 1.8)
    delay = base * persona.hesitation
    log("[HESITATE] {:.2f}s".format(delay))
    time.sleep(delay)


# -------------------------------------------------------------------
# POPUP / MODAL HANDLING
# -------------------------------------------------------------------
def handle_popups(driver, persona):
    """
    Best-effort: if there's a typical overlay/modal with a clear 'close' control,
    hover + click it. Very defensive to avoid clicking random big elements.
    """
    try:
        candidates = driver.find_elements(By.XPATH, "//button | //div | //span")
    except Exception:
        return

    for el in candidates:
        try:
            cls = (el.get_attribute("class") or "").lower()
            aria = (el.get_attribute("aria-label") or "").lower()
            text = (el.text or "").strip().lower()
            blob = " ".join([cls, aria, text])

            if not blob:
                continue

            if not any(h in blob for h in CLOSE_TEXT_HINTS):
                continue

            # Don't click huge containers; we want small close buttons
            size = el.size or {}
            if size.get("width", 0) > 600 and size.get("height", 0) > 400:
                continue

            actions = ActionChains(driver)
            actions.move_to_element(el).perform()
            log("[POPUP] Close control hovered: '{}'".format(text or aria or cls))
            time.sleep(random.uniform(0.3, 0.9))
            el.click()
            log("[POPUP] Closed overlay/pop-up")
            time.sleep(random.uniform(1.0, 2.0))
            return
        except StaleElementReferenceException:
            continue
        except WebDriverException:
            continue


# -------------------------------------------------------------------
# AD HOVER + CLICK
# -------------------------------------------------------------------
def _find_ad_candidates(driver):
    try:
        anchors = driver.find_elements(By.TAG_NAME, "a")
    except Exception as e:
        log("[AD] find_elements error: {}".format(e))
        return []

    candidates = []
    for a in anchors:
        try:
            href = a.get_attribute("href") or ""
            cls = a.get_attribute("class") or ""
            tid = a.get_attribute("id") or ""
            text = (a.text or "").lower()
            blob = " ".join([href, cls, tid, text]).lower()
            if any(k in blob for k in AD_KEYWORDS):
                candidates.append(a)
        except StaleElementReferenceException:
            continue
        except Exception:
            continue

    return candidates


def hover_ads(driver, persona):
    candidates = _find_ad_candidates(driver)
    if not candidates:
        return

    random.shuffle(candidates)
    limit = min(len(candidates), 3)

    for el in candidates[:limit]:
        if random.random() > persona.ad_hover_rate:
            continue

        try:
            actions = ActionChains(driver)
            actions.move_to_element(el).perform()

            href = el.get_attribute("href") or ""
            hover_time = random.uniform(persona.hover_min, persona.hover_max)
            log("[AD-HOVER] {} ({:.2f}s)".format(href, hover_time))
            time.sleep(hover_time)

            # Click probability
            p_click = AD_CLICK_CHANCE + getattr(persona, "ad_click_chance", 0.0)
            if p_click > 1.0:
                p_click = 1.0

            if random.random() < p_click:
                el.click()
                log("[AD-CLICK] {}".format(href))
                time.sleep(random.uniform(2.0, 5.0))
                return  # don't chain multiple ad clicks in a row
        except StaleElementReferenceException:
            continue
        except WebDriverException as e:
            log("[AD-ERROR] {}".format(e))
            continue


# -------------------------------------------------------------------
# INTERNAL LINK CLICKING (STAYS ON SAME HOST)
# -------------------------------------------------------------------
def click_internal(driver, persona, visited, return_href=False):
    """
    Click a single internal link on the same host, respecting persona.explore_rate
    and ALLOWED_HOSTS. Returns the href if return_href is True, else True/None.
    """
    # persona gate: often skip exploration this loop
    if random.random() > persona.explore_rate:
        log("[CLICK] Skipped this loop (explore_rate gate)")
        return None

    try:
        current_url = driver.current_url
        current_host = urlparse(current_url).hostname
    except Exception:
        return None

    if current_host not in ALLOWED_HOSTS:
        log("[CLICK] current host '{}' not in ALLOWED_HOSTS -> no internal clicks".format(current_host))
        return None

    try:
        anchors = driver.find_elements(By.TAG_NAME, "a")
    except Exception as e:
        log("[CLICK] Error finding anchors: {}".format(e))
        return None

    random.shuffle(anchors)

    for a in anchors:
        try:
            href_raw = a.get_attribute("href")
            if not href_raw:
                continue

            if href_raw.startswith("javascript:") or href_raw.startswith("#"):
                continue

            full = urljoin(current_url, href_raw)

            if full in visited:
                continue

            host = urlparse(full).hostname
            if host != current_host:
                continue

            actions = ActionChains(driver)
            actions.move_to_element(a).perform()
            log("[CLICK] → {}".format(full))
            a.click()
            visited.add(full)

            time.sleep(random.uniform(1.0, 3.0))
            return full if return_href else True

        except StaleElementReferenceException:
            continue
        except WebDriverException as e:
            log("[CLICK-ERROR] {}".format(e))
            continue

    log("[CLICK] No suitable internal link found")
    return None
