# utils.py
import os
from datetime import datetime

from config import LOG_FILE


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def log(message: str):
    """
    Simple logger:
      - prints to stdout
      - appends to LOG_FILE
    """
    ts = _timestamp()
    line = f"[{ts}] {message}"

    # stdout
    print(line, flush=True)

    # file append
    try:
        # ensure directory exists if user sets LOG_FILE like "logs/traffic_engine.log"
        directory = os.path.dirname(LOG_FILE)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # logging should never crash the bot
        pass
