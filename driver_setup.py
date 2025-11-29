# driver_setup.py
#
# AUTO-INSTALL + AUTO-UPGRADE for Chrome / Firefox / Drivers
# Works on all Ubuntu versions without breaking daemons.
# Strict upgrade mode: outdated geckodriver → auto-fix.
# Mobile bias: 79% mobile / 21% desktop.

import os
import shutil
import random
import subprocess
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from pyvirtualdisplay import Display

from persona import choose_persona
from config import MOBILE_UAS, DESKTOP_UAS
from utils import log


# ======================================================================
# SHELL UTIL
# ======================================================================

def run(cmd):
    """Run a shell command safely, capturing output."""
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode()
        return True, out
    except Exception as e:
        return False, str(e)


# ======================================================================
# INSTALL HELPERS (Ubuntu-safe)
# ======================================================================

def ensure_xvfb():
    """Install Xvfb if missing."""
    if shutil.which("Xvfb"):
        return
    log("[FIX] Installing Xvfb...")
    run("sudo apt update -y")
    run("sudo apt install -y xvfb")
    log("[FIX] Xvfb installed.")


def ensure_google_chrome():
    """Install Chrome if missing."""
    if shutil.which("google-chrome"):
        return
    log("[FIX] Installing Google Chrome...")
    run("wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O chrome.deb")
    run("sudo apt install -y ./chrome.deb")
    run("rm chrome.deb")
    log("[FIX] Google Chrome installed.")


def ensure_chromedriver():
    """Install Chromedriver if missing."""
    if shutil.which("chromedriver"):
        return

    log("[FIX] Installing ChromeDriver...")
    run("sudo apt update -y")
    run("sudo apt install -y chromium-chromedriver")

    # If still missing → fallback to manual install
    if shutil.which("chromedriver"):
        log("[FIX] ChromeDriver installed.")
        return

    log("[WARN] chromium-chromedriver unavailable, downloading manually...")
    ok, out = run("wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
    if ok:
        latest = out.strip()
        run(f"wget https://chromedriver.storage.googleapis.com/{latest}/chromedriver_linux64.zip -O cdrv.zip")
        run("unzip cdrv.zip")
        run("sudo mv chromedriver /usr/bin/chromedriver")
        run("sudo chmod +x /usr/bin/chromedriver")
        run("rm cdrv.zip")
        log("[FIX] ChromeDriver installed via fallback.")


def ensure_firefox():
    """Install Firefox if missing."""
    if shutil.which("firefox"):
        return
    log("[FIX] Installing Firefox...")
    run("sudo apt update -y")
    run("sudo apt install -y firefox")
    log("[FIX] Firefox installed.")


# ======================================================================
# STRICT GECKODRIVER VERSION CHECK (Option B)
# ======================================================================

def get_firefox_version():
    ok, out = run("firefox --version")
    if not ok:
        return None
    # Format: "Mozilla Firefox 136.0"
    try:
        return int(out.split()[2].split(".")[0])
    except:
        return None


def get_geckodriver_version():
    ok, out = run("geckodriver --version")
    if not ok:
        return None
    # Format: "geckodriver 0.36.0 ..."
    try:
        return float(out.split()[1])
    except:
        return None


def upgrade_geckodriver():
    """Force install the newest geckodriver."""
    log("[FIX] Installing latest GeckoDriver...")

    ok, out = run("wget -qO- https://api.github.com/repos/mozilla/geckodriver/releases/latest")
    if not ok:
        log("[WARN] Could not fetch GeckoDriver release list.")
        return

    try:
        tag = json.loads(out)["tag_name"]
        tar_url = f"https://github.com/mozilla/geckodriver/releases/download/{tag}/geckodriver-{tag}-linux64.tar.gz"

        run(f"wget {tar_url} -O g.tar.gz")
        run("tar -xzf g.tar.gz")
        run("sudo mv geckodriver /usr/bin/geckodriver")
        run("sudo chmod +x /usr/bin/geckodriver")
        run("rm g.tar.gz")

        log(f"[FIX] GeckoDriver upgraded to {tag}.")
    except Exception as e:
        log(f"[WARN] GeckoDriver upgrade failed: {e}")


def ensure_geckodriver():
    """Ensure GeckoDriver exists AND is correct version."""
    firefox_ver = get_firefox_version()
    if not firefox_ver:
        return

    # Required version for Firefox (strict)
    required = 0.36

    installed = get_geckodriver_version()

    # If missing, install immediately
    if installed is None:
        log("[FIX] GeckoDriver missing → installing.")
        upgrade_geckodriver()
        return

    # Version too old → replace automatically
    if installed < required:
        log(f"[FIX] GeckoDriver {installed} too old for Firefox {firefox_ver}. Upgrading…")
        run("sudo rm /usr/bin/geckodriver")
        upgrade_geckodriver()
        return

    # Version mismatch warning
    if firefox_ver >= 130 and installed < 0.36:
        log(f"[FIX] GeckoDriver {installed} is not optimal for Firefox {firefox_ver}. Upgrading…")
        run("sudo rm /usr/bin/geckodriver")
        upgrade_geckodriver()
        return

    # Otherwise OK
    return


# ======================================================================
# Choose Browser (persona influence)
# ======================================================================

def choose_browser(persona):
    chrome_weight = 0.70
    firefox_weight = 0.30

    if persona.name == "Desktop Researcher":
        firefox_weight += 0.10
    if persona.name == "Fast Clicker":
        chrome_weight += 0.05
    if persona.name == "Mobile Young User":
        chrome_weight += 0.10

    total = chrome_weight + firefox_weight
    return random.choices(
        ["chrome", "firefox"],
        weights=[chrome_weight / total, firefox_weight / total]
    )[0]


# ======================================================================
# Persona + UA
# ======================================================================

def load_persona():
    p = choose_persona()
    log(f"[PERSONA] {p.name} — {p.description}")
    return p


def pick_user_agent(persona, mobile_mode):
    pool = persona.ua_mobile_pool if mobile_mode else persona.ua_desktop_pool
    src = MOBILE_UAS if mobile_mode else DESKTOP_UAS
    return src[random.choice(pool)]


# ======================================================================
# CREATE CHROME DRIVER
# ======================================================================

def build_chrome_driver(ua, mobile_mode, use_xvfb, force_gui):
    opts = ChromeOptions()

    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-infobars")
    opts.add_argument(f"--user-agent={ua}")
    opts.add_argument("--disable-blink-features=AutomationControlled")

    if mobile_mode:
        opts.add_argument("--window-size=412,915")
        log("[DEVICE] Mobile mode")
    else:
        opts.add_argument("--start-maximized")
        log("[DEVICE] Desktop mode")

    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    if use_xvfb and not force_gui:
        Display(visible=0, size=(1366, 768)).start()
        log("[DISPLAY] Xvfb started")
    elif not force_gui:
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1366,768")
        log("[MODE] Headless (Chrome)")

    driver = webdriver.Chrome(options=opts)

    driver.execute_script("Object.defineProperty(navigator,'webdriver',{get:()=>false});")

    return driver


# ======================================================================
# CREATE FIREFOX DRIVER
# ======================================================================

def build_firefox_driver(ua, mobile_mode, use_xvfb, force_gui):
    opts = FirefoxOptions()
    opts.set_preference("general.useragent.override", ua)
    opts.set_preference("dom.webdriver.enabled", False)

    if not force_gui:
        opts.headless = not use_xvfb

    if use_xvfb and not force_gui:
        Display(visible=0, size=(1366, 768)).start()
        log("[DISPLAY] Xvfb started (Firefox)")

    try:
        return webdriver.Firefox(options=opts)
    except Exception as e:
        log(f"[WARN] Firefox failed → fallback to Chrome: {e}")
        return None


# ======================================================================
# DRIVER FACTORY
# ======================================================================

def make_driver(use_xvfb=False, force_gui=False):

    persona = load_persona()

    # 79% mobile bias
    mobile_mode = random.random() < 0.79

    ua = pick_user_agent(persona, mobile_mode)

    # AUTO FIX ENVIRONMENT
    if use_xvfb:
        ensure_xvfb()
    ensure_google_chrome()
    ensure_chromedriver()
    ensure_firefox()
    ensure_geckodriver()

    # Choose browser
    browser = choose_browser(persona)
    log(f"[BROWSER] Selected: {browser}")

    # Try Firefox first, fallback to Chrome
    if browser == "firefox":
        driver = build_firefox_driver(ua, mobile_mode, use_xvfb, force_gui)
        if driver:
            return driver, persona

    # Chrome fallback
    driver = build_chrome_driver(ua, mobile_mode, use_xvfb, force_gui)
    return driver, persona
