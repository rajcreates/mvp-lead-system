#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# ─────────────────────────────────────────────
#  MVP Lead Monitor — Main Runner
#  Run: python monitor.py
#  Schedule: Task Scheduler (Windows) every 2 hours
# ─────────────────────────────────────────────
import time
from config import (
    MONITOR_KEYWORDS, SUBREDDITS, LOOKBACK_HOURS,
    AD_LIBRARY_COUNTRIES, AD_LIBRARY_KEYWORDS,
    FUNDING_KEYWORDS,
)
from notifier import send_lead, send_outbound_lead, send
from storage import is_new, mark_seen, save_lead
from sources.reddit_monitor   import search_reddit
from sources.hn_monitor        import search_hn
from sources.rss_monitor       import search_rss
from sources.fb_ads_monitor    import search_fb_ads_api
from sources.funded_startups   import get_producthunt_launches, get_crunchbase_funded, get_funding_news

# Optional: set these in config.py if you have keys
try:
    from config import FB_ACCESS_TOKEN
except ImportError:
    FB_ACCESS_TOKEN = None

try:
    from config import CRUNCHBASE_API_KEY
except ImportError:
    CRUNCHBASE_API_KEY = None


def run_inbound_monitor():
    """Scan Reddit, HN, RSS for people actively asking for MVP dev help."""
    print("\n═══ INBOUND MONITOR ═══")
    total = 0

    for keyword in MONITOR_KEYWORDS:
        print(f"  Scanning: '{keyword}'")
        all_leads = []

        # Reddit
        all_leads += search_reddit(keyword, SUBREDDITS, LOOKBACK_HOURS)

        # Hacker News
        all_leads += search_hn(keyword, LOOKBACK_HOURS)

        # RSS (IndieHackers, ProductHunt, DEV)
        all_leads += search_rss(keyword, LOOKBACK_HOURS)

        for lead in all_leads:
            uid = lead["uid"]
            if not is_new(uid):
                continue


            mark_seen(uid)
            save_lead(
                source  = lead["source"],
                lead_type = "inbound",
                title   = lead["title"],
                url     = lead["url"],
                keyword = lead["keyword"],
                snippet = lead.get("body", ""),
            )
            send_lead(
                source  = lead["source"],
                title   = lead["title"],
                body    = lead.get("body", ""),
                url     = lead["url"],
                keyword = lead["keyword"],
            )
            total += 1
            time.sleep(0.5)

    print(f"  ✓ {total} new inbound leads found")
    return total


def run_outbound_finder():
    """Find funded startups and ad-running businesses for cold outreach."""
    print("\n═══ OUTBOUND FINDER ═══")
    total = 0

    # ── ProductHunt recent launches ──────────────
    print("  Scanning: ProductHunt launches")
    ph_leads = get_producthunt_launches(lookback_hours=48)
    for lead in ph_leads:
        uid = lead["uid"]
        if not is_new(uid):
            continue
        mark_seen(uid)
        save_lead(
            source    = lead["source"],
            lead_type = "outbound_launch",
            title     = lead["name"],
            url       = lead["url"],
            keyword   = "recent_launch",
            snippet   = lead["detail"],
        )
        send_outbound_lead(
            source = lead["source"],
            name   = lead["name"],
            detail = lead["detail"],
            link   = lead["url"],
        )
        total += 1

    # ── Reddit: Founders announcing their own raises ──
    print("  Scanning: Reddit funding announcements")
    FUNDING_SUBS = ["startups", "entrepreneur", "Entrepreneur", "SaaS", "indiehackers", "startup"]
    for kw in FUNDING_KEYWORDS:
        reddit_funded = search_reddit(kw, FUNDING_SUBS, LOOKBACK_HOURS)
        for lead in reddit_funded:
            uid = lead["uid"]
            if not is_new(uid):
                continue
            mark_seen(uid)
            save_lead(
                source    = lead["source"],
                lead_type = "outbound_funded",
                title     = lead["title"],
                url       = lead["url"],
                keyword   = kw,
                snippet   = lead.get("body", ""),
            )
            send_outbound_lead(
                source = lead["source"],
                name   = lead["title"],
                detail = f"Just raised! Keyword: '{kw}'\n{lead.get('body','')[:200]}",
                link   = lead["url"],
            )
            total += 1
        time.sleep(2)

    # ── TechCrunch + Crunchbase News (free) ─────
    print("  Scanning: TechCrunch + Crunchbase News")
    news_leads = get_funding_news(lookback_hours=72)
    for lead in news_leads:
        uid = lead["uid"]
        if not is_new(uid):
            continue
        mark_seen(uid)
        save_lead(
            source    = lead["source"],
            lead_type = "outbound_funded",
            title     = lead["name"],
            url       = lead["url"],
            keyword   = "funding_news",
            snippet   = lead["detail"],
        )
        send_outbound_lead(
            source = lead["source"],
            name   = lead["name"],
            detail = lead["detail"],
            link   = lead["url"],
        )
        total += 1

    # ── Crunchbase API (paid) ────────────────────
    if CRUNCHBASE_API_KEY:
        print("  Scanning: Crunchbase funded startups")
        cb_leads = get_crunchbase_funded(api_key=CRUNCHBASE_API_KEY, lookback_days=7)
        for lead in cb_leads:
            uid = lead["uid"]
            if not is_new(uid):
                continue
            mark_seen(uid)
            save_lead(
                source    = lead["source"],
                lead_type = "outbound_funded",
                title     = lead["name"],
                url       = lead["url"],
                keyword   = "funded",
                snippet   = lead["detail"],
            )
            send_outbound_lead(
                source = lead["source"],
                name   = lead["name"],
                detail = lead["detail"],
                link   = lead["url"],
            )
            total += 1
    else:
        print("  [Crunchbase] Skipped — no API key in config.py")

    # ── Facebook Ad Library ──────────────────────
    if FB_ACCESS_TOKEN:
        print("  Scanning: Facebook Ad Library")
        for kw in AD_LIBRARY_KEYWORDS:
            from sources.fb_ads_monitor import search_fb_ads_api
            ad_leads = search_fb_ads_api(kw, AD_LIBRARY_COUNTRIES, FB_ACCESS_TOKEN)
            for lead in ad_leads:
                uid = lead["uid"]
                if not is_new(uid):
                    continue
                mark_seen(uid)
                save_lead(
                    source    = lead["source"],
                    lead_type = "outbound_ad",
                    title     = lead["title"],
                    url       = lead["url"],
                    keyword   = kw,
                    snippet   = lead.get("body", ""),
                )
                send_outbound_lead(
                    source = lead["source"],
                    name   = lead.get("page", lead["title"]),
                    detail = f"Running ad: '{kw}'\n{lead.get('body', '')[:200]}",
                    link   = lead["url"],
                )
                total += 1
    else:
        print("  [FB Ads] Skipped — no FB_ACCESS_TOKEN in config.py")

    print(f"  ✓ {total} new outbound leads found")
    return total


def main():
    print(f"\n{'='*50}")
    print("  MVP Lead System — Starting scan")
    print(f"{'='*50}")

    inbound  = run_inbound_monitor()
    outbound = run_outbound_finder()

    summary = f"Scan complete — {inbound} inbound + {outbound} outbound leads"
    print(f"\n✓ {summary}")
    send(f"📊 <b>Scan Complete</b>\n{inbound} inbound leads + {outbound} outbound leads\nAll saved to leads.csv")


if __name__ == "__main__":
    main()
