# human_actions.py
# -------------------------------------------------------------------
# HUMAN-LIKE BROWSING ACTIONS (scrolling, hesitation, ad hover, link click)
# Fully updated to avoid stale-element crashes
# -------------------------------------------------------------------

import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException

from utils import log
from config import BASE_SCROLL_STEP, DOMAINS, AD_CLICK_CHANCE


# -------------------------------------------------------------------
# MOBILE TOUCH SCROLL
# -------------------------------------------------------------------

def mobile_swipe(driver, persona):
    """Simulate mobile finger swipe."""
    step = random.randint(BASE_SCROLL_STEP[0], BASE_SCROLL_STEP[1])
    duration = random.uniform(0.25, 0.55)

    driver.execute_script(f"window.scrollBy(0, {step});")
    time.sleep(duration * persona.scroll_speed)


# -------------------------------------------------------------------
# DESKTOP SCROLL
# -------------------------------------------------------------------

def desktop_scroll(driver, persona):
    """Simulate desktop scroll wheel."""
    step = random.randint(BASE_SCROLL_STEP[0], BASE_SCROLL_STEP[1])
    driver.execute_script(f"window.scrollBy(0, {step});")

    time.sleep(random.uniform(1.0, 2.8) * persona.scroll_speed)


# -------------------------------------------------------------------
# HUMAN MICRO-HESITATION
# -------------------------------------------------------------------

def micro_hesitate(driver, persona):
    """Random small pauses to simulate human reading time."""
    if random.random() < persona.hesitation:
        t = random.uniform(0.4, 1.8)
        log(f"[HUMAN] Hesitation: {t:.2f}s")
        time.sleep(t)


# -------------------------------------------------------------------
# AD HOVER + AD CLICK
# -------------------------------------------------------------------

def hover_ads(driver, persona):
    """
    Natural ad hover behavior.
    Now includes persona-specific hover timing AND click probability.
    """

    # Persona-driven hover decision
    if random.random() > persona.ad_hover_rate:
        return

    try:
        # Look for common ad container types
        ads = driver.find_elements(By.CSS_SELECTOR, "ins, iframe, .adsbygoogle, [data-ad]")
        ads = [a for a in ads if a.is_displayed()]
    except:
        return

    if not ads:
        return

    target = random.choice(ads)

    try:
        # Scroll ad into view
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)

        # Move cursor to ad
        ActionChains(driver).move_to_element(target).perform()

        # Persona hover duration
        hover_min = getattr(persona, "hover_min", 0.45)
        hover_max = getattr(persona, "hover_max", 2.5)

        t = random.uniform(hover_min, hover_max)
        log(f"[AD] Hovering {t:.2f}s")
        time.sleep(t)

        # Persona-based click chance (fallback to global AD_CLICK_CHANCE)
        click_chance = getattr(persona, "ad_click_chance", AD_CLICK_CHANCE)

        if random.random() < click_chance:
            ActionChains(driver).move_to_element(target).click().perform()
            log("[AD] *** CLICKED AD ***")
            time.sleep(random.uniform(4, 9))  # dwell after clicking ad

    except:
        pass


# -------------------------------------------------------------------
# INTERNAL LINK CLICKING (FULLY STALE-SAFE VERSION)
# -------------------------------------------------------------------

def click_internal(driver, persona, visited, return_href=False):
    """
    Click internal links while avoiding stale-element crashes.
    - Retries up to 3 times when DOM shifts occur
    - Rescans links on every retry
    - Skips login/reset/admin/cart pages
    """

    # Persona-level decision whether to explore
    if random.random() > persona.explore_rate:
        return None if return_href else False

    # Retry loop handles stale element conditions
    for attempt in range(3):

        try:
            links = driver.find_elements(By.TAG_NAME, "a")
        except:
            return None if return_href else False

        random.shuffle(links)

        for a in links:

            # Some elements become stale instantly after scroll
            try:
                href = a.get_attribute("href")
            except StaleElementReferenceException:
                break  # re-scan links in outer loop

            if not href:
                continue

            # Stay inside our domains
            if not any(href.startswith(domain) for domain in DOMAINS):
                continue

            h = href.lower()

            # Skip unwanted pages
            blocked = [
                "login", "wp-login", "lostpassword", "reset", "forgot",
                "admin", "xmlrpc", "cart", "checkout"
            ]
            if any(x in h for x in blocked):
                continue

            # Skip previously visited links
            if href in visited:
                continue

            # Attempt click
            try:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", a
                )

                ActionChains(driver)\
                    .move_to_element(a)\
                    .pause(random.uniform(0.2, 0.6))\
                    .click()\
                    .perform()

                visited.add(href)
                log(f"[CLICK] → {href}")

                return href if return_href else True

            except StaleElementReferenceException:
                # Link became stale right as we tried to click -> retry
                break

            except Exception:
                continue

    # No valid link clicked
    return None if return_href else False
