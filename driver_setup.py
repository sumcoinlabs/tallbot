# driver_setup.py
import random

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from config import MOBILE_USER_AGENTS, DESKTOP_USER_AGENTS, choose_browser_name
from utils import log


def _choose_user_agent(persona, is_mobile):
    """
    Pick a user-agent string based on persona and mobile/desktop mode.
    """
    if is_mobile:
        pool = persona.ua_mobile_pool or list(range(len(MOBILE_USER_AGENTS)))
        idx = random.choice(pool)
        ua = MOBILE_USER_AGENTS[idx]
        log("[UA] mobile index {} -> {}".format(idx, ua))
        return ua
    else:
        pool = persona.ua_desktop_pool or list(range(len(DESKTOP_USER_AGENTS)))
        idx = random.choice(pool)
        ua = DESKTOP_USER_AGENTS[idx]
        log("[UA] desktop index {} -> {}".format(idx, ua))
        return ua


def _create_chrome(user_agent, is_mobile):
    opts = ChromeOptions()

    # viewport size
    if is_mobile:
        opts.add_argument("--window-size=430,932")  # phone-ish
    else:
        opts.add_argument("--start-maximized")

    # UA
    opts.add_argument("--user-agent={}".format(user_agent))

    # Hide "Chrome is being controlled by automated test software"
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)

    # Reduce obvious automation signals
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    # NOTE: not using --headless so GUI & Xvfb both work
    driver = webdriver.Chrome(options=opts)

    # Extra stealth: kill navigator.webdriver
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    // marker so we know script injected
                    window.__tallbot_stealth = true;
                """
            },
        )
    except Exception as e:
        log("[WARN] CDP stealth injection failed: {}".format(e))

    return driver


def _create_firefox(user_agent, is_mobile):
    opts = FirefoxOptions()

    if is_mobile:
        # light DPI tweak to feel more phone-like
        opts.set_preference("layout.css.devPixelsPerPx", "1.0")

    opts.set_preference("general.useragent.override", user_agent)

    driver = webdriver.Firefox(options=opts)
    return driver


def create_driver(persona, use_xvfb=False, browser_name=None):
    """
    Creates a Selenium driver with:
      - persona-based UA
      - mobile/desktop decision based on persona.mobile_bias
      - optional Xvfb virtual display

    Returns: (driver, display, is_mobile)
    """
    is_mobile = random.random() < persona.mobile_bias
    user_agent = _choose_user_agent(persona, is_mobile)

    display = None
    if use_xvfb:
        display = Display(visible=False, size=(1920, 1080))
        display.start()
        log("[XVFB] virtual display started")

    if browser_name is None or browser_name == "auto":
        browser_name = choose_browser_name()
    browser_name = str(browser_name).lower()

    log("[BROWSER] {} (mobile={})".format(browser_name, is_mobile))

    if browser_name == "chrome":
        driver = _create_chrome(user_agent, is_mobile)
    else:
        driver = _create_firefox(user_agent, is_mobile)

    return driver, display, is_mobile
