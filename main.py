# main.py
import argparse
import time
import random

from driver_setup import make_driver
from session import run_session
from utils import log


parser = argparse.ArgumentParser()
parser.add_argument("--sessions", type=int, default=1)
parser.add_argument("--gui", action="store_true")
parser.add_argument("--xvfb", action="store_true")
args = parser.parse_args()


if __name__ == "__main__":
    log("SUMCOIN TRAFFIC ENGINE v5.0 STARTED")

    for i in range(args.sessions):

        driver, persona = make_driver(use_xvfb=args.xvfb, force_gui=args.gui)
        run_session(driver, persona)
        driver.quit()

        # Between-session rest
        if i < args.sessions - 1:
            t = random.uniform(20, 60)
            log(f"[REST] {t:.1f}s")
            time.sleep(t)

    log("ALL SESSIONS COMPLETE.")
