# ─────────────────────────────────────────────
#  Funded Startups Monitor
#  Sources: ProductHunt + TechCrunch + Crunchbase News
# ─────────────────────────────────────────────
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()

HEADERS = {"User-Agent": "mvp-lead-monitor/1.0"}


# ── ProductHunt: Recently launched (need tech iteration) ──────────────────────

def get_producthunt_launches(lookback_hours: int = 48) -> list:
    """
    ProductHunt RSS — founders who just launched often need
    v2 development, feature additions, or a full rebuild.
    These are warm outbound targets.
    """
    leads  = []
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=lookback_hours)

    try:
        r = requests.get("https://www.producthunt.com/feed", headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return leads

        root = ET.fromstring(r.content)
        # ProductHunt uses Atom (<entry>) not RSS (<item>)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall(".//atom:entry", ns) or root.findall(".//entry")

        for entry in entries:
            def _text(tag):
                el = entry.find(f"atom:{tag}", ns)
                return (el.text or "").strip() if el is not None else ""

            title   = _text("title")
            summary = _text("content") or _text("summary")
            pub     = _text("published") or _text("updated")
            link_el = entry.find("atom:link", ns) or entry.find("link")
            link    = (link_el.get("href", "") if link_el is not None else "")

            try:
                pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            except Exception:
                pub_dt = datetime.now(tz=timezone.utc)

            if pub_dt < cutoff:
                continue

            uid = f"ph_{hash(link)}"
            leads.append({
                "uid":    uid,
                "source": "ProductHunt",
                "name":   title,
                "detail": f"Just launched: {_strip_html(summary)[:200]}",
                "url":    link,
                "type":   "recent_launch",
            })

    except Exception as e:
        print(f"[ProductHunt error] {e}")

    return leads


# ── Crunchbase: Requires API key (free tier available) ────────────────────────

def get_crunchbase_funded(api_key: str = None, lookback_days: int = 7) -> list:
    """
    Fetch recently funded pre-seed/seed startups from Crunchbase.

    To get a free API key:
    1. Go to data.crunchbase.com
    2. Sign up for free Basic API access
    3. Add key to config.py as CRUNCHBASE_API_KEY

    Free tier: 200 requests/month
    """
    leads = []

    if not api_key:
        print(
            "[Crunchbase] No API key. To enable:\n"
            "  1. Go to data.crunchbase.com\n"
            "  2. Sign up for Basic (free) API access\n"
            "  3. Add key to config.py as CRUNCHBASE_API_KEY"
        )
        return leads

    cutoff = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    url = "https://api.crunchbase.com/api/v4/searches/funding_rounds"
    payload = {
        "field_ids": [
            "funded_organization_identifier",
            "funded_organization_location",
            "investment_type",
            "announced_on",
            "money_raised",
            "funded_organization_short_description",
        ],
        "query": [
            {
                "type": "predicate",
                "field_id": "announced_on",
                "operator_id": "gte",
                "values": [cutoff],
            },
            {
                "type": "predicate",
                "field_id": "investment_type",
                "operator_id": "includes",
                "values": ["pre_seed", "seed", "series_a"],
            },
        ],
        "order": [{"field_id": "announced_on", "sort": "desc"}],
        "limit": 50,
    }

    try:
        r = requests.post(
            url,
            json=payload,
            params={"user_key": api_key},
            timeout=20,
        )
        if r.status_code != 200:
            print(f"[Crunchbase] {r.status_code}: {r.text[:200]}")
            return leads

        entities = r.json().get("entities", [])

        for entity in entities:
            props   = entity.get("properties", {})
            org     = props.get("funded_organization_identifier", {})
            name    = org.get("value", "Unknown")
            desc    = props.get("funded_organization_short_description", "")
            stage   = props.get("investment_type", "")
            amount  = props.get("money_raised", {}).get("value_usd", 0)
            org_id  = org.get("permalink", "")
            link    = f"https://www.crunchbase.com/organization/{org_id}"

            uid = f"cb_{entity.get('uuid', hash(name))}"
            leads.append({
                "uid":    uid,
                "source": "Crunchbase",
                "name":   name,
                "detail": (
                    f"Stage: {stage.upper()} | "
                    f"Raised: ${amount:,} | "
                    f"{desc[:150]}"
                ),
                "url":    link,
                "type":   "funded_startup",
            })

    except Exception as e:
        print(f"[Crunchbase error] {e}")

    return leads


# ── TechCrunch + Crunchbase News: Free funding RSS feeds ─────────────────────

FUNDING_RSS_FEEDS = {
    "TechCrunch":          "https://techcrunch.com/feed/",
    "TechCrunch Startups": "https://techcrunch.com/category/startups/feed/",
    "Crunchbase News":     "https://news.crunchbase.com/feed/",
    "VentureBeat":         "https://venturebeat.com/feed/",
}

# Title must contain one of these to indicate a specific company raise
FUNDING_TITLE_KEYWORDS = [
    "raises", "raised", "secures", "closes", "funding round",
    "seed round", "pre-seed", "series a", "series b",
]
# Body can contain broader terms
FUNDING_BODY_KEYWORDS = [
    "million", "seed", "funding", "investment", "venture",
]


def get_funding_news(lookback_hours: int = 48) -> list:
    """
    Parse TechCrunch and Crunchbase News RSS for funding announcements.
    Free, no API key needed. Catches seed/Series-A raises as they're published.
    """
    leads  = []
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=lookback_hours)

    for source_name, feed_url in FUNDING_RSS_FEEDS.items():
        try:
            r = requests.get(feed_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue

            root  = ET.fromstring(r.content)
            items = root.findall(".//item")

            for item in items:
                title   = (item.findtext("title") or "").strip()
                desc    = _strip_html(item.findtext("description") or "")
                link    = (item.findtext("link") or "").strip()
                pub     = item.findtext("pubDate") or ""

                try:
                    pub_dt = parsedate_to_datetime(pub).replace(tzinfo=timezone.utc)
                except Exception:
                    pub_dt = datetime.now(tz=timezone.utc)

                if pub_dt < cutoff:
                    continue

                # Title must signal a specific company raise
                title_lower = title.lower()
                if not any(kw in title_lower for kw in FUNDING_TITLE_KEYWORDS):
                    continue

                uid = f"news_{hash(link)}"
                leads.append({
                    "uid":    uid,
                    "source": source_name,
                    "name":   title,
                    "detail": desc[:200],
                    "url":    link,
                    "type":   "funded_startup",
                })

        except Exception as e:
            print(f"[{source_name} error] {e}")

    return leads


# ── AngelList / Wellfound: Public listings ────────────────────────────────────

def get_angellist_startups(keyword: str = "MVP") -> list:
    """
    AngelList/Wellfound doesn't have a free public API.
    Best approach: manually search wellfound.com/jobs
    Filter: startup stage = seed, role = "technical co-founder"

    This function returns the search URL to open manually.
    """
    search_url = (
        f"https://wellfound.com/jobs?"
        f"role=technical-cofounder&"
        f"startup_stages[]=seed&startup_stages[]=early"
    )
    print(f"[AngelList] Manual search: {search_url}")
    return []
