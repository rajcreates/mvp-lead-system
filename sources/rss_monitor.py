# ─────────────────────────────────────────────
#  RSS Monitor — IndieHackers, ProductHunt, DEV
# ─────────────────────────────────────────────
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

RSS_FEEDS = {
    # IndieHackers main RSS is broken; use their group feeds instead
    "IndieHackers/startups": "https://www.indiehackers.com/group/startups/feed.rss",
    "ProductHunt":           "https://www.producthunt.com/feed",
    "DEV Community":         "https://dev.to/feed",
}

HEADERS = {"User-Agent": "mvp-lead-monitor/1.0"}


def _parse_date(date_str: str):
    try:
        return parsedate_to_datetime(date_str).replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.now(tz=timezone.utc)


def search_rss(keyword: str, lookback_hours: int = 24) -> list:
    leads  = []
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=lookback_hours)
    kw     = keyword.lower()

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            r = requests.get(feed_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue

            root  = ET.fromstring(r.content)
            items = root.findall(".//item")

            for item in items:
                title   = (item.findtext("title") or "").strip()
                desc    = (item.findtext("description") or "").strip()
                link    = (item.findtext("link") or "").strip()
                pub     = item.findtext("pubDate") or ""
                pub_dt  = _parse_date(pub)

                if pub_dt < cutoff:
                    continue

                combined = (title + " " + desc).lower()
                if kw not in combined:
                    continue

                uid = f"rss_{source_name}_{hash(link)}"
                leads.append({
                    "uid":     uid,
                    "source":  source_name,
                    "title":   title,
                    "body":    desc,
                    "url":     link,
                    "keyword": keyword,
                })

        except Exception as e:
            print(f"[RSS error] {source_name} / {keyword}: {e}")

    return leads
