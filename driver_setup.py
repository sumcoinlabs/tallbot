# driver_setup.py
import random

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from config import (
    MOBILE_USER_AGENTS,
    DESKTOP_USER_AGENTS,
    choose_browser_name,
)
from utils import log


def _choose_user_agent(persona, is_mobile: bool) -> str:
    """
    Pick a user-agent string based on persona and mobile/desktop mode.
    """
    if is_mobile:
        pool = persona.ua_mobile_pool or list(range(len(MOBILE_USER_AGENTS)))
        idx = random.choice(pool)
        ua = MOBILE_USER_AGENTS[idx]
        log(f"[UA] Mobile UA index {idx}")
        return ua
    else:
        pool = persona.ua_desktop_pool or list(range(len(DESKTOP_USER_AGENTS)))
        idx = random.choice(pool)
        ua = DESKTOP_USER_AGENTS[idx]
        log(f"[UA] Desktop UA index {idx}")
        return ua


def _create_chrome(user_agent: str, is_mobile: bool):
    opts = ChromeOptions()

    # viewport size
    if is_mobile:
        opts.add_argument("--window-size=430,932")  # approximate modern phone
    else:
        opts.add_argument("--start-maximized")

    # user agent
    opts.add_argument(f"--user-agent={user_agent}")

    # anti-automation flags
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    # Optional: comment out if you want visible non-headless chrome
    # (Xvfb will still provide a virtual display if used)
    # opts.add_argument("--headless=new")

    driver = webdriver.Chrome(options=opts)

    # additional stealth tweak
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
            },
        )
    except Exception:
        pass

    return driver


def _create_firefox(user_agent: str, is_mobile: bool):
    opts = FirefoxOptions()

    # Usually leave window size default or set manually
    if is_mobile:
        opts.set_preference("layout.css.devPixelsPerPx", "1.0")

    # user agent override
    opts.set_preference("general.useragent.override", user_agent)

    # optional: headless (Xvfb still works if you want a virtual display)
    # opts.add_argument("--headless")

    driver = webdriver.Firefox(options=opts)
    return driver


def create_driver(persona, use_xvfb: bool = False, browser_name: str | None = None):
    """
    Creates a Selenium driver with:
      - persona-based UA
      - mobile/desktop decision based on persona.mobile_bias
      - optional Xvfb virtual display

    Returns: (driver, display, is_mobile)
      - driver: Selenium WebDriver
      - display: Display object or None
      - is_mobile: bool
    """

    is_mobile = random.random() < persona.mobile_bias
    user_agent = _choose_user_agent(persona, is_mobile)

    display = None
    if use_xvfb:
        display = Display(visible=False, size=(1920, 1080))
        display.start()
        log("[XVFB] virtual display started")

    # which browser?
    if browser_name is None:
        browser_name = choose_browser_name()
    browser_name = browser_name.lower()

    log(f"[BROWSER] {browser_name} (mobile={is_mobile})")

    if browser_name == "chrome":
        driver = _create_chrome(user_agent, is_mobile)
    else:
        # default to firefox
        driver = _create_firefox(user_agent, is_mobile)

    return driver, display, is_mobile
