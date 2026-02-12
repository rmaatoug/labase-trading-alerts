import subprocess
import time
from datetime import datetime, timedelta

SCRIPT = "trade_breakout_multi_paper.py"

def sleep_until_next_5min():
    now = datetime.now()
    # prochain multiple de 5 minutes + 5 secondes
    next_min = (now.minute // 5 + 1) * 5
    if next_min >= 60:
        target = (now.replace(minute=0, second=5, microsecond=0) + timedelta(hours=1))
    else:
        target = now.replace(minute=next_min, second=5, microsecond=0)
    dt = (target - now).total_seconds()
    if dt > 0:
        time.sleep(dt)

while True:
    sleep_until_next_5min()
    print("\n=== RUN", datetime.now().isoformat(timespec="seconds"), "===")
    subprocess.run(["python3", SCRIPT], check=False)
