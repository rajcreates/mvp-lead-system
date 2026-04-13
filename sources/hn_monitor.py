# ─────────────────────────────────────────────
#  Hacker News Monitor — via Algolia API (free)
# ─────────────────────────────────────────────
import requests
from datetime import datetime, timezone, timedelta


def search_hn(keyword: str, lookback_hours: int = 24) -> list:
    """
    Search HN stories and comments via Algolia API.
    Free, no auth, very reliable.
    """
    leads  = []
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=lookback_hours)
    ts     = int(cutoff.timestamp())

    # Only search story titles — comments are too noisy
    url = (
        "https://hn.algolia.com/api/v1/search_by_date"
        f"?query={requests.utils.quote(keyword)}"
        f"&numericFilters=created_at_i>{ts}"
        "&tags=story"
        "&hitsPerPage=20"
    )

    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return leads

        hits = r.json().get("hits", [])

        for hit in hits:
            obj_id  = hit.get("objectID", "")
            uid     = f"hn_{obj_id}"
            title   = hit.get("title") or hit.get("comment_text", "")[:80]
            body    = hit.get("story_text") or hit.get("comment_text") or ""
            hn_url  = hit.get("url") or f"https://news.ycombinator.com/item?id={obj_id}"

            leads.append({
                "uid":     uid,
                "source":  "Hacker News",
                "title":   title,
                "body":    body,
                "url":     hn_url,
                "keyword": keyword,
            })

    except Exception as e:
        print(f"[HN error] {keyword}: {e}")

    return leads
