# ─────────────────────────────────────────────
#  Seen-lead deduplication + CSV export
# ─────────────────────────────────────────────
import csv
import json
import os
from datetime import datetime

SEEN_FILE  = "seen_ids.json"
LEADS_FILE = "leads.csv"

LEADS_HEADERS = ["timestamp", "source", "type", "title", "url", "keyword", "snippet"]


def _load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def _save_seen(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


_seen = _load_seen()


def is_new(uid: str) -> bool:
    return uid not in _seen


def mark_seen(uid: str):
    _seen.add(uid)
    _save_seen(_seen)


def save_lead(source: str, lead_type: str, title: str, url: str, keyword: str, snippet: str):
    """Append lead to leads.csv"""
    write_header = not os.path.exists(LEADS_FILE)
    with open(LEADS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEADS_HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "source":    source,
            "type":      lead_type,
            "title":     title,
            "url":       url,
            "keyword":   keyword,
            "snippet":   snippet[:300],
        })
