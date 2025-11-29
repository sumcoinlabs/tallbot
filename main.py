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
                        help="Number of sessions to run")

    parser.add_argument("--xvfb", action="store_true",
                        help="Run using Xvfb virtual display")

    parser.add_argument("--gui", action="store_true",
                        help="Force GUI mode (visible browser window)")

    parser.add_argument("--browser", type=str, default=None,
                        help="Browser: chrome or firefox")

    args = parser.parse_args()

    # Priority rules:
    # 1. If --gui is used → force GUI, disable Xvfb
    # 2. If --xvfb is used → headless virtual display
    # 3. If neither → run visible GUI (default behavior)
    use_xvfb = args.xvfb and not args.gui
    force_gui = args.gui

    for i in range(args.sessions):
        log("[MAIN] Starting session {}".format(i + 1))

        persona = choose_persona()
        log("[PERSONA] {}".format(persona.name))

        driver, display, is_mobile = create_driver(
            persona,
            use_xvfb=use_xvfb,
            browser_name=args.browser
        )

        try:
            run_session(driver, persona)
        except Exception as e:
            log("[FATAL] Session crashed: {}".format(e))
        finally:
            try:
                driver.quit()
            except:
                pass
            if display:
                display.stop()

        sleep_time = random.uniform(3, 8)
        log("[MAIN] Resting {:.1f}s before next session".format(sleep_time))
        time.sleep(sleep_time)

    log("[MAIN] All sessions finished")


if __name__ == "__main__":
    main()
