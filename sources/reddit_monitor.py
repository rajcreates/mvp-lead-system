# ─────────────────────────────────────────────
#  Reddit Monitor — no auth required
# ─────────────────────────────────────────────
import time
import requests
from datetime import datetime, timezone

HEADERS = {"User-Agent": "mvp-lead-monitor/1.0"}


def search_reddit(keyword: str, subreddits: list, lookback_hours: int = 24) -> list:
    """
    Search Reddit for posts/comments matching keyword.
    Uses the public JSON API — no credentials needed.
    """
    leads = []
    cutoff = time.time() - (lookback_hours * 3600)

    # Search across all target subreddits at once
    sub_str = "+".join(subreddits)
    url = (
        f"https://www.reddit.com/r/{sub_str}/search.json"
        f"?q={requests.utils.quote(keyword)}&sort=new&limit=25&restrict_sr=1"
    )

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return leads

        data = r.json()
        posts = data.get("data", {}).get("children", [])

        for post in posts:
            p = post.get("data", {})
            created = p.get("created_utc", 0)

            if created < cutoff:
                continue

            uid     = f"reddit_{p.get('id', '')}"
            title   = p.get("title", "")
            text    = p.get("selftext", "")
            link    = f"https://reddit.com{p.get('permalink', '')}"
            sub     = p.get("subreddit", "")
            author  = p.get("author", "")

            leads.append({
                "uid":     uid,
                "source":  f"Reddit r/{sub}",
                "title":   title,
                "body":    text,
                "url":     link,
                "keyword": keyword,
                "author":  author,
                "created": datetime.fromtimestamp(created, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
            })

        time.sleep(3)  # Respect Reddit rate limit (2 req/sec max)

    except Exception as e:
        print(f"[Reddit error] {keyword}: {e}")

    return leads
