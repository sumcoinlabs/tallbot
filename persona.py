# persona.py
import random


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
        self.name = name
        self.description = description

        # Behavior weights
        self.mobile_bias = mobile_bias      # chance to pick mobile UA
        self.scroll_speed = scroll_speed    # >1 = faster scroll moves, <1 = slower
        self.hesitation = hesitation        # >1 = more frequent / longer pauses
        self.ad_hover_rate = ad_hover_rate  # chance to hover an ad when seen
        self.explore_rate = explore_rate    # chance to click an internal link
        self.dwell_multiplier = dwell_multiplier  # scales BASE_* timings

        # UA pools (indices into MOBILE_USER_AGENTS / DESKTOP_USER_AGENTS)
        self.ua_mobile_pool = ua_mobile_pool
        self.ua_desktop_pool = ua_desktop_pool

        # Ad/hover details
        self.hover_min = hover_min
        self.hover_max = hover_max
        self.ad_click_chance = ad_click_chance  # added onto global AD_CLICK_CHANCE

    def __repr__(self):
        return f"<Persona {self.name}>"


# -------------------------------------------------------------------
# DEFINE PERSONAS
# -------------------------------------------------------------------

PERSONAS = [
    Persona(
        name="Casual Mobile Scroller",
        description="Mostly on phone, light scrolling, low ad interest.",
        mobile_bias=0.82,
        scroll_speed=0.9,
        hesitation=0.9,
        ad_hover_rate=0.35,
        explore_rate=0.55,
        dwell_multiplier=1.1,
        ua_mobile_pool=[0, 1, 2],
        ua_desktop_pool=[0, 1],
        hover_min=0.4,
        hover_max=1.8,
        ad_click_chance=0.005,   # +0.5% on top of global
    ),
    Persona(
        name="Research Desktop",
        description="Desktop user, reads more, slower scroll, almost never clicks ads.",
        mobile_bias=0.15,
        scroll_speed=0.6,
        hesitation=1.4,
        ad_hover_rate=0.25,
        explore_rate=0.75,
        dwell_multiplier=1.4,
        ua_mobile_pool=[1, 3],
        ua_desktop_pool=[1, 2, 3],
        hover_min=0.6,
        hover_max=2.4,
        ad_click_chance=0.0,
    ),
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
        ad_click_chance=0.015,  # +1.5% on top of global
    ),
    Persona(
        name="Skimmer",
        description="Quick hits, little reading, low exploration.",
        mobile_bias=0.7,
        scroll_speed=1.6,
        hesitation=0.5,
        ad_hover_rate=0.25,
        explore_rate=0.35,
        dwell_multiplier=0.8,
        ua_mobile_pool=[1, 2],
        ua_desktop_pool=[0, 3],
        hover_min=0.3,
        hover_max=1.2,
        ad_click_chance=0.004,
    ),
    Persona(
        name="Deep Diver",
        description="Reads more deeply, moderate ad hover, rare ad clicks.",
        mobile_bias=0.45,
        scroll_speed=0.8,
        hesitation=1.5,
        ad_hover_rate=0.4,
        explore_rate=0.9,
        dwell_multiplier=1.5,
        ua_mobile_pool=[0, 1],
        ua_desktop_pool=[1, 2, 3],
        hover_min=0.7,
        hover_max=2.8,
        ad_click_chance=0.008,
    ),
]


def choose_persona():
    """
    Weighted random persona selection.
    You can tune the weights to bias which types show up more often.
    """
    weights = [3, 3, 2, 2, 2]  # same length as PERSONAS
    return random.choices(PERSONAS, weights=weights, k=1)[0]
