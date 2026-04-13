# ─────────────────────────────────────────────
#  Telegram Notifier
# ─────────────────────────────────────────────
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send(message: str) -> bool:
    """Send a Telegram message. Returns True on success."""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[NOTIFY - not configured]", message[:120])
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[Telegram error] {e}")
        return False


def send_lead(source: str, title: str, body: str, url: str, keyword: str):
    msg = (
        f"🎯 <b>MVP Lead — {source}</b>\n\n"
        f"<b>Keyword:</b> {keyword}\n"
        f"<b>Title:</b> {title}\n\n"
        f"{body[:300]}{'...' if len(body) > 300 else ''}\n\n"
        f"🔗 <a href='{url}'>View post</a>"
    )
    return send(msg)


def send_outbound_lead(source: str, name: str, detail: str, link: str):
    msg = (
        f"🚀 <b>Outbound Lead — {source}</b>\n\n"
        f"<b>Company:</b> {name}\n"
        f"{detail}\n\n"
        f"🔗 <a href='{link}'>View</a>"
    )
    return send(msg)
