import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

def notify(text: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
        j = json.loads(body)
        return bool(j.get("ok"))
    except Exception:
        return False

def fmt_event(title: str, **fields) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [f"🟦 {title}", f"🕒 {ts}"]
    for k, v in fields.items():
        parts.append(f"- {k}: {v}")
    return "\n".join(parts)
