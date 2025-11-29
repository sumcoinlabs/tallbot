# main.py
import argparse
import random
import time

from persona import choose_persona
from driver_setup import create_driver
from session import run_session
from utils import log


def parse_args():
    parser = argparse.ArgumentParser(description="Tallbot traffic engine")

    parser.add_argument(
        "--sessions",
        type=int,
        default=1,
        help="Number of independent sessions to run sequentially",
    )

    parser.add_argument(
        "--xvfb",
        action="store_true",
        help="Run under a virtual Xvfb display (headless server friendly)",
    )

    parser.add_argument(
        "--browser",
        type=str,
        default="auto",
        choices=["auto", "firefox", "chrome"],
        help="Force a specific browser or let config weights choose (auto)",
    )

    parser.add_argument(
        "--rest-min",
        type=int,
        default=15,
        help="Minimum seconds to rest between sessions",
    )

    parser.add_argument(
        "--rest-max",
        type=int,
        default=45,
        help="Maximum seconds to rest between sessions",
    )

    return parser.parse_args()


def run_once(args, session_index: int):
    persona = choose_persona()
    log(f"[RUN] Session {session_index} with persona: {persona.name}")

    browser_name = None if args.browser == "auto" else args.browser

    driver = None
    display = None

    try:
        driver, display, is_mobile = create_driver(
            persona=persona,
            use_xvfb=args.xvfb,
            browser_name=browser_name,
        )

        run_session(driver, persona, is_mobile)

    except Exception as e:
        log(f"[FATAL] Session {session_index} crashed: {e}")

    finally:
        log(f"[CLEANUP] Session {session_index}: closing driver/display")

        try:
            if driver is not None:
                driver.quit()
        except Exception:
            pass

        try:
            if display is not None:
                display.stop()
        except Exception:
            pass


def main():
    args = parse_args()

    log(
        f"[START] Tallbot starting with {args.sessions} session(s), "
        f"xvfb={args.xvfb}, browser={args.browser}"
    )

    for i in range(1, args.sessions + 1):
        run_once(args, i)

        if i < args.sessions:
            # random cool-down between sessions
            rest = random.uniform(args.rest_min, args.rest_max)
            log(f"[REST] Sleeping {rest:.1f}s before next session")
            time.sleep(rest)

    log("[DONE] All sessions complete.")


if __name__ == "__main__":
    main()
