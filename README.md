# 🌐 Tallbot — Human-Like Traffic Engine for the Sumcoin Ecosystem

Tallbot is a **persona-driven, Selenium-based traffic engine** designed to browse a set of Sumcoin-related websites in a way that looks and feels **human**:

- It scrolls like a person.
- It hesitates and “reads”.
- It hovers ads and *occasionally* clicks them.
- It explores internal links while avoiding login/reset/admin traps.
- It can run on **Firefox or Chrome**, **desktop or mobile**, and under **Xvfb** on a headless server.

This document explains:

1. What Tallbot does and why it works  
2. How the browsing logic is structured (personas, actions, sessions)  
3. How each file fits into the system  
4. How to configure domains, entry points, and behavior  
5. How to run it (locally and on a headless server)  
6. What changed compared to the prior codebase  

---

## ⚠️ Disclaimer / Ethics

This code is provided for **educational and testing purposes only**.

You are responsible for complying with:

- Website terms of service  
- Local laws and regulations  
- Fair-use and acceptable-use policies  

Do **not** use this to attack, spam, or harass websites.

---

## 🧠 High-Level Overview

Tallbot’s job is to behave like a **real user** visiting your own properties.

For each run:

1. **Choose a persona**  
   A persona encodes behavior: mobile vs desktop bias, scroll speed, hesitation level, ad interest, exploration rate, and dwell time.

2. **Pick a browser + user agent**  
   - Chooses **Firefox or Chrome** (weighted by config).  
   - Chooses a **mobile or desktop user agent** based on the persona’s `mobile_bias`.

3. **Optionally start Xvfb (virtual display)**  
   - Allows full browsers to run on headless servers.

4. **Run one or more sessions**  
   For each session:
   - Randomly select **2–4 configured domains** (e.g. `sumcoinindex.com`, `sumcoinmarketplace.com`, `sumcoin.org`).
   - For each domain:
     - Pick a random **entry point** (e.g. `/`, `/transactions/`, `/listings/`).
     - Load the page and wait for the DOM to be “ready”.
     - For a **dwell window** (per domain):
       - Scroll (desktop) or swipe (mobile).
       - Pause briefly to “read”.
       - Find ad-like elements, hover them, and very occasionally click them.
       - Find internal links and occasionally click them, only if they are **safe**.
       - Avoid login/reset/admin/cart URLs.
       - Avoid wandering deeply on external ad sites.

5. **Log everything** to `traffic_engine.log` for inspection.

Every run is **randomized but constrained**, so it feels natural while staying inside guardrails.

---

## 🧩 Project Structure

Recommended directory layout:

```text
.
├── requirements.txt
├── config.py
├── persona.py
├── human_actions.py
├── driver_setup.py
├── session.py
├── utils.py
└── main.py
File	Purpose
requirements.txt	Python dependencies (Selenium + pyvirtualdisplay).
config.py	Global configuration: domains, entry points, timing, UA pools, base ad click settings.
persona.py	Persona definitions (behavioral profiles) and selector.
human_actions.py	Scrolling, hesitation, ad hover/click logic, internal link exploration.
driver_setup.py	Browser + Xvfb setup, user agent injection based on persona.
session.py	Main session loop: site selection, per-site dwell, interaction orchestration.
utils.py	Logging utilities (console + file).
main.py	CLI entrypoint: parses args, runs N sessions, coordinates everything.

⚙️ Installation
1. Python Environment
Use a virtual environment if possible:

bash
Copy code
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
This installs:

selenium

pyvirtualdisplay

2. Browser Drivers
You need the appropriate WebDriver binaries available on your PATH:

Firefox → geckodriver

Chrome → chromedriver

Install via your package manager or download from official sources.

3. Xvfb (for headless servers)
On Ubuntu/Debian:

bash
Copy code
sudo apt-get update
sudo apt-get install -y xvfb
Tallbot uses pyvirtualdisplay to wrap Xvfb when you pass --xvfb to main.py.

⚙️ Configuration (config.py)
config.py is the central control panel for Tallbot’s behavior.

Domains & Entry Points
These define what sites Tallbot knows about and where it can start on each.

python
Copy code
DOMAINS = [
    "https://sumcoinindex.com",
    "https://sumcoinmarketplace.com",
    "https://www.sumcoin.org",
]

ENTRY_POINTS = {
    "https://www.sumcoin.org": [
        "/",
        "/open-price-feed/",
        "/blog/",
        "/category/sumcoin/",
    ],
    "https://sumcoinindex.com": [
        "/",
        "/transactions/",
        "/markets/",
    ],
    "https://sumcoinmarketplace.com": [
        "/",
        "/listings/",
        "/sumcoin/",
    ],
}
To add a new site:

Add its base URL to DOMAINS.

Add an entry in ENTRY_POINTS using the same key ("https://example.com") with a list of paths.

Tallbot will randomly pick 2–4 domains per session, and for each domain, a random entry point.

User Agent Pools
Tallbot uses realistic user agents to avoid looking like a bot.

python
Copy code
MOBILE_USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) ...",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) ...",
    ...
]

DESKTOP_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) ...",
    ...
]
Personas reference these via index pools (ua_mobile_pool, ua_desktop_pool), so different personas appear as different “types” of devices/browsers.

Browser Selection Weights
You can control how often Firefox vs Chrome is used:

python
Copy code
BROWSER_WEIGHTS = {
    "firefox": 0.7,
    "chrome": 0.3,
}
main.py will use these by default (via choose_browser_name()).

You can override this per run using CLI: --browser firefox or --browser chrome.

Timing & Dwell
These define baseline behavior, which is then scaled by each persona.

python
Copy code
BASE_MIN_DWELL = 90         # min seconds per domain
BASE_MAX_DWELL = 240        # max seconds per domain
BASE_MAX_CLICKS = 4         # max internal clicks per domain
BASE_SCROLL_STEP = (350, 750)  # scroll delta in px

LOG_FILE = "traffic_engine.log"
For each domain visit:

A random dwell time in [BASE_MIN_DWELL, BASE_MAX_DWELL] is chosen.

This value is then multiplied by persona.dwell_multiplier.

Example:
If BASE_MIN_DWELL=90, BASE_MAX_DWELL=240, and dwell_multiplier=1.5, dwell per domain becomes ~135–360 seconds.

Ad Click Base Probability
Tallbot is designed to hover ads frequently but click them rarely.

python
Copy code
AD_CLICK_CHANCE = 0.055   # ~5.5% base per *ad-hover* event
Actual click probability per ad hover is:

text
Copy code
p_click = AD_CLICK_CHANCE + persona.ad_click_chance
…and capped at 1.0.
This lets you control global behavior and fine-tune per-persona differences.

🎭 Personas (persona.py)
A persona describes a browsing style:

python
Copy code
class Persona:
    def __init__(
        self,
        name,
        description,
        mobile_bias,
        scroll_speed,
        hesitation,
        ad_hover_rate,
        explore_rate,
        dwell_multiplier,
        ua_mobile_pool,
        ua_desktop_pool,
        hover_min=0.4,
        hover_max=2.4,
        ad_click_chance=0.0,
    ):
        ...
Key fields:

Field	Meaning
name	Human-readable label.
description	Short explanation of the behavior.
mobile_bias	Probability of using mobile UA (0–1).
scroll_speed	>1 = faster scrolling; <1 = slower.
hesitation	Scales reading pauses.
ad_hover_rate	Probability of hovering an ad when one is found.
explore_rate	Probability of clicking an internal link.
dwell_multiplier	Scales dwell time per domain.
ua_mobile_pool	Allowed indices into MOBILE_USER_AGENTS.
ua_desktop_pool	Allowed indices into DESKTOP_USER_AGENTS.
hover_min/max	Ad hover duration range in seconds.
ad_click_chance	Additive tweak on top of global AD_CLICK_CHANCE.

Example persona:

python
Copy code
Persona(
    name="Enthusiast Clicker",
    description="Engaged user, scrolls a lot, clicks around pretty aggressively.",
    mobile_bias=0.65,
    scroll_speed=1.4,
    hesitation=0.8,
    ad_hover_rate=0.55,
    explore_rate=0.88,
    dwell_multiplier=1.0,
    ua_mobile_pool=[0, 2, 3],
    ua_desktop_pool=[0, 2],
    hover_min=0.3,
    hover_max=1.6,
    ad_click_chance=0.015,  # +1.5% over global
)
Persona selection:

python
Copy code
PERSONAS = [ ... ]

def choose_persona():
    weights = [3, 3, 2, 2, 2]  # relative frequency of each persona
    return random.choices(PERSONAS, weights=weights, k=1)[0]
🕹 Human-Like Actions (human_actions.py)
This module implements the micro-behaviors that make Tallbot look human:

Scrolling / swiping

Pausing / hesitating

Hovering ads

Clicking internal links (on your own domains)

The main functions used by session.py are:

desktop_scroll(driver, persona)

mobile_swipe(driver, persona)

micro_hesitate(driver, persona)

hover_ads(driver, persona)

click_internal(driver, persona, visited, return_href=True)

Scrolling & Swiping
Desktop:

Random scroll amount between BASE_SCROLL_STEP.

Occasionally scrolls upward.

Delay is inversely proportional to persona.scroll_speed.

Mobile:

Smaller, more frequent scroll increments (thumb-like swipes).

Also uses persona.scroll_speed to set frequency.

Hesitation (Reading Pauses)
micro_hesitate simulates reading time:

Base range: 0.4–1.8 seconds.

Multiplied by persona.hesitation.

Logs as [HESITATE] X.XXs.

Ad Hover & Rare Click
hover_ads:

Scans <a> elements on the page and looks for:

“ad”, “ads”, “sponsored”, “promo”, “banner” in href/class/id/text.

Randomly selects up to 3 ad candidates.

For each candidate:

With probability persona.ad_hover_rate, hovers the mouse over it.

Hover duration in [persona.hover_min, persona.hover_max].

Logs [AD-HOVER] href (Xs).

After hovering:

With probability p_click = AD_CLICK_CHANCE + persona.ad_click_chance, performs a click.

Logs [AD-CLICK] href if it succeeds.

Any failures are logged but do not crash the session.

This gives:

Frequent, realistic ad hover activity,

Very rare, controlled ad clicks, and

Accurate logging that matches what actually happened.

Internal Link Clicking (On-Network Only)
click_internal(driver, persona, visited, return_href=False):

Determines the current host from driver.current_url.

If the host is not in the DOMAINS list, it logs:

text
Copy code
[CLICK] external host some-ad-site.com → no further internal clicks
…and refuses to click new links there. This stops the bot from going on deep journeys through ad networks.

If host is allowed:

Uses persona.explore_rate to decide whether to explore on this iteration.

Filters links:

Skips previously visited URLs.

Skips javascript:, #, mailto:, tel:.

Only follows links that stay on the same host.

Moves mouse to the element and clicks via ActionChains.

Adds URL to the visited set.

Logs [CLICK] → href.

🧪 Session Logic (session.py)
run_session(driver, persona, is_mobile) coordinates a single session.

Flow:

Select domains for this session

python
Copy code
max_depth = random.randint(2, 4)
sites = random.sample(DOMAINS, k=max_depth)
For each domain in sites:

Select a random entry path from ENTRY_POINTS[domain].

Join domain + path to build the entry URL.

Load using safe_get(driver, url):

Retries up to 3 times, with randomized delays.

Use WebDriverWait to wait for DOM readyState == "complete".

Compute dwell time per domain

python
Copy code
dwell_base = random.randint(BASE_MIN_DWELL, BASE_MAX_DWELL)
end_time = time.time() + dwell_base * persona.dwell_multiplier
clicks = 0
Interaction loop (until dwell time expires or click limit reached):

Scroll or swipe:

desktop_scroll(driver, persona) if is_mobile=False

mobile_swipe(driver, persona) if is_mobile=True

Hesitate:

micro_hesitate(driver, persona)

Ad hover:

hover_ads(driver, persona)

Internal exploration:

href = click_internal(driver, persona, visited, return_href=True)

If href exists:

Check is_safe_url(href) to avoid:

wp-login, wp-admin, lostpassword, reset, admin, checkout, cart, signin, signup, login, etc.

If safe:

Increment clicks.

Dwell 5–15 seconds ([EXPLORE] dwell X.Xs).

If blocked:

Log [SKIP] Blocked sensitive URL: href.

Each loop ends with a small pacing delay: 1–2 seconds.

After domains are processed, logs [SESSION] Completed.

🧰 Driver Setup & Xvfb (driver_setup.py)
create_driver(persona, use_xvfb=False, browser_name=None) returns:

driver (Selenium WebDriver)

display (Xvfb display or None)

is_mobile (whether we chose a mobile UA)

Key steps:

Decide mobile vs desktop:

python
Copy code
is_mobile = random.random() < persona.mobile_bias
Choose a user agent based on persona pools and is_mobile.

Optionally start Xvfb:

python
Copy code
if use_xvfb:
    display = Display(visible=False, size=(1920, 1080))
    display.start()
    log("[XVFB] virtual display started")
Choose browser:

If browser_name is None → use weighted BROWSER_WEIGHTS from config.py.

Otherwise, use the CLI-specified browser.

Create the actual driver:

_create_chrome sets UA, window size, and a few anti-automation flags.

_create_firefox sets UA via prefs.

Xvfb allows Tallbot to run full non-headless browsers on servers with no display attached.

🏁 Entry Point & CLI (main.py)
main.py is the script you actually run.

CLI Options
Run:

bash
Copy code
python3 main.py --help
You’ll see:

--sessions N
Number of independent sessions to run sequentially.
Default: 1.

--xvfb
Use Xvfb (virtual display).
Good for servers / headless environments.

--browser {auto,firefox,chrome}

auto (default): use the weights in config.BROWSER_WEIGHTS.

firefox or chrome: force a specific browser.

--rest-min SECONDS
Minimum rest time between sessions.
Default: 15.

--rest-max SECONDS
Maximum rest time between sessions.
Default: 45.

Example Commands
Single session, auto browser, no Xvfb:

bash
Copy code
python3 main.py --sessions 1
Single session, Firefox under Xvfb (headless server):

bash
Copy code
python3 main.py --sessions 1 --xvfb --browser firefox
Five sessions, with rest 30–90 seconds between each:

bash
Copy code
python3 main.py --sessions 5 --xvfb --rest-min 30 --rest-max 90
main.py will:

Parse CLI arguments.

For each session:

Choose a persona.

Create a driver (and optionally Xvfb display).

Call run_session(driver, persona, is_mobile).

Clean up driver and display.

Sleep for a random rest interval between rest-min and rest-max (except after the last session).

📝 Logging (utils.py)
Logging is simple and robust:

Logs go to stdout and to LOG_FILE (from config.py).

Each line is prefixed with a UTC timestamp like [YYYY-MM-DD HH:MM:SS].

Logging errors are swallowed silently to avoid crashing the bot.

Example log:

text
Copy code
[2025-11-29 20:12:03] [START] Tallbot starting with 3 session(s), xvfb=True, browser=auto
[2025-11-29 20:12:03] [RUN] Session 1 with persona: Enthusiast Clicker
[2025-11-29 20:12:04] [BROWSER] firefox (mobile=True)
[2025-11-29 20:12:07] [ENTRY] https://www.sumcoin.org/open-price-feed/
[2025-11-29 20:12:08] [SCROLL] desktop 523
[2025-11-29 20:12:09] [HESITATE] 0.93s
[2025-11-29 20:12:10] [AD-HOVER] https://ads.example.com/... (1.34s)
[2025-11-29 20:12:12] [CLICK] → https://www.sumcoin.org/blog/some-post/
[2025-11-29 20:12:28] [SESSION] Completed
🔄 Changes Compared to the Prior Codebase
This version is not just a light refactor — it’s a structured, behavior-focused upgrade.

1. Clear Separation of Concerns
Before:
Behavior and control logic overlapped across multiple files, making it hard to change one aspect (e.g., ad behavior) without touching others.

Now:

config.py — All global knobs in one place.

persona.py — All behavioral profiles.

human_actions.py — All low-level behavior (scrolling/hovering/clicking).

session.py — High-level “where to go next” and dwell logic.

driver_setup.py — Browser/Xvfb/UA setup only.

This makes future edits (like adding new personas or changing timing) much easier and safer.

2. Honest, Tunable Ad Interaction
Before:

Logging and behavior could get out of sync (e.g., saying it was hovering when actually clicking).

Ad clicks were less strictly controlled and were more likely to send the bot wandering on external domains.

Now:

Ad hover and ad click are separate, explicit behaviors.

Logs precisely reflect actions:

[AD-HOVER] only when we hover.

[AD-CLICK] only when we actually click.

Click probability is:

Globally controlled by AD_CLICK_CHANCE.

Tuned per persona with ad_click_chance.

3. No More “Ad Rabbit Holes”
Before:

After clicking an ad, the bot might continue exploring the external site, creating unnatural, unfocused behavior.

Now:

click_internal checks the current host against your own DOMAINS.

If the host is external, it refuses to click further links and logs this clearly.

It may still scroll / hover a bit (which is natural), but it does not do deep multi-click explorations on ad properties.

4. Personas Actually Drive Behavior
Before:

Persona attributes existed but weren’t tightly wired to all behaviors consistently.

Now:

scroll_speed affects scroll/swipe frequency.

hesitation affects reading pauses.

ad_hover_rate controls how often ads are hovered.

hover_min / hover_max control hover duration.

explore_rate controls internal click frequency.

dwell_multiplier scales per-domain dwell times.

ua_mobile_pool / ua_desktop_pool directly determine UA randomization.

The result is that each persona feels like a distinct type of user, not just a label.

5. Centralized, Understandable Configuration
Before:

Some behavior was defined in multiple places or implied by code.

Now:

Domains, entry points, UA pools, browser weights, dwell timings, and base ad click rate are all centralized in config.py.

Persona-level differences are all centralized in persona.py.

This makes it much easier for someone new to the project to see what it does and how to change it.

6. Xvfb Support Preserved & Simplified
Before:

Xvfb was supported but intertwined with other logic.

Now:

Xvfb is a simple, optional flag (--xvfb) passed into create_driver.

The lifetime of the Xvfb display is cleanly managed (start before driver, stop after).

➕ Extending Tallbot
Some ideas for evolution:

Add personas specific to roles (e.g., “Merchant”, “Trader”, “Investor”).

Add a “safe outbound” list for limited exploration of external sites (e.g., X/Twitter, GitHub, YouTube).

Add simple page-type detection (e.g., per-URL rules) to vary behavior depending on the kind of page:

Product/listing pages

Blog articles

Landing pages

🚀 Quick Start
Put all files in a folder:

requirements.txt

config.py

persona.py

human_actions.py

driver_setup.py

session.py

utils.py

main.py

Install dependencies:

bash
Copy code
pip install -r requirements.txt
Ensure geckodriver and/or chromedriver are installed.

Run:

bash
Copy code
python3 main.py --sessions 1 --xvfb
Watch the log output and traffic_engine.log to see exactly what Tallbot is doing.ß