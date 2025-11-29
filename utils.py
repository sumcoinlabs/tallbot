# utils.py
from datetime import datetime

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open("traffic_engine.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")
