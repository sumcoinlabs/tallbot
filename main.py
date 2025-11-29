# main.py
import argparse
import time
import random

from persona import choose_persona
from driver_setup import create_driver
from session import run_session
from utils import log


def main():
    parser = argparse.ArgumentParser(description="Tallbot Traffic Engine")

    parser.add_argument("--sessions", type=int, default=1,
                        help="How many sessions to run")

    parser.add_argument("--xvfb", action="store_true",
                        help="Run using Xvfb (headless virtual display)")

    parser.add_argument("--gui", action="store_true",
                        help="Force GUI mode (visible browser). Overrides --xvfb.")

    parser.add_argument("--browser", type=str, default=None,
                        choices=["chrome", "firefox", "auto", None],
                        help="Browser to use")

    args = parser.parse_args()

    # priority: GUI overrides Xvfb
    use_xvfb = args.xvfb and not args.gui

    for i in range(args.sessions):
        log("[MAIN] Starting session {}".format(i + 1))

        persona = choose_persona()
        log("[PERSONA] {}".format(persona.name))

        # create driver → returns (driver, display, is_mobile)
        driver, display, is_mobile = create_driver(
            persona,
            use_xvfb=use_xvfb,
            browser_name=args.browser
        )

        try:
            run_session(driver, persona, is_mobile)
        except Exception as e:
            log("[FATAL] Session crashed: {}".format(e))
        finally:
            try:
                driver.quit()
            except:
                pass
            if display:
                display.stop()

        rest = random.uniform(3, 8)
        log("[MAIN] Resting {:.1f}s".format(rest))
        time.sleep(rest)

    log("[MAIN] ALL sessions finished")


if __name__ == "__main__":
    main()
