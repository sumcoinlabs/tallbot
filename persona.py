# persona.py
import random

class Persona:
    def __init__(self, name, description, mobile_bias, scroll_speed,
                 hesitation, ad_hover_rate, explore_rate, dwell_multiplier,
                 ua_mobile_pool, ua_desktop_pool,
                 hover_min=0.4, hover_max=2.4, ad_click_chance=0.0005):

        self.name = name
        self.description = description

        # Behavior weights
        self.mobile_bias = mobile_bias
        self.scroll_speed = scroll_speed
        self.hesitation = hesitation
        self.ad_hover_rate = ad_hover_rate
        self.explore_rate = explore_rate
        self.dwell_multiplier = dwell_multiplier

        # Hover / click realism
        self.hover_min = hover_min
        self.hover_max = hover_max
        self.ad_click_chance = ad_click_chance

        # User Agent selection pools
        self.ua_mobile_pool = ua_mobile_pool
        self.ua_desktop_pool = ua_desktop_pool


PERSONAS = [

    Persona(
        name="Mobile Young User",
        description="Fast scroller, distracted, mobile dominant.",
        mobile_bias=0.92,
        scroll_speed=1.4,
        hesitation=0.10,
        ad_hover_rate=0.15,
        explore_rate=0.38,
        dwell_multiplier=0.85,
        ua_mobile_pool=[0,1,2],
        ua_desktop_pool=[0],
        hover_min=0.3,
        hover_max=1.6,
        ad_click_chance=0.0005
    ),

    Persona(
        name="Mobile Power User",
        description="Confident, fast, scrolls deep.",
        mobile_bias=0.88,
        scroll_speed=1.0,
        hesitation=0.05,
        ad_hover_rate=0.10,
        explore_rate=0.52,
        dwell_multiplier=1.1,
        ua_mobile_pool=[0,1,2],
        ua_desktop_pool=[1],
        hover_min=0.3,
        hover_max=1.8,
        ad_click_chance=0.0008
    ),

    Persona(
        name="Desktop Researcher",
        description="Slow, intentional, reads everything.",
        mobile_bias=0.22,
        scroll_speed=2.0,
        hesitation=0.22,
        ad_hover_rate=0.30,
        explore_rate=0.66,
        dwell_multiplier=1.7,
        ua_mobile_pool=[1],
        ua_desktop_pool=[0,1,2],
        hover_min=0.8,
        hover_max=3.0,
        ad_click_chance=0.0012
    ),

    Persona(
        name="Crypto Enthusiast",
        description="Tech savvy, explores many links.",
        mobile_bias=0.41,
        scroll_speed=1.2,
        hesitation=0.14,
        ad_hover_rate=0.20,
        explore_rate=0.72,
        dwell_multiplier=1.4,
        ua_mobile_pool=[0,2],
        ua_desktop_pool=[1,2],
        hover_min=0.5,
        hover_max=2.2,
        ad_click_chance=0.0010
    ),

    Persona(
        name="Slow Reader",
        description="Reads carefully, very long dwell.",
        mobile_bias=0.52,
        scroll_speed=2.3,
        hesitation=0.28,
        ad_hover_rate=0.15,
        explore_rate=0.25,
        dwell_multiplier=2.0,
        ua_mobile_pool=[0],
        ua_desktop_pool=[2],
        hover_min=1.0,
        hover_max=4.2,
        ad_click_chance=0.0006
    ),

    Persona(
        name="Fast Clicker",
        description="Erratic, jumps around frequently.",
        mobile_bias=0.64,
        scroll_speed=0.9,
        hesitation=0.10,
        ad_hover_rate=0.22,
        explore_rate=0.88,
        dwell_multiplier=1.0,
        ua_mobile_pool=[1,2],
        ua_desktop_pool=[0,1],
        hover_min=0.3,
        hover_max=1.4,
        ad_click_chance=0.0020   # highest clicker
    ),
]


def choose_persona():
    weights = [3, 3, 1, 3, 1, 3]
    return random.choices(PERSONAS, weights=weights, k=1)[0]
