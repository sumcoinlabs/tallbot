# human_actions.py
# -------------------------------------------------------------------
# HUMAN-LIKE BROWSING ACTIONS (scrolling, hesitation, ad hover, link click)
# Uses Persona behavior + global config values.
# -------------------------------------------------------------------

import random
import time
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException

from utils import log
from config import BASE_SCROLL_STEP, DOMAINS, AD_CLICK_CHANCE


# -------------------------------------------------------------------
# INTERNAL HELPERS
# -------------------------------------------------------------------

def _current_host(driver):
    try:
        return urlparse(driver.current_url).hostname or ""
    except Exception:
        return ""


def _allowed_hosts_from_domains():
    hosts = set()
    for d in DOMAINS:
        try:
            hosts.add(urlparse(d).hostname or "")
        except Exception:
            continue
    return {h for h in hosts if h}


ALLOWED_HOSTS = _allowed_hosts_from_domains()


# -------------------------------------------------------------------
# SCROLLING
# -------------------------------------------------------------------

def desktop_scroll(driver, persona):
    """
    Simulate desktop-style scroll:
      - scroll amount based on BASE_SCROLL_STEP + persona.scroll_speed
      - short pause between scrolls
    """
    min_step, max_step = BASE_SCROLL_STEP
    amount = random.randint(min_step, max_step)

    # scroll_speed > 1 = faster (less delay), < 1 = slower (more delay)
    delay = random.uniform(0.3, 0.8) / max(persona.scroll_speed, 0.1)

    direction = 1  # mostly downward
    if random.random() < 0.08:  # occasional up scroll
        direction = -1
        amount = random.randint(120, 320)

    try:
        driver.execute_script("window.scrollBy(0, arguments[0]);", direction * amount)
        log(f"[SCROLL] desktop {direction * amount}")
    except Exception:
        pass

    time.sleep(delay)


def mobile_swipe(driver, persona):
    """
    Simulate mobile-style swipe (smaller steps, more frequent).
    """
    min_step, max_step = BASE_SCROLL_STEP
    amount = random.randint(int(min_step * 0.5), int(max_step * 0.8))
    delay = random.uniform(0.25, 0.6) / max(persona.scroll_speed, 0.1)

    try:
        driver.execute_script("window.scrollBy(0, arguments[0]);", amount)
        log(f"[SWIPE] mobile {amount}")
    except Exception:
        pass

    time.sleep(delay)


# -------------------------------------------------------------------
# HESITATION / READING PAUSES
# -------------------------------------------------------------------

def micro_hesitate(driver, persona):
    """
    Short pause to simulate thinking/reading.
    persona.hesitation controls how long / how often.
    """
    base_min = 0.4
    base_max = 1.8
    scale = max(persona.hesitation, 0.05)

    duration = random.uniform(base_min, base_max) * scale
    log(f"[HESITATE] {duration:.2f}s")
    time.sleep(duration)


# -------------------------------------------------------------------
# AD HOVER + OPTIONAL CLICK
# -------------------------------------------------------------------

def hover_ads(driver, persona):
    """
    Find ad-like elements and hover them.
    Click only rarely, controlled by:
      - global AD_CLICK_CHANCE (config)
      - persona.ad_click_chance (per-persona tweak)
    """

    try:
        elements = driver.find_elements(By.TAG_NAME, "a")
    except Exception:
        return

    ad_candidates = []
    for el in elements:
        try:
            href = el.get_attribute("href") or ""
            cls = (el.get_attribute("class") or "").lower()
            tid = (el.get_attribute("id") or "").lower()
            txt = (el.text or "").lower()
        except StaleElementReferenceException:
            continue
        except Exception:
            continue

        blob = " ".join([href.lower(), cls, tid, txt])
        if any(k in blob for k in ["ad", "ads", "sponsored", "promo", "banner"]):
            ad_candidates.append((el, href))

    if not ad_candidates:
        return

    random.shuffle(ad_candidates)
    ad_candidates = ad_candidates[:3]  # limit per-page work

    # final per-hover click probability
    p_click = min(1.0, AD_CLICK_CHANCE + getattr(persona, "ad_click_chance", 0.0))

    for el, href in ad_candidates:
        # decide whether to hover at all
        if random.random() > getattr(persona, "ad_hover_rate", 0.1):
            continue

        try:
            actions = ActionChains(driver)
            actions.move_to_element(el).perform()

            hover_min = getattr(persona, "hover_min", 0.4)
            hover_max = getattr(persona, "hover_max", 2.4)
            duration = random.uniform(hover_min, hover_max)

            log(f"[AD-HOVER] {href} ({duration:.2f}s)")
            time.sleep(duration)
        except StaleElementReferenceException:
            continue
        except Exception:
            continue

        # maybe click the ad
        if random.random() < p_click:
            time.sleep(random.uniform(0.2, 0.8))
            try:
                el.click()
                log(f"[AD-CLICK] {href}")
            except StaleElementReferenceException:
                log("[AD-CLICK] failed: stale element")
            except Exception as e:
                log(f"[AD-CLICK] failed: {e}")


# -------------------------------------------------------------------
# INTERNAL LINK CLICKING (ON-NETWORK ONLY)
# -------------------------------------------------------------------

def click_internal(driver, persona, visited, return_href=False):
    """
    Click internal links while avoiding:
      - stale-element crashes
      - re-clicking the same href
      - wandering deeply on ad/external sites

    IMPORTANT:
      - If current host NOT in ALLOWED_HOSTS, we do NOT click further.
    """

    current_host = _current_host(driver)
    if ALLOWED_HOSTS and current_host not in ALLOWED_HOSTS:
        log(f"[CLICK] external host {current_host} → no further internal clicks")
        return None if return_href else False

    # Persona-level decision whether to explore at all this round
    if random.random() > getattr(persona, "explore_rate", 0.5):
        return None if return_href else False

    # Up to 3 retries to handle DOM shifts
    for _ in range(3):
        try:
            links = driver.find_elements(By.TAG_NAME, "a")
        except Exception:
            return None if return_href else False

        random.shuffle(links)

        for el in links:
            try:
                href = el.get_attribute("href")
                if not href:
                    continue

                # avoid previously visited URLs
                if href in visited:
                    continue

                low = href.lower()
                if low.startswith("javascript:") or low.startswith("#") or low.startswith("mailto:") or low.startswith("tel:"):
                    continue

                try:
                    target_host = urlparse(href).hostname or ""
                except Exception:
                    target_host = ""

                if target_host and target_host != current_host:
                    continue

                ActionChains(driver).move_to_element(el).pause(
                    random.uniform(0.1, 0.5)
                ).click().perform()

                visited.add(href)
                log(f"[CLICK] → {href}")

                return href if return_href else True

            except StaleElementReferenceException:
                # DOM changed; rescan
                break
            except Exception:
                continue

    return None if return_href else False
